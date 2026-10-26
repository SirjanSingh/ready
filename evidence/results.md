# Ready eval results

Appended by `eval/run.py`. Pairs: `evidence/pairs.jsonl`.

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
