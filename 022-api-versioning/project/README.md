# Project: Add Versioning with Migration Path

## Overview

Add API versioning to an existing FastAPI application with a complete migration path from v1 to v2. You'll create versioned routers, add deprecation headers, implement a shared service layer, and write tests for both versions.

This project ties together everything from Module 022 -- URL path versioning, header versioning, breaking vs non-breaking changes, deprecation headers, and version maintenance strategies.

## Requirements

### 1. URL Path Versioning
- [ ] Create `v1_router` with `APIRouter(prefix="/v1", tags=["v1 (deprecated)"])`
- [ ] Create `v2_router` with `APIRouter(prefix="/v2", tags=["v2"])`
- [ ] Both routers support: `GET /users/{user_id}`, `GET /users`, `POST /users`
- [ ] V1 returns flat responses: `{"id": 1, "name": "Alice"}`
- [ ] V2 returns wrapped responses: `{"data": {...}, "meta": {"version": "2.0"}}`

### 2. Shared Service Layer
- [ ] Create a `UserService` class with business logic (get, list, create)
- [ ] Both v1 and v2 routers use the same `UserService` via `Depends()`
- [ ] No business logic in route handlers -- only request/response transformation

### 3. Deprecation Headers on V1
- [ ] All v1 endpoints include `Deprecation: true` header
- [ ] All v1 endpoints include `Sunset` header with a future date
- [ ] Per-endpoint `Link` header pointing to the v2 successor
- [ ] Log deprecated endpoint usage with structlog (from Module 021)

### 4. Header-Based Version Negotiation
- [ ] Create `GET /users/{user_id}` (no prefix) that reads `X-API-Version` header
- [ ] Default to v1 when header is missing
- [ ] Return 400 for unsupported versions
- [ ] Include `Vary: X-API-Version` in the response

### 5. Tests
- [ ] Test v1 returns flat format
- [ ] Test v2 returns wrapped format
- [ ] Test v1 has Deprecation, Sunset, and Link headers
- [ ] Test v2 does NOT have deprecation headers
- [ ] Test header versioning defaults to v1
- [ ] Test header versioning returns 400 for unsupported version
- [ ] Test both versions return the same underlying data (parity test)

## Starter Template

Create the following file structure:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app with both routers
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py  # Shared business logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── users.py     # V1 routes
│   │   └── v2/
│   │       ├── __init__.py
│   │       └── users.py     # V2 routes
│   └── schemas/
│       ├── __init__.py
│       ├── v1.py            # V1 Pydantic models
│       └── v2.py            # V2 Pydantic models
└── tests/
    ├── __init__.py
    ├── test_v1.py           # V1 endpoint tests
    ├── test_v2.py           # V2 endpoint tests
    ├── test_deprecation.py  # Deprecation header tests
    └── test_parity.py       # Version parity tests
```

### main.py

```python
from fastapi import FastAPI
from app.api.v1.users import router as v1_router
from app.api.v2.users import router as v2_router


def create_app() -> FastAPI:
    app = FastAPI(title="Versioned API")

    app.include_router(v1_router)
    app.include_router(v2_router)

    return app


app = create_app()
```

### services/user_service.py

```python
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str


class UserService:
    """Shared business logic -- version-agnostic."""

    def __init__(self):
        self._users = {
            1: User(id=1, name="Alice", email="alice@example.com"),
            2: User(id=2, name="Bob", email="bob@example.com"),
        }

    def get_user(self, user_id: int) -> User:
        # TODO: implement
        pass

    def list_users(self) -> list[User]:
        # TODO: implement
        pass

    def create_user(self, name: str, email: str) -> User:
        # TODO: implement
        pass
```

## Success Criteria

When complete, you should be able to:

1. Call `GET /v1/users/1` and get a flat response with deprecation headers
2. Call `GET /v2/users/1` and get a wrapped response without deprecation headers
3. Call `GET /users/1` with `X-API-Version: 2.0` header and get v2 format
4. See both versions documented separately in `/docs` (Swagger UI)
5. Run `pytest` and have all tests pass
6. Observe deprecation log events in the console

## Stretch Goals

- Add a `POST /users` endpoint to both versions with different request schemas
- Implement a `301 Moved Permanently` redirect from `/v1/...` to `/v2/...` after sunset date
- Add rate limiting that varies by version (v1 gets lower limits to encourage migration)
- Create a migration guide document for API consumers
