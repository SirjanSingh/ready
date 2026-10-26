"""Deterministic readiness rules.

The rules come from Alan's own docs ("Create a task": "A task should be small enough to
execute and specific enough to verify", "Add criteria that can be checked", and the weak
title examples "Docs" and "Bug in tasks"). The model never decides pass or fail; these
rules do, and each one cites the sentence it enforces so a refusal can be argued with.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ALAN_TASK_DOC = "docs.tryalan.ai/docs/tasks/create-a-task"


@dataclass(frozen=True)
class Finding:
    rule: str
    ok: bool
    detail: str
    cites: str
    # A human-only gap cannot be filled from the repo; it is what we ask about.
    human_only: bool = False


_BUG_WORDS = re.compile(r"\b(bug|error|exception|traceback|crash|fail(s|ed|ing)?|broken|regression|wrong|incorrect|raises?)\b", re.I)
_EXPECT = re.compile(r"\b(expected|should|instead|actual(ly)?|but (it|got|we)|i (would )?expect)\b", re.I)
_REPRO = re.compile(r"(```|^\s*(>>>|\$|pip |python |npm |uv |pytest)|steps to reproduce|minimal (example|repro)|to reproduce)", re.I | re.M)
_CRITERIA = re.compile(r"(acceptance criteria|definition of done|- \[ \]|\bshould (return|raise|accept|work|be|not)\b|\bmust\b|\bexpected (output|behaviou?r|result)\b)", re.I)
_VAGUE_TITLE = re.compile(r"^\s*(bug|issue|problem|help|question|docs?|fix|error|broken|not working)[\s.!?:]*$", re.I)
_TRACEBACK = re.compile(r"(Traceback \(most recent call last\)|^\s*File \".+\", line \d+|\b\w+(Error|Exception):)", re.M)
_PATHISH = re.compile(r"[\w./-]+\.(py|ts|tsx|js|go|rs|java|rb)\b|\b[a-z_]+(\.[a-z_]+){1,}\b")


def is_bug_report(title: str, body: str) -> bool:
    return bool(_BUG_WORDS.search(f"{title}\n{body}"))


def evaluate(title: str, body: str) -> list[Finding]:
    text = f"{title}\n{body}"
    words = len(re.findall(r"\w+", body))
    bug = is_bug_report(title, body)
    out: list[Finding] = []

    out.append(Finding(
        "outcome_title",
        ok=bool(title.strip()) and not _VAGUE_TITLE.match(title) and len(title.split()) >= 3,
        detail="Title names an outcome" if len(title.split()) >= 3 else "Title is too short to name an outcome",
        cites=f'{ALAN_TASK_DOC}: "The best task titles describe the outcome, not the activity." Weak: "Docs", "Bug in tasks".',
    ))
    out.append(Finding(
        "context",
        ok=words >= 25,
        detail=f"Body has {words} words",
        cites=f'{ALAN_TASK_DOC}: "Description: context, constraints, and acceptance criteria."',
        human_only=True,
    ))
    if bug:
        out.append(Finding(
            "expected_vs_actual",
            ok=bool(_EXPECT.search(text)),
            detail="States what should happen vs what happens" if _EXPECT.search(text) else "Does not say what should happen instead",
            cites=f'{ALAN_TASK_DOC}: "Add criteria that can be checked."',
            human_only=True,
        ))
        out.append(Finding(
            "reproduction",
            ok=bool(_REPRO.search(body) or _TRACEBACK.search(body)),
            detail="Has a reproduction or traceback" if (_REPRO.search(body) or _TRACEBACK.search(body)) else "No code, command or traceback to reproduce",
            cites=f'{ALAN_TASK_DOC}: "A task should be small enough to execute and specific enough to verify."',
            human_only=True,
        ))
    else:
        out.append(Finding(
            "checkable_criteria",
            ok=bool(_CRITERIA.search(text)),
            detail="Has checkable criteria" if _CRITERIA.search(text) else "No checkable acceptance criteria",
            cites=f'{ALAN_TASK_DOC}: "Add criteria that can be checked. Avoid criteria such as \'looks good\'."',
            human_only=True,
        ))
    out.append(Finding(
        "locatable",
        ok=bool(_PATHISH.search(text) or _TRACEBACK.search(body)),
        detail="Names code it touches" if _PATHISH.search(text) else "Names no file, module or symbol (Ready will try to find them)",
        cites=f'{ALAN_TASK_DOC}: "Links: PRs, docs, incidents, designs, or customer context."',
        human_only=False,
    ))
    return out


# What to ask when a human-only rule fails, in priority order. One question, never a form.
QUESTIONS = {
    "expected_vs_actual": "What should happen instead? One sentence on the correct behaviour is enough for an agent to verify the fix.",
    "reproduction": "Can you add the smallest snippet or command that shows the problem, with the versions you ran it on?",
    "checkable_criteria": "How will we know this is done? Name one behaviour or output an agent can check.",
    "context": "Can you add a few lines of context: where you hit this and what you were trying to do?",
}
