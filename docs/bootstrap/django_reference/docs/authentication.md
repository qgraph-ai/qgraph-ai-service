# Authentication and Permissions

## Authentication Mechanism

The backend uses:

- Djoser for auth/user endpoints under `/api/auth/...`
- JWT authentication via `rest_framework_simplejwt`
- `Authorization: Bearer <access_token>` for authenticated API calls

Configured JWT lifetimes:

- access token: 15 minutes
- refresh token: 7 days

Login field is email (`DJOSER["LOGIN_FIELD"] = "email"`).

## User Ownership Model

Segmentation resources are ownership-based:

- `Workspace` has `owner`
- child resources (segmentation versions, segments, tags, outputs) are scoped to workspace ownership

Object-level permission checks resolve workspace ownership and allow access only when:

- request user is authenticated
- workspace owner matches request user

## Workspace Access Rules

Visibility exists at workspace level:

- `private`
- `public`
- `unlisted`

Current API behavior:

- public segmentation endpoints return only `visibility=public`
- authenticated owner endpoints return only workspaces owned by the current user
- cross-user access is blocked by queryset scoping plus object permission checks

## Public vs Authenticated Endpoints

Public/read-only:

- Quran read APIs (`/api/v1/quran/...`)
- segmentation public browsing APIs (`/api/v1/segmentation/public/...`)

Authenticated/owner-only writes:

- workspace CRUD (owner scope)
- workspace tags and segmentation version creation
- segmentation version update/delete/activate/save-snapshot
- tag update/delete

## Permission Boundaries by App

- `quran`: read-only domain APIs intended for broad consumption
- `segmentation`:
  - public endpoints: anonymous read for public workspaces only
  - owner endpoints: authenticated + owner-scoped lifecycle operations
- `accounts`: identity/auth issuance and current-user retrieval via Djoser

## Notes for Maintainers

- Authorization logic in segmentation relies on workspace ownership inheritance.
- If collaboration roles are introduced later (for example workspace members), `IsSegmentationOwner` and queryset scoping will need extension beyond owner-only checks.
