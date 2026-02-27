# Mocking Strategies

## Why This Matters

Your API calls external services: third-party APIs, email providers, payment gateways, cloud storage. In tests, you don't want real API calls. They're slow, cost money, and make tests flaky.

Mocking replaces real dependencies with test doubles — like OCMock (iOS), Mockito/MockK (Android), or mocktail (Dart). The patterns are universal: replace, control, verify.

## When to Mock

**Mock these:**
- External HTTP APIs (weather, payment, auth providers)
- Email services (SendGrid, Mailgun)
- Cloud storage (S3, GCS)
- Long-running operations (video processing, ML inference)
- Non-deterministic operations (random, current time)

**Don't mock these:**
- Your own database (use real database with fixtures)
- Your own business logic (test it for real)
- Simple pure functions (no need)

**Rule of thumb:** Mock at the boundaries. Test your code for real.

## unittest.mock Basics

Python's built-in `unittest.mock` provides mocking utilities:

```python
from unittest.mock import Mock, patch

# Create a mock object
mock_api = Mock()
mock_api.get_weather.return_value = {"temp": 72, "condition": "sunny"}

# Use the mock
result = mock_api.get_weather("New York")
assert result["temp"] == 72

# Verify it was called
mock_api.get_weather.assert_called_once_with("New York")
```

**Key features:**
- `Mock()`: Create mock object
- `return_value`: Set what the mock returns
- `side_effect`: Set exception or function to call
- `assert_called()`: Verify the mock was called

**Mobile Parallel:**

| Platform | Mocking Library |
|----------|----------------|
| **iOS** | OCMock, swift-mock, manual protocols |
| **Android** | Mockito, MockK |
| **Flutter** | mocktail, mockito |
| **Python** | unittest.mock (built-in) |

## Patching Functions

Use `@patch` to replace functions during tests:

```python
from unittest.mock import patch
import requests

def get_weather(city: str) -> dict:
    """Fetch weather from external API."""
    response = requests.get(f"https://api.weather.com/v1/{city}")
    return response.json()

# ============= Test with Mock =============

@patch("requests.get")
def test_get_weather(mock_get):
    """Test weather fetching with mocked HTTP call."""
    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {"temp": 72, "condition": "sunny"}
    mock_get.return_value = mock_response

    # Call function
    result = get_weather("New York")

    # Assert
    assert result["temp"] == 72
    assert result["condition"] == "sunny"

    # Verify HTTP call was made
    mock_get.assert_called_once_with("https://api.weather.com/v1/New York")
```

## Patching with Context Manager

Use `with patch()` for more control:

```python
from unittest.mock import patch, Mock

def test_get_weather_context():
    """Test with context manager."""
    with patch("requests.get") as mock_get:
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"temp": 65}
        mock_get.return_value = mock_response

        # Test
        result = get_weather("Boston")
        assert result["temp"] == 65
```

## Mocking Async Functions

Use `AsyncMock` for async functions:

```python
from unittest.mock import AsyncMock, patch
import httpx

async def fetch_user(user_id: int) -> dict:
    """Fetch user from external API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()

# ============= Test with AsyncMock =============

@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_user(mock_get):
    """Test async fetch with mocked HTTP call."""
    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_get.return_value = mock_response

    # Test
    result = await fetch_user(1)

    assert result["name"] == "Alice"
    mock_get.assert_called_once()
```

## Mocking with respx (for httpx)

`respx` is purpose-built for mocking httpx requests:

```bash
pip install respx
```

```python
import httpx
import respx
import pytest

@respx.mock
@pytest.mark.asyncio
async def test_fetch_user_with_respx():
    """Test with respx mock."""
    # Setup mock response
    respx.get("https://api.example.com/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Alice"})
    )

    # Test
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users/1")
        data = response.json()

    assert data["name"] == "Alice"

@respx.mock
@pytest.mark.asyncio
async def test_api_error():
    """Test handling API errors."""
    # Mock 500 error
    respx.get("https://api.example.com/users/999").mock(
        return_value=httpx.Response(500, json={"error": "Server error"})
    )

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users/999")

    assert response.status_code == 500
```

## FastAPI Dependency Override

The cleanest way to mock in FastAPI: override dependencies.

```python
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

# Real dependency
async def get_weather_service():
    """Get real weather service."""
    return WeatherAPI(api_key="real-key")

@app.get("/weather/{city}")
async def get_weather(city: str, service = Depends(get_weather_service)):
    """Get weather for city."""
    return await service.fetch(city)

# ============= Test with Mock Dependency =============

def test_weather_endpoint():
    """Test with mocked dependency."""
    # Create mock service
    mock_service = Mock()
    mock_service.fetch.return_value = {"temp": 70, "condition": "cloudy"}

    # Override dependency
    async def get_mock_service():
        return mock_service

    app.dependency_overrides[get_weather_service] = get_mock_service

    # Test
    client = TestClient(app)
    response = client.get("/weather/Seattle")

    assert response.status_code == 200
    assert response.json()["temp"] == 70

    # Clean up
    app.dependency_overrides.clear()
```

**This is the preferred pattern for FastAPI** — no patching needed.

## Mocking Database Queries

For complex database mocks:

```python
from unittest.mock import Mock

def test_get_user_service():
    """Test user service with mocked database."""
    # Create mock database session
    mock_db = Mock()

    # Setup mock query result
    mock_user = Mock()
    mock_user.id = 1
    mock_user.name = "Alice"

    mock_db.query().filter_by().first.return_value = mock_user

    # Test service
    from services import UserService
    service = UserService(mock_db)
    user = service.get_by_email("alice@example.com")

    assert user.name == "Alice"
    mock_db.query.assert_called_once()
```

**But prefer real database with fixtures** — database mocks get complex fast.

## Testing Error Cases

Mock errors to test error handling:

```python
from unittest.mock import patch, Mock
import requests

def fetch_data():
    """Fetch data that might fail."""
    try:
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@patch("requests.get")
def test_fetch_data_timeout(mock_get):
    """Test timeout handling."""
    mock_get.side_effect = requests.Timeout("Connection timeout")

    result = fetch_data()

    assert "error" in result
    assert "timeout" in result["error"].lower()

@patch("requests.get")
def test_fetch_data_500_error(mock_get):
    """Test 500 error handling."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    mock_get.return_value = mock_response

    result = fetch_data()

    assert "error" in result
```

## Verification

Verify mocks were called correctly:

```python
from unittest.mock import Mock

def test_verification():
    """Test mock verification methods."""
    mock = Mock()

    # Call the mock
    mock.send_email("alice@example.com", "Hello")

    # Verify it was called
    mock.send_email.assert_called()
    mock.send_email.assert_called_once()
    mock.send_email.assert_called_with("alice@example.com", "Hello")

    # Check call count
    assert mock.send_email.call_count == 1
```

## Best Practices

**1. Mock at the boundary:**
```python
# ✅ Good: Mock external API
@patch("httpx.AsyncClient.get")
async def test_fetch_user(mock_get):
    ...

# ❌ Bad: Mock your own function
@patch("services.user_service.get_user")
def test_something(mock_get_user):
    ...
```

**2. Use dependency override in FastAPI:**
```python
# ✅ Good: Override dependency
app.dependency_overrides[get_service] = get_mock_service

# ❌ Bad: Patch internal functions
@patch("api.users.some_internal_function")
def test_endpoint(mock_func):
    ...
```

**3. Keep mocks simple:**
```python
# ✅ Good: Simple mock
mock.return_value = {"temp": 72}

# ❌ Bad: Complex mock behavior
mock.side_effect = lambda x: {"temp": 72 if x == "NYC" else 65}
```

**4. Don't mock what you own:**
```python
# ✅ Good: Use real database with fixtures
def test_create_user(db_session):
    user = User(name="Alice")
    db_session.add(user)
    ...

# ❌ Bad: Mock your own database
@patch("models.User")
def test_create_user(mock_user):
    ...
```

## Key Takeaways

1. **Mock external dependencies** (APIs, services), not your own code
2. **unittest.mock** provides Mock, patch, AsyncMock
3. **respx** is great for mocking httpx requests
4. **FastAPI dependency override** is the cleanest pattern for FastAPI tests
5. **Mock at boundaries** (HTTP calls, external services)
6. **Use real database** with fixtures, not mocks
7. **Test error cases** with `side_effect`
8. **Verify calls** with `assert_called_once_with()`
