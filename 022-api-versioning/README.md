# Module 022: API Versioning

## Why This Module?

On iOS, you set a deployment target (iOS 15, 16, 17) so your app runs on older OS versions. On Android, you set `minSdkVersion` and `targetSdkVersion` to support a range of API levels. Both platforms teach you the same lesson: old clients exist, and you can't break them when you release something new.

API versioning is the same concept for the backend. When your mobile app v1.0 is already in the App Store, and you need to change the response format for v2.0, you can't just change the endpoint -- that would break v1.0 for every user who hasn't updated. You need to run both versions simultaneously until old clients are gone.

This module teaches you how to version your FastAPI endpoints, deprecate old versions gracefully, and maintain multiple versions without drowning in complexity.

## What You'll Learn

- Why API versioning matters and when to version (vs. when not to)
- URL path versioning with FastAPI's `APIRouter` prefix (`/v1/users`, `/v2/users`)
- Header-based versioning using the `X-API-Version` custom header
- The difference between breaking and non-breaking changes
- Deprecation headers (`Sunset`, `Deprecation`) for communicating API lifecycle
- Strategies for maintaining multiple API versions with shared business logic

## Mobile Developer Context

You already understand backward compatibility. This module translates that to API design.

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| API compatibility | Deployment target (iOS 15, 16, 17) | `minSdkVersion` (API 26, 33, 34) | API version prefix (`/v1`, `/v2`) |
| Deprecation | `@available(*, deprecated)` | `@Deprecated` annotation | `Sunset` + `Deprecation` headers |
| Backward compat | `#available` checks | `Build.VERSION` checks | Multiple routers with shared logic |
| Breaking change | Removing a public API | Removing a public API | Removing a field or changing response shape |

**Key Difference from Mobile:**
- On mobile, Apple and Google deprecate OS APIs but keep them working for years. On the backend, you decide the deprecation timeline yourself -- and you're responsible for communicating it to API consumers.

## Prerequisites

- [ ] FastAPI routing and `APIRouter` (Modules 003-004)
- [ ] HTTP headers (Module 002)
- [ ] Dependency injection with `Depends()` (Module 005)

## Installation

```bash
# No additional packages required -- uses FastAPI built-ins
# APIRouter, Header, Response are all part of FastAPI
```

## Topics

### Theory
1. **Why Version APIs?** -- The cost of breaking changes, API contracts, when to version
2. **URL Path Versioning** -- `APIRouter(prefix="/v1")` pattern with separate routers per version
3. **Header Versioning** -- `X-API-Version` header with `Header()` dependency
4. **Breaking vs Non-Breaking Changes** -- What requires a new version and what doesn't
5. **Deprecation Notices** -- `Sunset` and `Deprecation` headers for API lifecycle
6. **Maintaining Multiple Versions** -- Shared service layers, adapter pattern, sunset timelines

### Exercises
1. **URL Versioning** -- Create v1 and v2 routers with different response formats
2. **Header Versioning** -- Implement version selection via `X-API-Version` header
3. **Deprecation Headers** -- Add `Sunset` and `Deprecation` headers to v1 endpoints

### Project
Add API versioning with a migration path to an existing FastAPI application.

## Time Estimate

- Theory: ~75 minutes
- Exercises: ~45 minutes
- Project: ~90 minutes

## Example

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

v1_router = APIRouter(prefix="/v1", tags=["v1"])
v2_router = APIRouter(prefix="/v2", tags=["v2"])

@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    """V1: Returns flat user object."""
    return {"id": user_id, "name": "Alice"}

@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    """V2: Returns wrapped response with metadata."""
    return {
        "data": {"id": user_id, "name": "Alice", "email": "alice@example.com"},
        "meta": {"version": "2.0"}
    }

app.include_router(v1_router)
app.include_router(v2_router)
```
