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
# Concrete evidence of a failure implies its own expected behaviour ("this should not raise").
# Calibrated on 60 real issues that maintainers fixed without asking anything: requiring an
# explicit "expected vs actual" sentence flagged 22 of them, all clearly workable.
_ERROR_NAME = re.compile(r"\b[A-Z][A-Za-z]*(Error|Exception|Warning)\b|\bWinError \d+|\bexit (code|status) \d+|\bsegfault|\bpanic", re.I)
_VERSION_REGRESSION = re.compile(r"(\b\d+\.\d+(\.\d+)?\b.*\b(work(s|ed)|broke|fails?|regress))|\b(since|after|in) (v?\d+\.\d+)|\bno longer\b|\bused to\b|\bstopped working\b", re.I | re.S)
_INLINE_CALL = re.compile(r"`[^`\n]*\w\([^`\n]*\)[^`\n]*`")
_CHANGE_VERB = re.compile(r"\b(support|add|allow|change|rename|remove|deprecate|expose|accept|return|raise|make|use|update|bump|drop)\b", re.I)
_CODE_SYMBOL = re.compile(r"`[^`\n]{2,}`|\b\w+\.\w+\(|\b[A-Za-z_]+(_[A-Za-z]+)+\b|[A-Z][a-z]+[A-Z]\w+|\b\w+\s*[<>=]=?\s*\d+\.\d+")
_INJECTION = re.compile(
    r"(ignore (all |any |your )?(previous|prior|above)? ?(instructions|checklist|rules)"
    r"|ignore your \w+|disregard (the|your|all) \w+|you are (now )?an? (ai|agent|assistant)"
    r"|(label|mark) (it|this)( as)? agent-ready|tell the (agent|ai|assistant) to|system prompt)",
    re.I,
)
_PATHISH = re.compile(r"[\w./-]+\.(py|ts|tsx|js|go|rs|java|rb)\b|\b[a-z_]+(\.[a-z_]+){1,}\b")


def is_bug_report(title: str, body: str) -> bool:
    # "Change X to Y" / "Support Z" is a change request even if its body mentions errors.
    if re.match(r"\s*(\[\w+\]\s*)?(support|add|allow|change|rename|remove|deprecate|expose|bump|drop|update)\b", title, re.I):
        return False
    return bool(_BUG_WORDS.search(f"{title}\n{body}"))


def evaluate(title: str, body: str) -> list[Finding]:
    text = f"{title}\n{body}"
    words = len(re.findall(r"\w+", body))
    bug = is_bug_report(title, body)
    out: list[Finding] = []

    inj = _INJECTION.search(text)
    out.append(Finding(
        "addressed_to_agent",
        ok=not inj,
        detail=f'Contains instructions aimed at an AI agent: "{inj.group(0)[:80]}"' if inj else "No instructions aimed at an agent",
        cites="An issue is data for the agent, not instructions to it; a human must confirm intent.",
        human_only=True,
    ))
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
    has_repro = bool(_REPRO.search(body) or _TRACEBACK.search(body) or _INLINE_CALL.search(body))
    concrete_failure = bool(_ERROR_NAME.search(text) or _VERSION_REGRESSION.search(text))
    if bug:
        expect_ok = bool(_EXPECT.search(text)) or concrete_failure
        out.append(Finding(
            "expected_vs_actual",
            ok=expect_ok,
            detail=("States what should happen vs what happens" if _EXPECT.search(text)
                    else "A named error or version regression implies the expected behaviour" if expect_ok
                    else "Does not say what should happen instead"),
            cites=f'{ALAN_TASK_DOC}: "Add criteria that can be checked."',
            human_only=True,
        ))
        repro_ok = has_repro or (concrete_failure and bool(_CODE_SYMBOL.search(text)))
        out.append(Finding(
            "reproduction",
            ok=repro_ok,
            detail="Has a reproduction, traceback or a named failing call" if repro_ok else "No code, command or traceback to reproduce",
            cites=f'{ALAN_TASK_DOC}: "A task should be small enough to execute and specific enough to verify."',
            human_only=True,
        ))
    else:
        # A change request is checkable when it names the change and the thing it applies to.
        crit_ok = bool(_CRITERIA.search(text)) or (bool(_CHANGE_VERB.search(title)) and bool(_CODE_SYMBOL.search(text))) or has_repro
        out.append(Finding(
            "checkable_criteria",
            ok=crit_ok,
            detail="Has checkable criteria or names a concrete change" if crit_ok else "No checkable acceptance criteria",
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
    "addressed_to_agent": "This issue contains instructions aimed at an AI agent, which Ready ignored. Can a maintainer restate what change is actually wanted?",
    "expected_vs_actual": "What should happen instead? One sentence on the correct behaviour is enough for an agent to verify the fix.",
    "reproduction": "Can you add the smallest snippet or command that shows the problem, with the versions you ran it on?",
    "checkable_criteria": "How will we know this is done? Name one behaviour or output an agent can check.",
    "context": "Can you add a few lines of context: where you hit this and what you were trying to do?",
}
