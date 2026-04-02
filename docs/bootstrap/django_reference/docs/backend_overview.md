# Backend Overview

## Project Structure

The backend follows a standard Django project layout:

- `qgraph/`: project settings and root URL config
- `accounts/`: custom user model + auth serializers
- `quran/`: canonical Quran data models and read APIs
- `segmentation/`: workspace and segmentation artifact APIs
- `search/`: search orchestration, execution tracking, and user search artifacts

Each app keeps its own:

- `models.py`
- `serializers.py`
- `views.py`
- `urls.py`
- `tests/`

The project package `qgraph/` also contains process-level wiring such as Celery bootstrap (`qgraph/celery.py`), project-level validation tasks (`qgraph/tasks.py`), and settings integration.

## Core Pattern: Model -> Serializer -> ViewSet/APIView

Across apps, request handling follows DRF layering:

1. `models.py` defines data structures and DB constraints.
2. `serializers.py` validates request payloads and shapes response payloads.
3. `views.py` provides query logic, actions, and orchestration.
4. `urls.py` mounts routers and custom routes.

Segmentation actions like `activate` and `save-snapshot` are implemented as explicit DRF `@action` endpoints to keep lifecycle behavior explicit.

## API Versioning Strategy

Versioning is path-based:

- main product APIs: `/api/v1/...`
- auth APIs: `/api/auth/...` (Djoser endpoints)

There is currently no DRF header/query version negotiation configured; versioning is handled by URL namespace.

## Public Identifiers and Internal IDs

The backend uses both internal and external identifiers:

- internal DB PKs (integers) are relational implementation details
- segmentation-facing external identifiers are UUID `public_id` (versions/tags/segments)
- workspace external identifier is slug
- Quran endpoints primarily use domain-native numeric identifiers (`surah.number`, `ayah.number_global`)

In segmentation responses, both `id` and `public_id` may be present, but route lookups for key resources use `public_id`/slug.

## Integrity via Database Constraints

Important invariants are enforced at the model/database layer, including:

- one active segmentation version per `(workspace, surah)` (conditional unique constraint)
- unique tag names per workspace
- unique segment-tag assignment per `(segment, tag)`
- unique Quran ayah numbering per `(surah, number_in_surah)`
- unique translation row per `(ayah, source)`

Serializer-level validation adds request-time guarantees (for example, snapshot segments must be ordered, non-overlapping, and in the same surah/workspace context).

## Performance Patterns in Use

The codebase already applies common ORM performance techniques:

- `select_related(...)` for foreign key traversal
- `prefetch_related(...)` for reverse/many relations
- filtered `Prefetch(...)` for targeted translation/tag loading
- `bulk_create(...)` for snapshot segment/tag insertion
- deterministic ordering for stable segment and ayah responses

These patterns are especially important for segmentation snapshots and for Quran list/search endpoints that can return larger payloads.
