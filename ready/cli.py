"""`ready check <issue-url-or-file> --repo <checkout> [--post] [--json] [--no-model]`"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from ready import github
from ready.gate import render_comment, run_gate

app = typer.Typer(add_completion=False, help="Check a task is fit to hand to a coding agent.")
console = Console()


@app.callback()
def _root() -> None:
    """Ready: a readiness gate for tasks before they reach a coding agent."""


@app.command()
def check(
    issue: str = typer.Argument(..., help="GitHub issue URL, or a path to a text file whose first line is the title"),
    repo: Path = typer.Option(Path("."), "--repo", help="Local checkout to search"),
    post: bool = typer.Option(False, "--post", help="Comment and label on the issue"),
    as_json: bool = typer.Option(False, "--json"),
    no_model: bool = typer.Option(False, "--no-model", help="Repo search only, no model call"),
    recheck: bool = typer.Option(False, "--recheck", help="Only re-check issues Ready already commented on (for issue_comment events)"),
) -> None:
    if issue.startswith("http"):
        data = github.fetch_issue(issue)
        if recheck and not data["checked"]:
            console.print("Ready has not checked this issue yet; nothing to re-check.")
            raise typer.Exit(0)
        text, url = github.issue_text(data), data["url"]
    else:
        text, url = Path(issue).read_text(encoding="utf-8"), None
    v = run_gate(text, repo, use_model=not no_model)
    if as_json:
        print(json.dumps(v.to_dict(), indent=2))
    else:
        console.print(Markdown(render_comment(v)))
    if post:
        if not url:
            raise typer.BadParameter("--post needs a GitHub issue URL")
        link = github.post_verdict(url, render_comment(v, url), v.status)
        console.print(f"[green]posted[/green] {link}")
    raise typer.Exit(0 if v.status == "agent_ready" else 3)


@app.command("plan")
def plan_cmd(
    issues: list[str] = typer.Argument(..., help="GitHub issue URLs, in priority order"),
    repo: Path = typer.Option(Path("."), "--repo"),
    no_model: bool = typer.Option(False, "--no-model"),
) -> None:
    """Say which issues can go to agents in parallel and which must wait for another."""
    from ready.plan import plan, render

    tasks = []
    for url in issues:
        data = github.fetch_issue(url)
        tasks.append((f"#{data['number']}", github.issue_text(data)))
    console.print(Markdown(render(plan(tasks, repo, use_model=not no_model))))


if __name__ == "__main__":
    app()
