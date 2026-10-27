# Ready eval results

Appended by `eval/run.py`. DEV set: `evidence/pairs.jsonl` (readiness rules were calibrated on it). HELD-OUT set: `evidence/heldout.jsonl`. Each section header says which.

**Commit hashes.** On 27 Oct, before the repo went public, git history was rewritten to drop local notes files (agent instructions, session notes, worker briefs). No file under `ready/`, `eval/`, `tests/` or `evidence/` changed, but every commit hash did. The sections below are left exactly as they were logged, with the old hashes. Map them with this table:

| logged as | now |
|---|---|
| 7b70010 | d546470 |
| 47a0fea | e1040b7 |
| 5636dee | 0448d92 |
| a0a5b79 | b3f6d16 |
| f3f66db | 933477a |
| 6076543 | 4f2d4d8 |
| 08d54cf | 7302779 |
| e130718 | d8bfcd2 |
| 79d8054 | 7da69b3 |
| 6b779fc | 80eec2b |
| a4a094b | 6783148 |
| 78267f5 | 86603f2 |
| db48ecf | 814b843 |
| fe8c67b | c553a27 |
| 435236b | 112c71d |

## 2026-10-27 02:22 | variant `grep` | k=5 | n=60

SUPERSEDED: this run started at 01:53:05 while `ready/repo.py` was still being edited (last write 01:53:26, committed in 47a0fea), so it measured an engine version that was never committed. Truth paths starting with `.github/` are also shown without the leading dot. The 02:23 section below rescored it with the path fix and has the same caveat. Use the next section that names an engine commit.

Pairs scored: 60, errors: 0, wall time: 1774s. Truth files: 91, of which 2 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| encode/httpx | 20 | 0.400 | 0.550 | 0.700 | 0.237 | 0.425 | 0.583 |
| fastapi/sqlmodel | 7 | 0.857 | 0.857 | 0.857 | 0.714 | 0.857 | 0.857 |
| pallets/click | 13 | 0.462 | 0.846 | 0.846 | 0.462 | 0.808 | 0.808 |
| pydantic/pydantic | 20 | 0.350 | 0.650 | 0.750 | 0.275 | 0.525 | 0.625 |
| **overall** | 60 | 0.450 | 0.683 | 0.767 | 0.354 | 0.592 | 0.678 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 2 | FP 34 |
| predicted agent_ready | FN 1 | TN 23 |

n=60, accuracy 0.417, precision 0.056, recall 0.667, predicted needs_human 36, gold positives 3.

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/encode/httpx/issues/2884 cov@5=0.000 | truth: pyproject.toml | predicted: httpx/_client.py, httpx/_transports/default.py, httpx/_main.py
- https://github.com/encode/httpx/issues/309 cov@5=0.000 | truth: httpx/middleware.py | predicted: httpx/dispatch/http11.py, httpx/client.py, httpx/dispatch/connection_pool.py
- https://github.com/encode/httpx/issues/2599 cov@5=0.000 | truth: mkdocs.yml | predicted: httpx/_client.py, httpx/_main.py, httpx/_models.py
- https://github.com/encode/httpx/issues/2694 cov@5=0.000 | truth: httpx/_urlparse.py | predicted: httpx/_client.py, httpx/_transports/asgi.py, httpx/_exceptions.py
- https://github.com/fastapi/sqlmodel/issues/189 cov@5=0.000 | truth: sqlmodel/sql/expression.py.jinja2 | predicted: sqlmodel/orm/session.py, sqlmodel/ext/asyncio/session.py, sqlmodel/main.py
- https://github.com/pallets/click/issues/3786 cov@5=0.000 | truth: pyproject.toml | predicted: src/click/shell_completion.py, src/click/core.py, src/click/_termui_impl.py
- https://github.com/pallets/click/issues/3766 cov@5=0.000 | truth: github/workflows/nightly.yaml | predicted: src/click/core.py, src/click/testing.py, tests/test_context.py
- https://github.com/pydantic/pydantic/issues/13977 cov@5=0.000 | truth: github/workflows/ci.yml | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/python/pydantic_core/core_schema.py, pydantic-core/src/errors/validation_exception.rs
- https://github.com/pydantic/pydantic/issues/13976 cov@5=0.000 | truth: pydantic/_internal/_validators.py | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic/_internal/_model_construction.py, pydantic/_internal/_generate_schema.py
- https://github.com/pydantic/pydantic/issues/14041 cov@5=0.000 | truth: pydantic/_internal/_docs_extraction.py | predicted: pydantic/main.py, pydantic/json_schema.py, pydantic/config.py

## 2026-10-27 02:23 | variant `grep` | k=5 | n=60

Note: Rescored on 2026-10-27 from the run dated 2026-10-27T02:22:39 (no new predictions). SUPERSEDED, same engine-version caveat as the section above.

Pairs scored: 60, errors: 0, wall time: n/a. Truth files: 91, of which 2 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| encode/httpx | 20 | 0.400 | 0.550 | 0.700 | 0.237 | 0.425 | 0.583 |
| fastapi/sqlmodel | 7 | 0.857 | 0.857 | 0.857 | 0.714 | 0.857 | 0.857 |
| pallets/click | 13 | 0.462 | 0.846 | 0.846 | 0.462 | 0.808 | 0.808 |
| pydantic/pydantic | 20 | 0.350 | 0.650 | 0.750 | 0.275 | 0.525 | 0.625 |
| **overall** | 60 | 0.450 | 0.683 | 0.767 | 0.354 | 0.592 | 0.678 |
| overall, pairs with a code file in truth | 54 | 0.500 | 0.759 | 0.852 | 0.394 | 0.657 | 0.753 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 2 | FP 34 |
| predicted agent_ready | FN 1 | TN 23 |

n=60, accuracy 0.417, precision 0.056, recall 0.667, predicted needs_human 36, gold positives 3.

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/encode/httpx/issues/2884 cov@5=0.000 | truth: pyproject.toml | predicted: httpx/_client.py, httpx/_transports/default.py, httpx/_main.py
- https://github.com/encode/httpx/issues/309 cov@5=0.000 | truth: httpx/middleware.py | predicted: httpx/dispatch/http11.py, httpx/client.py, httpx/dispatch/connection_pool.py
- https://github.com/encode/httpx/issues/2599 cov@5=0.000 | truth: mkdocs.yml | predicted: httpx/_client.py, httpx/_main.py, httpx/_models.py
- https://github.com/encode/httpx/issues/2694 cov@5=0.000 | truth: httpx/_urlparse.py | predicted: httpx/_client.py, httpx/_transports/asgi.py, httpx/_exceptions.py
- https://github.com/fastapi/sqlmodel/issues/189 cov@5=0.000 | truth: sqlmodel/sql/expression.py.jinja2 | predicted: sqlmodel/orm/session.py, sqlmodel/ext/asyncio/session.py, sqlmodel/main.py
- https://github.com/pallets/click/issues/3786 cov@5=0.000 | truth: pyproject.toml | predicted: src/click/shell_completion.py, src/click/core.py, src/click/_termui_impl.py
- https://github.com/pallets/click/issues/3766 cov@5=0.000 | truth: .github/workflows/nightly.yaml | predicted: src/click/core.py, src/click/testing.py, tests/test_context.py
- https://github.com/pydantic/pydantic/issues/13977 cov@5=0.000 | truth: .github/workflows/ci.yml | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/python/pydantic_core/core_schema.py, pydantic-core/src/errors/validation_exception.rs
- https://github.com/pydantic/pydantic/issues/13976 cov@5=0.000 | truth: pydantic/_internal/_validators.py | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic/_internal/_model_construction.py, pydantic/_internal/_generate_schema.py
- https://github.com/pydantic/pydantic/issues/14041 cov@5=0.000 | truth: pydantic/_internal/_docs_extraction.py | predicted: pydantic/main.py, pydantic/json_schema.py, pydantic/config.py

## 2026-10-27 03:01 | variant `grep` | k=5 | n=60

SUPERSEDED by the 05:51 DEV section below (engine f3f66db, after the a0a5b79 readiness calibration). Footprint numbers are identical; readiness changed from 36 needs_human to 6.

Note: engine 47a0fea. (The run logged "5636dee at end", but that commit only touched eval/ and evidence/; `git diff 47a0fea 5636dee -- ready` is empty, so every pair was scored on 47a0fea. The check now keys on the last commit touching ready/.)

Pairs scored: 60, errors: 0, wall time: 2240s. Truth files: 91, of which 0 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| encode/httpx | 20 | 0.400 | 0.600 | 0.650 | 0.237 | 0.475 | 0.533 |
| fastapi/sqlmodel | 7 | 0.857 | 0.857 | 0.857 | 0.714 | 0.857 | 0.857 |
| pallets/click | 13 | 0.538 | 0.846 | 0.846 | 0.500 | 0.808 | 0.808 |
| pydantic/pydantic | 20 | 0.350 | 0.700 | 0.800 | 0.275 | 0.550 | 0.650 |
| **overall** | 60 | 0.467 | 0.717 | 0.767 | 0.362 | 0.617 | 0.669 |
| overall, pairs with a code file in truth | 54 | 0.519 | 0.796 | 0.852 | 0.403 | 0.685 | 0.744 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 2 | FP 34 |
| predicted agent_ready | FN 1 | TN 23 |

n=60, accuracy 0.417, precision 0.056, recall 0.667, predicted needs_human 36, gold positives 3.

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/encode/httpx/issues/2884 cov@5=0.000 | truth: pyproject.toml | predicted: httpx/_client.py, httpx/_transports/default.py, httpx/_main.py
- https://github.com/encode/httpx/issues/309 cov@5=0.000 | truth: httpx/middleware.py | predicted: httpx/dispatch/http11.py, httpx/client.py, httpx/models.py
- https://github.com/encode/httpx/issues/2599 cov@5=0.000 | truth: mkdocs.yml | predicted: httpx/_client.py, httpx/_main.py, httpx/_models.py
- https://github.com/encode/httpx/issues/2694 cov@5=0.000 | truth: httpx/_urlparse.py | predicted: httpx/_client.py, httpx/_transports/asgi.py, httpx/_exceptions.py
- https://github.com/encode/httpx/issues/2810 cov@5=0.000 | truth: httpx/_transports/asgi.py | predicted: httpx/_urls.py, httpx/_decoders.py, httpx/_client.py
- https://github.com/fastapi/sqlmodel/issues/189 cov@5=0.000 | truth: sqlmodel/sql/expression.py.jinja2 | predicted: sqlmodel/orm/session.py, sqlmodel/ext/asyncio/session.py, .github/actions/comment-docs-preview-in-pr/app/main.py
- https://github.com/pallets/click/issues/3786 cov@5=0.000 | truth: pyproject.toml | predicted: src/click/core.py, src/click/_termui_impl.py, src/click/termui.py
- https://github.com/pallets/click/issues/3766 cov@5=0.000 | truth: .github/workflows/nightly.yaml | predicted: src/click/core.py, src/click/testing.py, tests/test_context.py
- https://github.com/pydantic/pydantic/issues/13977 cov@5=0.000 | truth: .github/workflows/ci.yml | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/src/errors/validation_exception.rs, pydantic-core/python/pydantic_core/core_schema.py
- https://github.com/pydantic/pydantic/issues/13976 cov@5=0.000 | truth: pydantic/_internal/_validators.py | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/python/pydantic_core/core_schema.py, pydantic/_internal/_generate_schema.py

## 2026-10-27 05:33 | HELD-OUT set | variant `grep` | k=5 | n=58

Set: held-out (`evidence/heldout.jsonl`). None of these issues were used to build or tune Ready.

Note: engine HEAD 6076543 (ready/ last changed in f3f66db).

Set composition: 40 random pairs, 10 from each of pallets/flask, Kludex/starlette (encode/starlette was transferred; GitHub search only answers to the new name), fastapi/typer and psf/requests. Plus 18 enriched positives from those 4 repos and the 4 dev repos (no issue overlaps evidence/pairs.jsonl): 10 by label (`question` x8, `awaiting author response` x2) and 8 by the clarification regex. Gold positives total 21 (3 random pairs also fire the regex).
Caveat on the gold label: reading the 21 matched snippets by hand, several regex hits are not real info requests (a `which` inside a pasted bash script, an "Example:" heading, a maintainer musing "which line were you mentioning?"), and `question` labels often mean "user asked how to", not "underspecified". So precision and recall below are measured against a noisy proxy. The label rows are the more trustworthy slice.

Pairs scored: 58, errors: 0, wall time: 412s. Truth files: 139, of which 3 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| Kludex/starlette | 12 | 0.667 | 0.833 | 0.833 | 0.591 | 0.691 | 0.691 |
| encode/httpx | 2 | 0.000 | 0.500 | 1.000 | 0.000 | 0.125 | 0.750 |
| fastapi/typer | 14 | 0.214 | 0.714 | 0.857 | 0.121 | 0.440 | 0.655 |
| pallets/click | 1 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 |
| pallets/flask | 11 | 0.727 | 0.909 | 1.000 | 0.258 | 0.470 | 0.553 |
| psf/requests | 11 | 0.545 | 0.818 | 0.909 | 0.500 | 0.727 | 0.773 |
| pydantic/pydantic | 7 | 0.143 | 0.571 | 0.714 | 0.143 | 0.500 | 0.643 |
| **overall** | 58 | 0.466 | 0.776 | 0.879 | 0.321 | 0.550 | 0.664 |
| overall, pairs with a code file in truth | 57 | 0.474 | 0.789 | 0.895 | 0.327 | 0.559 | 0.676 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 4 | FP 10 |
| predicted agent_ready | FN 17 | TN 27 |

n=58, accuracy 0.534, precision 0.286, recall 0.190, predicted needs_human 14, gold positives 21. needs_human rate on gold positives 0.190, on gold negatives (false-alarm rate) 0.270.

needs_human rate by how the pair was selected:

| source / gold | n | needs_human | rate |
|---|---|---|---|
| label / pos | 10 | 4 | 0.400 |
| random / neg | 37 | 10 | 0.270 |
| random / pos | 3 | 0 | 0.000 |
| regex / pos | 8 | 0 | 0.000 |

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/Kludex/starlette/issues/1724 cov@5=0.000 | truth: mkdocs.yml | predicted: starlette/routing.py, starlette/applications.py, starlette/background.py
- https://github.com/fastapi/typer/issues/438 cov@5=0.000 | truth: typer/rich_utils.py | predicted: typer/main.py, typer/params.py, typer/_click/utils.py
- https://github.com/fastapi/typer/issues/359 cov@5=0.000 | truth: typer/_completion_classes.py | predicted: typer/main.py, typer/_completion_shared.py, typer/core.py
- https://github.com/psf/requests/issues/7434 cov@5=0.000 | truth: src/requests/_types.py | predicted: src/requests/models.py, src/requests/sessions.py, src/requests/utils.py
- https://github.com/pydantic/pydantic/issues/9909 cov@5=0.000 | truth: pydantic/_internal/_generate_schema.py | predicted: pydantic/main.py, pydantic/json_schema.py, pydantic/fields.py
- https://github.com/Kludex/starlette/issues/2155 cov@5=0.000 | truth: starlette/applications.py, starlette/formparsers.py, starlette/middleware/body_limit.py, starlette/routing.py | predicted: starlette/requests.py, starlette/responses.py, starlette/testclient.py
- https://github.com/pydantic/pydantic/issues/7713 cov@5=0.000 | truth: pydantic-core/src/lookup_key.rs, pydantic-core/src/serializers/infer.rs, pydantic-core/src/serializers/polymorphism_trampoline.rs, pydantic-core/src/tools.rs ... | predicted: pydantic/main.py, pydantic/v1/main.py, pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi
- https://github.com/Kludex/starlette/issues/64 cov@5=0.091 | truth: .travis.yml, mkdocs.yml, scripts/lint, scripts/test ... | predicted: starlette/applications.py, starlette/exceptions.py, starlette/middleware/httpsredirect.py
- https://github.com/fastapi/typer/issues/1503 cov@5=0.167 | truth: .github/workflows/test-redistribute.yml, pdm_build.py, pyproject.toml, typer/_completion_shared.py ... | predicted: typer/main.py, typer/_completion_shared.py, typer/params.py
- https://github.com/Kludex/starlette/issues/3308 cov@5=0.200 | truth: mkdocs.yml, starlette/endpoints.py, starlette/middleware/base.py, starlette/middleware/gzip.py ... | predicted: starlette/status.py, starlette/requests.py, starlette/routing.py

## 2026-10-27 05:51 | DEV set | variant `grep` | k=5 | n=60

Set: dev (`evidence/pairs.jsonl`). ready/checklist.py was calibrated on these issues, so readiness numbers here are optimistic.

Note: engine HEAD 6076543 (ready/ last changed in f3f66db) at start, HEAD 6076543 (ready/ last changed in f3f66db) +uncommitted ready/ edits at end (ready/ changed during the run; numbers may mix versions).

Checked after the run: the uncommitted edits are ready/checklist.py and ready/cli.py (mtime 05:48), plus a new ready/plan.py. The run started at about 05:34 with a clean ready/, and run.py imports ready.api (and through it checklist) once at startup, so every pair was scored with the committed f3f66db code. The mid-run edits were never loaded.

Pairs scored: 60, errors: 0, wall time: 1064s. Truth files: 91, of which 0 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| encode/httpx | 20 | 0.400 | 0.600 | 0.650 | 0.237 | 0.475 | 0.533 |
| fastapi/sqlmodel | 7 | 0.857 | 0.857 | 0.857 | 0.714 | 0.857 | 0.857 |
| pallets/click | 13 | 0.538 | 0.846 | 0.846 | 0.500 | 0.808 | 0.808 |
| pydantic/pydantic | 20 | 0.350 | 0.700 | 0.800 | 0.275 | 0.550 | 0.650 |
| **overall** | 60 | 0.467 | 0.717 | 0.767 | 0.362 | 0.617 | 0.669 |
| overall, pairs with a code file in truth | 54 | 0.519 | 0.796 | 0.852 | 0.403 | 0.685 | 0.744 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 0 | FP 6 |
| predicted agent_ready | FN 3 | TN 51 |

n=60, accuracy 0.850, precision 0.000, recall 0.000, predicted needs_human 6, gold positives 3. needs_human rate on gold positives 0.000, on gold negatives (false-alarm rate) 0.105.

needs_human rate by how the pair was selected:

| source / gold | n | needs_human | rate |
|---|---|---|---|
| random / neg | 57 | 6 | 0.105 |
| random / pos | 3 | 0 | 0.000 |

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/encode/httpx/issues/2884 cov@5=0.000 | truth: pyproject.toml | predicted: httpx/_client.py, httpx/_transports/default.py, httpx/_main.py
- https://github.com/encode/httpx/issues/309 cov@5=0.000 | truth: httpx/middleware.py | predicted: httpx/dispatch/http11.py, httpx/client.py, httpx/models.py
- https://github.com/encode/httpx/issues/2599 cov@5=0.000 | truth: mkdocs.yml | predicted: httpx/_client.py, httpx/_main.py, httpx/_models.py
- https://github.com/encode/httpx/issues/2694 cov@5=0.000 | truth: httpx/_urlparse.py | predicted: httpx/_client.py, httpx/_transports/asgi.py, httpx/_exceptions.py
- https://github.com/encode/httpx/issues/2810 cov@5=0.000 | truth: httpx/_transports/asgi.py | predicted: httpx/_urls.py, httpx/_decoders.py, httpx/_client.py
- https://github.com/fastapi/sqlmodel/issues/189 cov@5=0.000 | truth: sqlmodel/sql/expression.py.jinja2 | predicted: sqlmodel/orm/session.py, sqlmodel/ext/asyncio/session.py, .github/actions/comment-docs-preview-in-pr/app/main.py
- https://github.com/pallets/click/issues/3786 cov@5=0.000 | truth: pyproject.toml | predicted: src/click/core.py, src/click/_termui_impl.py, src/click/termui.py
- https://github.com/pallets/click/issues/3766 cov@5=0.000 | truth: .github/workflows/nightly.yaml | predicted: src/click/core.py, src/click/testing.py, tests/test_context.py
- https://github.com/pydantic/pydantic/issues/13977 cov@5=0.000 | truth: .github/workflows/ci.yml | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/src/errors/validation_exception.rs, pydantic-core/python/pydantic_core/core_schema.py
- https://github.com/pydantic/pydantic/issues/13976 cov@5=0.000 | truth: pydantic/_internal/_validators.py | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/python/pydantic_core/core_schema.py, pydantic/_internal/_generate_schema.py

## 2026-10-27 06:28 | HELD-OUT set | variant `grep` | k=5 | n=58

Set: held-out (`evidence/heldout.jsonl`). None of these issues were used to build or tune Ready.

Note: engine HEAD e130718 (ready/ last changed in e130718) at start, HEAD 79d8054 (ready/ last changed in e130718) at end (ready/ changed during the run; numbers may mix versions).

Pairs scored: 58, errors: 0, wall time: 283s. Truth files: 139, of which 3 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| Kludex/starlette | 12 | 0.667 | 0.833 | 0.833 | 0.591 | 0.691 | 0.691 |
| encode/httpx | 2 | 0.000 | 0.500 | 1.000 | 0.000 | 0.125 | 0.750 |
| fastapi/typer | 14 | 0.214 | 0.714 | 0.786 | 0.121 | 0.452 | 0.617 |
| pallets/click | 1 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 |
| pallets/flask | 11 | 0.727 | 0.818 | 1.000 | 0.258 | 0.424 | 0.553 |
| psf/requests | 11 | 0.545 | 0.636 | 0.909 | 0.500 | 0.636 | 0.818 |
| pydantic/pydantic | 7 | 0.143 | 0.429 | 0.571 | 0.143 | 0.357 | 0.500 |
| **overall** | 58 | 0.466 | 0.707 | 0.845 | 0.321 | 0.509 | 0.647 |
| overall, pairs with a code file in truth | 57 | 0.474 | 0.719 | 0.860 | 0.327 | 0.518 | 0.658 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 4 | FP 10 |
| predicted agent_ready | FN 17 | TN 27 |

n=58, accuracy 0.534, precision 0.286, recall 0.190, predicted needs_human 14, gold positives 21. needs_human rate on gold positives 0.190, on gold negatives (false-alarm rate) 0.270.

needs_human rate by how the pair was selected:

| source / gold | n | needs_human | rate |
|---|---|---|---|
| label / pos | 10 | 4 | 0.400 |
| random / neg | 37 | 10 | 0.270 |
| random / pos | 3 | 0 | 0.000 |
| regex / pos | 8 | 0 | 0.000 |

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/Kludex/starlette/issues/1724 cov@5=0.000 | truth: mkdocs.yml | predicted: starlette/routing.py, starlette/applications.py, starlette/background.py
- https://github.com/fastapi/typer/issues/1156 cov@5=0.000 | truth: typer/rich_utils.py | predicted: typer/main.py, typer/params.py, pyproject.toml
- https://github.com/fastapi/typer/issues/438 cov@5=0.000 | truth: typer/rich_utils.py | predicted: typer/main.py, typer/params.py, typer/_click/utils.py
- https://github.com/fastapi/typer/issues/359 cov@5=0.000 | truth: typer/_completion_classes.py | predicted: typer/main.py, typer/_completion_shared.py, typer/core.py
- https://github.com/psf/requests/issues/7434 cov@5=0.000 | truth: src/requests/_types.py | predicted: src/requests/models.py, src/requests/sessions.py, src/requests/utils.py
- https://github.com/pydantic/pydantic/issues/8071 cov@5=0.000 | truth: pydantic/_internal/_generate_schema.py | predicted: pydantic/main.py, pydantic/v1/main.py, pyproject.toml
- https://github.com/pydantic/pydantic/issues/9909 cov@5=0.000 | truth: pydantic/_internal/_generate_schema.py | predicted: pydantic/main.py, pydantic/json_schema.py, pyproject.toml
- https://github.com/Kludex/starlette/issues/2155 cov@5=0.000 | truth: starlette/applications.py, starlette/formparsers.py, starlette/middleware/body_limit.py, starlette/routing.py | predicted: starlette/requests.py, starlette/responses.py, starlette/testclient.py
- https://github.com/pydantic/pydantic/issues/7713 cov@5=0.000 | truth: pydantic-core/src/lookup_key.rs, pydantic-core/src/serializers/infer.rs, pydantic-core/src/serializers/polymorphism_trampoline.rs, pydantic-core/src/tools.rs ... | predicted: pydantic/main.py, pydantic/v1/main.py, pyproject.toml
- https://github.com/Kludex/starlette/issues/64 cov@5=0.091 | truth: .travis.yml, mkdocs.yml, scripts/lint, scripts/test ... | predicted: starlette/applications.py, starlette/exceptions.py, starlette/middleware/httpsredirect.py

## 2026-10-27 06:43 | DEV set | variant `grep` | k=5 | n=60

Set: dev (`evidence/pairs.jsonl`). ready/checklist.py was calibrated on these issues, so readiness numbers here are optimistic.

Note: engine HEAD 79d8054 (ready/ last changed in e130718).

Pairs scored: 60, errors: 0, wall time: 913s. Truth files: 91, of which 0 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| encode/httpx | 20 | 0.400 | 0.650 | 0.700 | 0.237 | 0.550 | 0.600 |
| fastapi/sqlmodel | 7 | 0.857 | 0.857 | 0.857 | 0.714 | 0.857 | 0.857 |
| pallets/click | 13 | 0.538 | 0.846 | 0.846 | 0.500 | 0.808 | 0.808 |
| pydantic/pydantic | 20 | 0.350 | 0.600 | 0.750 | 0.275 | 0.442 | 0.575 |
| **overall** | 60 | 0.467 | 0.700 | 0.767 | 0.362 | 0.606 | 0.667 |
| overall, pairs with a code file in truth | 54 | 0.519 | 0.759 | 0.833 | 0.403 | 0.654 | 0.722 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 0 | FP 6 |
| predicted agent_ready | FN 3 | TN 51 |

n=60, accuracy 0.850, precision 0.000, recall 0.000, predicted needs_human 6, gold positives 3. needs_human rate on gold positives 0.000, on gold negatives (false-alarm rate) 0.105.

needs_human rate by how the pair was selected:

| source / gold | n | needs_human | rate |
|---|---|---|---|
| random / neg | 57 | 6 | 0.105 |
| random / pos | 3 | 0 | 0.000 |

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/encode/httpx/issues/309 cov@5=0.000 | truth: httpx/middleware.py | predicted: httpx/dispatch/http11.py, httpx/client.py, setup.cfg
- https://github.com/encode/httpx/issues/2599 cov@5=0.000 | truth: mkdocs.yml | predicted: httpx/_client.py, httpx/_main.py, httpx/_models.py
- https://github.com/encode/httpx/issues/2694 cov@5=0.000 | truth: httpx/_urlparse.py | predicted: httpx/_client.py, httpx/_transports/asgi.py, httpx/_exceptions.py
- https://github.com/encode/httpx/issues/2810 cov@5=0.000 | truth: httpx/_transports/asgi.py | predicted: httpx/_urls.py, httpx/_decoders.py, httpx/_client.py
- https://github.com/fastapi/sqlmodel/issues/189 cov@5=0.000 | truth: sqlmodel/sql/expression.py.jinja2 | predicted: sqlmodel/orm/session.py, sqlmodel/ext/asyncio/session.py, mkdocs.yml
- https://github.com/pallets/click/issues/3786 cov@5=0.000 | truth: pyproject.toml | predicted: src/click/core.py, src/click/_termui_impl.py, .github/workflows/lock.yaml
- https://github.com/pallets/click/issues/3766 cov@5=0.000 | truth: .github/workflows/nightly.yaml | predicted: src/click/core.py, src/click/testing.py, .github/workflows/lock.yaml
- https://github.com/pydantic/pydantic/issues/13977 cov@5=0.000 | truth: .github/workflows/ci.yml | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/src/errors/validation_exception.rs, pyproject.toml
- https://github.com/pydantic/pydantic/issues/13976 cov@5=0.000 | truth: pydantic/_internal/_validators.py | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/python/pydantic_core/core_schema.py, pyproject.toml
- https://github.com/pydantic/pydantic/issues/14041 cov@5=0.000 | truth: pydantic/_internal/_docs_extraction.py | predicted: pydantic/main.py, pydantic/json_schema.py, pyproject.toml

## 2026-10-27 06:48 | HELD-OUT set | variant `grep` | k=5 | n=58

Set: held-out (`evidence/heldout.jsonl`). None of these issues were used to build or tune Ready.

Note: engine HEAD a4a094b (ready/ last changed in a4a094b).

Pairs scored: 58, errors: 0, wall time: 276s. Truth files: 139, of which 3 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| Kludex/starlette | 12 | 0.667 | 0.833 | 0.833 | 0.591 | 0.691 | 0.691 |
| encode/httpx | 2 | 0.000 | 0.500 | 1.000 | 0.000 | 0.125 | 0.750 |
| fastapi/typer | 14 | 0.214 | 0.714 | 0.857 | 0.121 | 0.440 | 0.655 |
| pallets/click | 1 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 |
| pallets/flask | 11 | 0.727 | 0.909 | 1.000 | 0.258 | 0.470 | 0.553 |
| psf/requests | 11 | 0.545 | 0.818 | 0.909 | 0.500 | 0.727 | 0.773 |
| pydantic/pydantic | 7 | 0.143 | 0.571 | 0.714 | 0.143 | 0.500 | 0.643 |
| **overall** | 58 | 0.466 | 0.776 | 0.879 | 0.321 | 0.550 | 0.664 |
| overall, pairs with a code file in truth | 57 | 0.474 | 0.789 | 0.895 | 0.327 | 0.559 | 0.676 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 4 | FP 10 |
| predicted agent_ready | FN 17 | TN 27 |

n=58, accuracy 0.534, precision 0.286, recall 0.190, predicted needs_human 14, gold positives 21. needs_human rate on gold positives 0.190, on gold negatives (false-alarm rate) 0.270.

needs_human rate by how the pair was selected:

| source / gold | n | needs_human | rate |
|---|---|---|---|
| label / pos | 10 | 4 | 0.400 |
| random / neg | 37 | 10 | 0.270 |
| random / pos | 3 | 0 | 0.000 |
| regex / pos | 8 | 0 | 0.000 |

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/Kludex/starlette/issues/1724 cov@5=0.000 | truth: mkdocs.yml | predicted: starlette/routing.py, starlette/applications.py, starlette/background.py
- https://github.com/fastapi/typer/issues/438 cov@5=0.000 | truth: typer/rich_utils.py | predicted: typer/main.py, typer/params.py, typer/_click/utils.py
- https://github.com/fastapi/typer/issues/359 cov@5=0.000 | truth: typer/_completion_classes.py | predicted: typer/main.py, typer/_completion_shared.py, typer/core.py
- https://github.com/psf/requests/issues/7434 cov@5=0.000 | truth: src/requests/_types.py | predicted: src/requests/models.py, src/requests/sessions.py, src/requests/utils.py
- https://github.com/pydantic/pydantic/issues/9909 cov@5=0.000 | truth: pydantic/_internal/_generate_schema.py | predicted: pydantic/main.py, pydantic/json_schema.py, pydantic/fields.py
- https://github.com/Kludex/starlette/issues/2155 cov@5=0.000 | truth: starlette/applications.py, starlette/formparsers.py, starlette/middleware/body_limit.py, starlette/routing.py | predicted: starlette/requests.py, starlette/responses.py, starlette/testclient.py
- https://github.com/pydantic/pydantic/issues/7713 cov@5=0.000 | truth: pydantic-core/src/lookup_key.rs, pydantic-core/src/serializers/infer.rs, pydantic-core/src/serializers/polymorphism_trampoline.rs, pydantic-core/src/tools.rs ... | predicted: pydantic/main.py, pydantic/v1/main.py, pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi
- https://github.com/Kludex/starlette/issues/64 cov@5=0.091 | truth: .travis.yml, mkdocs.yml, scripts/lint, scripts/test ... | predicted: starlette/applications.py, starlette/exceptions.py, starlette/middleware/httpsredirect.py
- https://github.com/fastapi/typer/issues/1503 cov@5=0.167 | truth: .github/workflows/test-redistribute.yml, pdm_build.py, pyproject.toml, typer/_completion_shared.py ... | predicted: typer/main.py, typer/_completion_shared.py, typer/params.py
- https://github.com/Kludex/starlette/issues/3308 cov@5=0.200 | truth: mkdocs.yml, starlette/endpoints.py, starlette/middleware/base.py, starlette/middleware/gzip.py ... | predicted: starlette/status.py, starlette/requests.py, starlette/routing.py

## 2026-10-27 09:23 | HELD-OUT set | variant `grep` | k=5 | n=58

Set: held-out (`evidence/heldout.jsonl`). None of these issues were used to build or tune Ready.

Note: engine HEAD db48ecf (ready/ last changed in db48ecf).

Pairs scored: 58, errors: 0, wall time: 369s. Truth files: 139, of which 3 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| Kludex/starlette | 12 | 0.667 | 0.833 | 0.833 | 0.591 | 0.691 | 0.691 |
| encode/httpx | 2 | 0.000 | 0.500 | 1.000 | 0.000 | 0.125 | 0.750 |
| fastapi/typer | 14 | 0.214 | 0.714 | 0.857 | 0.121 | 0.440 | 0.655 |
| pallets/click | 1 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 |
| pallets/flask | 11 | 0.727 | 0.909 | 1.000 | 0.258 | 0.470 | 0.553 |
| psf/requests | 11 | 0.455 | 0.727 | 0.909 | 0.455 | 0.636 | 0.773 |
| pydantic/pydantic | 7 | 0.143 | 0.571 | 0.714 | 0.143 | 0.500 | 0.643 |
| **overall** | 58 | 0.448 | 0.759 | 0.879 | 0.312 | 0.532 | 0.664 |
| overall, pairs with a code file in truth | 57 | 0.456 | 0.772 | 0.895 | 0.318 | 0.542 | 0.676 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 4 | FP 10 |
| predicted agent_ready | FN 17 | TN 27 |

n=58, accuracy 0.534, precision 0.286, recall 0.190, predicted needs_human 14, gold positives 21. needs_human rate on gold positives 0.190, on gold negatives (false-alarm rate) 0.270.

needs_human rate by how the pair was selected:

| source / gold | n | needs_human | rate |
|---|---|---|---|
| label / pos | 10 | 4 | 0.400 |
| random / neg | 37 | 10 | 0.270 |
| random / pos | 3 | 0 | 0.000 |
| regex / pos | 8 | 0 | 0.000 |

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/Kludex/starlette/issues/1724 cov@5=0.000 | truth: mkdocs.yml | predicted: starlette/routing.py, starlette/applications.py, starlette/background.py
- https://github.com/fastapi/typer/issues/438 cov@5=0.000 | truth: typer/rich_utils.py | predicted: typer/main.py, typer/params.py, typer/_click/utils.py
- https://github.com/fastapi/typer/issues/359 cov@5=0.000 | truth: typer/_completion_classes.py | predicted: typer/main.py, typer/_completion_shared.py, typer/core.py
- https://github.com/psf/requests/issues/7434 cov@5=0.000 | truth: src/requests/_types.py | predicted: src/requests/models.py, src/requests/sessions.py, src/requests/utils.py
- https://github.com/pydantic/pydantic/issues/9909 cov@5=0.000 | truth: pydantic/_internal/_generate_schema.py | predicted: pydantic/main.py, pydantic/json_schema.py, pydantic/fields.py
- https://github.com/Kludex/starlette/issues/2155 cov@5=0.000 | truth: starlette/applications.py, starlette/formparsers.py, starlette/middleware/body_limit.py, starlette/routing.py | predicted: starlette/requests.py, starlette/responses.py, starlette/testclient.py
- https://github.com/pydantic/pydantic/issues/7713 cov@5=0.000 | truth: pydantic-core/src/lookup_key.rs, pydantic-core/src/serializers/infer.rs, pydantic-core/src/serializers/polymorphism_trampoline.rs, pydantic-core/src/tools.rs ... | predicted: pydantic/main.py, pydantic/v1/main.py, pydantic/root_model.py
- https://github.com/Kludex/starlette/issues/64 cov@5=0.091 | truth: .travis.yml, mkdocs.yml, scripts/lint, scripts/test ... | predicted: starlette/applications.py, starlette/exceptions.py, starlette/middleware/httpsredirect.py
- https://github.com/fastapi/typer/issues/1503 cov@5=0.167 | truth: .github/workflows/test-redistribute.yml, pdm_build.py, pyproject.toml, typer/_completion_shared.py ... | predicted: typer/main.py, typer/_completion_shared.py, typer/params.py
- https://github.com/Kludex/starlette/issues/3308 cov@5=0.200 | truth: mkdocs.yml, starlette/endpoints.py, starlette/middleware/base.py, starlette/middleware/gzip.py ... | predicted: starlette/status.py, starlette/requests.py, starlette/routing.py

## 2026-10-27 09:43 | DEV set | variant `grep` | k=5 | n=60

Set: dev (`evidence/pairs.jsonl`). ready/checklist.py was calibrated on these issues, so readiness numbers here are optimistic.

Note: engine HEAD db48ecf (ready/ last changed in db48ecf).

Pairs scored: 60, errors: 0, wall time: 1239s. Truth files: 91, of which 0 do not exist at base_sha (new files, unpredictable by retrieval).

hit@k = at least one true file in the top k. cov@k = mean fraction of the PR's source files found in the top k.

| repo | n | hit@1 | hit@3 | hit@5 | cov@1 | cov@3 | cov@5 |
|---|---|---|---|---|---|---|---|
| encode/httpx | 20 | 0.400 | 0.600 | 0.650 | 0.237 | 0.475 | 0.533 |
| fastapi/sqlmodel | 7 | 0.857 | 0.857 | 0.857 | 0.714 | 0.857 | 0.857 |
| pallets/click | 13 | 0.462 | 0.846 | 0.846 | 0.462 | 0.808 | 0.808 |
| pydantic/pydantic | 20 | 0.350 | 0.700 | 0.800 | 0.275 | 0.550 | 0.650 |
| **overall** | 60 | 0.450 | 0.717 | 0.767 | 0.354 | 0.617 | 0.669 |
| overall, pairs with a code file in truth | 54 | 0.500 | 0.796 | 0.852 | 0.394 | 0.685 | 0.744 |

Readiness check: `verdict.status == "needs_human"` vs proxy label `needed_clarification`.

| | gold needed_clarification | gold not |
|---|---|---|
| predicted needs_human | TP 0 | FP 6 |
| predicted agent_ready | FN 3 | TN 51 |

n=60, accuracy 0.850, precision 0.000, recall 0.000, predicted needs_human 6, gold positives 3. needs_human rate on gold positives 0.000, on gold negatives (false-alarm rate) 0.105.

needs_human rate by how the pair was selected:

| source / gold | n | needs_human | rate |
|---|---|---|---|
| random / neg | 57 | 6 | 0.105 |
| random / pos | 3 | 0 | 0.000 |

Worst 10 misses (lowest cov@5, fewest true files first):

- https://github.com/encode/httpx/issues/2884 cov@5=0.000 | truth: pyproject.toml | predicted: httpx/_client.py, httpx/_transports/default.py, httpx/_main.py
- https://github.com/encode/httpx/issues/309 cov@5=0.000 | truth: httpx/middleware.py | predicted: httpx/dispatch/http11.py, httpx/client.py, httpx/models.py
- https://github.com/encode/httpx/issues/2599 cov@5=0.000 | truth: mkdocs.yml | predicted: httpx/_client.py, httpx/_main.py, httpx/_models.py
- https://github.com/encode/httpx/issues/2694 cov@5=0.000 | truth: httpx/_urlparse.py | predicted: httpx/_client.py, httpx/_transports/asgi.py, httpx/_exceptions.py
- https://github.com/encode/httpx/issues/2810 cov@5=0.000 | truth: httpx/_transports/asgi.py | predicted: httpx/_urls.py, httpx/_decoders.py, httpx/_client.py
- https://github.com/fastapi/sqlmodel/issues/189 cov@5=0.000 | truth: sqlmodel/sql/expression.py.jinja2 | predicted: sqlmodel/orm/session.py, sqlmodel/ext/asyncio/session.py, .github/actions/comment-docs-preview-in-pr/app/main.py
- https://github.com/pallets/click/issues/3786 cov@5=0.000 | truth: pyproject.toml | predicted: src/click/core.py, src/click/_termui_impl.py, src/click/termui.py
- https://github.com/pallets/click/issues/3766 cov@5=0.000 | truth: .github/workflows/nightly.yaml | predicted: src/click/core.py, src/click/testing.py, tests/test_context.py
- https://github.com/pydantic/pydantic/issues/13977 cov@5=0.000 | truth: .github/workflows/ci.yml | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/src/errors/validation_exception.rs, pydantic-core/python/pydantic_core/core_schema.py
- https://github.com/pydantic/pydantic/issues/13976 cov@5=0.000 | truth: pydantic/_internal/_validators.py | predicted: pydantic-core/python/pydantic_core/_pydantic_core/__init__.pyi, pydantic-core/python/pydantic_core/core_schema.py, pydantic/_internal/_generate_schema.py

## Backtest on an unseen repo: pallets/werkzeug (27 Oct, engine commit `34198de`, grep variant)

werkzeug was in neither the dev set nor the held-out set, and nothing was tuned on it. The 20 most recently updated closed issues linked to a merged PR were collected with `eval/fetch.py`; 3 failed to check out (git lock files on an exFAT drive), so n = 17. Ground truth is the PR's changed files at its base commit.

| repo | n | hit@1 | hit@3 | hit@5 |
|---|---|---|---|---|
| pallets/werkzeug | 17 | 1.00 | 1.00 | 1.00 |

Read this as an easy set, not as Ready's typical accuracy: 15 of the 17 issues were filed by werkzeug's maintainer and name the exact function or class (for example "`make_conditional` has a lot of problems"). n is small and the result is noisy.

Readiness on the same 17: 1 issue was labelled as needing more information, and Ready did not catch it. Ready flagged 5 of the 16 ordinary issues as needs-human (31%), in line with the 27% false-alarm rate on held-out. The readiness gate is still the weak part.

Files: `evidence/backtest-werkzeug.jsonl`, `evidence/results-grep-backtest-werkzeug.json`.
