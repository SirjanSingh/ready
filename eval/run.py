"""Score Ready's footprint prediction and readiness verdict against a pairs file.

    uv run python eval/run.py --variant grep|model --k 5 [--limit N] [--pairs evidence/heldout.jsonl]

For each pair the repo is checked out at the fix PR's base commit and Ready sees only the
issue as filed (title + body, no comments). Writes evidence/results-<variant>[-<set>].json
and appends a summary to evidence/results.md.

Sets: evidence/pairs.jsonl is the DEV set (ready/checklist.py was calibrated on it in
a0a5b79, so its readiness numbers are optimistic). evidence/heldout.jsonl is HELD-OUT.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checkout import PAIRS, ROOT, checkout  # noqa: E402

EVIDENCE = ROOT / "evidence"
CUTOFFS = (1, 3, 5)

try:
    sys.path.insert(0, str(ROOT))
    from ready.api import check, predict_footprint  # type: ignore
    ENGINE_ERROR = None
except Exception as exc:  # engine not importable yet
    check = predict_footprint = None
    ENGINE_ERROR = f"{type(exc).__name__}: {exc}"


# ---------- internal fallback baseline (used only if ready.api cannot be imported) ----------

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_./]{2,}")
_STOP = set("the and for with that this from have not are was but you can when what which "
            "there their then than into also should would could does using used use like "
            "python error issue bug code example expected actual version none true false self".split())


def _baseline_predict(issue_text: str, repo: Path, k: int) -> list[str]:
    files = subprocess.run(["git", "-C", str(repo), "ls-files", "*.py", "*.ts"],
                           capture_output=True, text=True, encoding="utf-8").stdout.split()
    files = [f for f in files if "tests/" not in f and not f.startswith(("docs/", "docs_src/"))]
    terms = {t.strip("./").lower() for t in _TOKEN.findall(issue_text)}
    terms = {t for t in terms if t not in _STOP and len(t) > 3}
    scores: Counter[str] = Counter()
    for f in files:
        low = f.lower()
        for t in terms:
            if "/" in t and low.endswith(t):
                scores[f] += 10
            elif t.split(".")[-1] == Path(low).stem:
                scores[f] += 5
        try:
            text = (repo / f).read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        for t in terms:
            if t.isidentifier() and t in text:
                scores[f] += 1
    return [f for f, _ in scores.most_common(k)]


# ---------- scoring ----------

CODE_EXT = (".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs")


def engine_state() -> str:
    """HEAD short sha, the last commit touching ready/, and a marker if ready/ has uncommitted edits."""
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    sha = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%h", "--", "ready"],
                         capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "ready"],
                           capture_output=True, text=True).stdout.strip()
    return f"HEAD {head} (ready/ last changed in {sha})" + (" +uncommitted ready/ edits" if dirty else "")


def set_name(pairs_path: Path) -> str:
    return "dev" if pairs_path.resolve() == PAIRS.resolve() else "held-out"


def results_path(variant: str, pairs_path: Path) -> Path:
    suffix = "" if set_name(pairs_path) == "dev" else f"-{pairs_path.stem}"
    return EVIDENCE / f"results-{variant}{suffix}.json"


def norm(p: str) -> str:
    p = p.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def has_code_truth(row: dict) -> bool:
    return any(f.endswith(CODE_EXT) for f in row["truth"])


def score(pred: list[str], truth: list[str]) -> dict:
    t = set(truth)
    out = {}
    for c in CUTOFFS:
        top = set(pred[:c])
        inter = top & t
        out[f"hit@{c}"] = bool(inter)
        out[f"cov@{c}"] = len(inter) / len(t) if t else 0.0
    out["first_hit_rank"] = next((i + 1 for i, p in enumerate(pred) if p in t), None)
    return out


def summarize(rows: list[dict]) -> dict:
    ok = [r for r in rows if r.get("error") is None]
    s = {"n": len(ok), "errors": len(rows) - len(ok)}
    for c in CUTOFFS:
        s[f"hit@{c}"] = sum(r["metrics"][f"hit@{c}"] for r in ok) / len(ok) if ok else 0.0
        s[f"cov@{c}"] = sum(r["metrics"][f"cov@{c}"] for r in ok) / len(ok) if ok else 0.0
    s["truth_files"] = sum(len(r["truth"]) for r in ok)
    s["truth_files_absent_at_base"] = sum(len(r["truth_absent_at_base"]) for r in ok)
    return s


def confusion(rows: list[dict]) -> dict:
    cm = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for r in rows:
        if r.get("verdict_status") is None:
            continue
        pred = r["verdict_status"] == "needs_human"
        gold = r["needed_clarification"]
        cm[("t" if pred == gold else "f") + ("p" if pred else "n")] += 1
    n = sum(cm.values())
    prec = cm["tp"] / (cm["tp"] + cm["fp"]) if cm["tp"] + cm["fp"] else None
    rec = cm["tp"] / (cm["tp"] + cm["fn"]) if cm["tp"] + cm["fn"] else None
    neg = cm["fp"] + cm["tn"]
    cm.update(n=n, accuracy=(cm["tp"] + cm["tn"]) / n if n else None, precision=prec,
              recall=rec, predicted_needs_human=cm["tp"] + cm["fp"], gold_positive=cm["tp"] + cm["fn"],
              needs_human_rate_on_negatives=cm["fp"] / neg if neg else None)
    return cm


def by_source(rows: list[dict]) -> dict:
    """needs_human rate per (source, gold label); dev pairs predate `source` and count as random."""
    out: dict = {}
    for r in rows:
        if r.get("verdict_status") is None:
            continue
        key = f"{r.get('source') or 'random'} / {'pos' if r['needed_clarification'] else 'neg'}"
        n, h = out.get(key, (0, 0))
        out[key] = (n + 1, h + (r["verdict_status"] == "needs_human"))
    return {k: {"n": n, "needs_human": h, "rate": h / n} for k, (n, h) in sorted(out.items())}


def fmt(x) -> str:
    if x is None:
        return "n/a"
    return f"{x:.3f}" if isinstance(x, float) else str(x)


def write_markdown(variant: str, k: int, rows: list[dict], overall: dict, per_repo: dict,
                   cm: dict, note: str | None, elapsed: float | None, set_label: str = "dev",
                   pairs_file: str = "evidence/pairs.jsonl", src: dict | None = None) -> None:
    lines = [
        f"\n## {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} | {set_label.upper()} set | "
        f"variant `{variant}` | k={k} | n={overall['n']}",
        "",
        f"Set: {set_label} (`{pairs_file}`)."
        + (" ready/checklist.py was calibrated on these issues, so readiness numbers here are optimistic."
           if set_label == "dev" else " None of these issues were used to build or tune Ready."),
        "",
    ]
    if note:
        lines += [f"Note: {note}", ""]
    lines += [
        f"Pairs scored: {overall['n']}, errors: {overall['errors']}, wall time: "
        f"{f'{elapsed:.0f}s' if elapsed is not None else 'n/a'}. "
        f"Truth files: {overall['truth_files']}, of which {overall['truth_files_absent_at_base']} "
        "do not exist at base_sha (new files, unpredictable by retrieval).",
        "",
        "hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.",
        "",
        "| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    code_only = summarize([r for r in rows if has_code_truth(r)])
    for name, s in [*sorted(per_repo.items()), ("**overall**", overall),
                    ("overall, pairs with a code file in truth", code_only)]:
        lines.append(f"| {name} | {s['n']} | " + " | ".join(
            fmt(s[f"{m}@{c}"]) for m in ("hit", "cov") for c in CUTOFFS) + " |")
    lines += [
        "",
        "Readiness check: `verdict.status == \"needs_human\"` vs proxy label `needed_clarification`.",
        "",
        "| | gold needed_clarification | gold not |",
        "|---|---|---|",
        f"| predicted needs_human | TP {cm['tp']} | FP {cm['fp']} |",
        f"| predicted agent_ready | FN {cm['fn']} | TN {cm['tn']} |",
        "",
        f"n={cm['n']}, accuracy {fmt(cm['accuracy'])}, precision {fmt(cm['precision'])}, "
        f"recall {fmt(cm['recall'])}, predicted needs_human {cm['predicted_needs_human']}, "
        f"gold positives {cm['gold_positive']}. needs_human rate on gold positives "
        f"{fmt(cm['recall'])}, on gold negatives (false-alarm rate) {fmt(cm.get('needs_human_rate_on_negatives'))}.",
        "",
    ]
    if src:
        lines += ["needs_human rate by how the pair was selected:", "",
                  "| source / gold | n | needs_human | rate |", "|---|---|---|---|"]
        lines += [f"| {key} | {v['n']} | {v['needs_human']} | {fmt(v['rate'])} |" for key, v in src.items()]
        lines.append("")
    lines += [
        "Worst 10 misses (lowest cov@5, fewest true files first):",
        "",
    ]
    ok = [r for r in rows if r.get("error") is None]
    worst = sorted(ok, key=lambda r: (r["metrics"]["cov@5"], len(r["truth"]), r["repo"]))[:10]
    for r in worst:
        lines.append(f"- {r['issue_url']} cov@5={fmt(r['metrics']['cov@5'])} | truth: "
                     f"{', '.join(r['truth'][:4])}{' ...' if len(r['truth']) > 4 else ''} | "
                     f"predicted: {', '.join(r['predicted'][:3]) or '(none)'}")
    errs = [r for r in rows if r.get("error")]
    if errs:
        lines += ["", "Errors:", ""]
        lines += [f"- {r['issue_url']}: {r['error'].splitlines()[-1][:200]}" for r in errs[:10]]
    md = EVIDENCE / "results.md"
    if not md.exists():
        md.write_text("# Ready eval results\n\nAppended by `eval/run.py`.\n",
                      encoding="utf-8")
    with md.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["grep", "model"], required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--pairs", default=str(PAIRS.relative_to(ROOT)),
                    help="pairs file; evidence/pairs.jsonl is the dev set, anything else is held-out")
    ap.add_argument("--rescore", action="store_true",
                    help="recompute metrics from evidence/results-<variant>.json instead of running Ready")
    args = ap.parse_args()
    pairs_path = Path(args.pairs) if Path(args.pairs).is_absolute() else ROOT / args.pairs
    if args.rescore:
        rescore(args.variant, pairs_path)
        return

    use_model = args.variant == "model"
    variant = args.variant if ENGINE_ERROR is None else "baseline-internal"
    note = None
    if ENGINE_ERROR:
        note = f"ready.api import failed ({ENGINE_ERROR}); used the internal grep baseline."
        print(note, file=sys.stderr)

    pairs = [json.loads(l) for l in pairs_path.open(encoding="utf-8") if l.strip()]
    if args.limit:
        pairs = pairs[: args.limit]
    pairs.sort(key=lambda p: (p["repo"], p["base_sha"]))

    engine_before = engine_state()
    rows: list[dict] = []
    t0 = time.time()
    for i, p in enumerate(pairs, 1):
        truth = [norm(f) for f in p["changed_files_src"]]
        row = {"repo": p["repo"], "issue_number": p["issue_number"], "issue_url": p["issue_url"],
               "pr_number": p["pr_number"], "base_sha": p["base_sha"], "truth": truth,
               "needed_clarification": p["needed_clarification"], "source": p.get("source"),
               "predicted": [],
               "verdict_status": None, "error": None}
        text = f"{p['issue_title']}\n\n{p['issue_body']}"
        try:
            repo = checkout(p["repo"], p["base_sha"])
            row["truth_absent_at_base"] = [f for f in truth if not (repo / f).exists()]
            if ENGINE_ERROR is None:
                verdict = check(text, repo, use_model=use_model)
                if use_model or args.k > 8:
                    pred = predict_footprint(text, repo, k=args.k, use_model=use_model)
                else:
                    # without the model, predict_footprint == candidate_files[:k] == verdict.footprint[:k]
                    # (gate.py keeps the grep order, cut at 8), so one gate call is enough
                    pred = verdict.footprint
                row["verdict_status"] = verdict.status
                row["verdict"] = verdict.to_dict() if hasattr(verdict, "to_dict") else str(verdict)
            else:
                pred = _baseline_predict(text, repo, args.k)
            row["predicted"] = [norm(x) for x in pred][: args.k]
            row["metrics"] = score(row["predicted"], truth)
        except Exception:
            row["error"] = traceback.format_exc()
            row.setdefault("truth_absent_at_base", [])
        rows.append(row)
        m = row.get("metrics") or {}
        print(f"[{i}/{len(pairs)}] {p['repo']}#{p['issue_number']} hit@5={m.get('hit@5')} "
              f"status={row['verdict_status']}{' ERROR' if row['error'] else ''}", file=sys.stderr)
    engine_after = engine_state()
    engine = f"engine {engine_before}" + (
        "" if engine_after == engine_before
        else f" at start, {engine_after} at end (ready/ changed during the run; numbers may mix versions)")
    note = f"{note} {engine}." if note else f"{engine}."
    report(variant, args.k, rows, note, time.time() - t0, pairs_path)


def report(variant: str, k: int, rows: list[dict], note: str | None, elapsed: float | None,
           pairs_path: Path = PAIRS) -> None:
    ok = [r for r in rows if r["error"] is None]
    overall = summarize(rows)
    per_repo = {repo: summarize([r for r in rows if r["repo"] == repo]) for repo in sorted({r["repo"] for r in rows})}
    code_only = summarize([r for r in rows if has_code_truth(r)])
    cm = confusion(ok)
    src = by_source(ok)
    label = set_name(pairs_path)
    rel = pairs_path.resolve().relative_to(ROOT).as_posix()

    out = results_path(variant, pairs_path)
    out.write_text(json.dumps({
        "variant": variant, "k": k, "date": dt.datetime.now().isoformat(timespec="seconds"),
        "set": label, "pairs_file": rel,
        "note": note, "elapsed_s": round(elapsed) if elapsed is not None else None, "overall": overall,
        "overall_code_truth_only": code_only, "per_repo": per_repo, "confusion": cm,
        "needs_human_by_source": src, "pairs": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(variant, k, rows, overall, per_repo, cm, note, elapsed, label, rel, src)
    print(json.dumps({"set": label, "overall": overall, "code_truth_only": code_only, "confusion": cm,
                      "by_source": src}, indent=2), file=sys.stderr)
    print(f"wrote {out} and appended evidence/results.md", file=sys.stderr)


def rescore(variant: str, pairs_path: Path = PAIRS) -> None:
    """Recompute metrics from a saved results file without re-running Ready (truth re-read from pairs)."""
    saved = json.loads(results_path(variant, pairs_path).read_text(encoding="utf-8"))
    pairs = {(p["repo"], p["issue_number"]): p for p in
             (json.loads(l) for l in pairs_path.open(encoding="utf-8") if l.strip())}
    rows = saved["pairs"]
    for r in rows:
        r["truth"] = [norm(f) for f in pairs[(r["repo"], r["issue_number"])]["changed_files_src"]]
        r["truth_absent_at_base"] = [norm(f) for f in r.get("truth_absent_at_base", [])]
        if r.get("error") is None:
            r["predicted"] = [norm(x) for x in r["predicted"]]
            r["metrics"] = score(r["predicted"], r["truth"])
    note = ((saved.get("note") + " ") if saved.get("note") else "") + \
        f"Rescored on {dt.date.today()} from the run dated {saved['date']} (no new predictions)."
    report(saved["variant"], saved["k"], rows, note, saved.get("elapsed_s"), pairs_path)


if __name__ == "__main__":
    main()
