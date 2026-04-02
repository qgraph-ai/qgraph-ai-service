# QGraph Django Backend Context for AI Backend

## 1. Why this file exists

This document is a portable context handoff for the separate AI backend repository.

Goals:
- explain the big picture of the current QGraph Django backend
- identify which Django apps need AI-backend collaboration
- define endpoint contracts the AI backend should expose so integration can be implemented cleanly

Status clarity:
- `search` has explicit integration seams and is the primary immediate AI dependency
- `segmentation` stores AI output provenance and is the secondary AI dependency (currently data-model ready, not fully wired to generation calls)
- `quran` and `accounts` are not direct AI-backend consumers

---

## 2. Big Picture of the Django Backend

### 2.1 Stack and architecture

Core stack:
- Django + Django REST Framework
- PostgreSQL as canonical state
- Celery + Redis for async/background execution
- Djoser + JWT for auth
- drf-spectacular for OpenAPI docs

Project-level boundaries:
- `qgraph/` = settings, root URLs, logging, Celery bootstrap
- `accounts/` = custom user model and auth identity
- `quran/` = canonical Quran data (surahs, ayahs, translations, structure boundaries)
- `segmentation/` = user workspaces + versioned segmentation artifacts + AI provenance metadata
- `search/` = search orchestration + execution tracking + structured response persistence

### 2.2 API surface

Versioned routes are mounted under:
- `/api/v1/quran/...`
- `/api/v1/segmentation/...`
- `/api/v1/search/...`
- `/api/auth/...`

OpenAPI:
- `/api/schema/`
- `/api/docs/`
- `/api/redoc/`

### 2.3 Identifier strategy

- Segmentation uses public IDs for external routes:
  - workspace: `slug`
  - segmentation version: UUID `public_id`
  - tag: UUID `public_id`
- Quran uses domain-native numbers:
  - surah by `number`
  - ayah by `number_global` or `(surah_number, number_in_surah)`
- Internal integer DB PKs still exist and appear in payloads

### 2.4 Auth/access model

- JWT auth for owner-scoped write surfaces
- Public read surfaces exist for Quran and public segmentation browsing
- Search has mixed mode:
  - authenticated users: normal ownership checks
  - guests: token-based access to specific execution/result (`X-Search-Guest-Token`)

### 2.5 Async model

- Celery is wired and used by `search` async execution mode
- Django remains source of truth for execution lifecycle/status
- Async is currently orchestration-side in Django, not offloaded as a first-class job system to external AI backend

---

## 3. Which apps need AI backend?

## 3.1 Search app (`search`) — YES (immediate)

This is the main integration target.

Current state:
- planner + executor are placeholders (`search/services/planning.py`, `search/services/execution_backend.py`)
- orchestration lifecycle and persistence are production-style and already in place
- settings already include:
  - `SEARCH_AI_BACKEND_URL`
  - `SEARCH_AI_BACKEND_TIMEOUT_SECONDS`

So the AI backend should replace placeholder planning/execution behavior while preserving the existing Django execution state machine and response persistence model.

## 3.2 Segmentation app (`segmentation`) — YES (second phase, but important)

Current state:
- model layer already supports AI provenance via `SegmentationOutput`
- AI-origin metadata is first-class (`Origin.AI`, model name/version, params, produced_at, external_id)
- public API already exposes outputs for a segmentation version (`.../public/segmentation-versions/{public_id}/outputs/`)

What is missing:
- dedicated Django endpoint/service path that requests segmentation generation from AI backend and ingests returned segments/tags/output metadata automatically

Conclusion: segmentation needs AI backend collaboration, but generation integration is not yet wired.

## 3.3 Quran app (`quran`) — NO direct AI dependency

Current state:
- canonical scripture/translation data provider
- includes a basic text/translation search endpoint (DB filter based)
- no direct outbound call to AI backend

AI backend may consume Quran data indirectly (for retrieval/context), but Django `quran` app itself does not require AI backend integration now.

## 3.4 Accounts app (`accounts`) — NO

Identity/auth only. No AI integration seam.

## 3.5 Project app (`qgraph`) — infrastructure support only

Provides settings + async infra used by search orchestration. Not an AI consumer by itself.

---

## 4. AI Backend Endpoint Contracts (recommended)

Design principle: keep contracts close to Django's existing search and segmentation persistence models.

## 4.1 Search endpoints (required first)

### Endpoint A (recommended): planning handshake

`POST /v1/search/plan`

Request:
```json
{
  "query": "verses about patience",
  "filters": {"surah_ids": [2]},
  "output_preferences": {"include_summary": true, "include_statistics": true}
}
```

Response:
```json
{
  "mode": "sync",
  "policy_label": "router_v1",
  "policy_snapshot": {
    "ruleset": "router_v1",
    "thresholds": {"max_tokens_sync": 500}
  },
  "routing_metadata": {
    "reason": "short_query",
    "model_route": "search-fast"
  },
  "backend_name": "qgraph-ai-search",
  "backend_version": "2026-04-01"
}
```

How Django uses it:
- maps 1:1 to `PlanningDecision`
- writes fields into `SearchExecution` (`policy_*`, `routing_metadata`, `backend_*`)

### Endpoint B (required): execute search

`POST /v1/search/execute`

Request:
```json
{
  "query": "verses about patience",
  "filters": {"surah_ids": [2]},
  "output_preferences": {
    "include_summary": true,
    "include_statistics": true,
    "include_explanation": false
  },
  "context": {
    "query_id": 123,
    "execution_id": 456
  }
}
```

Response must map to Django `PlaceholderExecutionResult` structure:
```json
{
  "title": "Search results for: verses about patience",
  "overall_confidence": 0.84,
  "render_schema_version": "v1",
  "metadata": {
    "retrieval_ms": 120,
    "generation_ms": 420,
    "provider": "internal"
  },
  "blocks": [
    {
      "order": 1,
      "block_type": "summary",
      "title": "Summary",
      "payload": {"text": "..."},
      "explanation": "...",
      "confidence": 0.83,
      "provenance": {"component": "summarizer"},
      "warning_text": "",
      "items": []
    },
    {
      "order": 2,
      "block_type": "result_hits",
      "title": "Result Hits",
      "payload": {"total_hits": 3, "query_terms": ["patience"]},
      "explanation": "...",
      "confidence": 0.81,
      "provenance": {"component": "retrieval"},
      "warning_text": "",
      "items": [
        {
          "rank": 1,
          "result_type": "ayah",
          "score": 0.93,
          "title": "Al-Baqarah 2:153",
          "snippet_text": "...",
          "highlighted_text": "...",
          "match_metadata": {"matched_terms": ["patience"]},
          "explanation": "...",
          "provenance": {"index": "quran-ayah"}
        }
      ]
    }
  ]
}
```

Critical compatibility requirements:
- `blocks[].order` must be unique per response
- `items[].rank` must be unique per block
- keep JSON objects for `payload`, `metadata`, `provenance`, `match_metadata`

### Endpoint C (recommended): service health/version

`GET /health`

Use for Django startup/integration checks; include service version and model/router version.

### Optional async-in-AI-backend API

Only needed if you want AI backend to manage long-running jobs itself:
- `POST /v1/search/executions` -> returns `run_id`
- `GET /v1/search/executions/{run_id}` -> status
- `GET /v1/search/executions/{run_id}/result` -> final payload
- `POST /v1/search/executions/{run_id}/cancel`

Note: Django already has local async orchestration with Celery, so this is optional.

---

## 4.2 Segmentation endpoints (recommended second phase)

Segmentation model semantics that must be respected:
- a segmentation version contains contiguous ayah ranges (`start_ayah`, `end_ayah`)
- all segments must be in same surah as version
- expected snapshot quality: ordered, non-overlapping ranges
- tag assignments are workspace-scoped in Django

### Endpoint D: generate segmentation for a surah

`POST /v1/segmentation/generate`

Request:
```json
{
  "surah_id": 2,
  "ayahs": [
    {"id": 8, "number_in_surah": 1, "text_ar": "...", "translations": [{"lang": "en", "text": "..."}]}
  ],
  "options": {
    "granularity": "medium",
    "max_segments": 20,
    "include_tags": true,
    "include_summaries": true
  },
  "context": {
    "workspace_slug": "my-workspace",
    "requested_by_user_id": 42
  }
}
```

Response:
```json
{
  "external_id": "run_abc123",
  "model_name": "segmentation-pipeline",
  "model_version": "2026-04-01",
  "params": {"granularity": "medium", "max_segments": 20},
  "produced_at": "2026-04-02T18:30:00Z",
  "segments": [
    {
      "start_ayah": 8,
      "end_ayah": 12,
      "title": "...",
      "summary": "...",
      "tags": [
        {"name": "patience", "color": "#22c55e", "description": "..."}
      ]
    }
  ]
}
```

Django ingestion target:
- create `SegmentationVersion` with `origin=ai`
- create `Segment` rows (`origin=ai`)
- create/reuse `Tag` rows (`origin=ai` if newly created)
- create `SegmentTag` rows (`source=ai`)
- create `SegmentationOutput` with returned provenance fields

### Endpoint E (optional): tag suggestion for existing segments

`POST /v1/segmentation/suggest-tags`

Use when user already edited segment boundaries and only wants AI thematic labeling.

---

## 5. Data contract alignment notes for AI-backend implementation

## 5.1 Search contract alignment

Keep output fields aligned with Django persistence schema:
- response-level: `title`, `overall_confidence`, `render_schema_version`, `metadata`
- block-level: `block_type`, `order`, `title`, `payload`, `explanation`, `confidence`, `provenance`, `warning_text`
- item-level: `result_type`, `rank`, `score`, `title`, `snippet_text`, `highlighted_text`, `match_metadata`, `explanation`, `provenance`

Django stores everything structurally and exposes it via `/api/v1/search/executions/{id}/response/`.

## 5.2 Segmentation contract alignment

Produce segment lists that satisfy Django validation expectations:
- same surah for all start/end ayahs
- `start_ayah.number_in_surah <= end_ayah.number_in_surah`
- sorted by start ayah
- no overlaps

## 5.3 Provenance expectations

For reproducibility and admin/debug UX, include:
- stable run/external ID
- model name/version
- generation params used
- produced timestamp

---

## 6. Integration status summary (implemented vs planned)

Implemented now:
- search orchestration lifecycle, execution tracking, persistence, sync+async modes
- placeholder planner/executor that can be swapped
- segmentation data models include AI provenance entities

Planned / not yet wired:
- outbound call from Django search services to real AI backend
- Django service/action to request segmentation generation from AI backend and ingest result

---

## 7. Practical next steps for AI backend repo

1. Implement `POST /v1/search/execute` first (highest immediate value).
2. Add `POST /v1/search/plan` if routing policy should live in AI backend; otherwise keep planner in Django for now.
3. Keep response schema strictly compatible with Django `persist_execution_result` expectations.
4. Implement `POST /v1/segmentation/generate` as second phase to unlock AI-produced segmentation version ingestion.
5. Add health/version endpoint and include model/router version metadata in every response for traceability.

---

## 8. File/path references in this Django repo

Primary files for integration context:
- `docs/apps/search.md`
- `search/services/planning.py`
- `search/services/execution_backend.py`
- `search/services/orchestration.py`
- `search/services/persistence.py`
- `search/models.py`
- `segmentation/models.py`
- `segmentation/views.py`
- `docs/apps/segmentation.md`
- `qgraph/settings.py`

