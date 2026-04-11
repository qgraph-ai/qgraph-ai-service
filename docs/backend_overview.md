# AI Backend Overview

## Purpose

`qgraph-ai-service` is the bootstrap AI backend for QGraph.
Its current job is to provide schema-correct, dummy responses to Django while keeping endpoint contracts stable.

## Current Scope

- FastAPI request-response service
- Search planning endpoint: `POST /v1/search/plan`
- Search execution endpoint: `POST /v1/search/execute`
- Search async job create endpoint: `POST /v1/search/jobs`
- Search async job status endpoint: `GET /v1/search/jobs/{job_id}`
- Search async job result endpoint: `GET /v1/search/jobs/{job_id}/result`
- Segmentation generation endpoint: `POST /v1/segmentation/generate`
- Health endpoint: `GET /health`

## Project Structure (Bootstrap)

```text
src/
  api/          # HTTP routes and request/response schemas
  services/     # request-level orchestration with dummy logic
  stores/       # placeholder data-access modules (vector/graph)
  workflows/    # placeholder workflow modules
```

## Non-Goals In This Phase

- real AI retrieval or generation
- async job orchestration inside this service
- model quality optimization
- complex architecture or abstractions
