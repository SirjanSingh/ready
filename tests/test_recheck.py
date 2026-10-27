from ready.gate import run_gate
from ready.github import MARKER, issue_text, thread_replies

VAGUE = {"title": "checkout broken", "body": "pls fix asap, customers complaining"}


def _cm(body, login="alice", assoc="NONE", kind="User"):
    return {"body": body, "author_association": assoc, "user": {"login": login, "type": kind}}


def test_replies_keep_author_and_maintainers_only():
    comments = [
        _cm(f"{MARKER}\nReady: needs one answer", login="github-actions[bot]", kind="Bot"),
        _cm("Expected: the total ignores unknown codes", login="alice"),
        _cm("+1 same here", login="stranger"),
        _cm("It is apply_coupon in shop/pricing.py", login="maint", assoc="MEMBER"),
        _cm("auto reply", login="somebot", assoc="OWNER", kind="Bot"),
    ]
    assert thread_replies(comments, "alice") == [
        "Expected: the total ignores unknown codes",
        "It is apply_coupon in shop/pricing.py",
    ]


def test_vague_issue_is_held_until_a_human_answers(shop):
    assert run_gate(issue_text(VAGUE), shop, use_model=False).status == "needs_human"
    answer = (
        "`apply_coupon` raises KeyError for an unknown coupon code at checkout.\n"
        "Expected: an unknown code is ignored and the normal total is returned."
    )
    v = run_gate(issue_text({**VAGUE, "replies": [answer]}), shop, use_model=False)
    assert v.status == "agent_ready", (v.question, v.findings)
    assert any("unknown code is ignored" in a for a in v.acceptance)
