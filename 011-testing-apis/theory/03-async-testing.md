# Async Testing with pytest-asyncio

## Why This Matters

FastAPI is built on async Python. Your endpoints are `async def`, your database calls are `await`, and your HTTP clients use `async with`. To test async code properly, you need async tests.

This is like async testing in Swift (XCTest expectations), Kotlin (`runBlocking` in tests), or Flutter (async test support). The pattern is the same: run async code in a test context that waits for completion.

## Sync vs Async Testing

**TestClient (sync)** works for most FastAPI tests because it handles async endpoints internally:

```python
from fastapi.testclient import TestClient

# This works even though the endpoint is async
def test_read_user():
    response = client.get("/users/1")
    assert response.status_code == 200
```

**AsyncClient (async)** is needed when:
- Testing async dependencies or background tasks
- Testing WebSocket connections
- Testing streaming responses
- You want full control over the async context

## Installing pytest-asyncio

```bash
pip install pytest-asyncio httpx
```

Add to `pytest.ini` or `pyproject.toml`:

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

Or in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Basic Async Test

```python
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello"}

# ============= Async Test =============

@pytest.mark.asyncio
async def test_read_root():
    """Test root endpoint with AsyncClient."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}
```

**Key differences from TestClient:**
- Use `@pytest.mark.asyncio` decorator
- Test function is `async def`
- Use `async with AsyncClient(app=app, base_url="http://test")`
- `await` the request: `await ac.get("/")`

**Mobile Parallel:**

| Platform | Async Test Support |
|----------|-------------------|
| **Swift (XCTest)** | `XCTestExpectation`, `await` in async test methods |
| **Kotlin (JUnit)** | `runBlocking { }` or `runTest { }` |
| **Flutter (flutter_test)** | `testWidgets` with async/await support |
| **Python (pytest-asyncio)** | `@pytest.mark.asyncio` with async def |

## Testing Async Endpoints

```python
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient
import pytest

app = FastAPI()

users = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bob"}
}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.post("/users")
async def create_user(user: dict):
    user_id = max(users.keys()) + 1
    users[user_id] = {"id": user_id, **user}
    return users[user_id]

# ============= Async Tests =============

@pytest.mark.asyncio
async def test_get_user():
    """Test getting a user."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

@pytest.mark.asyncio
async def test_get_user_not_found():
    """Test 404 for non-existent user."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/999")

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_user():
    """Test creating a user."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users", json={"name": "Charlie"})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Charlie"
    assert "id" in data
```

## Testing Async Dependencies

When your endpoints use async dependencies (like database sessions), async tests give you full control.

```python
from fastapi import FastAPI, Depends
from httpx import AsyncClient
import pytest

app = FastAPI()

async def get_db():
    """Simulate async database connection."""
    # In real code: yield async session
    yield {"connected": True}

@app.get("/status")
async def get_status(db = Depends(get_db)):
    return {"db_connected": db["connected"]}

# ============= Test with Dependency Override =============

@pytest.mark.asyncio
async def test_with_dependency_override():
    """Test with mocked async dependency."""
    async def get_test_db():
        yield {"connected": False}

    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/status")

    assert response.json()["db_connected"] is False

    # Clean up
    app.dependency_overrides.clear()
```

## Multiple Async Requests

```python
@pytest.mark.asyncio
async def test_multiple_requests():
    """Test multiple concurrent requests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Make multiple requests concurrently
        responses = await asyncio.gather(
            ac.get("/users/1"),
            ac.get("/users/2"),
            ac.post("/users", json={"name": "Dave"})
        )

    assert responses[0].json()["name"] == "Alice"
    assert responses[1].json()["name"] == "Bob"
    assert responses[2].json()["name"] == "Dave"
```

## When to Use TestClient vs AsyncClient

**Use TestClient (sync) when:**
- Testing basic CRUD endpoints
- You don't need to control async behavior
- Your tests are simple and straightforward
- You want faster test execution

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_simple_endpoint():
    response = client.get("/users/1")
    assert response.status_code == 200
```

**Use AsyncClient (async) when:**
- Testing async dependencies
- Testing background tasks
- Testing WebSocket connections
- Testing streaming responses
- You need concurrent requests in one test

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complex_async_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users", json={"name": "Test"})
        user_id = response.json()["id"]

        response = await ac.get(f"/users/{user_id}")
        assert response.json()["name"] == "Test"
```

## AsyncClient Context Manager

Always use `async with` to ensure proper cleanup:

```python
# ✅ Correct: async context manager
@pytest.mark.asyncio
async def test_with_context_manager():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    # Client is automatically closed

# ❌ Wrong: manual creation (requires manual cleanup)
@pytest.mark.asyncio
async def test_without_context_manager():
    ac = AsyncClient(app=app, base_url="http://test")
    response = await ac.get("/")
    await ac.aclose()  # Easy to forget!
```

## Bridging to Module 012

This async testing pattern is your introduction to Python's async ecosystem. In Module 012, you'll learn:
- How the event loop works under the hood
- `asyncio.gather()` for concurrent operations (like the multiple requests example above)
- Semaphores for rate limiting
- Async context managers (like `async with AsyncClient`)
- Error handling in async code

Every async test you write uses these patterns — you're already doing async Python!

## Key Takeaways

1. **TestClient handles async endpoints** automatically (use for simple tests)
2. **AsyncClient gives full async control** (use for complex scenarios)
3. **@pytest.mark.asyncio** decorator marks async tests
4. **async with AsyncClient** ensures proper resource cleanup
5. **await requests**: `await ac.get("/")` not `ac.get("/")`
6. **Dependency overrides work** with both sync and async tests
7. **This bridges to Module 012**: async testing uses event loops, gather, context managers
