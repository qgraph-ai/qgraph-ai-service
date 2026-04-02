# Accounts App

## Purpose

The `accounts` app defines the user identity model used across the backend and integrates with Djoser/JWT authentication flows.

It is the foundation for ownership and authorization decisions in other apps (notably segmentation workspaces).

## User Model

The project uses a custom Django user model:

- class: `accounts.User`
- `email` is unique and used as login identifier
- `username` is removed (`USERNAME_FIELD = "email"`)

Custom user manager methods implement `create_user` and `create_superuser` with email normalization and expected Django flags.

## Authentication Integration

Auth endpoints are provided via Djoser routes under `/api/auth/...` and JWT routes under the same prefix.

Typical flow:

1. register user (`/api/auth/users/`)
2. obtain JWT pair (`/api/auth/jwt/create/`)
3. call authenticated endpoints with bearer token
4. retrieve current user (`/api/auth/users/me/`)

## Ownership Model for Resources

While `accounts` itself stores user identities, resource ownership is implemented in domain apps:

- segmentation `Workspace.owner` references `accounts.User`
- object-level access checks enforce owner-only mutation/access for private resources

So the accounts app acts as the identity root for authorization policies elsewhere.

## User Interaction with Workspaces

From a user perspective:

- each user can create and manage their own workspaces
- workspace children (versions/tags/segments outputs) inherit ownership through workspace
- users cannot access other users’ private workspace resources via owner endpoints

Public segmentation browsing is decoupled from account ownership and available anonymously for public workspaces.

## Access Control Principles

Current access control is:

- authentication by JWT
- authorization primarily by ownership
- object access scoped by queryset filtering + object permission checks

This is intentionally simple and predictable for v1.

## Extensibility Notes

Areas to extend as requirements grow:

- workspace membership/collaboration roles
- finer-grained role-based permissions
- profile fields and account metadata
- audit/security policies around auth events

When such features are introduced, this page should be expanded with lifecycle diagrams and permission matrixes.
