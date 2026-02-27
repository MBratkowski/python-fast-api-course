# TestClient Basics

## Why This Matters

FastAPI's `TestClient` lets you test your API endpoints without running a server — like unit testing mobile network code with MockWebServer (Android), URLProtocol stubs (iOS), or http.MockClient (Dart).

You make real HTTP requests (`GET`, `POST`, `PUT`, `DELETE`), check status codes, validate JSON responses, and verify error handling. All in-process, fast, and deterministic.

## TestClient Overview

`TestClient` wraps your FastAPI app and provides an interface that looks like `httpx` (Python's modern HTTP client).

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Create test client
client = TestClient(app)

def test_read_root():
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

**Key features:**
- No server required (runs in-process)
- Synchronous API (even for async endpoints)
- Full HTTP support (status codes, headers, cookies, redirects)
- Automatic JSON serialization/deserialization

**Mobile Parallel:**

| Platform | Testing HTTP Requests |
|----------|----------------------|
| **iOS** | `URLProtocol` stubs, `URLSession` mocks |
| **Android** | `MockWebServer` (OkHttp), Retrofit test utilities |
| **Flutter** | `http.MockClient`, mocked responses |
| **FastAPI** | `TestClient` (in-process HTTP testing) |

## Basic HTTP Methods

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

items = {}  # In-memory storage

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
async def create_item(item: Item):
    item_id = len(items) + 1
    items[item_id] = item.model_dump()
    return {"id": item_id, **items[item_id]}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items[item_id]}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item.model_dump()
    return {"id": item_id, **items[item_id]}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"message": "Item deleted"}

# ============= Tests =============

client = TestClient(app)

def test_create_item():
    """Test creating an item."""
    response = client.post("/items", json={"name": "Laptop", "price": 999.99})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99

def test_read_item():
    """Test reading an item."""
    # Create item first
    client.post("/items", json={"name": "Mouse", "price": 25.00})

    # Read it
    response = client.get("/items/2")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Mouse"
    assert data["price"] == 25.00

def test_read_item_not_found():
    """Test 404 for non-existent item."""
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_update_item():
    """Test updating an item."""
    # Create item
    client.post("/items", json={"name": "Keyboard", "price": 75.00})

    # Update it
    response = client.put("/items/3", json={"name": "Keyboard Pro", "price": 120.00})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Keyboard Pro"
    assert data["price"] == 120.00

def test_delete_item():
    """Test deleting an item."""
    # Create item
    client.post("/items", json={"name": "Monitor", "price": 300.00})

    # Delete it
    response = client.delete("/items/4")

    assert response.status_code == 200
    assert response.json() == {"message": "Item deleted"}

    # Verify it's gone
    response = client.get("/items/4")
    assert response.status_code == 404
```

## Path, Query, and Header Parameters

```python
from fastapi import FastAPI, Query, Header
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: int,
    q: str | None = None,
    limit: int = Query(10, ge=1, le=100)
):
    return {"item_id": item_id, "q": q, "limit": limit}

@app.get("/protected")
async def protected(authorization: str = Header()):
    return {"token": authorization}

# ============= Tests =============

client = TestClient(app)

def test_path_parameters():
    """Test path parameters."""
    response = client.get("/items/42")

    assert response.status_code == 200
    assert response.json()["item_id"] == 42

def test_query_parameters():
    """Test query parameters."""
    response = client.get("/items/42?q=search&limit=20")

    data = response.json()
    assert data["item_id"] == 42
    assert data["q"] == "search"
    assert data["limit"] == 20

def test_query_parameter_defaults():
    """Test default query parameter values."""
    response = client.get("/items/42")

    data = response.json()
    assert data["q"] is None
    assert data["limit"] == 10

def test_headers():
    """Test custom headers."""
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer abc123"}
    )

    assert response.status_code == 200
    assert response.json()["token"] == "Bearer abc123"
```

## Checking Status Codes

```python
def test_successful_request():
    """Test 200 OK response."""
    response = client.get("/items/1")
    assert response.status_code == 200

def test_created_response():
    """Test 201 Created response."""
    response = client.post("/items", json={"name": "Item", "price": 10})
    assert response.status_code == 201  # If your endpoint returns 201

def test_not_found():
    """Test 404 Not Found."""
    response = client.get("/items/999")
    assert response.status_code == 404

def test_bad_request():
    """Test 400 Bad Request for invalid data."""
    response = client.post("/items", json={"name": "Item"})  # Missing price
    assert response.status_code == 422  # FastAPI validation error

def test_unauthorized():
    """Test 401 Unauthorized."""
    response = client.get("/admin")
    assert response.status_code == 401
```

## Validating JSON Responses

```python
def test_json_structure():
    """Test response JSON structure."""
    response = client.get("/items/1")

    data = response.json()

    # Check keys exist
    assert "id" in data
    assert "name" in data
    assert "price" in data

    # Check types
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["price"], float)

def test_json_exact_match():
    """Test exact JSON match."""
    response = client.post("/items", json={"name": "Test", "price": 5.0})

    assert response.json() == {
        "id": 1,
        "name": "Test",
        "price": 5.0
    }

def test_json_partial_match():
    """Test partial JSON match."""
    response = client.get("/items/1")

    data = response.json()
    assert data["name"] == "Test"
    assert data["price"] > 0
```

## Testing Validation Errors

FastAPI automatically validates request data using Pydantic. Invalid data returns 422 status codes.

```python
def test_missing_required_field():
    """Test validation error for missing field."""
    response = client.post("/items", json={"name": "Incomplete"})

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", "price"] for error in errors)

def test_invalid_type():
    """Test validation error for wrong type."""
    response = client.post("/items", json={"name": "Item", "price": "invalid"})

    assert response.status_code == 422

def test_invalid_path_parameter():
    """Test validation error for invalid path parameter."""
    response = client.get("/items/not-a-number")

    assert response.status_code == 422
```

## Testing with Cookies and Sessions

```python
def test_with_cookies():
    """Test sending cookies."""
    response = client.get("/profile", cookies={"session_id": "abc123"})

    assert response.status_code == 200

def test_response_sets_cookie():
    """Test that response sets cookie."""
    response = client.post("/login", json={"username": "alice", "password": "pass"})

    assert response.status_code == 200
    assert "session_id" in response.cookies
```

## Key Takeaways

1. **TestClient wraps your FastAPI app** for in-process testing (no server needed)
2. **Full HTTP support**: GET, POST, PUT, DELETE with real status codes and headers
3. **Synchronous API**: Use `client.get()` even for async endpoints
4. **JSON handling**: Automatic serialization with `.json()` parameter and deserialization with `.json()` method
5. **Path/query/headers**: Pass parameters just like real HTTP requests
6. **Validation testing**: FastAPI returns 422 for invalid request data
7. **Fast and deterministic**: Tests run in milliseconds, no network calls
