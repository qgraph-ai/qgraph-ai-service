# Django Integration Handoff (Temporary)

## 1. Purpose

This file is a temporary handoff for work in the Django backend repository.
It explains the **current, implemented** AI backend surface so Django can replace local dummy planner/executor behavior with real HTTP calls.
Use this as an integration note, not as long-term architecture documentation.

## 2. Current role of AI backend

`qgraph-ai-service` now exists as a separate FastAPI service.
In this bootstrap phase, it provides contract-correct responses for search and segmentation using placeholder logic.
Its main value right now is stable request/response wiring compatible with Django persistence models.

## 3. What Django should know

- The AI backend is a separate service and should be called over HTTP.
- Django should treat it as an external dependency (API contract), not import or depend on its internals.
- Django should keep ownership of:
  - auth/access control
  - execution lifecycle/state machine
  - persistence of search and segmentation artifacts
- AI backend behavior is currently dummy; response **shape** is the important part for integration.

## 4. Current available endpoints

### `GET /health`
- Purpose: service liveness + version metadata.
- Behavior: meaningful for health checks.
- Request: none.
- Response shape:
  - `status` (currently `"ok"`)
  - `service` (default: `"qgraph-ai-service"`)
  - `version` (default: `"0.1.0"`)

### `POST /v1/search/plan`
- Purpose: planning handshake (mode + policy metadata) for Django orchestration.
- Behavior: **dummy** mode decision (random `sync`/`async`).
- Request shape:
  - `query: str`
  - `filters: object` (optional/default `{}`)
  - `output_preferences: object` (optional/default `{}`)
- Response shape:
  - `mode` (`"sync"` or `"async"`)
  - `policy_label`
  - `policy_snapshot` (object)
  - `routing_metadata` (object)
  - `backend_name`
  - `backend_version`

### `POST /v1/search/execute`
- Purpose: return structured search payload for Django persistence.
- Behavior: **dummy content**, contract-correct structure.
- Request shape:
  - `query: str`
  - `filters: object` (optional/default `{}`)
  - `output_preferences: object` (optional/default `{}`)
  - `context: object` (optional/default `{}`)
- Response shape:
  - `title`
  - `overall_confidence`
  - `render_schema_version` (currently `"v1"`)
  - `metadata` (object)
  - `blocks[]` where each block contains:
    - `order`, `block_type`, `title`, `payload`, `explanation`, `confidence`, `provenance`, `warning_text`, `items[]`
  - `items[]` contain:
    - `rank`, `result_type`, `score`, `title`, `snippet_text`, `highlighted_text`, `match_metadata`, `explanation`, `provenance`
- Important contract guarantees:
  - `blocks[].order` is unique per response
  - `items[].rank` is unique within each block

### `POST /v1/segmentation/generate`
- Purpose: return AI-style segmentation output payload (for Django ingestion path).
- Behavior: **dummy content**, contract-correct structure.
- Request shape:
  - `surah_id`
  - `ayahs[]`
  - `options` (e.g. `granularity`, `max_segments`, `include_tags`, `include_summaries`)
  - `context`
- Response shape:
  - `external_id`
  - `model_name`
  - `model_version`
  - `params` (object)
  - `produced_at` (ISO datetime)
  - `segments[]` with:
    - `start_ayah`, `end_ayah`, `title`, `summary`, `tags[]`
- Current response validator enforces:
  - `start_ayah <= end_ayah`
  - segments sorted/non-overlapping

## 5. Integration expectations for Django

What Django can replace now:

1. Replace Django-side search planning dummy logic with HTTP call to `POST /v1/search/plan`.
2. Replace Django-side search execution dummy logic with HTTP call to `POST /v1/search/execute`.
3. Keep Django orchestration lifecycle (sync/async status, Celery flow) unchanged.
4. Keep Django persistence mapping unchanged; current AI backend response shapes are built for that.

For segmentation:

1. Add/update Django service path to call `POST /v1/segmentation/generate`.
2. Ingest returned segments/tags/provenance into existing segmentation models (`SegmentationVersion`, `Segment`, `Tag`, `SegmentTag`, `SegmentationOutput`).

Settings/use in Django:

- Continue using Django-side service URL/timeout settings (as previously documented):
  - `SEARCH_AI_BACKEND_URL`
  - `SEARCH_AI_BACKEND_TIMEOUT_SECONDS`
- Add equivalent segmentation timeout/base-url usage if not already centralized.

## 6. Current limitations

- Responses are placeholder/dummy (not real AI quality).
- No real retrieval/model inference logic.
- Request-response only; no async job orchestration inside AI backend.
- No auth middleware in AI backend (expected to be internal service behind Django/infrastructure boundaries).
- Error envelope is minimal and currently:
  - validation: `{"error": "validation_error", "detail": [...]}`
  - HTTP errors: `{"error": "http_error", "detail": {...}}`
  - unexpected: `{"error": "internal_server_error", "detail": {"message": "Unexpected server error"}}`

## 7. Local development notes

Default local service URL:

- `http://127.0.0.1:8001`

Run options:

- Native:
  - `uv run uvicorn src.main:app --reload --port 8001`
- Docker Compose:
  - `docker compose up --build` (first run)
  - `docker compose up` (next runs)

Connectivity assumptions:

- Django on host machine -> call `http://127.0.0.1:8001`
- Django in same Compose network -> call `http://ai-backend:8001`

## 8. Suggested next step inside Django backend

Implement a small HTTP client adapter in Django `search/services/` that calls:

1. `POST /v1/search/plan`
2. `POST /v1/search/execute`

Then switch planner/executor placeholders to this adapter while keeping Django lifecycle/persistence code unchanged.
After that, wire segmentation generation call to `POST /v1/segmentation/generate` using the same pattern.
