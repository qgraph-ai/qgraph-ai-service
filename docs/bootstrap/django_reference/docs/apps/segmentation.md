# Segmentation App

## Purpose

The segmentation app supports structured analysis of Quran Surahs by dividing ayahs into semantic segments.

A segment is a contiguous ayah range representing a thematic unit, with optional metadata such as:

- title
- summary
- thematic tags

The system is built for research exploration, AI-assisted analysis, and collaborative interpretation workflows.

## Core Design Philosophy

The segmentation domain is designed around versioned, workspace-scoped artifacts:

- segmentation is treated as immutable snapshots, not mutable in-place records
- editing is modeled as creating new versions
- work is grouped inside user-owned workspaces
- public sharing is handled at workspace visibility level

This supports traceability, rollback, reproducibility, and safer concurrent usage.

## Workspace Scoping

All segmentation artifacts live under `Workspace`.

A workspace is a container for:

- segmentation versions
- workspace-scoped tags
- AI provenance records
- future analysis artifacts

Workspace visibility modes:

- `private`
- `public`
- `unlisted`

Public API browsing only exposes workspaces marked `public`.

## Versioned Segmentation Model

`SegmentationVersion` is the central snapshot entity:

- belongs to exactly one workspace
- targets exactly one Surah
- identified publicly by UUID `public_id`
- may optionally reference `base_version` (fork lineage)

Versions are used as immutable snapshots in workflow terms: user edits happen client-side, then `save-snapshot` creates a new version.

## SegmentationVersion Status System

Each version has lifecycle status:

- `draft`
- `active`
- `archived`

Invariant:

- only one `active` version per `(workspace, surah)`

This is enforced by a conditional database unique constraint and reinforced by activation transaction logic.

## Segment Model Design

`Segment` stores a contiguous ayah range:

- `start_ayah`
- `end_ayah`
- optional `title`
- optional `summary`
- `origin` (`ai` or `user`)

Validation constraints:

- start/end must belong to the same surah
- both must match the version’s surah
- start position must be less than or equal to end position

Intentionally not enforced:

- full surah coverage
- gap-free coverage

This allows partial or selective segmentation for different research strategies.

## Tagging System

`Tag` provides reusable thematic labels such as creation, prophethood, or judgment.

Tag scope is workspace-level, not version-level:

- reusable across versions in the same workspace
- consistent thematic vocabulary per workspace
- unique by `(workspace, name)`

Tags carry origin provenance (`ai` or `user`).

## SegmentTag Assignment Model

`SegmentTag` is the join model between segments and tags.

It enables:

- many tags per segment
- provenance on assignment itself (`source`: `ai` or `user`)
- uniqueness of each `(segment, tag)` association

This distinction allows tracking of AI-suggested tags versus user-confirmed/edited assignments.

## Snapshot Editing Model

Primary editing operation: save full snapshot.

Flow:

1. Client sends complete segment list for a base version.
2. Backend validates the payload.
3. Backend creates a new `SegmentationVersion` (`draft`, `base_version=<current>`).
4. Backend bulk-inserts segments.
5. Backend bulk-inserts segment-tag assignments.

Validation includes:

- ayah existence checks
- same-surah constraints
- ordered segments
- non-overlapping segments
- tag ownership checks (tags must belong to same workspace)

This keeps each version self-contained and avoids complex in-place diff logic.

## Forking and Reuse

New versions can be created from a public base version using `base_version_public_id`.

Fork behavior:

- segment structure is copied
- segment-tag assignments are copied
- tags are reused or recreated in the target workspace by name

Result:

- forked version is independent in the target workspace
- source workspace linkage remains only through `base_version` lineage metadata

## Public vs Authenticated Access

Public segmentation endpoints (anonymous read):

- list public workspaces
- get featured public workspace
- browse public versions
- inspect public segments/tags/AI outputs

Authenticated owner endpoints:

- manage own workspaces
- create versions/tags
- update/delete versions and tags
- activate version
- save snapshots

Owner isolation is enforced via query scoping and object-level permission checks.

## Activation Logic

Activation is explicit (`POST .../activate/`).

When activating a version:

- target version is set to `active`
- any other active version in same `(workspace, surah)` is demoted to `draft`

This guarantees a single canonical active version while preserving experimental drafts.

## AI Integration

AI-produced segmentation results are persisted as normal `SegmentationVersion` rows.

`SegmentationOutput` stores provenance metadata, including:

- external run/artifact ID
- model name
- model version
- generation parameters (`params`)
- production timestamp

This supports reproducibility and comparison of model outputs over time.

## Identifier Strategy

Segmentation APIs avoid integer lookup IDs for major public routes:

- workspace: `slug`
- segmentation version: UUID `public_id`
- tags: UUID `public_id`

Integer PKs remain internal relational keys and can still appear in payload fields.

## Performance Considerations

Patterns used in app code:

- `select_related` on foreign keys
- `prefetch_related` and filtered `Prefetch` for tag joins
- `bulk_create` for snapshot segment and assignment writes
- deterministic ordering by ayah position

These are important because versions can contain many segments and tag assignments.

## Future Extensibility

The snapshot-based architecture is compatible with future additions such as:

- collaborative editing
- richer AI suggestion loops
- semantic segment search
- cross-module linkage to other analysis artifacts
- comparative segmentation studies

Because each version is a self-contained artifact, extensions can be layered without rewriting core history semantics.
