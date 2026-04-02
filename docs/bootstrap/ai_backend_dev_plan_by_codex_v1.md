# AI Backend Dev Plan (Bootstrap Phase)

## 1. Short summary
The next goal is to stand up a minimal FastAPI service that Django can call for search and segmentation.
This phase is only about wiring, endpoint contracts, and correct response schemas with dummy behavior.
Real AI retrieval, generation, and optimization stay out of scope.

## 2. Proposed folder structure under `src/`

```text
src/
  main.py
  config.py
  api/
    health.py
    search.py
    segmentation.py
    schemas/
      search.py
      segmentation.py
  services/
    planning.py
    search_dummy.py
    segmentation_dummy.py
  ai_placeholders/
    vector_store.py
    graph_store.py
    workflow.py
```

- `src/main.py`: FastAPI app entrypoint; registers routers and exposes service startup surface.
- `src/config.py`: minimal settings/constants (service name, version, default metadata values).
- `src/api/health.py`: `GET /health` endpoint for readiness and version checks.
- `src/api/search.py`: handlers for `POST /v1/search/plan` and `POST /v1/search/execute`.
- `src/api/segmentation.py`: handler for `POST /v1/segmentation/generate`.
- `src/api/schemas/search.py`: Pydantic request/response models for search endpoints.
- `src/api/schemas/segmentation.py`: Pydantic request/response models for segmentation endpoint.
- `src/services/planning.py`: dummy planning decision (random `sync`/`async`, equal probability).
- `src/services/search_dummy.py`: builds schema-correct placeholder search payload (blocks/items).
- `src/services/segmentation_dummy.py`: builds schema-correct placeholder segmentation payload.
- `src/ai_placeholders/vector_store.py`: stub object/interface for future vector retrieval integration.
- `src/ai_placeholders/graph_store.py`: stub object/interface for future graph retrieval integration.
- `src/ai_placeholders/workflow.py`: stub object/interface for future LangGraph workflow integration.

## 3. Minimal scripts/components to implement next
- FastAPI app bootstrap and router registration.
- `GET /health` with static service/version payload.
- `POST /v1/search/plan` using dummy random routing policy.
- `POST /v1/search/execute` returning Django-compatible placeholder blocks/items.
- `POST /v1/segmentation/generate` returning Django-compatible placeholder segments/provenance.
- Shared dummy response builders that enforce unique `blocks[].order` and `items[].rank`.

## 4. Suggested development order
1. Create `src/main.py` and wire routers for `health`, `search`, and `segmentation`.
2. Add Pydantic schemas for all three endpoints (request + response contracts first).
3. Implement `services/planning.py` with random equal-probability mode selection.
4. Implement `services/search_dummy.py` with fixed, schema-correct placeholder output.
5. Implement `services/segmentation_dummy.py` with fixed, schema-correct placeholder output.
6. Connect API handlers to services and return serialized responses only (no side effects).
7. Run local smoke checks to validate response shape against Django expectations.

## 5. Notes / guardrails
- Keep logic flat and explicit; avoid unnecessary layers and abstractions.
- Prioritize contract correctness over content quality.
- Do not add external AI providers, vector DBs, or job orchestration in this phase.
- Keep placeholders small but structured so Django can persist responses safely.
