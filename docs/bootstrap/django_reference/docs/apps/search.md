# Search App

## Purpose

The `search` app is the orchestration and persistence layer for user search workflows.

It is responsible for:

- receiving search requests from the API
- persisting query/execution lifecycle records
- routing each execution through a planning handshake (`sync` vs `async`)
- persisting structured response payloads (response, blocks, ranked items)
- supporting saved searches, bookmarks, feedback, and interaction events

The app intentionally does not include a real AI/search backend yet. It uses replaceable placeholder planner/executor services behind clear interfaces.

## Core Data Relationships

The primary runtime chain is:

`SearchQuery -> SearchExecution -> SearchResponse -> SearchResponseBlock -> SearchResultItem`

Supporting user features:

- `SavedSearch`: reusable query templates owned by a user
- `SearchBookmark`: bookmark either a whole response or a specific result item
- `SearchFeedback`: user feedback attached to exactly one target level
- `SearchInteractionEvent`: analytics-style interaction logs

## API Surface

Base path: `/api/v1/search/`

### Core search

- `POST /api/v1/search/`
  - creates `SearchQuery` and `SearchExecution`
  - runs planning handshake
  - executes sync immediately or dispatches async task
- `GET /api/v1/search/queries/{id}/`
- `GET /api/v1/search/executions/{id}/`
- `GET /api/v1/search/executions/{id}/response/`
- `GET /api/v1/search/history/`

### Saved searches

- `GET /api/v1/search/saved-searches/`
- `POST /api/v1/search/saved-searches/`
- `GET /api/v1/search/saved-searches/{id}/`
- `PATCH /api/v1/search/saved-searches/{id}/`
- `DELETE /api/v1/search/saved-searches/{id}/`
- `POST /api/v1/search/saved-searches/{id}/run/`

### Bookmarks

- `GET /api/v1/search/bookmarks/`
- `POST /api/v1/search/bookmarks/`
- `DELETE /api/v1/search/bookmarks/{id}/`

### Feedback and interactions

- `POST /api/v1/search/feedback/`
- `POST /api/v1/search/interactions/`

## Guest Access

Guest access is stateless and token-based.

### Guest submission

Unauthenticated clients can call `POST /api/v1/search/`.

The backend stores guest submissions as:

- `SearchQuery.user = null`
- `SearchQuery.is_guest = true`
- `SearchQuery.guest_token = <secure random token>`

The submission response includes `guest_token` only for guest submissions.

### Guest read access

Guests can read only these endpoints:

- `GET /api/v1/search/executions/{id}/`
- `GET /api/v1/search/executions/{id}/response/`

Access rule:

- authenticated owner can read their own execution
- guest execution can be read only when the caller provides the matching guest token

Guest token input:

- preferred: `X-Search-Guest-Token` header
- fallback: `?guest_token=...` query param

Unauthorized access is returned as `404` to avoid leaking execution existence.

### Guest limitations

Guest users do not have access to:

- history
- saved searches
- bookmarks
- feedback
- interaction logging

These endpoints remain authenticated-only.

## Planning Handshake and Orchestration

All submissions go through an explicit planning step in `search/services/planning.py`.

Planner output includes:

- execution `mode` (`sync` or `async`)
- `policy_label`
- `policy_snapshot`
- `routing_metadata`
- placeholder backend identity (`backend_name`, `backend_version`)

The current planner is heuristic and intentionally lightweight:

- simple queries are routed to `sync`
- longer/analysis-heavy requests are routed to `async`

This is an integration seam for future backend routing logic.

## Sync vs Async Execution

### Sync path

1. API creates query + execution.
2. Planner returns `mode=sync`.
3. Execution runs immediately through placeholder executor.
4. Response/blocks/items are persisted.
5. API returns `201` with completed response envelope.

### Async path

1. API creates query + execution.
2. Planner returns `mode=async`.
3. Execution is marked `queued` and Celery task is dispatched.
4. API returns `202` with polling URLs and no response payload yet.
5. Task runs placeholder execution and persists final response.

Celery task entrypoint: `search.tasks.run_search_execution_task`.

## Polling Behavior

For async submissions, the response envelope includes:

- `query_id`
- `execution_id`
- `execution_status`
- `mode`
- `poll_url`
- `response_url`
- `guest_token` (guest submissions only)

Frontend flow:

1. poll `GET /api/v1/search/executions/{id}/` until terminal status
2. fetch structured payload from `GET /api/v1/search/executions/{id}/response/`

If response is requested before it exists, the API returns `409` with current execution status.

## Placeholder Backend Integration Points

Replaceable service boundaries:

- planner: `search/services/planning.py`
- executor: `search/services/execution_backend.py`
- persistence mapping: `search/services/persistence.py`
- orchestration flow: `search/services/orchestration.py`

The current executor returns deterministic placeholder blocks/items to exercise full API, persistence, and frontend integration paths without external dependencies.

## Permissions and Data Isolation

Current access policy:

- public:
  - `POST /api/v1/search/`
  - `GET /api/v1/search/executions/{id}/`
  - `GET /api/v1/search/executions/{id}/response/`
- authenticated-only:
  - history
  - saved searches
  - bookmarks
  - feedback
  - interaction events

Data isolation is enforced via owner checks (authenticated users) and guest-token checks (guest queries).

## Logging

Search lifecycle logs are emitted under the `search` logger and include key boundaries:

- request received
- query/execution created
- planning decision selected
- async dispatch
- execution started/completed/failed

This follows project-wide request-ID-aware logging configuration in `qgraph/settings.py`.

## Demo Seed Command

Use the built-in management command to populate realistic synthetic search data for API debugging and query-count/N+1 inspection.

```bash
python manage.py seed_search_demo --reset
```

Useful options:

- `--users` (default: `3`)
- `--queries-per-user` (default: `12`)
- `--guest-queries` (default: `10`)
- `--executions-per-query` (default: `2`)
- `--saved-searches-per-user` (default: `3`)
- `--bookmarks-per-user` (default: `4`)
- `--feedback-per-user` (default: `4`)
- `--interactions-per-user` (default: `8`)
- `--password` (default: `DemoPass123!`) for demo authenticated users

Maintenance helpers:

```bash
python manage.py seed_search_demo --clean-only
python manage.py seed_search_demo --reset
```

Notes:

- Demo query rows are identified by raw query prefix `"[DEMO_SEARCH]"`.
- Demo users are created as `search-demo-user-01@example.com`, `search-demo-user-02@example.com`, etc.
- The command creates a mix of succeeded and queued executions, plus related responses/blocks/items, bookmarks, feedback, and interaction events.
- Command output includes a sample guest token + execution id to quickly test guest polling endpoints.
