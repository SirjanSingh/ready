"""Score Ready's footprint prediction and readiness verdict against evidence/pairs.jsonl.

    uv run python eval/run.py --variant grep|model --k 5 [--limit N]

For each pair the repo is checked out at the fix PR's base commit and Ready sees only the
issue as filed (title + body, no comments). Writes evidence/results-<variant>.json and
appends a summary to evidence/results.md.
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

def norm(p: str) -> str:
    return p.replace("\\", "/").lstrip("./")


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
    cm.update(n=n, accuracy=(cm["tp"] + cm["tn"]) / n if n else None, precision=prec,
              recall=rec, predicted_needs_human=cm["tp"] + cm["fp"], gold_positive=cm["tp"] + cm["fn"])
    return cm


def fmt(x) -> str:
    if x is None:
        return "n/a"
    return f"{x:.3f}" if isinstance(x, float) else str(x)


def write_markdown(variant: str, k: int, rows: list[dict], overall: dict, per_repo: dict,
                   cm: dict, note: str | None, elapsed: float) -> None:
    lines = [
        f"\n## {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} | variant `{variant}` | k={k} | n={overall['n']}",
        "",
    ]
    if note:
        lines += [f"Note: {note}", ""]
    lines += [
        f"Pairs scored: {overall['n']}, errors: {overall['errors']}, wall time: {elapsed:.0f}s. "
        f"Truth files: {overall['truth_files']}, of which {overall['truth_files_absent_at_base']} "
        "do not exist at base_sha (new files, unpredictable by retrieval).",
        "",
        "hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.",
        "",
        "| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, s in [*sorted(per_repo.items()), ("**overall**", overall)]:
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
        f"gold positives {cm['gold_positive']}.",
        "",
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
        md.write_text("# Ready eval results\n\nAppended by `eval/run.py`. Pairs: `evidence/pairs.jsonl`.\n",
                      encoding="utf-8")
    with md.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["grep", "model"], required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    use_model = args.variant == "model"
    variant = args.variant if ENGINE_ERROR is None else "baseline-internal"
    note = None
    if ENGINE_ERROR:
        note = f"ready.api import failed ({ENGINE_ERROR}); used the internal grep baseline."
        print(note, file=sys.stderr)

    pairs = [json.loads(l) for l in PAIRS.open(encoding="utf-8") if l.strip()]
    if args.limit:
        pairs = pairs[: args.limit]
    pairs.sort(key=lambda p: (p["repo"], p["base_sha"]))

    rows: list[dict] = []
    t0 = time.time()
    for i, p in enumerate(pairs, 1):
        truth = [norm(f) for f in p["changed_files_src"]]
        row = {"repo": p["repo"], "issue_number": p["issue_number"], "issue_url": p["issue_url"],
               "pr_number": p["pr_number"], "base_sha": p["base_sha"], "truth": truth,
               "needed_clarification": p["needed_clarification"], "predicted": [],
               "verdict_status": None, "error": None}
        text = f"{p['issue_title']}\n\n{p['issue_body']}"
        try:
            repo = checkout(p["repo"], p["base_sha"])
            row["truth_absent_at_base"] = [f for f in truth if not (repo / f).exists()]
            if ENGINE_ERROR is None:
                pred = predict_footprint(text, repo, k=args.k, use_model=use_model)
                verdict = check(text, repo, use_model=use_model)
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
    elapsed = time.time() - t0

    ok = [r for r in rows if r["error"] is None]
    overall = summarize(rows)
    per_repo = {repo: summarize([r for r in rows if r["repo"] == repo]) for repo in sorted({r["repo"] for r in rows})}
    cm = confusion(ok)

    out = EVIDENCE / f"results-{variant}.json"
    out.write_text(json.dumps({
        "variant": variant, "k": args.k, "date": dt.datetime.now().isoformat(timespec="seconds"),
        "note": note, "overall": overall, "per_repo": per_repo, "confusion": cm, "pairs": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(variant, args.k, rows, overall, per_repo, cm, note, elapsed)
    print(json.dumps({"overall": overall, "confusion": cm}, indent=2), file=sys.stderr)
    print(f"wrote {out} and appended evidence/results.md", file=sys.stderr)


if __name__ == "__main__":
    main()
