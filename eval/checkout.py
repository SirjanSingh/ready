"""Blobless clones under .eval-cache/ and per-pair checkouts of the PR base commit.

    python eval/checkout.py [pairs.jsonl]   # clone every repo named in the pairs file
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".eval-cache"
PAIRS = ROOT / "evidence" / "pairs.jsonl"


def repo_dir(repo: str) -> Path:
    return CACHE / repo.replace("/", "__")


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")


def ensure_clone(repo: str) -> Path:
    d = repo_dir(repo)
    if (d / ".git").exists():
        return d
    CACHE.mkdir(parents=True, exist_ok=True)
    proc = _git("clone", "-q", "--filter=blob:none", f"https://github.com/{repo}", str(d))
    if proc.returncode != 0:
        raise RuntimeError(f"clone {repo} failed: {proc.stderr.strip()}")
    return d


_current: dict[str, str] = {}  # repo -> sha this process last checked out


def checkout(repo: str, sha: str) -> Path:
    """Force the working tree of `repo` to `sha`, fetching the commit if it is not local.

    Callers that sort pairs by (repo, base_sha) get consecutive same-sha pairs for free.
    """
    d = ensure_clone(repo)
    if _current.get(repo) == sha:
        return d
    proc = _git("-C", str(d), "checkout", "-q", "--force", sha)
    if proc.returncode != 0:
        _git("-C", str(d), "fetch", "-q", "--filter=blob:none", "origin", sha)
        proc = _git("-C", str(d), "checkout", "-q", "--force", sha)
        if proc.returncode != 0:
            raise RuntimeError(f"checkout {repo}@{sha[:10]} failed: {proc.stderr.strip()}")
    _git("-C", str(d), "clean", "-q", "-fdx")
    _current[repo] = sha
    return d


def main() -> None:
    pairs = Path(sys.argv[1]) if len(sys.argv) > 1 else PAIRS
    repos = sorted({json.loads(l)["repo"] for l in pairs.open(encoding="utf-8") if l.strip()})
    for r in repos:
        print(f"{r} -> {ensure_clone(r)}", file=sys.stderr)


if __name__ == "__main__":
    main()
