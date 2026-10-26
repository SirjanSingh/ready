"""The only side effects Ready has: one comment (updated in place) and one label.

It never edits the issue body, closes, assigns, or touches code. Uses `GITHUB_TOKEN` when set
(the Actions path), otherwise the local `gh` CLI's auth.
"""

from __future__ import annotations

import json
import os
import re
import subprocess

import httpx

MARKER = "<!-- ready-gate -->"
LABELS = {"agent_ready": ("agent-ready", "0e8a16", "Ready: an agent can start"), "needs_human": ("needs-human", "d93f0b", "Ready: needs one human answer")}


def parse_issue_url(url: str) -> tuple[str, str, int]:
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)", url.strip())
    if not m:
        raise ValueError(f"not a GitHub issue URL: {url!r} (expected https://github.com/<owner>/<repo>/issues/<n>)")
    return m.group(1), m.group(2), int(m.group(3))


def _token() -> str:
    tok = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if tok:
        return tok
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def _client() -> httpx.Client:
    return httpx.Client(base_url="https://api.github.com", headers={"Authorization": f"Bearer {_token()}", "Accept": "application/vnd.github+json"}, timeout=30)


def fetch_issue(url: str) -> dict:
    owner, repo, n = parse_issue_url(url)
    with _client() as c:
        issue = c.get(f"/repos/{owner}/{repo}/issues/{n}").raise_for_status().json()
    return {"owner": owner, "repo": repo, "number": n, "title": issue["title"], "body": issue.get("body") or "", "url": issue["html_url"]}


def post_verdict(url: str, comment_md: str, status: str) -> str:
    owner, repo, n = parse_issue_url(url)
    name, color, desc = LABELS[status]
    other = LABELS["needs_human" if status == "agent_ready" else "agent_ready"][0]
    with _client() as c:
        c.post(f"/repos/{owner}/{repo}/labels", json={"name": name, "color": color, "description": desc})  # 422 if exists: fine
        comments = c.get(f"/repos/{owner}/{repo}/issues/{n}/comments", params={"per_page": 100}).raise_for_status().json()
        mine = next((cm for cm in comments if MARKER in (cm.get("body") or "")), None)
        if mine:
            r = c.patch(f"/repos/{owner}/{repo}/issues/comments/{mine['id']}", json={"body": comment_md}).raise_for_status().json()
        else:
            r = c.post(f"/repos/{owner}/{repo}/issues/{n}/comments", json={"body": comment_md}).raise_for_status().json()
        c.delete(f"/repos/{owner}/{repo}/issues/{n}/labels/{other}")  # 404 if absent: fine
        c.post(f"/repos/{owner}/{repo}/issues/{n}/labels", json={"labels": [name]}).raise_for_status()
    return r["html_url"]


def issue_text(issue: dict) -> str:
    return f"{issue['title']}\n{issue['body']}"


if __name__ == "__main__":  # pragma: no cover
    import sys
    print(json.dumps(fetch_issue(sys.argv[1]), indent=2))
