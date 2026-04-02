# Architecture

## Stack

The backend is built with:

- Django (project/app structure, ORM, admin)
- Django REST Framework (API layer)
- Djoser + SimpleJWT (authentication endpoints + JWT auth)
- drf-spectacular (OpenAPI schema and docs UI)
- PostgreSQL (primary datastore)
- Celery (asynchronous/background execution runtime)
- Redis (Celery broker + result backend)

## Application Boundaries

The project is organized into app-level domains:

- `accounts`: identity/authentication domain (custom user model, email login)
- `quran`: canonical Quran domain (Surah, Ayah, structures, translations)
- `segmentation`: research/product artifact domain (workspaces, segmentation versions, segments, tags, AI output provenance)

This separation keeps each domain independently evolvable while still enabling cross-app relations (for example, segmentation references Quran ayahs/surahs).

## High-Level Data Flow

Typical request flow:

1. Request enters versioned URL namespace (`/api/v1/...`) or auth namespace (`/api/auth/...`).
2. DRF router dispatches to viewsets/APIViews.
3. Serializers validate and normalize payloads.
4. ORM persists or reads domain models.
5. Response is returned as JSON (usually paginated for list endpoints).

For segmentation snapshot saves, the flow is intentionally version-creating rather than in-place mutation: validate snapshot -> create new version -> bulk insert segments and tag assignments.

## Canonical State vs Async Processing

- Django + PostgreSQL remain the canonical application state layer.
- Celery + Redis handle asynchronous/background execution only.
- Interactive workflows can still use regular HTTP request/response (including streaming when needed).
- Redis should be treated as queue/result infrastructure, not long-term artifact storage.

## Public vs Authenticated Surfaces

The API surface is split into two operational layers:

- Public/read-focused:
  - Quran endpoints are read-only.
  - Segmentation has explicit public endpoints under `segmentation/public/...` for browsing public workspaces and versions.
- Authenticated/owner-scoped:
  - Workspace, segmentation version, and tag management endpoints require authentication.
  - Access is scoped to resources owned by the authenticated user.

This keeps exploration open where needed while preserving strong write isolation.

## Identifier Strategy

The system uses different identifier styles based on domain semantics:

- Segmentation:
  - workspace lookup by `slug`
  - segmentation versions and tags looked up by UUID `public_id`
  - integer DB primary keys remain internal storage keys
- Quran:
  - lookups use domain-native numeric IDs (for example `surah.number`, `ayah.number_global`)
- Auth:
  - user references are internal IDs in payloads managed by auth endpoints

The segmentation `public_id` approach reduces predictable enumeration and decouples public API URLs from internal integer PKs.

## Modular Design Philosophy

Design choices in this backend prioritize:

- domain isolation at app boundaries
- explicit ownership and permission boundaries
- versioned analytical artifacts instead of mutable opaque state
- data integrity via database constraints plus serializer validation
- predictable API contracts for frontend workflows

This architecture supports incremental extension (new artifact types, richer collaboration flows, additional AI metadata) without requiring monolithic rewrites.
