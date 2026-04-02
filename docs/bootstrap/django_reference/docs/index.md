# Developer Documentation

This documentation explains how the QGraph backend is organized and how to work with its APIs beyond endpoint-level OpenAPI descriptions.

It is intended for:

- backend developers extending the system
- frontend developers integrating workflows
- maintainers onboarding to existing design decisions

## System Overview

The backend is split into modular Django apps:

- `accounts`: custom user model and JWT-based auth integration
- `quran`: canonical Quran structure/text and translation access APIs
- `segmentation`: workspace-scoped, versioned segmentation artifacts over Quran ayahs

## Documentation Map

- [Architecture](architecture.md)
- [Backend Overview](backend_overview.md)
- [Async Jobs (Celery + Redis)](async_jobs.md)
- [API Conventions](api_conventions.md)
- [Authentication](authentication.md)
- [Logging](logging.md)
- [Workflows](workflows.md)
- App docs:
  - [Segmentation App](apps/segmentation.md)
  - [Quran App](apps/quran.md)
  - [Accounts App](apps/accounts.md)
  - [Search App](apps/search.md)

## Recommended Reading Order

1. [Architecture](architecture.md)
2. [Async Jobs (Celery + Redis)](async_jobs.md)
3. [Authentication](authentication.md)
4. [API Conventions](api_conventions.md)
5. [Workflows](workflows.md)
6. App-specific pages in `docs/apps/`
