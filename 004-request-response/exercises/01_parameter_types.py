"""
Exercise 1: Parameter Types

Build endpoints with various parameter types: path, query, and combinations.
Run: pytest 004-request-response/exercises/01_parameter_types.py -v
"""

from fastapi import FastAPI, Path, Query
from fastapi.testclient import TestClient
from typing import Annotated

app = FastAPI()

# Simulated data
ITEMS = [
    {"id": 1, "name": "Laptop", "price": 999.99, "description": "High-performance laptop"},
    {"id": 2, "name": "Mouse", "price": 29.99, "description": "Wireless mouse"},
    {"id": 3, "name": "Keyboard", "price": 79.99, "description": "Mechanical keyboard"},
    {"id": 4, "name": "Monitor", "price": 299.99, "description": "27-inch 4K monitor"},
    {"id": 5, "name": "Webcam", "price": 89.99, "description": "1080p webcam"},
]

USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]


# Exercise 1.1: Path parameter with validation
# TODO: Implement GET /users/{user_id} endpoint
# - user_id must be an integer >= 1 (use Path with ge=1)
# - Return user dict if found, else {"error": "User not found"}
@app.get("/users/{user_id}")
async def get_user(
    user_id: Annotated[int, Path(ge=1, description="User ID must be positive")]
):
    """Get user by ID."""
    pass  # TODO: Implement


# Exercise 1.2: Query parameters with defaults
# TODO: Implement GET /items endpoint
# - skip: int = 0 (must be >= 0)
# - limit: int = 10 (must be between 1 and 100)
# - search: str | None = None (optional search term, filters by name if provided)
# - Return {"items": [...], "skip": skip, "limit": limit, "search": search}
# - If search is provided, filter items where search term is in name (case-insensitive)
@app.get("/items")
async def list_items(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[str | None, Query(max_length=100)] = None
):
    """List items with pagination and optional search."""
    pass  # TODO: Implement


# Exercise 1.3: Combining path and query parameters
# TODO: Implement GET /items/{item_id} endpoint
# - item_id: int path parameter (must be >= 1)
# - details: bool query parameter = False (if True, include description in response)
# - Return item dict with id, name, price
# - If details=True, also include "description" field
# - If item not found, return {"error": "Item not found"}
@app.get("/items/{item_id}")
async def get_item(
    item_id: Annotated[int, Path(ge=1)],
    details: bool = False
):
    """Get item by ID with optional details."""
    pass  # TODO: Implement


# Exercise 1.4: Path parameter with :path converter
# TODO: Implement GET /files/{file_path:path} endpoint
# - file_path captures full path including slashes
# - Return {"file_path": file_path, "segments": [list of path segments]}
# - Example: /files/docs/api/intro.md -> {"file_path": "docs/api/intro.md", "segments": ["docs", "api", "intro.md"]}
@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    """Get file by full path."""
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 004-request-response/exercises/01_parameter_types.py -v

client = TestClient(app)

def test_get_user_success():
    """Test getting user by valid ID."""
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"

def test_get_user_not_found():
    """Test getting non-existent user."""
    response = client.get("/users/999")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

def test_get_user_invalid_id():
    """Test user_id validation (must be >= 1)."""
    response = client.get("/users/0")
    assert response.status_code == 422  # Validation error

def test_list_items_default():
    """Test listing items with default pagination."""
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert data["search"] is None
    assert len(data["items"]) <= 10

def test_list_items_with_pagination():
    """Test listing items with custom pagination."""
    response = client.get("/items?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 2
    assert data["limit"] == 2
    assert len(data["items"]) <= 2

def test_list_items_with_search():
    """Test searching items by name."""
    response = client.get("/items?search=key")
    assert response.status_code == 200
    data = response.json()
    assert data["search"] == "key"
    # Should only return items with "key" in name
    for item in data["items"]:
        assert "key" in item["name"].lower()

def test_list_items_validation():
    """Test query parameter validation."""
    # limit too high
    response = client.get("/items?limit=200")
    assert response.status_code == 422

    # skip negative
    response = client.get("/items?skip=-1")
    assert response.status_code == 422

def test_get_item_basic():
    """Test getting item without details."""
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99
    assert "description" not in data  # details=False by default

def test_get_item_with_details():
    """Test getting item with details."""
    response = client.get("/items/2?details=true")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert "description" in data  # details=True
    assert data["description"] == "Wireless mouse"

def test_get_item_not_found():
    """Test getting non-existent item."""
    response = client.get("/items/999")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

def test_get_file_path():
    """Test file path parameter with :path converter."""
    response = client.get("/files/docs/api/intro.md")
    assert response.status_code == 200
    data = response.json()
    assert data["file_path"] == "docs/api/intro.md"
    assert data["segments"] == ["docs", "api", "intro.md"]

def test_get_file_single_level():
    """Test file path with single level."""
    response = client.get("/files/readme.txt")
    assert response.status_code == 200
    data = response.json()
    assert data["file_path"] == "readme.txt"
    assert data["segments"] == ["readme.txt"]
