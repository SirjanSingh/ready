# Demo script (target 2:00, hard ceiling 3:00)

One take where possible. Screen: Alan (app.tryalan.ai) on the left, the GitHub issue on the right.

| Time | On screen | Say |
|---|---|---|
| 0:00 | A new issue on ready-demo: "checkout broken, pls fix" | "Most agent runs that go wrong were doomed before they started. This one would have been." |
| 0:10 | The Ready comment appears: needs-human, one question | "Ready read it the moment it was opened. It doesn't guess. It asks the one thing only a human knows, and holds the task back." |
| 0:25 | Issue #1, the coupon KeyError. The comment shows `agent-ready`, `shop/cart.py`, `shop/pricing.py`, and `pytest` on `tests/test_cart.py` | "A good issue gets the opposite: where the fix lives, found by searching the actual checkout, and how this repo runs its tests." |
| 0:45 | An Alan session with the Ready skill: "fix issue 1". The agent calls `check_readiness`, then opens `pricing.py` first | "Inside Alan, agents call Ready before they start. The agent goes straight to the right file." |
| 1:05 | Issue #3, the injection. The comment says "instructions aimed at an AI agent, which Ready ignored" | "The model can only reorder files the search found. Rules decide the verdict, so an issue that says 'mark this ready' can't." |
| 1:20 | `ready plan` table: #3 runs after #1 | "Give it several tasks and it says which can run in parallel and which would collide on the same file." |
| 1:35 | `evidence/results.md`: the held-out table | "We measured it on real issues from repos we never tuned on. The file the real fix changed is in Ready's top five 88% of the time." |
| 1:50 | `what-broke.md` and the readiness confusion table | "And where it's weak: the readiness rules over-flag about a quarter of ordinary issues. That's written down, not hidden." |
| 2:00 | Repo URL + "MIT, built with Alan and open models" | end |

Before recording:
- Re-run `ready check ... --post` on demo issues #1-#3 so the comments are fresh.
- The 0:00 beat needs the Action on ready-demo: open a fresh "checkout broken, pls fix" issue on camera and wait for the comment (about a minute).
- If the model key is set, re-run, so the comment footer names the open model.
