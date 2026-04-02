# Async Jobs (Celery + Redis)

## What Was Added

QGraph now includes foundational asynchronous infrastructure:

- Celery is configured at project level (`qgraph/celery.py`).
- Redis is configured as both Celery broker and result backend.
- Flower is included as a monitoring tool for local/dev workflows.
- A minimal project-level task (`qgraph.tasks.ping`) is available to validate wiring.

This is intentionally infrastructure-first. No product/domain workflow has been moved to Celery yet.

## Why This Exists Now

This step prepares the backend for future background workloads, especially:

- asynchronous processing that should not block HTTP request/response cycles
- longer-running AI-related processing
- scheduled or queued backend work

Current scope is intentionally small so we can validate runtime/ops patterns before adding feature-level jobs.

There is intentionally no dedicated shared Django app for async workflows yet.

## Configuration

Celery settings live in [`qgraph/settings.py`](../qgraph/settings.py) and are namespaced with `CELERY_`.

Environment variables used:

- `CELERY_BROKER_URL` (default: `redis://127.0.0.1:6379/0`)
- `CELERY_RESULT_BACKEND` (default: `redis://127.0.0.1:6379/1`)
- optional for tests/local overrides:
  - `CELERY_TASK_ALWAYS_EAGER`
  - `CELERY_TASK_EAGER_PROPAGATES`

Key baseline defaults:

- JSON serializers and accepted content
- timezone aligned with Django `TIME_ZONE`/`USE_TZ`
- broker retry on startup enabled
- worker root logger hijack disabled (keeps Django logging policy predictable)

## Local Development

Start infrastructure:

```bash
docker compose up -d db redis
```

Run Django API:

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Run Celery worker:

```bash
uv run celery -A qgraph worker --loglevel=INFO
```

Run Flower:

```bash
uv run celery -A qgraph flower --port=5555
```

Flower UI: `http://127.0.0.1:5555/`

## Validate The Setup

Use the demo task from a Django shell:

```bash
uv run python manage.py shell -c "from qgraph.tasks import ping; r = ping.delay('local-check'); print(r.get(timeout=10))"
```

Expected output:

```text
{'status': 'ok', 'message': 'local-check'}
```

## Design Notes

- Django/PostgreSQL remains the canonical source of truth for business/application state.
- Celery is for asynchronous/background work; future interactive streaming AI UX can still use direct HTTP streaming where appropriate.
- Redis is queue/result/coordination infrastructure, not artifact/blob storage.
- Large reports/files/final artifacts should not be persisted in Redis.
- New domain-specific async jobs should normally live in their domain app (for example, `segmentation/tasks.py`).
- A cross-domain shared app should only be introduced if there is a concrete need (for example, unified job tracking/artifact management).
- Direction for shared artifact storage:
  - development: likely shared local filesystem directory mounted into API + worker containers
  - production: likely S3-compatible object storage

Those storage choices are architectural direction only and are not implemented in this step.
