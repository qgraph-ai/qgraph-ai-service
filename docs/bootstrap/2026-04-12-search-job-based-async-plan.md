# Search App Migration Plan: Backend Job-Based Async Execution

Date: 2026-04-12
Owner: Django `search` app + AI backend service
Status: Planned (implementation not started)

## 1) Decision Summary

We will move async search from **worker-blocking HTTP execute calls** to a **job-based backend model**.

- Keep planning handshake (`/v1/search/plan`) in place.
- Keep sync execution path for fast queries.
- Replace async execute path with:
  - create backend job,
  - persist backend job id in Django,
  - poll backend job status via Celery,
  - fetch final result payload when job completes,
  - persist response in Django as today.

Important project constraint captured here: **backward compatibility is not required**. We can make clean contract changes where they improve architecture clarity.

---

## 2) Why This Change

Current async behavior is client-async but worker-sync:

- Django returns `202` quickly, but a Celery worker still blocks on long `/v1/search/execute` requests.
- For LLM-heavy workloads (30s to 2min+), this is inefficient and reduces throughput.

Target behavior:

- AI backend owns long-running execution lifecycle.
- Django owns auth/access, execution records, and persisted response structure.
- Celery does lightweight orchestration/polling work, not long blocking compute calls.

---

## 3) Target Architecture

### 3.1 Sync path (unchanged conceptually)

1. `POST /api/v1/search/` -> Django creates `SearchQuery` + `SearchExecution`.
2. Django calls `/v1/search/plan`.
3. If mode=`sync`, Django calls `/v1/search/execute`.
4. Django persists `SearchResponse` + blocks + items and returns `201`.

### 3.2 Async path (new job-based flow)

1. `POST /api/v1/search/` -> Django creates `SearchQuery` + `SearchExecution`.
2. Django calls `/v1/search/plan`.
3. If mode=`async`, Django calls backend job-create endpoint.
4. Django stores `backend_job_id` on `SearchExecution`, sets status `queued`, dispatches polling task, returns `202`.
5. Poll task checks backend job status (`queued/running/...`) and updates Django execution status.
6. On backend job success, poll task fetches result payload and persists response.
7. Frontend continues using existing execution poll/read endpoints.

---

## 4) Required AI Backend API Contract

The backend must expose these endpoints for Django integration.

### 4.1 `GET /health` (existing)

No change required.

### 4.2 `POST /v1/search/plan` (existing)

No breaking change required. Keep payload/shape currently used by Django.

Request:

```json
{
  "query": "patience",
  "filters": {"surah": 2},
  "output_preferences": {"format": "summary"}
}
```

Response:

```json
{
  "mode": "sync",
  "policy_label": "default_fast",
  "policy_snapshot": {},
  "routing_metadata": {"mode": "sync"},
  "backend_name": "qgraph-ai",
  "backend_version": "v1"
}
```

### 4.3 `POST /v1/search/execute` (existing, sync only)

Used for sync mode only. Keep output shape compatible with Django persistence mapper.

### 4.4 `POST /v1/search/jobs` (new, required)

Create async backend job.

Request (proposed):

```json
{
  "query": "patience",
  "filters": {"surah": 2},
  "output_preferences": {"format": "summary"},
  "context": {},
  "idempotency_key": "search-exec-4054",
  "client_ref": {
    "query_id": 1354,
    "execution_id": 4054
  }
}
```

Response `202`:

```json
{
  "job_id": "job_01JV...",
  "status": "queued",
  "created_at": "2026-04-12T10:30:00Z",
  "poll_after_seconds": 3
}
```

Notes:

- `idempotency_key` should return same active job for duplicate calls.
- Endpoint should be fast and non-blocking.

### 4.5 `GET /v1/search/jobs/{job_id}` (new, required)

Return job status + progress metadata.

Response `200`:

```json
{
  "job_id": "job_01JV...",
  "status": "queued",
  "created_at": "2026-04-12T10:30:00Z",
  "started_at": null,
  "completed_at": null,
  "poll_after_seconds": 3,
  "result_available": false,
  "error": null,
  "progress": {
    "stage": "retrieval",
    "percent": 20
  }
}
```

Terminal status example:

```json
{
  "job_id": "job_01JV...",
  "status": "succeeded",
  "created_at": "2026-04-12T10:30:00Z",
  "started_at": "2026-04-12T10:30:01Z",
  "completed_at": "2026-04-12T10:31:10Z",
  "poll_after_seconds": 0,
  "result_available": true,
  "error": null,
  "progress": {
    "stage": "completed",
    "percent": 100
  }
}
```

### 4.6 `GET /v1/search/jobs/{job_id}/result` (new, required)

Return final execution payload using same schema as `/v1/search/execute` response.

- `200` if ready.
- `409` if not ready.
- `404` if unknown job.

### 4.7 `POST /v1/search/jobs/{job_id}/cancel` (optional but recommended)

Used for future cancellation support; not required in first Django implementation.

---

## 5) Django Changes Plan

### 5.1 Model updates (`search/models.py`)

Add explicit backend job tracking to `SearchExecution`:

- `backend_job_id: CharField(max_length=128, blank=True, db_index=True)`
- `backend_job_status: CharField(max_length=32, blank=True)`
- `backend_job_meta: JSONField(default=dict, blank=True)`  
  (stores progress/error snippets, poll hints, timestamps from backend)

Rationale:

- avoids overloading `debug_metadata` for critical lifecycle fields.
- improves admin/API inspectability.

Migration: create schema migration + data migration (if needed) with default blank values.

### 5.2 Client adapter (`search/services/ai_backend_client.py`)

Add methods:

- `create_search_job(...)`
- `get_search_job(job_id=...)`
- `get_search_job_result(job_id=...)`

Add payload validators + typed exception mapping for new endpoints.

### 5.3 Execution backend adapter (`search/services/execution_backend.py`)

Keep `execute(...)` for sync path.
Add:

- `create_async_job(...) -> BackendJobCreateResult`
- `get_async_job_status(...) -> BackendJobStatusResult`
- `get_async_job_result(...) -> ExecutionResult`

Keep execution-result mapping centralized here.

### 5.4 Orchestration (`search/services/orchestration.py`)

In async branch of `submit_search(...)`:

1. call backend `create_async_job(...)` immediately,
2. persist `backend_job_id`, `backend_job_status='queued'`,
3. set `execution.status='queued'`,
4. dispatch Celery poll task,
5. return async submission envelope.

Failure behavior:

- backend job-create failure -> mark execution/query failed and return service-unavailable error.

### 5.5 Celery tasks (`search/tasks.py`)

Replace current async execute task behavior with polling orchestration:

- `poll_search_execution_job_task(execution_id: int)`

Task behavior:

1. load execution by id (safe locking where needed),
2. fetch backend job status,
3. map backend status to Django execution status,
4. if `queued/running`: re-enqueue self with `poll_after_seconds` (or default backoff),
5. if `succeeded`: fetch result, call `persist_execution_result(...)`, mark success,
6. if `failed/canceled`: mark failure/canceled with backend error details.

Important: use re-dispatch strategy for polling, not retry-as-error for normal non-terminal states.

### 5.6 Access/API layer

Public Django endpoints can remain unchanged:

- `POST /api/v1/search/`
- `GET /api/v1/search/executions/{id}/`
- `GET /api/v1/search/executions/{id}/response/`

Optional additive response fields:

- include `backend_job_status` in execution detail serializer for debug transparency.

### 5.7 Settings

Keep existing:

- `SEARCH_AI_BACKEND_URL`
- `SEARCH_AI_BACKEND_TIMEOUT_SECONDS`

Add (if needed):

- `SEARCH_AI_BACKEND_JOB_POLL_DEFAULT_SECONDS` (e.g., `3`)
- `SEARCH_AI_BACKEND_JOB_POLL_MAX_ATTEMPTS` (safety bound)

---

## 6) Status Mapping Rules

Backend status -> Django `SearchExecution.status` mapping:

- `queued` -> `queued`
- `running` -> `running`
- `succeeded` -> `succeeded`
- `failed` -> `failed`
- `canceled` -> `canceled`

`SearchQuery.status` should follow latest execution lifecycle as currently done.

---

## 7) Error Handling Policy

- Planning failure: fail early (`SearchExecutionError`), persist failure on query/execution.
- Async job creation failure: fail early and mark execution failed.
- Polling transient failures (timeout/connection): retry task with backoff/jitter.
- Terminal backend failure: persist error code/message to execution.
- Malformed backend payloads: treat as failure with clear `payload_error` code.

No silent swallowing of backend failures.

---

## 8) Testing Plan

### 8.1 Unit/service tests

- job create success/failure mapping in client/executor adapters.
- job status parsing and terminal/non-terminal behavior.
- job result parsing into `ExecutionResult`.

### 8.2 Orchestration tests

- async submit stores `backend_job_id` and dispatches poll task.
- async submit handles backend job-create failure correctly.

### 8.3 Task tests

- poll queued -> re-enqueue.
- poll running -> re-enqueue + status update.
- poll succeeded -> fetch result + persist response.
- poll failed -> execution/query marked failed.

### 8.4 API tests

- async submit still returns `202` envelope.
- execution detail reflects status transitions.
- response endpoint remains `409` until persisted then `200`.

Use mocks for backend client; no live backend required in tests.

---

## 9) Documentation Updates (after implementation)

Update `docs/apps/search.md` to document:

- sync vs async job-based execution,
- backend job lifecycle,
- polling model and status transitions,
- integration boundary between Django and AI backend.

---

## 10) Rollout Sequence

1. **AI backend first**: implement and stabilize job endpoints + contracts in this plan.
2. Django integration changes (model/service/task/view/tests).
3. Run migrations + test suite.
4. Validate end-to-end with real async jobs.
5. Update docs.

---

## 11) Implementation Guardrails

- No broad redesign beyond async execution architecture.
- Keep Django ownership of auth/access, lifecycle records, and persistence.
- Keep AI backend ownership of heavy execution runtime.
- Backward compatibility is intentionally not a requirement for this migration.
