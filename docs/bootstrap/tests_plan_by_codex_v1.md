# Tests Plan (Bootstrap Phase, v1)

## 1. Short summary
The testing goal in this phase is to protect FastAPI wiring and Django-facing response contracts.
Tests should verify endpoint availability, schema shape, and key structural constraints (`order`, `rank`) using dummy outputs.
This is not the phase for testing real AI quality, retrieval relevance, or performance.

## 2. Proposed `tests/` structure

```text
tests/
  conftest.py
  api/
    test_health.py
    test_search_plan.py
    test_search_execute.py
    test_segmentation_generate.py
  services/
    test_planning.py
```

- `conftest.py`: should exist now. Keep it minimal for shared `TestClient` and small request payload fixtures.
- `unit/`: not needed now as a separate top-level folder; current scope is small and covered by `api/` + one focused service test.
- `regression/`: later. Add only after real bugs appear and need dedicated non-regression tests.
- `quality/`: later. No real AI quality metrics exist in bootstrap phase.
- `performance/`: later. Do not add before real model/store calls and realistic workloads exist.

## 3. What each part is for
- `tests/conftest.py`: shared test setup to avoid duplication and keep endpoint tests concise.
- `tests/api/test_health.py`: verifies service liveness and version metadata contract.
- `tests/api/test_search_plan.py`: verifies plan endpoint contract and valid mode values.
- `tests/api/test_search_execute.py`: verifies search response schema shape and uniqueness constraints for blocks/items.
- `tests/api/test_segmentation_generate.py`: verifies segmentation response schema and required provenance fields.
- `tests/services/test_planning.py`: verifies dummy planning behavior returns only allowed modes.

## 4. Suggested first tests
1. `GET /health` returns `200` and includes expected service/version fields.
2. `POST /v1/search/plan` returns `200` with required keys:
   `mode`, `policy_label`, `policy_snapshot`, `routing_metadata`, `backend_name`, `backend_version`.
3. `POST /v1/search/plan` returns `mode` only in `{"sync", "async"}`.
4. `POST /v1/search/execute` returns `200` with required top-level fields:
   `title`, `overall_confidence`, `render_schema_version`, `metadata`, `blocks`.
5. `POST /v1/search/execute` enforces unique `blocks[].order`.
6. `POST /v1/search/execute` enforces unique `items[].rank` within each block.
7. `POST /v1/segmentation/generate` returns `200` with required provenance fields:
   `external_id`, `model_name`, `model_version`, `params`, `produced_at`, `segments`.
8. `POST /v1/segmentation/generate` returns segments with valid shape (`start_ayah`, `end_ayah`, optional `tags` list).

## 5. Guardrails
- Avoid tests for model quality, semantic relevance, or advanced AI behavior.
- Avoid heavy fixture factories and large synthetic datasets.
- Avoid flaky randomness checks; for planning, assert allowed outputs, not statistical distribution.
- Keep tests small, contract-focused, and easy to update while wiring evolves.
