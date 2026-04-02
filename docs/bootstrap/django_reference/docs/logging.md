# Logging Guide

## Overview

QGraph uses Python's standard `logging` module through Django's `LOGGING` dictConfig in [`qgraph/settings.py`](../qgraph/settings.py).

- logs are emitted to `stdout` and `stderr` only
- no local file handlers are used
- every log line includes timestamp, level, logger name, and `request_id`

This works well for Docker/Kubernetes/Render-style deployments where log collection happens at the platform layer.

## Log Levels

- root logger:
  - `DEBUG` when `DEBUG=True`
  - `INFO` when `DEBUG=False`
  - override with `DJANGO_LOG_LEVEL` environment variable (for example: `INFO`, `WARNING`, `ERROR`)
- `django`: `INFO`
- `django.request`: `WARNING` (so server-side failures stand out)
- app loggers (`accounts`, `quran`, `segmentation`, `qgraph`):
  - `DEBUG` in development
  - `INFO` in production

## Request ID Tracing

`qgraph.middleware.RequestIDMiddleware` handles request correlation:

- if `X-Request-ID` is provided by the caller, it is reused
- otherwise, a UUID4 is generated
- the value is returned in the response header as `X-Request-ID`
- logs emitted during that request automatically include the same `request_id`

Use `X-Request-ID` to trace a request across API gateway, app logs, and worker logs.

## Where To Add Logs

Add logs in domain/service flows and job boundaries:

- start/finish of major operations (`activate`, `save_snapshot`, seeds, batch jobs)
- recoverable anomalies as `WARNING`
- failures as `logger.exception(...)` so traceback is preserved

Prefer adding logs in services/domain modules over views unless the view owns the business action.

## What Not To Log

Never log:

- passwords, tokens, API keys, secrets
- raw document text or large payload bodies
- sensitive user data when a stable public identifier is enough

Prefer public IDs, workspace slugs, counts, and status values.

## Practical Usage

- Use module-scoped loggers:
  - `logger = logging.getLogger(__name__)`
- Keep logs high-signal:
  - avoid per-item logs in tight loops
  - summarize with counts and IDs instead

## Future Improvements

The following are intentionally tracked as future work (not blockers right now):

1. Request completion policy:
   - decide whether selected `GET` routes should also be logged in production
   - optionally include an allowlist/denylist approach for noisy paths
2. Stream routing policy:
   - evaluate routing `WARNING` to `stderr` (keeping `stdout` for `DEBUG/INFO`)
3. Logger config hardening:
   - keep documenting the propagation model and revisit if per-logger handlers are introduced
4. Structured logs:
   - add optional JSON formatter for production when/if operational tooling requires it
5. Middleware placement review:
   - re-check ordering when middleware stack changes significantly
6. Test robustness:
   - expand logging tests to cover more handler/filter combinations if logging architecture evolves
