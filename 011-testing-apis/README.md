# Module 011: Testing APIs

## Why This Module?

You can't ship untested code. Learn pytest and FastAPI's test client to write reliable, maintainable tests.

## What You'll Learn

- pytest fundamentals
- FastAPI TestClient
- Async testing
- Fixtures & factories
- Mocking external services
- Test database setup

## Topics

### Theory
1. pytest Basics
2. FastAPI TestClient
3. Testing Async Endpoints
4. Database Fixtures
5. Mocking with pytest-mock
6. Test Coverage

### Project
Write comprehensive tests for your CRUD API.

## Example

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def client(app, db_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def auth_headers(client, test_user):
    response = await client.post("/auth/login", json={
        "username": test_user.username,
        "password": "testpass"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_get_users(client, auth_headers):
    response = await client.get("/users", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```
