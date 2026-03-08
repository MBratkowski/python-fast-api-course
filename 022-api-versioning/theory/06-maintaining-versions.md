# Maintaining Multiple Versions

## Why This Matters

On mobile, you regularly maintain backward compatibility across multiple OS versions. Your iOS app might support iOS 15 through iOS 18, using `#available` checks for newer APIs while keeping older code paths working. On Android, you handle API level differences constantly.

Maintaining multiple API versions is the same challenge. When v1 and v2 coexist, you need strategies to avoid duplicating business logic, keep tests manageable, and eventually sunset old versions. Without a strategy, maintaining two versions quickly becomes maintaining two separate applications.

## Strategy 1: Shared Service Layer with Version-Specific Routers

This is the recommended approach. Business logic lives in a shared service layer. Each version has its own router that transforms the service layer output into version-specific responses.

```
v1 Router  ──┐
              ├──>  Service Layer  ──>  Database
v2 Router  ──┘
```

```python
# services/user_service.py -- shared, version-agnostic
from dataclasses import dataclass


@dataclass
class UserData:
    id: int
    name: str
    email: str
    role: str
    created_at: str


class UserService:
    def get_user(self, user_id: int) -> UserData:
        """Business logic is the same regardless of API version."""
        user = self.db.query(User).get(user_id)
        if not user:
            raise NotFoundError(f"User {user_id}")
        return UserData(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at.isoformat(),
        )


# api/v1/users.py -- v1 response format
from fastapi import APIRouter, Depends

v1_router = APIRouter(prefix="/v1", tags=["v1"])


@v1_router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(),
):
    user = service.get_user(user_id)
    # V1: flat response, limited fields
    return {"id": user.id, "name": user.name}


# api/v2/users.py -- v2 response format
v2_router = APIRouter(prefix="/v2", tags=["v2"])


@v2_router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(),
):
    user = service.get_user(user_id)
    # V2: wrapped response, all fields
    return {
        "data": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
        "meta": {
            "version": "2.0",
            "created_at": user.created_at,
        },
    }
```

**Key benefit:** When you fix a bug in `UserService.get_user()`, both versions get the fix automatically.

## Strategy 2: Adapter Pattern

When v2 is a transformation of v1's data, use adapter functions:

```python
def adapt_user_v1_to_v2(v1_response: dict) -> dict:
    """Transform v1 response format to v2 format."""
    return {
        "data": {
            "id": v1_response["id"],
            "name": v1_response["name"],
        },
        "meta": {"version": "2.0"},
    }


def adapt_user_v2_to_v1(v2_response: dict) -> dict:
    """Transform v2 response format to v1 format."""
    return {
        "id": v2_response["data"]["id"],
        "name": v2_response["data"]["name"],
    }
```

This pattern is useful when one version is clearly the "canonical" format and the other is a transformation of it.

## Strategy 3: Pydantic Schema Versioning

Use separate Pydantic models per version for type safety:

```python
from pydantic import BaseModel


# V1 schemas
class UserResponseV1(BaseModel):
    id: int
    name: str


# V2 schemas
class UserDataV2(BaseModel):
    id: int
    name: str
    email: str
    role: str


class MetaV2(BaseModel):
    version: str = "2.0"


class UserResponseV2(BaseModel):
    data: UserDataV2
    meta: MetaV2


# Routes with typed responses
@v1_router.get("/users/{user_id}", response_model=UserResponseV1)
async def get_user_v1(user_id: int):
    ...


@v2_router.get("/users/{user_id}", response_model=UserResponseV2)
async def get_user_v2(user_id: int):
    ...
```

Pydantic validates the response shape, so if v1 accidentally returns v2 fields, they get filtered out.

## Testing Both Versions

Every test should run against both versions:

```python
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


class TestGetUserV1:
    def test_returns_flat_response(self, client):
        response = client.get("/v1/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "email" not in data  # V1 doesn't include email

    def test_not_found(self, client):
        response = client.get("/v1/users/999")
        assert response.status_code == 404


class TestGetUserV2:
    def test_returns_wrapped_response(self, client):
        response = client.get("/v2/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"]["email"]  # V2 includes email
        assert data["meta"]["version"] == "2.0"

    def test_not_found(self, client):
        response = client.get("/v2/users/999")
        assert response.status_code == 404


class TestVersionParity:
    """Ensure both versions return the same underlying data."""

    def test_same_user_data(self, client):
        v1 = client.get("/v1/users/1").json()
        v2 = client.get("/v2/users/1").json()

        assert v1["id"] == v2["data"]["id"]
        assert v1["name"] == v2["data"]["name"]
```

## When to Drop a Version

Sunset a version when:

1. **Usage is near zero.** Check your deprecated endpoint logs (from the previous topic).
2. **The sunset date has passed.** You communicated a deadline; honor it.
3. **Maintenance burden is high.** If supporting v1 blocks v3 development, it's time.
4. **Security concerns.** If v1 has a vulnerability that can't be patched without breaking changes.

### The Removal Process

```
1. Stop accepting new consumers on v1 (documentation update)
2. Add deprecation headers if not already present
3. Set a sunset date (3-6 months out)
4. Notify consumers via email, documentation, API changelog
5. Monitor usage decline
6. At sunset date: return 410 Gone
7. After grace period: remove v1 code entirely
```

### Cleaning Up After Removal

When you remove v1:

```python
# Before: two routers
app.include_router(v1_router)  # Remove this
app.include_router(v2_router)

# After: v2 becomes the primary
app.include_router(v2_router)

# Optional: redirect old URLs
@app.get("/v1/{path:path}")
async def v1_redirect(path: str):
    return RedirectResponse(
        url=f"/v2/{path}",
        status_code=301,  # Permanent redirect
    )
```

## Mobile Analogy: Supporting Multiple OS Versions

The parallel is direct:

| Backend Versioning | Mobile Development |
|---|---|
| Running v1 and v2 simultaneously | Supporting iOS 15 and iOS 18 |
| Shared service layer | Shared ViewModel/business logic |
| Version-specific routers | `#available` / `Build.VERSION` checks |
| Deprecation headers | `@available(*, deprecated)` compiler warnings |
| Sunset date | Apple dropping iOS 15 support |
| Removing v1 code | Removing `#available` checks for old OS |

Both require maintaining backward compatibility while evolving. Both have a cost. Both eventually need cleanup.

## Best Practices Summary

1. **Keep business logic version-agnostic.** Services don't know about API versions.
2. **Use Pydantic schemas per version.** Type-safe response shaping catches format errors.
3. **Test both versions.** Every endpoint test should have v1 and v2 variants.
4. **Monitor deprecated usage.** You can't sunset what you can't measure.
5. **Communicate timelines clearly.** Publish sunset dates in headers, documentation, and direct communication.
6. **Clean up after sunset.** Dead code increases maintenance burden. Remove old versions completely.

## Key Takeaways

1. **Shared service layer is the foundation.** Business logic doesn't change between versions -- only the request/response format does.
2. **Adapters transform between formats.** Write simple functions that convert v1 shape to v2 shape and vice versa.
3. **Test version parity.** Both versions should return the same underlying data, just in different shapes.
4. **Sunset with data, not feelings.** Use usage metrics to decide when to remove a version.
5. **The removal process takes months.** Announce, deprecate, monitor, sunset, redirect, then remove.
6. **Limit active versions to two.** Supporting v1, v2, and v3 simultaneously is a maintenance nightmare. Sunset v1 before releasing v3.
