# Phase 04: Testing and Async - Research

**Researched:** 2026-02-27
**Domain:** API testing with pytest and advanced async patterns in Python
**Confidence:** HIGH

## Summary

This research covers comprehensive API testing with pytest and advanced async programming patterns in Python. The standard approach uses pytest 8.0+ with pytest-asyncio for async test support, FastAPI's TestClient for API testing, and respx for mocking HTTP calls. Advanced async patterns center on asyncio's modern structured concurrency features (TaskGroup, gather, semaphores) introduced in Python 3.11+, providing safe concurrent operations with proper error handling.

The testing ecosystem is mature and stable, with pytest as the undisputed standard. FastAPI provides first-class testing support through TestClient (sync) and httpx.AsyncClient (async). The async landscape has evolved significantly with Python 3.11's TaskGroup bringing structured concurrency similar to Swift and Kotlin, replacing gather() as the recommended pattern for managing concurrent tasks with superior safety guarantees.

For mobile developers transitioning from Swift's XCTest/async-await, Kotlin's coroutines/dispatchers, or Dart's test package, the patterns are remarkably similar: marking tests as async, using await for async operations, leveraging fixtures (equivalent to setUp/tearDown), and structured concurrency with TaskGroup mirroring Swift's withTaskGroup and Kotlin's coroutineScope.

**Primary recommendation:** Use pytest 8.0+ with pytest-asyncio for all testing. Structure tests with fixtures in conftest.py for reusable setups (database, auth clients). Use TestClient for simple sync tests and AsyncClient for real async endpoints. For concurrent operations, prefer TaskGroup over gather() for structured concurrency with automatic cancellation and exception grouping. Mock external HTTP calls with respx. Compare async patterns to mobile equivalents throughout (Swift async/await, Kotlin coroutines, Dart Futures).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

All implementation decisions are at Claude's discretion, following the established patterns from Modules 001-010. Specifically:

**Module 011 — Testing APIs:**
- Theory files cover pytest fundamentals, TestClient usage, async test patterns, fixtures/conftest, mocking with unittest.mock, and testing CRUD operations
- Exercises provide a pre-built FastAPI app to test against (students write tests, not the app)
- Mobile parallels: XCTest (Swift), JUnit/Espresso (Kotlin), flutter_test (Dart) — use comparison tables
- Project: fully test a mini CRUD API with fixtures, mocking external services, and async endpoint tests

**Module 012 — Advanced Async Python:**
- Theory files cover asyncio event loop, coroutines, asyncio.gather/wait, semaphores, async context managers, and async error handling
- Exercises are standalone runnable async scripts progressing from simple gather to semaphore-controlled concurrency
- Mobile parallels: GCD/structured concurrency (Swift), Kotlin coroutines/Dispatchers, Dart Futures/Streams — side-by-side code blocks
- Project: async data pipeline that fetches from multiple APIs concurrently with error handling and rate limiting

**Cross-module:**
- Module 011 introduces async test patterns (pytest-asyncio) as a bridge to Module 012
- Standard file naming: theory/ uses `01-kebab-case.md`, exercises/ uses `01_snake_case.py`
- Each module: 5-6 theory files, 3 exercise files, 1 project README with starter template
- README.md per module includes: Why This Module, Quick Assessment, Time Estimate, Key Differences from Mobile

### Claude's Discretion

No additional constraints — full discretion within the patterns above.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ADVN-01 | Module 011 — Testing APIs: 6 theory files (pytest basics, TestClient, async testing, DB fixtures, mocking, coverage), 3 exercises (basic tests, fixture usage, mocking), 1 project (comprehensive CRUD API tests) | Pytest 8.0+ documentation, FastAPI TestClient patterns, pytest-asyncio for async testing, respx for HTTP mocking, conftest.py fixture organization |
| ADVN-02 | Module 012 — Advanced Async Python: 6 theory files (event loop, gather/wait/as_completed, semaphores, async context managers, async generators, exception handling), 3 exercises (concurrent operations, semaphore limiting, error handling), 1 project (data aggregation from multiple services) | Python asyncio official docs, TaskGroup structured concurrency (3.11+), semaphore patterns, async context managers, mobile concurrency comparisons (Swift/Kotlin/Dart) |

</phase_requirements>

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 8.0+ | Test framework | Undisputed Python testing standard, rich plugin ecosystem, powerful fixtures |
| pytest-asyncio | 0.23+ | Async test support | Official async plugin for pytest, event loop management, async fixtures |
| pytest-cov | 4.1+ | Code coverage | Standard coverage tool, integrates with pytest, clear reports |
| FastAPI TestClient | built-in | Sync API testing | Built into FastAPI, wraps httpx, no async/await needed for simple tests |
| httpx | 0.26+ | Async HTTP client | Modern async HTTP library, used by TestClient, respx mocking support |
| respx | latest | HTTP mocking | Purpose-built for httpx/HTTPX, pattern matching, pytest fixtures |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| AsyncClient (httpx) | 0.26+ | Async API testing | Testing real async endpoints, async database operations |
| unittest.mock | built-in | General mocking | Mocking functions, classes, database calls |
| pytest-mock | latest | pytest mock integration | Cleaner pytest-style mocking with mocker fixture |
| asyncio | 3.11+ | Async operations | Event loop, gather, TaskGroup, semaphores, async context managers |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest | unittest | unittest is built-in but verbose; pytest has better DX, fixtures, and ecosystem |
| pytest-asyncio | trio-pytest | trio has different concurrency model; asyncio is standard library |
| respx | httpretty, responses | Those mock stdlib urllib/requests; respx designed specifically for httpx |
| TaskGroup (3.11+) | gather() | gather() still works but TaskGroup provides structured concurrency, better error handling |
| pytest-cov | coverage.py | pytest-cov wraps coverage.py with pytest integration; either works |

**Installation:**
```bash
# Already in requirements.txt
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
httpx>=0.26.0

# Add respx for HTTP mocking
pip install respx
```

## Architecture Patterns

### Recommended Project Structure
```
tests/
├── conftest.py              # Shared fixtures (db, client, auth)
├── test_auth.py             # Authentication endpoint tests
├── test_users.py            # User CRUD tests
├── test_posts.py            # Post CRUD tests
└── test_external_api.py     # External API integration tests

# Module 011 exercise structure
011-testing-apis/
├── exercises/
│   ├── 01_basic_tests.py           # pytest basics, TestClient
│   ├── 02_fixtures_and_db.py       # conftest.py, database fixtures
│   └── 03_mocking_external.py      # respx mocking
├── theory/
│   ├── 01-pytest-fundamentals.md
│   ├── 02-testclient-basics.md
│   ├── 03-async-testing.md
│   ├── 04-fixtures-conftest.md
│   ├── 05-mocking-strategies.md
│   └── 06-test-coverage.md
└── project/
    ├── README.md            # Full CRUD API testing project
    └── app.py               # Pre-built app for testing

# Module 012 exercise structure
012-async-python/
├── exercises/
│   ├── 01_concurrent_gather.py     # asyncio.gather basics
│   ├── 02_semaphores.py            # Limiting concurrency
│   └── 03_error_handling.py        # Exception handling patterns
├── theory/
│   ├── 01-event-loop-basics.md
│   ├── 02-gather-wait-completed.md
│   ├── 03-semaphores-limiting.md
│   ├── 04-async-context-managers.md
│   ├── 05-async-generators.md
│   └── 06-exception-handling.md
└── project/
    ├── README.md            # Data aggregation pipeline
    └── starter.py           # Async pipeline starter template
```

### Pattern 1: Basic pytest with TestClient

**What:** Simple sync testing of FastAPI endpoints using TestClient

**When to use:** Testing basic CRUD endpoints without complex async operations

**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/testing/
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_read_main():
    """Test functions use normal def, not async."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_create_item():
    """Client calls are synchronous, no await needed."""
    response = client.post(
        "/items/",
        json={"name": "Foo", "price": 42.0}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Foo"
```

### Pattern 2: Async Testing with pytest-asyncio

**What:** Testing async endpoints with AsyncClient and pytest-asyncio

**When to use:** Testing endpoints that use async database calls or external async operations

**Example:**
```python
# Source: https://fastapi.tiangolo.com/advanced/async-tests/
import pytest
from httpx import AsyncClient
from app import app

@pytest.mark.asyncio
async def test_create_user():
    """Async tests use @pytest.mark.asyncio decorator."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json={"username": "alice"})
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_users(async_client):
    """Can use async fixtures."""
    response = await async_client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Pattern 3: Fixtures in conftest.py

**What:** Reusable test setup with different scopes (function, module, session)

**When to use:** Database setup, authenticated clients, test data

**Example:**
```python
# Source: https://docs.pytest.org/en/stable/how-to/fixtures.html
# conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Session-scoped: created once per test session
@pytest.fixture(scope="session")
def engine():
    """Database engine for all tests."""
    return create_engine("sqlite:///test.db")

# Function-scoped: created/destroyed per test (default)
@pytest.fixture
async def db_session(engine):
    """Fresh database session for each test."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
async def async_client():
    """Async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def auth_client(async_client, db_session):
    """Pre-authenticated client."""
    # Create test user
    user = User(username="testuser", hashed_password=hash_password("test"))
    db_session.add(user)
    db_session.commit()

    # Login
    response = await async_client.post(
        "/auth/login",
        data={"username": "testuser", "password": "test"}
    )
    token = response.json()["access_token"]
    async_client.headers = {"Authorization": f"Bearer {token}"}
    return async_client
```

### Pattern 4: Mocking External HTTP Calls with respx

**What:** Mock httpx requests to external APIs using respx

**When to use:** Testing code that calls external APIs without making real HTTP requests

**Example:**
```python
# Source: https://lundberg.github.io/respx/
import respx
from httpx import AsyncClient

@pytest.mark.asyncio
@respx.mock
async def test_fetch_weather():
    """Mock external weather API."""
    # Mock the external API endpoint
    respx.get("https://api.weather.com/forecast").mock(
        return_value=httpx.Response(200, json={"temp": 72, "condition": "sunny"})
    )

    # Call your function that uses httpx
    result = await fetch_weather_data("San Francisco")

    assert result["temp"] == 72
    assert result["condition"] == "sunny"

@pytest.mark.asyncio
async def test_fetch_multiple_apis(respx_mock):
    """Use respx_mock fixture for multiple mocks."""
    respx_mock.get("https://api1.com/data").mock(return_value=httpx.Response(200, json={"data": "A"}))
    respx_mock.get("https://api2.com/data").mock(return_value=httpx.Response(200, json={"data": "B"}))

    results = await fetch_from_multiple_sources()
    assert len(results) == 2
```

### Pattern 5: TaskGroup for Structured Concurrency (Python 3.11+)

**What:** Modern structured concurrency with automatic cancellation and exception grouping

**When to use:** Running multiple concurrent tasks with proper error handling and cancellation

**Example:**
```python
# Source: https://docs.python.org/3/library/asyncio-task.html
import asyncio

async def fetch_data(url: str) -> dict:
    """Simulated async fetch."""
    await asyncio.sleep(0.1)
    return {"url": url, "status": 200}

async def process_urls_structured():
    """Use TaskGroup for structured concurrency."""
    urls = ["https://api1.com", "https://api2.com", "https://api3.com"]
    results = []

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_data(url)) for url in urls]

    # All tasks completed when context exits
    results = [task.result() for task in tasks]
    return results

# Mobile parallel: Swift's withTaskGroup
# Swift:
#   await withTaskGroup(of: Data.self) { group in
#       for url in urls {
#           group.addTask { await fetch(url) }
#       }
#   }
```

### Pattern 6: Semaphore for Concurrency Limiting

**What:** Limit number of concurrent operations using asyncio.Semaphore

**When to use:** Rate limiting API calls, controlling database connections, preventing resource exhaustion

**Example:**
```python
# Source: https://docs.python.org/3/library/asyncio-sync.html
import asyncio
from httpx import AsyncClient

async def fetch_with_limit(url: str, semaphore: asyncio.Semaphore) -> dict:
    """Fetch URL with concurrency limit."""
    async with semaphore:  # Acquire semaphore
        async with AsyncClient() as client:
            response = await client.get(url)
            return response.json()
    # Semaphore automatically released

async def fetch_many_urls(urls: list[str], max_concurrent: int = 10):
    """Fetch many URLs with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [fetch_with_limit(url, semaphore) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Mobile parallel: Kotlin coroutines with Dispatchers
# Kotlin:
#   val dispatcher = Dispatchers.IO.limitedParallelism(10)
#   urls.map { url ->
#       async(dispatcher) { fetchUrl(url) }
#   }.awaitAll()
```

### Pattern 7: Async Error Handling with gather

**What:** Handle exceptions in concurrent operations using gather with return_exceptions

**When to use:** When some tasks may fail but you want to process successful results

**Example:**
```python
# Source: https://docs.python.org/3/library/asyncio-task.html
import asyncio

async def fetch_or_fail(url: str):
    """May raise exception."""
    if "bad" in url:
        raise ValueError(f"Bad URL: {url}")
    await asyncio.sleep(0.1)
    return {"url": url, "status": 200}

async def fetch_with_error_handling(urls: list[str]):
    """Handle errors gracefully."""
    # return_exceptions=True: exceptions returned as list items
    results = await asyncio.gather(
        *[fetch_or_fail(url) for url in urls],
        return_exceptions=True
    )

    # Separate successful results from errors
    successful = [r for r in results if not isinstance(r, Exception)]
    errors = [r for r in results if isinstance(r, Exception)]

    return {"successful": successful, "errors": errors}

# TaskGroup alternative (automatically groups exceptions)
async def fetch_with_taskgroup(urls: list[str]):
    """TaskGroup raises ExceptionGroup on any failure."""
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch_or_fail(url)) for url in urls]
    except* ValueError as eg:
        # Exception groups use except* syntax
        print(f"Caught {len(eg.exceptions)} ValueError(s)")
        for exc in eg.exceptions:
            print(f"  - {exc}")
```

### Pattern 8: Async Context Managers

**What:** Resource management with async __aenter__ and __aexit__

**When to use:** Managing async resources (database connections, HTTP clients, file handles)

**Example:**
```python
# Source: Python asyncio patterns
import asyncio
from httpx import AsyncClient

class AsyncAPIClient:
    """Async context manager for API client."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = None

    async def __aenter__(self):
        """Async setup."""
        self.client = AsyncClient(base_url=self.base_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async cleanup."""
        if self.client:
            await self.client.aclose()

    async def fetch(self, endpoint: str):
        """Fetch data from endpoint."""
        response = await self.client.get(endpoint)
        return response.json()

# Usage
async def use_api():
    async with AsyncAPIClient("https://api.example.com") as api:
        data = await api.fetch("/users")
        return data

# Mobile parallel: Swift's deferring and structured concurrency
# Swift automatically handles resource cleanup in task scope
```

### Anti-Patterns to Avoid

- **Not marking async tests with @pytest.mark.asyncio**: Tests will fail silently or run incorrectly
- **Mixing sync TestClient with async code**: Use AsyncClient for async endpoints
- **Session-scoped fixtures for mutable state**: Use function scope to avoid test pollution
- **Using time.sleep in async code**: Always use await asyncio.sleep() in coroutines
- **Forgetting return_exceptions=True in gather**: Uncaught exceptions stop all tasks
- **Not using async with for semaphores**: Manual acquire/release prone to deadlocks
- **Creating new event loop per test**: Let pytest-asyncio manage event loops
- **Not mocking external HTTP calls**: Tests become slow, flaky, and depend on external services

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Test fixtures | Manual setup/teardown in each test | pytest fixtures with conftest.py | Scope management, dependency injection, reusability |
| Async test support | Custom event loop management | pytest-asyncio | Event loop lifecycle, proper cleanup, pytest integration |
| HTTP mocking | Manual request interception | respx for httpx | Pattern matching, context managers, pytest fixtures |
| Database test isolation | Manual transaction management | pytest fixtures with rollback | Automatic cleanup, scope control, parallel testing |
| Concurrency limiting | Custom queue/lock logic | asyncio.Semaphore | Proven, efficient, handles edge cases |
| Concurrent task management | Manual task tracking with gather | asyncio.TaskGroup (3.11+) | Structured concurrency, automatic cancellation, exception grouping |

**Key insight:** Testing and async patterns have mature, battle-tested solutions in Python's ecosystem. pytest's fixture system handles complex setup/teardown scenarios. asyncio provides robust primitives for concurrency. Reinventing these wastes time and introduces bugs.

## Common Pitfalls

### Pitfall 1: Forgetting @pytest.mark.asyncio on Async Tests

**What goes wrong:** Async test functions run but don't actually await, causing test passes when they should fail

**Why it happens:** pytest doesn't know to run async functions without the marker

**How to avoid:**
- Always use `@pytest.mark.asyncio` on async test functions
- Configure pytest-asyncio in pytest.ini for auto mode (optional)

**Warning signs:**
```python
# BAD - test passes but doesn't actually run
async def test_create_user():
    response = await client.post("/users/", json={"username": "alice"})
    assert response.status_code == 201  # Never executed!

# GOOD
@pytest.mark.asyncio
async def test_create_user():
    response = await client.post("/users/", json={"username": "alice"})
    assert response.status_code == 201
```

### Pitfall 2: Using time.sleep() in Async Code

**What goes wrong:** Blocks entire event loop, making async code synchronous

**Why it happens:** Confusion between sync and async sleep functions

**How to avoid:**
- Always use `await asyncio.sleep()` in coroutines
- Never use `time.sleep()` in async functions

**Warning signs:**
```python
# BAD - blocks event loop
import time
async def fetch_data():
    time.sleep(1)  # Blocks everything!
    return data

# GOOD
async def fetch_data():
    await asyncio.sleep(1)  # Cooperative
    return data
```

### Pitfall 3: Session-Scoped Fixtures with Mutable State

**What goes wrong:** Tests modify shared state, causing test order dependencies and flaky tests

**Why it happens:** Optimizing for speed by reusing database/objects across tests

**How to avoid:**
- Use function scope (default) for mutable resources
- Use session scope only for immutable setup (engine, app instance)
- Always rollback/reset state after each test

**Warning signs:**
```python
# BAD - shared mutable state
@pytest.fixture(scope="session")
def user_list():
    return []  # All tests share same list!

# GOOD - fresh list per test
@pytest.fixture
def user_list():
    return []
```

### Pitfall 4: Not Mocking External Services

**What goes wrong:** Tests make real HTTP calls, becoming slow, flaky, and dependent on external services

**Why it happens:** Forgetting to mock or not knowing how to mock httpx

**How to avoid:**
- Use respx to mock all httpx calls in tests
- Use @respx.mock decorator or respx_mock fixture
- Verify tests run without network access

**Warning signs:**
- Tests fail when offline or VPN active
- Tests take > 1 second to run
- Random test failures due to API rate limits or downtime

### Pitfall 5: Mixing gather() Without return_exceptions=True

**What goes wrong:** First exception cancels all remaining tasks and raises immediately

**Why it happens:** Not understanding gather's exception handling modes

**How to avoid:**
- Use `return_exceptions=True` when you want partial results
- Use TaskGroup when you want structured cancellation
- Handle exceptions from results list

**Warning signs:**
```python
# BAD - one failure stops everything
results = await asyncio.gather(
    fetch_url("https://api1.com"),  # If this fails...
    fetch_url("https://api2.com"),  # ...these never run
    fetch_url("https://api3.com")
)

# GOOD - all run, exceptions in results
results = await asyncio.gather(
    fetch_url("https://api1.com"),
    fetch_url("https://api2.com"),
    fetch_url("https://api3.com"),
    return_exceptions=True
)
# Filter out exceptions
successful = [r for r in results if not isinstance(r, Exception)]
```

### Pitfall 6: Manual Semaphore acquire() Without Release

**What goes wrong:** Semaphore never released if exception occurs, causing deadlock

**Why it happens:** Forgetting to release or not handling exceptions

**How to avoid:**
- Always use `async with semaphore:` for automatic release
- Never use manual acquire()/release() unless absolutely necessary

**Warning signs:**
```python
# BAD - semaphore leaks on exception
semaphore = asyncio.Semaphore(10)
await semaphore.acquire()
await fetch_data(url)  # If this raises, semaphore never released!
semaphore.release()

# GOOD - automatic release even on exception
async with semaphore:
    await fetch_data(url)
```

### Pitfall 7: Creating New Event Loop in Tests

**What goes wrong:** Multiple event loops conflict, causing "Event loop is closed" errors

**Why it happens:** Calling asyncio.run() or get_event_loop() in fixtures

**How to avoid:**
- Let pytest-asyncio manage event loops
- Don't call asyncio.run() in test code
- Use async fixtures with pytest-asyncio

**Warning signs:**
```python
# BAD - conflicts with pytest-asyncio
@pytest.fixture
def db_session():
    loop = asyncio.new_event_loop()  # Don't!
    asyncio.set_event_loop(loop)
    return create_session()

# GOOD - let pytest-asyncio handle it
@pytest.fixture
async def db_session():
    session = await create_session()
    yield session
    await session.close()
```

### Pitfall 8: Not Testing Async Database Operations

**What goes wrong:** Tests use sync TestClient but code uses async database calls, causing confusion

**Why it happens:** Mixing sync TestClient with async database code

**How to avoid:**
- Use AsyncClient when testing endpoints with async database operations
- Override database dependency in tests
- Use async fixtures for database sessions

**Warning signs:**
- Tests work but production code fails with "Event loop is closed"
- Deprecation warnings about sync vs async usage
- Database connections not properly closed

## Code Examples

Verified patterns from official sources:

### Complete Test Suite Structure

```python
# Source: pytest best practices + FastAPI patterns
# conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from database import Base, get_db

# Session-scoped database engine
@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

# Function-scoped database session
@pytest.fixture
def db_session(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

# Override database dependency
@pytest.fixture
def override_db(db_session):
    async def get_test_db():
        yield db_session
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()

# Async client fixture
@pytest.fixture
async def async_client(override_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Authenticated client fixture
@pytest.fixture
async def auth_client(async_client, db_session):
    # Create test user
    user = User(username="testuser", hashed_password=hash_password("test123"))
    db_session.add(user)
    db_session.commit()

    # Login
    response = await async_client.post(
        "/auth/login",
        data={"username": "testuser", "password": "test123"}
    )
    token = response.json()["access_token"]
    async_client.headers = {"Authorization": f"Bearer {token}"}
    return async_client

# test_users.py
@pytest.mark.asyncio
async def test_create_user(async_client):
    response = await async_client.post(
        "/users/",
        json={"username": "alice", "email": "alice@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "alice"

@pytest.mark.asyncio
async def test_get_users_requires_auth(async_client):
    response = await async_client.get("/users/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_users_with_auth(auth_client):
    response = await auth_client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Mobile Framework Comparison Table

```python
# Source: Various mobile testing frameworks
"""
Testing Framework Comparison for Mobile Developers:

┌─────────────┬──────────────────┬────────────────────┬─────────────────┐
│ Concept     │ Swift (XCTest)   │ Kotlin (JUnit)     │ Python (pytest) │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Test Func   │ func testX()     │ @Test fun testX()  │ def test_x()    │
│ Async Test  │ func testX()     │ @Test fun testX()  │ @pytest.mark    │
│             │   async throws   │   = runBlocking    │   .asyncio      │
│             │                  │                    │ async def test  │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Setup       │ override func    │ @BeforeEach        │ @pytest.fixture │
│             │   setUp()        │ fun setUp()        │ def setup()     │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Teardown    │ override func    │ @AfterEach         │ fixture with    │
│             │   tearDown()     │ fun tearDown()     │   yield         │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Assertions  │ XCTAssertEqual   │ assertEquals       │ assert x == y   │
│             │ XCTAssertTrue    │ assertTrue         │ assert x is True│
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Async Wait  │ await task()     │ runBlocking {      │ await task()    │
│             │                  │   task()           │                 │
│             │                  │ }                  │                 │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ HTTP Mock   │ URLProtocol      │ MockWebServer      │ respx           │
│             │ Stub             │ WireMock           │ responses       │
└─────────────┴──────────────────┴────────────────────┴─────────────────┘

Async Concurrency Comparison:

┌─────────────┬──────────────────┬────────────────────┬─────────────────┐
│ Pattern     │ Swift            │ Kotlin             │ Python          │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Parallel    │ await withTask   │ coroutineScope {   │ async with      │
│ Tasks       │   Group(of:) {   │   listOf(          │   TaskGroup():  │
│             │   group in       │     async { a() }, │   tg.create_    │
│             │   group.addTask  │     async { b() }  │     task(a())   │
│             │   { a() }        │   ).awaitAll()     │   tg.create_    │
│             │   group.addTask  │ }                  │     task(b())   │
│             │   { b() }        │                    │                 │
│             │ }                │                    │                 │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Rate Limit  │ (custom with     │ Dispatchers.IO     │ Semaphore(10)   │
│             │  semaphores)     │   .limitedPara     │ async with sem: │
│             │                  │   llelism(10)      │                 │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Error       │ try/catch in     │ supervisorScope    │ try/except* or  │
│ Handling    │ task             │ with try/catch     │ gather(...,     │
│             │                  │                    │   return_exc=T) │
├─────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Context     │ (no direct       │ withContext(       │ async with      │
│ Manager     │  equivalent)     │   dispatcher) {}   │   obj: ...      │
└─────────────┴──────────────────┴────────────────────┴─────────────────┘
"""
```

### Concurrent API Aggregation (Module 012 Project Example)

```python
# Source: asyncio patterns + structured concurrency
import asyncio
from httpx import AsyncClient
from typing import Any

class APIAggregator:
    """Fetch data from multiple APIs concurrently with rate limiting."""

    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client: AsyncClient | None = None

    async def __aenter__(self):
        self.client = AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def fetch_one(self, url: str) -> dict[str, Any]:
        """Fetch single URL with rate limiting."""
        async with self.semaphore:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return {"url": url, "data": response.json(), "error": None}
            except Exception as e:
                return {"url": url, "data": None, "error": str(e)}

    async def fetch_many(self, urls: list[str]) -> list[dict[str, Any]]:
        """Fetch many URLs concurrently using TaskGroup."""
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(self.fetch_one(url)) for url in urls]

        # Extract results (tasks completed when TaskGroup exits)
        return [task.result() for task in tasks]

    async def fetch_many_gather(self, urls: list[str]) -> list[dict[str, Any]]:
        """Alternative using gather (older pattern)."""
        results = await asyncio.gather(
            *[self.fetch_one(url) for url in urls],
            return_exceptions=True
        )

        # Convert exceptions to error dicts
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({
                    "url": urls[i],
                    "data": None,
                    "error": str(result)
                })
            else:
                processed.append(result)

        return processed

# Usage
async def main():
    urls = [
        "https://api.github.com/users/python",
        "https://api.github.com/users/microsoft",
        "https://api.github.com/users/google",
        # ... 100 more URLs
    ]

    async with APIAggregator(max_concurrent=10) as aggregator:
        results = await aggregator.fetch_many(urls)

        successful = [r for r in results if r["error"] is None]
        failed = [r for r in results if r["error"] is not None]

        print(f"Successful: {len(successful)}, Failed: {len(failed)}")

asyncio.run(main())
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| unittest | pytest | Always preferred | Better DX, fixtures, plugins, assertion introspection |
| Manual async test setup | pytest-asyncio | 2020+ | Automatic event loop management, async fixtures |
| gather() for concurrency | TaskGroup (3.11+) | 2022 (Python 3.11) | Structured concurrency, automatic cancellation, exception grouping |
| responses/httpretty | respx for httpx | 2020+ | Purpose-built for httpx, better async support |
| Manual request mocking | respx.mock decorator | Current | Cleaner test code, pattern matching |
| requests library | httpx | 2020+ | Modern async HTTP client, used by FastAPI TestClient |
| asyncio.wait() | gather() or TaskGroup | 3.11+ | Simpler API, better error handling |
| Manual semaphore acquire/release | async with semaphore | Always | Automatic cleanup, exception safety |

**Deprecated/outdated:**

- **unittest for new projects**: pytest is the community standard
- **nose/nose2**: Abandoned, use pytest
- **asyncio.wait()**: Low-level, prefer gather() or TaskGroup
- **Manual event loop management in tests**: pytest-asyncio handles it
- **requests library for new code**: Use httpx for async/await support
- **gather() for critical concurrent code**: Use TaskGroup (3.11+) for better safety

## Open Questions

Things that couldn't be fully resolved:

1. **pytest-asyncio auto mode vs manual markers**
   - What we know: Can configure `asyncio_mode = auto` in pytest.ini to skip @pytest.mark.asyncio
   - What's unclear: Community consensus on best practice, tradeoffs
   - Recommendation: Use explicit markers for clarity, especially for learning content

2. **TestClient vs AsyncClient: When to Teach Which First**
   - What we know: TestClient is simpler (no async/await), AsyncClient is more realistic
   - What's unclear: Optimal learning path for mobile developers already familiar with async
   - Recommendation: Start with TestClient in Module 011 exercises 1-2, introduce AsyncClient in exercise 3 as bridge to Module 012

3. **TaskGroup vs gather: Migration Path**
   - What we know: TaskGroup is newer and better, gather() is more common in existing code
   - What's unclear: When to prioritize teaching older gather() for code reading
   - Recommendation: Teach both—gather() first (simpler), then TaskGroup as "modern improvement" with comparison

4. **Database Testing: Rollback vs Fresh DB Per Test**
   - What we know: Rollback is faster, fresh DB is more isolated
   - What's unclear: Best practice for teaching, performance impact
   - Recommendation: Use rollback in fixtures (faster), note fresh DB option for complex scenarios

## Sources

### Primary (HIGH confidence)

- [FastAPI Testing Official Docs](https://fastapi.tiangolo.com/tutorial/testing/) - TestClient patterns and examples
- [FastAPI Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/) - AsyncClient usage
- [Python asyncio Tasks](https://docs.python.org/3/library/asyncio-task.html) - gather, TaskGroup, patterns
- [Python asyncio Sync](https://docs.python.org/3/library/asyncio-sync.html) - Semaphore, Lock, Event
- [pytest Fixtures Official](https://docs.pytest.org/en/stable/how-to/fixtures.html) - Fixture system and scopes
- [pytest-asyncio Official](https://pytest-asyncio.readthedocs.io/en/latest/) - Async test support
- [RESPX Official Docs](https://lundberg.github.io/respx/) - httpx mocking library

### Secondary (MEDIUM confidence)

- [Testing FastAPI Applications Complete Guide](https://pythoneo.com/testing-fastapi-applications/) - Comprehensive pytest + FastAPI patterns
- [FastAPI Testing Strategies 2025](https://blog.greeden.me/en/2025/11/04/fastapi-testing-strategies-to-raise-quality-pytest-testclient-httpx-dependency-overrides-db-rollbacks-mocks-contract-tests-and-load-testing/) - Modern testing approaches
- [Pytest Asyncio Guide](https://pytest-with-eric.com/pytest-advanced/pytest-asyncio/) - Practical async testing patterns
- [Python Asyncio Complete Guide 2026](https://devtoolbox.dedyn.io/blog/python-asyncio-complete-guide) - Modern async patterns
- [Mastering Python Async Patterns 2026](https://dev.to/shehzan/mastering-python-async-patterns-a-complete-guide-to-asyncio-in-2026-10o6) - Current best practices
- [Swift XCTest Async Testing](https://www.swiftbysundell.com/articles/unit-testing-code-that-uses-async-await/) - Mobile comparison reference
- [Kotlin Coroutines Testing](https://kt.academy/article/cc-testing) - Mobile comparison reference
- [Comparing Coroutines: Kotlin and Python](https://medium.com/@ms.carmen.alvarez/comparing-coroutines-by-example-in-kotlin-and-python-7e60746eae18) - Direct language comparison

### Testing Resources (HIGH confidence)

- [Building and Testing FastAPI CRUD](https://pytest-with-eric.com/pytest-advanced/pytest-fastapi-testing/) - End-to-end testing guide
- [FastAPI Best Practices 2026](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026) - Production testing patterns
- [Pytest Test Categories Async](https://pytest-test-categories.readthedocs.io/en/latest/examples/async-testing.html) - Async testing examples

### Community Examples (MEDIUM confidence)

- [FastAPI Testing with Async DB](https://dev.to/whchi/testing-fastapi-with-async-database-session-1b5d) - Database fixture patterns
- [Python Structured Concurrency](https://applifting.io/blog/python-structured-concurrency) - TaskGroup patterns
- [Pytest HTTPX VCR RESPX](https://rogulski.it/blog/pytest-httpx-vcr-respx-remote-service-tests/) - HTTP mocking strategies

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official pytest and FastAPI documentation, stable libraries
- Architecture: HIGH - Patterns from official docs and proven tutorials
- Pitfalls: MEDIUM-HIGH - Community experience, some require validation in teaching context

**Research date:** 2026-02-27
**Valid until:** ~2026-04-27 (60 days - testing and async patterns are stable)

**Note:** The testing domain with pytest is very mature and stable. asyncio patterns evolved significantly with Python 3.11 (TaskGroup) but are now settled. Main expected changes: new pytest plugins, FastAPI testing utilities, potential new async patterns in future Python versions. The research should remain valid for course development and beyond.
