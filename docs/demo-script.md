# Demo script (target 2:00, hard ceiling 3:00)

Screen: Alan on the left, the GitHub issue on the right. Every issue below is in `docs/demo-issues.yaml`, and `tests/test_demo.py` checks each beat against a copy of ready-demo's code, so what is on camera is what the tests assert.

| Time | On screen | Say |
|---|---|---|
| 0:00 | ready-demo #4 "cart icon number wrong". Ready's comment: needs-human, one question | "Most agent runs that go wrong were doomed before they started. Ready read this one the moment it was opened and asked the one thing only a human knows." |
| 0:15 | Paste the reply from `docs/demo-issues.yaml` (badge-vague) as a comment on #4. Cut. The same Ready comment now says agent-ready, `shop/badge.py`, and the label flips | "Answer it on the issue and Ready re-checks: same comment, updated in place, label flipped. Now an agent can start." |
| 0:35 | Issue #1, the coupon KeyError: agent-ready, `shop/cart.py`, `shop/pricing.py`, `pytest` on `tests/test_cart.py` | "A clear issue gets where the fix lives, searched from the actual checkout, and how this repo runs its tests." |
| 0:45 | The Alan session (this laptop, "OMEN"): the agent calls `check_readiness` on #1 and starts from those files | "Inside Alan, agents call Ready before they start, so they begin from the two files that matter and the test that proves the fix." |
| 1:05 | Issue #3, the injection: "instructions aimed at an AI agent, which Ready ignored" | "Rules decide the verdict, not the model, so an issue that says 'mark this ready' can't." |
| 1:15 | `ready plan` on #1 #3 #4 #5 #6: #1 and #5 run now in parallel, #6 waits for #1, #3 and #4 are held | "Give it a backlog and it says which tasks agents can take now, which would edit the same file, and which still need a person." |
| 1:35 | README results: held-out hit@5 0.88, and the werkzeug backtest row with its caveat | "Measured on real issues from repos we never tuned on, ground truth from the merged PR. On werkzeug, a repo it had never seen, the right file was first in all 20, and we say why that set is easy." |
| 1:50 | `what-broke.md`: the readiness false alarms and the cold start | "Where it's weak is written down: the readiness rules over-flag about a quarter of ordinary issues, and a cold install misses Alan's five-second start." |
| 2:00 | Repo URL, `uvx ready-gate`, MIT | end |

Commands for the 1:15 beat (from `D:\projs\ready`, after `git -C D:\projs\ready-demo pull`):

```
uv run ready plan https://github.com/SirjanSingh/ready-demo/issues/1 https://github.com/SirjanSingh/ready-demo/issues/3 https://github.com/SirjanSingh/ready-demo/issues/4 https://github.com/SirjanSingh/ready-demo/issues/5 https://github.com/SirjanSingh/ready-demo/issues/6 --repo D:\projs\ready-demo --no-model
```

Before recording:
- `uv run python scripts/demo_preflight.py` must end with READY TO RECORD. It checks the Action pin, the last runs, every demo issue's label and the MCP start time against Alan's 5 s limit.
- Keep #4 unanswered until the 0:15 beat. The Action takes about a minute after the reply, so cut there.
- Use the local Alan session (machine OMEN): its uv cache is warm. A cloud session would start Ready cold (see what-broke.md).
- If a take goes wrong on #4, delete the reply comment and edit the issue once: Ready re-checks on edits and goes back to needs-human.
