# AI Backend Review (Bootstrap Phase) — Claude v1

## 1. Overall opinion

The current direction is solid. The scope documents are unusually well-disciplined for a bootstrap phase — they correctly prioritize contract correctness over AI logic, keep Django as the source of truth, and avoid premature abstractions. The v1→feedback→v2 iteration on folder structure shows good architectural taste: treating AI modules as first-class citizens rather than API sub-components is the right call and will pay off when real pipelines land. The project is ready to move from planning to implementation.

## 2. What looks good

- **Contract-first approach.** Defining Pydantic schemas before implementation ensures Django compatibility from day one. The response shapes (blocks/items with unique `order`/`rank`) are well-specified.
- **Thin API layer.** The v2 structure correctly keeps `api/` as a thin router layer, with `services/` handling orchestration. This separation is clean and appropriate for the current scope.
- **First-class AI module layout.** Moving from `ai_placeholders/` to top-level `stores/`, `workflows/` was the right decision. Placeholders live where real code will live — no future rename churn.
- **Scope discipline.** The scope doc explicitly lists what NOT to do. This is rare and valuable — it prevents AI agents and contributors from gold-plating.
- **Test plan is contract-focused.** Testing schema shape and uniqueness constraints (not AI quality) is exactly right for this phase.
- **Django context doc is thorough.** Having the full contract, identifier strategy, and persistence expectations in one portable file gives any implementer (human or AI) everything needed to build compatible endpoints.

## 3. Small gaps or risks

- **No dependencies declared.** `pyproject.toml` has `dependencies = []`. FastAPI, Pydantic, uvicorn, and pytest are not listed yet. This will be the first blocker when implementation starts.
- **No `conftest.py` or test scaffolding.** The test plan references `tests/conftest.py` with a shared `TestClient`, but no `tests/` directory exists yet. Easy to forget during first implementation rush.
- **Missing error response contract.** The Django context doc defines happy-path responses but says nothing about error shapes. When the AI backend returns a 4xx/5xx, what does Django expect? Even a simple `{"error": "message"}` envelope should be agreed on early — otherwise Django error handling will be ad-hoc.
- **No `src/` package structure yet.** Only an empty `src/__init__.py` exists. The gap between the detailed plan and the empty repo means the first implementation PR will be large. Consider splitting it (scaffolding PR → endpoint PR).
- **Config story is underspecified.** `config.py` is mentioned for "minimal constants" but there's no mention of how environment-specific values (host, port, log level) will be loaded. Even for bootstrap, a simple `pydantic-settings` or env-var pattern avoids hardcoding.

## 4. Small suggestions (incremental only)

- **Add core dependencies now.** A quick `uv add fastapi uvicorn pydantic pytest httpx` (httpx for `TestClient`) unblocks implementation immediately.
- **Create the empty folder skeleton.** Even empty `__init__.py` files in `src/api/`, `src/services/`, `src/stores/`, `src/workflows/`, and `tests/` would make the v2 structure tangible and reduce the first PR's diff noise.
- **Define a minimal error response schema.** One Pydantic model (`ErrorResponse` with `error: str` and optional `detail: dict`) shared across all endpoints. Tiny effort, avoids inconsistency.
- **Add a `Makefile` or `scripts/` entry point.** Something like `make run`, `make test`, `make lint`. Reduces onboarding friction and makes CI setup trivial later.
- **Pin a minimum response for `/health`.** The plan says "static service/version info" — consider also returning `{"status": "ok", "service": "qgraph-ai", "version": "0.1.0"}` as the explicit shape so Django can health-check without guessing.

## 5. Things to explicitly NOT change now

- **Do not add async job orchestration in the AI backend.** Django already owns execution lifecycle via Celery. Duplicating that here creates two sources of truth. Keep the AI backend as a synchronous request-response service for now.
- **Do not introduce a base class / interface hierarchy for stores or workflows.** A `VectorStore` ABC with a single dummy implementation is premature abstraction. A plain module with functions is enough until there are two real implementations to generalize from.
- **Do not add authentication or middleware.** The AI backend is an internal service called by Django. Auth, rate limiting, and CORS belong at the network/infra level, not in the bootstrap app code.
- **Do not split into multiple packages or microservices.** One `src/` package, one FastAPI app, one deployment unit. The current flat structure is correct for the current scale.
