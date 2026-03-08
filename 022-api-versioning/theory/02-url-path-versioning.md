# URL Path Versioning

## Why This Matters

On iOS, when Apple introduces a new framework API, you check availability with `#available(iOS 16, *)`. The old API still works on iOS 15. Both versions coexist. On Android, you check `Build.VERSION.SDK_INT` to use new APIs while keeping backward compatibility.

URL path versioning is the same pattern for your backend. Instead of `#available` checks, you have separate URL prefixes: `/v1/users` and `/v2/users`. Each version has its own router, its own response format, but shares the same business logic underneath.

This is the most common versioning strategy. GitHub, Stripe, Twitter, and most major APIs use it.

## The Pattern

```
/v1/users/1  -->  {"id": 1, "name": "Alice"}
/v2/users/1  -->  {"data": {"id": 1, "name": "Alice", "email": "alice@example.com"}, "meta": {"version": "2.0"}}
```

In FastAPI, this is implemented with `APIRouter` prefix:

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1 router
v1_router = APIRouter(prefix="/v1", tags=["v1"])

# Version 2 router
v2_router = APIRouter(prefix="/v2", tags=["v2"])
```

## Complete Example

Here's a full implementation with shared business logic:

```python
from fastapi import FastAPI, APIRouter, HTTPException

app = FastAPI(title="Versioned API")

# ---- Shared business logic (same for both versions) ----

# Simulated database
USERS_DB = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
}


def get_user_from_db(user_id: int) -> dict:
    """Shared service function -- both versions use this."""
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---- Version 1: Flat response ----

v1_router = APIRouter(prefix="/v1", tags=["v1"])


@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    """V1: Returns a flat user object.

    Response: {"id": 1, "name": "Alice"}
    """
    user = get_user_from_db(user_id)
    # V1 only returns id and name (the original contract)
    return {"id": user["id"], "name": user["name"]}


@v1_router.get("/users")
async def list_users_v1():
    """V1: Returns a list of users."""
    return [
        {"id": u["id"], "name": u["name"]}
        for u in USERS_DB.values()
    ]


# ---- Version 2: Wrapped response with metadata ----

v2_router = APIRouter(prefix="/v2", tags=["v2"])


@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    """V2: Returns wrapped response with metadata.

    Response: {"data": {"id": 1, "name": "Alice", "email": "..."}, "meta": {"version": "2.0"}}
    """
    user = get_user_from_db(user_id)
    # V2 returns more fields and wraps in standard envelope
    return {
        "data": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
        "meta": {
            "version": "2.0",
            "deprecated_fields": [],
        },
    }


@v2_router.get("/users")
async def list_users_v2():
    """V2: Returns a paginated list of users."""
    users = [
        {"id": u["id"], "name": u["name"], "email": u["email"]}
        for u in USERS_DB.values()
    ]
    return {
        "data": users,
        "meta": {"version": "2.0", "total": len(users)},
    }


# ---- Include both routers ----

app.include_router(v1_router)
app.include_router(v2_router)
```

## OpenAPI Documentation Separation

Using `tags` on each router groups endpoints by version in the Swagger docs:

```python
v1_router = APIRouter(prefix="/v1", tags=["v1"])
v2_router = APIRouter(prefix="/v2", tags=["v2"])
```

When you visit `/docs`, you'll see:
- **v1** section with all v1 endpoints
- **v2** section with all v2 endpoints

This makes it clear which version each endpoint belongs to.

## Shared Business Logic Pattern

The key to maintainable versioning: **routers handle request/response shaping, services handle business logic.**

```
Request --> v1 Router --> Service Layer --> Database
                |
Request --> v2 Router ----^
```

Both routers call the same service functions. The difference is how they format the response:

```python
# services/user_service.py
class UserService:
    def get_user(self, user_id: int) -> dict:
        """Business logic is version-agnostic."""
        user = db.query(User).get(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
        }


# v1/routes.py
@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int, service: UserService = Depends()):
    user = service.get_user(user_id)
    # V1 adapter: return flat subset
    return {"id": user["id"], "name": user["name"]}


# v2/routes.py
@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int, service: UserService = Depends()):
    user = service.get_user(user_id)
    # V2 adapter: return wrapped response
    return {
        "data": {"id": user["id"], "name": user["name"], "email": user["email"]},
        "meta": {"version": "2.0"},
    }
```

**Mobile analogy:** This is like having a shared ViewModel that both a SwiftUI view and a UIKit view use. The data source is the same; only the presentation differs.

## Project Structure for Versioned APIs

```
src/
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py       # v1 routes
│   │   └── schemas.py      # v1 Pydantic models
│   ├── v2/
│   │   ├── __init__.py
│   │   ├── router.py       # v2 routes
│   │   └── schemas.py      # v2 Pydantic models
│   └── __init__.py
├── services/
│   ├── __init__.py
│   └── user_service.py     # Shared business logic
├── models/
│   └── user.py             # Database model (shared)
└── main.py                 # Include both routers
```

```python
# main.py
from fastapi import FastAPI
from src.api.v1.router import router as v1_router
from src.api.v2.router import router as v2_router

app = FastAPI()
app.include_router(v1_router, prefix="/v1", tags=["v1"])
app.include_router(v2_router, prefix="/v2", tags=["v2"])
```

## When NOT to Use Separate Routers

If the only difference between v1 and v2 is one field, you might not need a full separate router. Consider:

```python
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = get_user_from_db(user_id)
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],  # New field -- non-breaking addition
    }
```

Adding a new optional field is non-breaking. Clients that don't expect `email` will simply ignore it. No versioning needed.

**Version only when you must make a breaking change.**

## Key Takeaways

1. **Use `APIRouter(prefix="/v1")` for URL path versioning.** Each version gets its own router with separate endpoints.
2. **Share business logic between versions.** The service layer is version-agnostic. Only the routers shape the request/response format.
3. **Use `tags` for OpenAPI separation.** Tag each router so Swagger docs group endpoints by version.
4. **Don't duplicate business logic.** Both `v1_router` and `v2_router` call the same service functions. The difference is response formatting.
5. **URL versioning is the most explicit strategy.** The version is visible in the URL, in documentation, in logs, and in browser history.
6. **Only create a new version for breaking changes.** Adding optional fields doesn't require a new version.
