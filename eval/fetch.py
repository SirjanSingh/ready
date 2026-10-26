"""Collect (issue, merged fix PR) pairs from GitHub into evidence/pairs.jsonl.

Stdlib plus the authenticated `gh` CLI only. Usage:

    python eval/fetch.py [--per-repo 20] [--max-total 60]

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


def build_pair(repo: str, issue: dict) -> tuple[dict | None, str]:
    if not (issue.get("body") or "").strip():
        return None, "empty body"
    prs = [p for p in issue["closedByPullRequestsReferences"]["nodes"]
           if p and p.get("merged") and p["repository"]["nameWithOwner"].lower() == repo.lower()]
    if not prs:
        return None, "no merged same-repo PR"
    prs.sort(key=lambda p: p["mergedAt"])
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


def collect(repo: str, want: int, max_pages: int = 12) -> list[dict]:
    q = f"repo:{repo} is:issue is:closed linked:pr sort:updated-desc"
    cursor = None
    pairs: list[dict] = []
    skipped: dict[str, int] = {}
    for _ in range(max_pages):
        args = ["api", "graphql", "-f", f"query={SEARCH_QUERY}", "-f", f"q={q}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        data = json.loads(gh(*args))["data"]["search"]
        for issue in data["nodes"]:
            if not issue or "number" not in issue:
                continue
            pair, reason = build_pair(repo, issue)
            if pair:
                pairs.append(pair)
                if len(pairs) >= want:
                    break
            else:
                skipped[reason] = skipped.get(reason, 0) + 1
        if len(pairs) >= want or not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]
    print(f"{repo}: {len(pairs)} pairs; skipped {skipped}", file=sys.stderr)
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-repo", type=int, default=20)
    ap.add_argument("--max-total", type=int, default=60)
    args = ap.parse_args()

    all_pairs: list[dict] = []
    for repo in REPOS:
        room = args.max_total - len(all_pairs)
        if room <= 0:
            break
        all_pairs += collect(repo, min(args.per_repo, room))

    counts = {r: sum(p["repo"] == r for p in all_pairs) for r in REPOS}
    if any(n < MIN_PER_REPO for n in counts.values()):
        room = args.max_total - len(all_pairs)
        if room > 0:
            all_pairs += collect(FALLBACK_REPO, min(args.per_repo, room))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        for p in all_pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    by_repo: dict[str, list[int]] = {}
    for p in all_pairs:
        by_repo.setdefault(p["repo"], [0, 0])
        by_repo[p["repo"]][0] += 1
        by_repo[p["repo"]][1] += p["needed_clarification"]
    for r, (n, c) in by_repo.items():
        print(f"{r}: {n} pairs, {c} needed_clarification", file=sys.stderr)
    print(f"wrote {len(all_pairs)} pairs to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
