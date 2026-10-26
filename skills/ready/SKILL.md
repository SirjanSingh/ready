---
name: ready
description: Before starting work on any GitHub issue or Alan task, check it is ready for an agent. Use when asked to work on, fix, implement or pick up an issue or task, and when a task arrives from an automation.
---

# Ready: check the task before you start

A vague task wastes a whole run. Before writing any code for an issue or task:

1. Call the `check_readiness` tool (Ready MCP server) with the issue URL, or the task's title and description as text, and `repo_path` set to the checkout you are working in. If the MCP server is not connected, run `ready check <issue-url> --repo . --json` instead.
2. If `status` is `needs_human`:
   - Do not start coding.
   - Ask exactly the returned `question` (in the task, or as an issue comment with `post: true`), then stop.
3. If `status` is `agent_ready`:
   - Start from the `footprint` files, in order. They come from searching this checkout, not from guessing.
   - Use `acceptance` as your definition of done. Never add requirements it does not state.
   - Verify with `test_cmd` (and the listed `tests`) before you say the work is done.
4. In your final message, say which footprint files you actually changed. This tells the team how good Ready's prediction was.
