"""Which of several tasks can run at the same time.

Two tasks whose predicted footprints share a source file get an `after:#N` edge, so a second
agent does not start editing the same file. A task the gate holds for a human is shown as held
and claims no files, since no agent starts on it yet. Kept small on purpose: on 82 pairs of real PRs
that were open at the same time, only about 5% shared a source file, so this is a guard, not
the headline (see ideas/openfire-council.md in the planning repo).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ready.gate import run_gate
from ready.repo import is_test_path

TOP = 3  # only the confident head of each footprint counts as a claim on a file


@dataclass
class Lane:
    task: str
    files: list[str]
    after: list[str]
    held: bool = False


def plan(tasks: list[tuple[str, str]], repo: Path, use_model: bool = True) -> list[Lane]:
    claims: list[tuple[str, set[str]]] = []
    lanes: list[Lane] = []
    for task_id, text in tasks:
        v = run_gate(text, repo, use_model=use_model)
        fp = [p for p in v.footprint if not is_test_path(p)][:TOP]
        if v.status != "agent_ready":
            lanes.append(Lane(task_id, fp, [], held=True))
            continue
        after = [prev for prev, files in claims if files & set(fp)]
        lanes.append(Lane(task_id, fp, after))
        claims.append((task_id, set(fp)))
    return lanes


def render(lanes: list[Lane]) -> str:
    rows = ["| task | likely files | run |", "|---|---|---|"]
    for l in lanes:
        if l.held:
            run = "held: needs a human answer first"
        else:
            run = "after " + ", ".join(l.after) if l.after else "now, in parallel"
        rows.append(f"| {l.task} | {', '.join(f'`{f}`' for f in l.files) or '(none found)'} | {run} |")
    return "\n".join(rows)
