# API Conventions

## Base Paths and Versioning

- Product APIs use `/api/v1/...`
  - `/api/v1/quran/...`
  - `/api/v1/segmentation/...`
- Auth APIs use `/api/auth/...` (Djoser + JWT)
- OpenAPI endpoints:
  - `/api/schema/`
  - `/api/docs/`
  - `/api/redoc/`

## REST Resource Design

Conventions used in this codebase:

- plural resource names (`surahs`, `ayahs`, `workspaces`, `segmentation-versions`)
- read and write separated where needed (for example, public segmentation routes vs owner routes)
- custom lifecycle operations exposed as explicit action endpoints instead of implicit field changes

Examples:

- `POST /api/v1/segmentation/segmentation-versions/{public_id}/activate/`
- `POST /api/v1/segmentation/segmentation-versions/{public_id}/save-snapshot/`
- `GET /api/v1/segmentation/segmentation-versions/{public_id}/segments/`

## Endpoint Naming Patterns

Current naming style:

- kebab-case for multiword URL segments (`segmentation-versions`, `hizb-quarters`, `save-snapshot`)
- nested read actions where needed (`/surahs/{number}/ayahs/`, `/workspaces/{slug}/tags/`)
- explicit `public/` prefix for anonymous segmentation browsing endpoints

## Request and Response Shape

General conventions:

- JSON request/response bodies
- serializer-driven validation with field-level errors
- list endpoints are generally paginated

Paginated response shape follows DRF defaults:

- `count`
- `next`
- `previous`
- `results`

## Error Handling Strategy

The API uses standard DRF error patterns:

- `400 Bad Request` for validation issues (field keyed errors or `detail`)
- `401 Unauthorized` when auth is required and missing/invalid
- `404 Not Found` when resource is absent or outside accessible scope

Custom validation logic (for example segmentation snapshot checks) returns structured serializer errors under relevant fields.

## Filtering, Searching, and Ordering

Global DRF defaults enable:

- `DjangoFilterBackend`
- `SearchFilter`
- `OrderingFilter`

App-specific conventions:

- Quran endpoints expose `filterset_fields`, `search_fields`, and `ordering_fields` per viewset.
- Segmentation endpoints use focused query params where appropriate:
  - workspace public versions: `surah`, `status`
  - workspace tags: `q` (name contains)

## Pagination

- Global default: `PageNumberPagination`, page size `25`.
- Quran endpoints use a custom pagination class that also supports `page_size` (max `200`).
- Segmentation list actions rely on default pagination behavior.

## ID Exposure Policy

The project uses a mixed identifier policy:

- Segmentation write/lookups:
  - workspace by `slug`
  - version/tag lookups by UUID `public_id`
- Quran lookups:
  - surah by `number`
  - ayah by `number_global` or `(surah_number, number_in_surah)`
- Internal integer IDs may still appear in payloads for relational convenience.

When integrating from frontend, use URL lookup IDs (`slug`/`public_id`/domain numbers) as canonical route identifiers.
