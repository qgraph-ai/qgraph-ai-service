# Django Integration Handoff Addendum (Search Jobs API)

Date: 2026-04-12  
Related base doc: `docs/bootstrap/django_integration_handoff.md`

## 1) Purpose

This addendum fills practical integration details for Django implementation:

- concrete JSON examples for async search job endpoints
- polling guidance
- idempotency behavior details
- current mock limitations to account for during development

---

## 2) Endpoint Examples

## 2.1 Create backend job

`POST /v1/search/jobs`

Request:

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
  "job_id": "job_0d6a4f59b00b4066a4b8a8f1",
  "status": "queued",
  "created_at": "2026-04-12T12:10:00.000000Z",
  "poll_after_seconds": 3
}
```

---

## 2.2 Poll backend job status

`GET /v1/search/jobs/{job_id}`

Non-terminal example (`200`):

```json
{
  "job_id": "job_0d6a4f59b00b4066a4b8a8f1",
  "status": "running",
  "created_at": "2026-04-12T12:10:00.000000Z",
  "started_at": "2026-04-12T12:10:06.000000Z",
  "completed_at": null,
  "poll_after_seconds": 3,
  "result_available": false,
  "error": null,
  "progress": {
    "stage": "retrieval",
    "percent": 65
  }
}
```

Terminal success example (`200`):

```json
{
  "job_id": "job_0d6a4f59b00b4066a4b8a8f1",
  "status": "succeeded",
  "created_at": "2026-04-12T12:10:00.000000Z",
  "started_at": "2026-04-12T12:10:06.000000Z",
  "completed_at": "2026-04-12T12:10:12.000000Z",
  "poll_after_seconds": 0,
  "result_available": true,
  "error": null,
  "progress": {
    "stage": "completed",
    "percent": 100
  }
}
```

Unknown job example (`404`):

```json
{
  "error": "http_error",
  "detail": {
    "message": "Search job not found",
    "job_id": "job_missing"
  }
}
```

---

## 2.3 Fetch backend job result

`GET /v1/search/jobs/{job_id}/result`

Result-not-ready example (`409`):

```json
{
  "error": "http_error",
  "detail": {
    "message": "Search job result not ready",
    "job_id": "job_0d6a4f59b00b4066a4b8a8f1",
    "status": "running"
  }
}
```

Ready example (`200`): response body is the same schema as `POST /v1/search/execute`.

Unknown job example (`404`):

```json
{
  "error": "http_error",
  "detail": {
    "message": "Search job not found",
    "job_id": "job_missing"
  }
}
```

---

## 3) Polling Guidance for Django

- Use `poll_after_seconds` from status response as first choice.
- If unavailable/invalid, fallback to 3 seconds.
- Continue polling while status in: `queued`, `running`.
- When status is `succeeded`, call `/v1/search/jobs/{job_id}/result` and persist as usual.
- If status is `failed` or `canceled`, mark execution terminal in Django and store backend details.
- Treat `409` from `/result` as non-terminal (not an error), and continue polling.

---

## 4) Idempotency Notes

- `idempotency_key` is required in job-create request.
- Repeated active submissions with the same key return the same active `job_id`.
- Current implementation reuses active jobs for statuses `queued`/`running`.
- Once terminal, same key may create a new job in a later call (current mock behavior).

---

## 5) Current Mock Limitations (Important)

- Job state is in-memory only (process-local), not Redis/DB.
- State is lost on service restart/deploy.
- Lifecycle progression is poll-count based in mock service:
  - queued -> running at 2nd state advance
  - running -> succeeded at 4th state advance
  - with 3-second polling this is roughly ~12 seconds to success
- `/result` currently also advances mock state once per call.

These limitations are expected for bootstrap; Django should still implement the real polling/orchestration contract.

