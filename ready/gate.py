"""Combine the rules, the repo search and the model into one verdict.

Decision order is fixed: rules decide the status, the repo fills what it can, the model only
ranks and phrases. `needs_human` always carries exactly one question.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from ready import checklist, llm
from ready.repo import candidate_files, config_candidates, extract_terms, related_tests, detect_test_command

PRIORITY = ["addressed_to_agent", "expected_vs_actual", "reproduction", "checkable_criteria", "context"]


@dataclass
class Verdict:
    status: str  # "agent_ready" | "needs_human"
    question: str | None
    footprint: list[str]
    tests: list[str]
    test_cmd: str | None
    summary: str
    acceptance: list[str]
    findings: list[dict] = field(default_factory=list)
    model: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def split_issue(issue_text: str) -> tuple[str, str]:
    title, _, body = issue_text.partition("\n")
    return title.strip(), body.strip()


def run_gate(issue_text: str, repo: Path, use_model: bool = True) -> Verdict:
    title, body = split_issue(issue_text)
    findings = checklist.evaluate(title, body)
    cands = candidate_files(issue_text, repo)
    terms = sorted(extract_terms(issue_text), key=lambda t: -extract_terms(issue_text)[t])

    draft = llm.rank_and_draft(issue_text, cands, repo, terms) if use_model else None
    grep_order = [c.path for c in cands]
    if draft and draft.ranked:
        footprint = draft.ranked + [p for p in grep_order if p not in draft.ranked]
    else:
        footprint = grep_order
    cfg = [p for p in config_candidates(issue_text, repo) if p not in footprint]
    if cfg:
        # After the top 5, never inside it: at positions 3-4 these cost held-out hit@3
        # 0.78 -> 0.71 (see what-broke.md), so they are listed as "also check", not ranked.
        footprint = footprint[:5] + cfg + footprint[5:]
    footprint = footprint[:8]
    src = [p for p in footprint if not p.startswith("tests/")][:3]

    failed = {f.rule for f in findings if not f.ok and f.human_only}
    if not footprint:
        failed.add("locatable_hard")
    question = None
    for rule in PRIORITY:
        if rule in failed:
            question = checklist.QUESTIONS[rule]
            break
    if question is None and "locatable_hard" in failed:
        question = "Which part of the code is this about? Ready could not find any file matching the issue's words."

    return Verdict(
        status="needs_human" if question else "agent_ready",
        question=question,
        footprint=footprint,
        tests=related_tests(src, repo),
        test_cmd=detect_test_command(repo),
        summary=(draft.summary if draft else "") or title,
        acceptance=(draft.acceptance if draft and draft.acceptance else checklist.stated_expectations(body)),
        findings=[asdict(f) for f in findings],
        model=draft.model if draft else None,
    )


def render_comment(v: Verdict, issue_url: str | None = None) -> str:
    """The single comment Ready posts. Marker line lets us update it in place."""
    head = "**Ready: agent-ready**" if v.status == "agent_ready" else "**Ready: needs one answer before an agent starts**"
    lines = ["<!-- ready-gate -->", head, ""]
    if v.question:
        lines += [f"> {v.question}", ""]
    lines += [f"**What must change:** {v.summary}", ""]
    if v.footprint:
        lines.append("**Where (from the repo, best first):**")
        lines += [f"- `{p}`" for p in v.footprint[:5]]
        lines.append("")
    if v.tests or v.test_cmd:
        lines.append("**How to verify:** " + (f"`{v.test_cmd}`" if v.test_cmd else "") + (" on " + ", ".join(f"`{t}`" for t in v.tests) if v.tests else ""))
        lines.append("")
    if v.acceptance:
        lines.append("**Done when (from the issue, not invented):**")
        lines += [f"- [ ] {a}" for a in v.acceptance]
        lines.append("")
    misses = [f for f in v.findings if not f["ok"]]
    if misses:
        lines.append("<details><summary>Checklist (rules cite Alan's task guide)</summary>\n")
        lines += [f"- {f['rule']}: {f['detail']}" for f in v.findings]
        lines.append("\n</details>")
    lines.append("\n<sub>Ready decides with rules; the open model" + (f" ({v.model})" if v.model else "") + " only ranks files and phrases the summary.</sub>")
    return "\n".join(lines)
