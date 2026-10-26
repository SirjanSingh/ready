"""Ready as an MCP server, so any agent in an Alan session can ask before it starts work.

Tools:
- check_readiness: verdict for an issue (URL or pasted text) against a local checkout.
- predict_footprint: the files most likely to change, best first.

Refusals are raised as ToolError, never ValueError: the SDK passes a ToolError's text to the
client, and swallows anything else into a bare "Error executing tool". (Learned the hard way
in vendable; see its what-broke.md.)

Run: `ready-mcp` (stdio) or `ready-mcp --http --port 8765` (Streamable HTTP).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from pydantic import BaseModel, Field

try:  # mcp >= 2 renamed FastMCP to MCPServer
    from mcp.server import MCPServer as _Server
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # pragma: no cover
    from mcp.server.fastmcp import FastMCP as _Server
    from mcp.server.fastmcp.exceptions import ToolError

from ready import github
from ready.gate import render_comment, run_gate


class ReadinessOut(BaseModel):
    status: str = Field(description="agent_ready or needs_human")
    question: str | None = Field(description="The one question a human must answer, if any")
    footprint: list[str] = Field(description="Files most likely to change, best first")
    tests: list[str]
    test_cmd: str | None
    summary: str
    acceptance: list[str]
    comment_markdown: str


server = _Server("ready")


def _repo(repo_path: str | None) -> Path:
    p = Path(repo_path or os.getenv("READY_REPO") or ".").resolve()
    if not p.is_dir():
        raise ToolError(f"repo_path {str(p)!r} is not a directory. Pass the local checkout the agent will work in, or set READY_REPO.")
    return p


@server.tool()
def check_readiness(issue: str, repo_path: str | None = None, post: bool = False) -> ReadinessOut:
    """Check whether an issue is ready to hand to a coding agent, before starting work on it.

    `issue` is a GitHub issue URL or the issue text (first line = title). If the result is
    needs_human, do not start: ask the returned question instead. If agent_ready, start from
    the footprint files and verify with test_cmd.
    """
    repo = _repo(repo_path)
    url = None
    if issue.strip().startswith("http"):
        try:
            data = github.fetch_issue(issue)
        except ValueError as e:
            raise ToolError(str(e)) from e
        text, url = github.issue_text(data), data["url"]
    else:
        text = issue
    if len(text.strip()) < 3:
        raise ToolError("issue is empty. Pass a GitHub issue URL or the issue text with its title on the first line.")
    v = run_gate(text, repo)
    md = render_comment(v, url)
    if post:
        if not url:
            raise ToolError("post=true needs a GitHub issue URL, not pasted text.")
        github.post_verdict(url, md, v.status)
    return ReadinessOut(status=v.status, question=v.question, footprint=v.footprint, tests=v.tests,
                        test_cmd=v.test_cmd, summary=v.summary, acceptance=v.acceptance, comment_markdown=md)


@server.tool()
def predict_footprint(issue: str, repo_path: str | None = None, k: int = 5) -> list[str]:
    """Files in the checkout most likely to need editing for this issue text, best first."""
    return run_gate(issue, _repo(repo_path)).footprint[: max(1, min(k, 8))]


def main() -> None:
    ap = argparse.ArgumentParser(prog="ready-mcp")
    ap.add_argument("--http", action="store_true", help="Serve Streamable HTTP instead of stdio")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    if a.http:
        os.environ.setdefault("FASTMCP_PORT", str(a.port))
        try:
            server.run(transport="streamable-http", port=a.port)
        except TypeError:
            server.settings.port = a.port
            server.run(transport="streamable-http")
    else:
        server.run()


if __name__ == "__main__":
    main()
