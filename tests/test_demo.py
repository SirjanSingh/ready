"""Every beat of the demo video, checked against a copy of the demo repo's code.

The issue texts live in docs/demo-issues.yaml, the same file used to seed the demo repo,
so what goes on camera is what these tests assert.
"""

from pathlib import Path

import pytest
import yaml

from ready.gate import run_gate
from ready.github import issue_text
from ready.plan import plan

ISSUES = yaml.safe_load((Path(__file__).parent.parent / "docs" / "demo-issues.yaml").read_text(encoding="utf-8"))
BY_ID = {i["id"]: i for i in ISSUES}


def _text(i, with_reply=False):
    title, _, body = i["issue"].partition("\n")
    return issue_text({"title": title, "body": body, "replies": [i["reply"]] if with_reply else []})


@pytest.mark.parametrize("i", ISSUES, ids=[i["id"] for i in ISSUES])
def test_demo_issue_verdict(i, demo):
    v = run_gate(_text(i), demo, use_model=False)
    assert v.status == i["expect"], (v.question, v.findings)
    for path in i.get("expect_top", []) if v.status == "agent_ready" else []:
        assert path in v.footprint[:3], v.footprint


@pytest.mark.parametrize("i", [i for i in ISSUES if i.get("reply")], ids=lambda i: i["id"])
def test_demo_reply_flips_to_ready(i, demo):
    v = run_gate(_text(i, with_reply=True), demo, use_model=False)
    assert v.status == i["expect_after_reply"], (v.question, v.findings)
    for path in i.get("expect_top", []):
        assert path in v.footprint[:3], v.footprint


def test_demo_plan_lanes(demo):
    ids = ["coupon", "injection", "badge-vague", "free-shipping", "coupon-case"]
    lanes = {l.task: l for l in plan([(k, _text(BY_ID[k])) for k in ids], demo, use_model=False)}
    assert lanes["coupon"].after == [] and not lanes["coupon"].held
    assert lanes["free-shipping"].after == []          # different module: runs alongside
    assert lanes["coupon-case"].after == ["coupon"]    # same files as coupon: waits
    assert lanes["injection"].held and lanes["badge-vague"].held
