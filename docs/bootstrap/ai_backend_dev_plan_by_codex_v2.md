# AI Backend Dev Plan (Bootstrap Phase, v2)

## 1. Short summary
The next goal is to deliver a minimal FastAPI service that Django can call for search and segmentation.
The focus remains contract-safe wiring, endpoint shape correctness, and dummy behavior.
The API should stay thin; core AI-related modules should already exist as first-class root modules.

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
    search_service.py
    segmentation_service.py
  stores/
    vector_store.py
    graph_store.py
  workflows/
    search_workflow.py
    segmentation_workflow.py
```

- `src/main.py`: FastAPI entrypoint; creates app and mounts routers.
- `src/config.py`: minimal constants/settings (service version, backend identity fields).
- `src/api/health.py`: `GET /health` readiness/version endpoint.
- `src/api/search.py`: `POST /v1/search/plan` and `POST /v1/search/execute` handlers.
- `src/api/segmentation.py`: `POST /v1/segmentation/generate` handler.
- `src/api/schemas/search.py`: request/response models for search contracts.
- `src/api/schemas/segmentation.py`: request/response models for segmentation contracts.
- `src/services/planning.py`: dummy planning decision (`sync`/`async` random 50/50).
- `src/services/search_service.py`: search request orchestration + placeholder response build.
- `src/services/segmentation_service.py`: segmentation request orchestration + placeholder response build.
- `src/stores/vector_store.py`: dummy vector store client/interface placeholder.
- `src/stores/graph_store.py`: dummy graph store client/interface placeholder.
- `src/workflows/search_workflow.py`: minimal/dummy search workflow boundary.
- `src/workflows/segmentation_workflow.py`: minimal/dummy segmentation workflow boundary.

## 3. Minimal scripts/components to implement next
- FastAPI app bootstrap and router registration.
- `GET /health` with static service/version info.
- `POST /v1/search/plan` with random equal-probability mode selection.
- `POST /v1/search/execute` with Django-compatible placeholder blocks/items.
- `POST /v1/segmentation/generate` with Django-compatible placeholder segments/provenance.
- Minimal stubs in `stores/` and `workflows/` (no real AI logic).

## 4. Suggested development order
1. Create `src/main.py` and route wiring for health/search/segmentation.
2. Add Pydantic schemas first, so endpoint contracts are explicit and validated.
3. Implement `services/planning.py` and wire `POST /v1/search/plan`.
4. Implement `search_service.py` with fixed placeholder response for `/v1/search/execute`.
5. Implement `segmentation_service.py` with fixed placeholder response for `/v1/segmentation/generate`.
6. Add root-level placeholders in `stores/` and `workflows/`.
7. Run local smoke checks to confirm schema shape and uniqueness constraints (`order`, `rank`).

## 5. Notes / guardrails
- Keep the API thin; keep request-level orchestration in `services/`.
- Keep AI capabilities first-class in root modules, even when dummy.
- Do not add abstractions for future scenarios that are not needed now.
- Do not implement real retrieval, model calls, or async job orchestration.
- Prioritize schema correctness and predictable placeholder outputs.
