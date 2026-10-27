"""Collect (issue, merged fix PR) pairs from GitHub into evidence/pairs.jsonl.

Stdlib plus the authenticated `gh` CLI only. Usage:

    python eval/fetch.py [--per-repo 20] [--max-total 60]
    python eval/fetch.py --repos pallets/flask,psf/requests --per-repo 10 --max-total 40 \
        --no-fallback --out evidence/heldout.jsonl --exclude evidence/pairs.jsonl \
        --positives-from pallets/flask,encode/httpx --positive-target 15

Every pair carries `source`: "random" (sampled from recently updated closed issues),
"label" (issue carries an info-request label, so it counts as needed_clarification) or
"regex" (found by scanning for issues where the maintainer-question regex fires).

A pair is usable when the issue has a body and its closing PR (same repo, merged) touches
between 1 and 15 source files once docs, tests, changelogs, markdown and lockfiles are dropped.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence" / "pairs.jsonl"

REPOS = ["fastapi/sqlmodel", "encode/httpx", "pydantic/pydantic"]
FALLBACK_REPO = "pallets/click"
MIN_PER_REPO = 12
MAX_SRC_FILES = 15

MAINTAINER_ASSOC = {"OWNER", "MEMBER", "COLLABORATOR", "CONTRIBUTOR"}
ASKS_FOR_INFO = re.compile(
    r"can you|could you|would you|what version|which version|reproduc|minimal|example|"
    r"more info|more detail|which|share (?:the|your|a)|traceback|stack ?trace",
    re.IGNORECASE,
)

LOCKFILES = {"uv.lock", "poetry.lock", "pdm.lock", "pipfile.lock", "package-lock.json",
             "yarn.lock", "pnpm-lock.yaml", "cargo.lock"}

SEARCH_QUERY = """
query($q: String!, $cursor: String) {
  search(query: $q, type: ISSUE, first: 25, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on Issue {
        number title body createdAt
        author { login }
        labels(first: 20) { nodes { name } }
        comments(first: 40) {
          nodes { author { login } authorAssociation createdAt body }
        }
        closedByPullRequestsReferences(first: 5, includeClosedPrs: false) {
          nodes {
            number merged mergedAt createdAt baseRefOid
            repository { nameWithOwner }
            commits(first: 1) {
              nodes { commit { oid committedDate parents(first: 1) { nodes { oid } } } }
            }
          }
        }
      }
    }
  }
}
"""


def gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {proc.stderr.strip()[:500]}")
    return proc.stdout


def is_src_file(path: str) -> bool:
    p = path.replace("\\", "/")
    parts = p.split("/")
    name = parts[-1]
    low = name.lower()
    if parts[0] in {"docs", "docs_src"}:
        return False
    if "tests" in parts[:-1] or parts[0] == "test":
        return False
    if low.startswith("changelog") or low.endswith(".md") or low in LOCKFILES:
        return False
    return True


def pr_files(repo: str, number: int) -> list[str]:
    out = gh("api", f"repos/{repo}/pulls/{number}/files", "--paginate", "--jq", ".[].filename")
    return [line.strip() for line in out.splitlines() if line.strip()]


def clarification(issue: dict, pr_created_at: str) -> tuple[bool, dict | None]:
    """Proxy label: a maintainer-ish person (not the reporter) asked for info before the PR."""
    reporter = (issue.get("author") or {}).get("login")
    for c in issue["comments"]["nodes"]:
        author = (c.get("author") or {}).get("login")
        if not author or author == reporter:
            continue
        if c.get("authorAssociation") not in MAINTAINER_ASSOC:
            continue
        if c["createdAt"] >= pr_created_at:
            continue
        body = c.get("body") or ""
        if "?" not in body:
            continue
        m = ASKS_FOR_INFO.search(body)
        if not m:
            continue
        lo, hi = max(0, m.start() - 120), min(len(body), m.end() + 120)
        return True, {"author": author, "created_at": c["createdAt"], "match": m.group(0),
                      "snippet": body[lo:hi].replace("\r", "")}
    return False, None


# Labels that mean "a maintainer could not act on this as filed". Checked against the label
# lists of all eight eval repos on 2026-10-27; starlette and click have none of these.
INFO_LABEL = re.compile(
    r"^(?:question|question/not a bug|waiting|need-info|needs info|needs more information|"
    r"awaiting author response|needs reproduction|more info needed|waiting for author)$",
    re.IGNORECASE,
)


def build_pair(repo: str, issue: dict, need_regex: bool = False) -> tuple[dict | None, str]:
    if not (issue.get("body") or "").strip():
        return None, "empty body"
    prs = [p for p in issue["closedByPullRequestsReferences"]["nodes"]
           if p and p.get("merged") and p["repository"]["nameWithOwner"].lower() == repo.lower()]
    if not prs:
        return None, "no merged same-repo PR"
    prs.sort(key=lambda p: p["mergedAt"])
    if need_regex and not clarification(issue, max(p["createdAt"] for p in prs))[0]:
        return None, "regex did not fire"  # cheap pre-check before the per-PR files call
    last_reason = "no usable PR"
    for pr in prs:
        files = pr_files(repo, pr["number"])
        src = [f for f in files if is_src_file(f)]
        if not src:
            last_reason = "no source files"
            continue
        if len(src) > MAX_SRC_FILES:
            last_reason = f"{len(src)} source files"
            continue
        commits = pr["commits"]["nodes"]
        first = commits[0]["commit"] if commits else None
        base = pr.get("baseRefOid")
        if not base and first and first["parents"]["nodes"]:
            base = first["parents"]["nodes"][0]["oid"]
        if not base:
            last_reason = "no base sha"
            continue
        needed, evidence = clarification(issue, pr["createdAt"])
        return {
            "repo": repo,
            "issue_number": issue["number"],
            "issue_url": f"https://github.com/{repo}/issues/{issue['number']}",
            "issue_title": issue["title"],
            "issue_body": issue["body"],
            "comments": [
                {"author": (c.get("author") or {}).get("login"),
                 "author_association": c.get("authorAssociation"),
                 "created_at": c["createdAt"], "body": c.get("body") or ""}
                for c in issue["comments"]["nodes"]
            ],
            "issue_author": (issue.get("author") or {}).get("login"),
            "issue_created_at": issue["createdAt"],
            "pr_number": pr["number"],
            "pr_url": f"https://github.com/{repo}/pull/{pr['number']}",
            "pr_merged_at": pr["mergedAt"],
            "pr_created_at": pr["createdAt"],
            "base_sha": base,
            "changed_files": files,
            "changed_files_src": src,
            "first_fix_commit_time": first["committedDate"] if first else None,
            "labels": [l["name"] for l in (issue.get("labels") or {}).get("nodes", [])],
            "needed_clarification": needed,
            "clarification_evidence": evidence,
        }, "ok"
    return None, last_reason


def collect(repo: str, want: int, max_pages: int = 12, query: str | None = None,
            keep=None, need_regex: bool = False, skip: set | None = None) -> list[dict]:
    q = query or f"repo:{repo} is:issue is:closed linked:pr sort:updated-desc"
    cursor = None
    pairs: list[dict] = []
    skipped: dict[str, int] = {}
    skip = skip if skip is not None else set()
    for _ in range(max_pages):
        args = ["api", "graphql", "-f", f"query={SEARCH_QUERY}", "-f", f"q={q}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        data = json.loads(gh(*args))["data"]["search"]
        for issue in data["nodes"]:
            if not issue or "number" not in issue:
                continue
            if (repo, issue["number"]) in skip:
                skipped["already used"] = skipped.get("already used", 0) + 1
                continue
            pair, reason = build_pair(repo, issue, need_regex=need_regex)
            if pair and keep and not keep(pair):
                pair, reason = None, "filtered"
            if pair:
                pairs.append(pair)
                skip.add((repo, issue["number"]))
                if len(pairs) >= want:
                    break
            else:
                skipped[reason] = skipped.get(reason, 0) + 1
        if len(pairs) >= want or not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]
    print(f"{repo} [{q[len(f'repo:{repo} '):]}]: {len(pairs)} pairs; skipped {skipped}", file=sys.stderr)
    return pairs


def repo_info_labels(repo: str) -> list[str]:
    names = gh("api", f"repos/{repo}/labels", "--paginate", "--jq", ".[].name").splitlines()
    return [n.strip() for n in names if INFO_LABEL.match(n.strip())]


def collect_positives(repos: list[str], target: int, skip: set) -> list[dict]:
    """Label hits first (stronger signal), then regex-only scans spread over the repos."""
    found: list[dict] = []
    for repo in repos:
        for label in repo_info_labels(repo):
            q = f'repo:{repo} is:issue is:closed linked:pr label:"{label}" sort:updated-desc'
            for pair in collect(repo, 4, max_pages=4, query=q, skip=skip):  # cap so no repo dominates
                ev = {"label": label}
                if pair["clarification_evidence"]:
                    ev["regex"] = pair["clarification_evidence"]
                pair.update(source="label", needed_clarification=True, clarification_evidence=ev)
                found.append(pair)
    print(f"label positives: {len(found)}", file=sys.stderr)
    if len(found) < target:
        per_repo = max(1, -(-(target - len(found)) // len(repos)))
        for repo in repos:
            q = f"repo:{repo} is:issue is:closed linked:pr comments:>=2 sort:updated-desc"
            for pair in collect(repo, per_repo, max_pages=6, query=q, need_regex=True,
                                keep=lambda p: p["needed_clarification"], skip=skip):
                pair["source"] = "regex"
                found.append(pair)
    return found


def load_keys(paths: list[str]) -> set:
    keys = set()
    for path in paths:
        f = Path(path) if Path(path).is_absolute() else ROOT / path
        if f.exists():
            keys |= {(p["repo"], p["issue_number"]) for p in
                     (json.loads(l) for l in f.open(encoding="utf-8") if l.strip())}
    return keys


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-repo", type=int, default=20)
    ap.add_argument("--max-total", type=int, default=60)
    ap.add_argument("--repos", default=",".join(REPOS), help="comma-separated owner/name list")
    ap.add_argument("--no-fallback", action="store_true", help=f"never top up from {FALLBACK_REPO}")
    ap.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    ap.add_argument("--exclude", default="", help="comma-separated pair files whose issues must not reappear")
    ap.add_argument("--positives-from", default="", help="comma-separated repos to mine for positives")
    ap.add_argument("--positive-target", type=int, default=10)
    args = ap.parse_args()
    repos = [r.strip() for r in args.repos.split(",") if r.strip()]
    out = Path(args.out) if Path(args.out).is_absolute() else ROOT / args.out
    skip = load_keys([x for x in args.exclude.split(",") if x.strip()])

    all_pairs: list[dict] = []
    for repo in repos:
        room = args.max_total - len(all_pairs)
        if room <= 0:
            break
        all_pairs += collect(repo, min(args.per_repo, room), skip=skip)

    counts = {r: sum(p["repo"] == r for p in all_pairs) for r in repos}
    if not args.no_fallback and any(n < MIN_PER_REPO for n in counts.values()):
        room = args.max_total - len(all_pairs)
        if room > 0:
            all_pairs += collect(FALLBACK_REPO, min(args.per_repo, room), skip=skip)
    for p in all_pairs:
        p["source"] = "random"

    pos_repos = [r.strip() for r in args.positives_from.split(",") if r.strip()]
    if pos_repos:
        all_pairs += collect_positives(pos_repos, args.positive_target, skip)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for p in all_pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    by: dict[tuple, list[int]] = {}
    for p in all_pairs:
        key = (p["repo"], p["source"])
        by.setdefault(key, [0, 0])
        by[key][0] += 1
        by[key][1] += p["needed_clarification"]
    for (r, src), (n, c) in sorted(by.items()):
        print(f"{r} [{src}]: {n} pairs, {c} needed_clarification", file=sys.stderr)
    print(f"wrote {len(all_pairs)} pairs to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
