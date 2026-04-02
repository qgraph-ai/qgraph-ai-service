# Frontend Workflows

This page explains multi-call workflows rather than single endpoints.

## 1. Create and Manage Workspaces

Typical flow:

1. Authenticate (`/api/auth/...`) and obtain JWT.
2. Create workspace via `POST /api/v1/segmentation/workspaces/` with title/description.
3. Use returned `slug` as workspace route identifier.
4. List/update/delete through `/api/v1/segmentation/workspaces/{slug}/`.

Notes:

- created workspaces default to `private`
- owner-only access applies to workspace management endpoints

## 2. Create Segmentation Versions

From workspace context:

1. `POST /api/v1/segmentation/workspaces/{slug}/segmentation-versions/`
2. Choose one of:
   - new version from a `surah`
   - fork from `base_version_public_id` (public source version)

Result:

- a new `SegmentationVersion` in `draft` state
- if forked, segments/tag assignments are copied into the target workspace context

## 3. Save Segmentation Snapshots

Snapshot-based editing flow:

1. Frontend loads a base version (`GET .../segmentation-versions/{public_id}/segments/`).
2. User edits locally in client state.
3. Frontend sends full segment list to:
   - `POST /api/v1/segmentation/segmentation-versions/{public_id}/save-snapshot/`
4. Backend validates and creates a new draft version with copied metadata and new segment rows.

Important behavior:

- this creates a new version; it does not mutate existing segment rows in place
- snapshot validation enforces same-surah consistency, ordering, and non-overlap

## 4. Activate a Segmentation Version

Canonicalization flow:

1. Choose a draft/archived version to promote.
2. Call `POST /api/v1/segmentation/segmentation-versions/{public_id}/activate/`.
3. Backend marks target version as `active` and demotes any other active version for the same `(workspace, surah)` to `draft`.

Outcome:

- exactly one active version per workspace+surah remains.

## 5. Browse Public Segmentation Work

Anonymous or authenticated users can inspect published work:

1. Discover public workspaces:
   - `GET /api/v1/segmentation/public/workspaces/`
   - `GET /api/v1/segmentation/public/workspaces/featured/`
2. List workspace versions:
   - `GET /api/v1/segmentation/public/workspaces/{slug}/segmentation-versions/`
3. Inspect a version:
   - version detail by `public_id`
   - segments, tags, and outputs via dedicated sub-endpoints

Notes:

- public workspace version listing defaults to active versions unless `status` is provided
- public endpoints are read-only

## 6. Access Quran Text and Metadata

Frontend data access patterns:

1. Load surah catalog: `GET /api/v1/quran/surahs/`
2. Load ayahs for a surah: `GET /api/v1/quran/surahs/{number}/ayahs/`
3. Optional translation projection per ayah:
   - pass `translation_source_id`
4. Use helper endpoints as needed:
   - ayah detail by global number
   - ayah detail by `(surah_number, number_in_surah)`
   - translation source listing
   - search (`/api/v1/quran/search/ayahs/`)
   - structure boundaries (`juz`, `hizb-quarters`, `manzils`, `rukus`)

Segmentation workflows depend on this canonical Quran layer because segment boundaries are expressed as Ayah references.
