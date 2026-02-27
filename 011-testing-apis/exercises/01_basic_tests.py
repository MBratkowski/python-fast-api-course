"""
Exercise 1: Basic API Tests with TestClient

Learn to test FastAPI endpoints using TestClient. Write tests for CRUD operations,
check status codes, validate JSON responses, and test error cases.

A simple items API is provided below. Your job: write tests for it.

Run: pytest 011-testing-apis/exercises/01_basic_tests.py -v
"""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

# ============= PROVIDED API (DO NOT MODIFY) =============

app = FastAPI()

items = {}  # In-memory storage

class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float

@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    """Create a new item."""
    item_id = len(items) + 1
    items[item_id] = item.model_dump()
    return {"id": item_id, **items[item_id]}

@app.get("/items")
def list_items():
    """List all items."""
    return [{"id": id, **data} for id, data in items.items()]

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Get item by ID."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items[item_id]}

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    """Delete item by ID."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]

# ============= TODO: Create TestClient =============

client = None  # TODO: Create TestClient for app


# ============= TODO: Exercise 1.1 =============
# Test creating an item
# - POST to /items with valid item data
# - Assert status code is 201
# - Assert response contains id, name, description, price
# - Assert id is assigned (not None)

def test_create_item():
    """Test creating an item."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.2 =============
# Test listing items
# - Create 2-3 items first
# - GET /items
# - Assert status code is 200
# - Assert response is a list
# - Assert list contains the created items

def test_list_items():
    """Test listing all items."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.3 =============
# Test getting a specific item
# - Create an item first
# - GET /items/{item_id}
# - Assert status code is 200
# - Assert response contains correct item data

def test_get_item():
    """Test getting an item by ID."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.4 =============
# Test getting non-existent item
# - GET /items/999999 (non-existent ID)
# - Assert status code is 404
# - Assert response contains error detail

def test_get_item_not_found():
    """Test 404 for non-existent item."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.5 =============
# Test deleting an item
# - Create an item first
# - DELETE /items/{item_id}
# - Assert status code is 204
# - Verify item is deleted (GET returns 404)

def test_delete_item():
    """Test deleting an item."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.6 =============
# Test validation error
# - POST to /items with invalid data (missing required field)
# - Assert status code is 422 (validation error)
# - Assert response contains error details

def test_create_item_validation_error():
    """Test validation error for invalid data."""
    # TODO: Implement
    pass


# ============= TESTS =============
# These tests verify YOUR test implementations

def test_client_exists():
    """Verify TestClient was created."""
    assert client is not None, "Create TestClient in TODO section"
    assert hasattr(client, 'get'), "client should be a TestClient instance"

def test_create_item_implementation():
    """Verify test_create_item is implemented."""
    # Clear items
    items.clear()

    # Run the learner's test
    test_create_item()

    # Verify it actually created an item
    assert len(items) > 0, "test_create_item should create an item"

def test_list_items_implementation():
    """Verify test_list_items is implemented."""
    items.clear()

    test_list_items()

    # Should have created items
    assert len(items) > 0, "test_list_items should create items to list"

def test_get_item_implementation():
    """Verify test_get_item is implemented."""
    items.clear()

    test_get_item()

    # Should have created and retrieved an item
    assert len(items) > 0, "test_get_item should create an item to get"

def test_get_item_not_found_implementation():
    """Verify test_get_item_not_found is implemented."""
    items.clear()

    # Should not raise exception
    test_get_item_not_found()

def test_delete_item_implementation():
    """Verify test_delete_item is implemented."""
    items.clear()

    test_delete_item()

    # Should have created and deleted an item
    # Items dict might be empty after delete

def test_create_item_validation_error_implementation():
    """Verify test_create_item_validation_error is implemented."""
    items.clear()

    # Should not raise exception
    test_create_item_validation_error()
