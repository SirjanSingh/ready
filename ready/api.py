"""The two calls everything else is built on. The eval, the CLI and the MCP server all go
through here, so a number in evidence/ always describes the same code the demo runs.
"""

from __future__ import annotations

from pathlib import Path

from ready.gate import Verdict, run_gate


def predict_footprint(issue_text: str, repo_path: Path, k: int = 5, use_model: bool = True) -> list[str]:
    """Repo-relative paths most likely to change to resolve this issue, best first."""
    # Always through the gate, so the eval measures exactly what the demo posts.
    return run_gate(issue_text, Path(repo_path), use_model=use_model).footprint[:k]


def check(issue_text: str, repo_path: Path, use_model: bool = True) -> Verdict:
    """Full readiness verdict for one issue against one checkout."""
    return run_gate(issue_text, Path(repo_path), use_model=use_model)
