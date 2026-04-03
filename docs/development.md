# Development and Run Guide

## Prerequisites

- Python `3.12+`
- `uv` installed

## Install Dependencies

```bash
uv sync --dev
```

## Run the API Locally

```bash
uv run uvicorn src.main:app --reload --port 8001
```

Service will be available at `http://127.0.0.1:8001`.

## Quick Smoke Checks

```bash
curl http://127.0.0.1:8001/health
```

```bash
curl -X POST http://127.0.0.1:8001/v1/search/plan \
  -H "Content-Type: application/json" \
  -d '{"query":"verses about patience","filters":{},"output_preferences":{}}'
```

```bash
curl -X POST http://127.0.0.1:8001/v1/search/execute \
  -H "Content-Type: application/json" \
  -d '{"query":"verses about patience","filters":{},"output_preferences":{},"context":{}}'
```

```bash
curl -X POST http://127.0.0.1:8001/v1/segmentation/generate \
  -H "Content-Type: application/json" \
  -d '{"surah_id":2,"ayahs":[],"options":{},"context":{}}'
```
