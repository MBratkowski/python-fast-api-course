# Testing Strategy

## Why This Matters

As a mobile developer, you know testing is different from the backend world. In iOS, UI tests are slow and flaky. In Android, instrumented tests require an emulator. Both platforms push you toward snapshot tests and manual QA. The backend is different: you can test every endpoint, every business rule, every edge case in seconds with no emulator, no device, no simulator.

This is one of the biggest advantages of backend development. A comprehensive test suite means you can refactor with confidence, deploy without fear, and catch regressions before they reach users. But only if you test the right things in the right order.

This file synthesizes Modules 011 and 012 into a testing strategy you can apply to your capstone project from day one.

## Quick Review

- **pytest fundamentals** (Module 011): Test functions start with `test_`. Fixtures provide shared setup (database sessions, test clients). `conftest.py` makes fixtures available across test files.
- **TestClient for API testing** (Module 011): FastAPI's TestClient (built on httpx) lets you call endpoints without running a server. Override dependencies (like `get_db`) to use a test database.
- **Async patterns** (Module 012): `pytest-asyncio` enables testing async endpoints and services. `@pytest.mark.asyncio` marks async test functions. AsyncClient replaces TestClient for async route testing.
- **Fixture strategy** (Module 011): Fixtures can be scoped (function, module, session). Database fixtures typically create tables once (session scope) and roll back transactions per test (function scope).

## How They Compose

Testing is not just "write tests." It is a strategy with layers:

```
         /\
        /  \       E2E Tests (few)
       /    \      Full request through all layers
      /------\
     /        \    Integration Tests (some)
    /          \   Service + database, multiple components
   /------------\
  /              \ Unit Tests (many)
 /                \ Single function, mocked dependencies
/------------------\
```

### The Test Pyramid for APIs

| Layer | Tests | Speed | What It Catches |
|-------|-------|-------|-----------------|
| Unit | Service functions with mocked DB | Fast (ms) | Business logic errors |
| Integration | Routes with real test DB | Medium (100ms) | Wiring errors, query bugs, schema mismatches |
| E2E | Full auth flow, multi-step scenarios | Slow (1s+) | Workflow bugs, auth integration |

### How Each Module Contributes

- **Unit tests** use service functions directly, mocking the database session. They test business rules: "Can a user edit another user's post?" "Does the task limit work?"
- **Integration tests** use TestClient and a real test database. They test the full request pipeline: "Does `POST /posts` with valid data return 201 and persist to the database?"
- **E2E tests** chain multiple requests: "Register, login, create a post, comment on it, delete it." They test the system as a user would.

### Fixture Architecture

```python
# conftest.py -- the foundation of your test strategy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Session-scoped: create test database tables once
@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

# Function-scoped: fresh session per test (rolled back)
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# TestClient with overridden database
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# Helper: create an authenticated user
@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "TestPassword123"
    })
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "TestPassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

This fixture chain means every test gets a clean database and an authenticated user -- without any manual setup.

## Decision Framework

### "What to Test First, What to Test Last"

```
Priority 1 (Critical -- test first):
  - Authentication: register, login, token refresh, token expiry
  - Authorization: protected endpoint without token returns 401
  - Authorization: accessing another user's data returns 403
  - Input validation: missing required fields return 422

Priority 2 (High -- test second):
  - CRUD happy paths: create, read, update, delete with valid data
  - Relationship queries: nested resources return correct data
  - Pagination: list endpoints respect page/size parameters
  - Unique constraints: duplicate email returns 409

Priority 3 (Medium -- test third):
  - Edge cases: empty strings, max length, boundary values
  - Error handling: database errors return 500 with safe message
  - Background task triggering: verify task is enqueued (not executed)
  - Cache behavior: cached response matches fresh response

Priority 4 (Low -- test if time permits):
  - Performance: response time under threshold
  - Concurrency: parallel requests do not corrupt data
  - Rate limiting: excessive requests return 429
```

### What NOT to Test

| Skip | Why |
|------|-----|
| SQLAlchemy itself | It is tested by SQLAlchemy maintainers |
| FastAPI routing | Covered by FastAPI's own test suite |
| Pydantic validation details | Test that your schema rejects bad input, not how Pydantic works internally |
| External library internals | Test your integration with the library, not the library |

### Mocking Strategy

| What | Mock It? | Why |
|------|----------|-----|
| Database in unit tests | Yes | Speed. Test business logic, not SQL. |
| Database in integration tests | No | This IS the integration you are testing. |
| External APIs (email, payment) | Always | Unreliable, slow, costs money. |
| Redis in unit tests | Yes (fakeredis) | No Docker dependency in tests. |
| Time/dates | Yes | Make tests deterministic (token expiry). |
| Background tasks | Yes (mock .delay()) | Test that task is enqueued, not executed. |

## Capstone Application

**Social Media API -- Test Strategy**

Here is the testing plan for the Social Media capstone option:

**Test directory structure:**
```
tests/
├── conftest.py           # Fixtures: engine, db_session, client, auth_headers
├── api/
│   ├── test_auth.py      # 8-10 tests: register, login, refresh, validation
│   ├── test_users.py     # 5-7 tests: get profile, update profile, permissions
│   ├── test_posts.py     # 10-12 tests: CRUD, permissions, pagination, feed
│   ├── test_comments.py  # 6-8 tests: create, list, delete, permissions
│   └── test_likes.py     # 4-5 tests: like, unlike, duplicate like, counts
└── services/
    ├── test_auth_service.py  # Unit tests for token creation, password hashing
    └── test_post_service.py  # Unit tests for feed algorithm, permissions
```

**Priority 1 tests (write first):**
```python
# test_auth.py
def test_register_creates_user(client):
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "StrongPass123",
        "full_name": "New User"
    })
    assert response.status_code == 201
    assert "id" in response.json()

def test_register_duplicate_email(client, auth_headers):
    # auth_headers fixture already registered test@example.com
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "AnotherPass123",
        "full_name": "Duplicate"
    })
    assert response.status_code == 409

def test_login_returns_tokens(client, auth_headers):
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "TestPassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_protected_endpoint_without_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401
```

**Coverage target:** 80% line coverage minimum. Auth and CRUD paths should be at 95%+.

## Checklist

Before submitting your capstone project, verify your test suite:

- [ ] `conftest.py` provides `client`, `db_session`, and `auth_headers` fixtures
- [ ] Test database is separate from development database (SQLite or test PostgreSQL)
- [ ] Each test is independent (no test depends on another test's side effects)
- [ ] Auth tests cover: register, login, refresh, invalid credentials, expired token
- [ ] CRUD tests cover: create (201), read (200), update (200), delete (204)
- [ ] Permission tests cover: 401 without token, 403 for another user's resource
- [ ] Validation tests cover: missing fields (422), invalid types, boundary values
- [ ] Error tests cover: 404 for nonexistent resources, 409 for duplicates
- [ ] External services mocked (email, background tasks)
- [ ] `pytest -v` passes with 0 failures before every commit

## Key Takeaways

1. **Test authentication first.** If auth is broken, nothing else matters. Make it your first test file.
2. **Use the test pyramid.** Many unit tests (fast, cheap), some integration tests (slower, higher confidence), few E2E tests (slowest, catch workflow bugs).
3. **Fixtures are your testing infrastructure.** A well-designed `conftest.py` makes every test file 3 lines of setup instead of 30.
4. **Mock external services, not your own code.** If you are mocking your own service layer in integration tests, you are testing nothing.
5. **80% coverage is the target, not 100%.** The last 20% (error handlers, edge cases in third-party integrations) costs disproportionate effort. Ship at 80%, improve incrementally.
