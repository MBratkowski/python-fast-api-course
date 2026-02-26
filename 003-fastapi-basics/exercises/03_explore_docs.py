"""
Exercise 3: Exploring OpenAPI Documentation

Practice adding metadata and documentation to your API.
Run: pytest 003-fastapi-basics/exercises/03_explore_docs.py -v
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


# Exercise 3.1: Create FastAPI app with metadata
# TODO: Create app with title, description, and version
app = None  # TODO: Replace with FastAPI(title="...", description="...", version="...")


class Item(BaseModel):
    name: str
    price: float


# Exercise 3.2: Create endpoint with tags
# TODO: Implement GET /items with tags=["items"]
@app.get("/items")
async def list_items():
    """List all items.

    Returns a list of all available items in the store.
    """
    pass  # TODO: Implement - return {"items": []}


# Exercise 3.3: Create endpoint with summary and description
# TODO: Implement POST /items with:
# - tags=["items"]
# - summary="Create a new item"
# - description="Add a new item to the store inventory"
@app.post("/items")
async def create_item(item: Item):
    """Create a new item."""
    pass  # TODO: Implement - return the item


# Exercise 3.4: Create endpoint with detailed docstring
# TODO: Implement GET /items/{item_id} with:
# - tags=["items"]
# - Detailed docstring explaining parameters and return value
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """
    Get an item by ID.

    TODO: Add detailed docstring here explaining:
    - What this endpoint does
    - Parameters description
    - Return value description
    """
    pass  # TODO: Implement - return {"id": item_id, "name": f"Item {item_id}", "price": 9.99}


# ============= TESTS =============
# Run with: pytest 003-fastapi-basics/exercises/03_explore_docs.py -v

client = TestClient(app)


def test_openapi_schema_exists():
    """Test that OpenAPI schema is generated."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


def test_app_metadata():
    """Test that app has title, description, and version."""
    response = client.get("/openapi.json")
    schema = response.json()
    info = schema["info"]

    assert "title" in info
    assert info["title"] != "FastAPI"  # Should be custom title

    assert "description" in info
    assert len(info["description"]) > 0

    assert "version" in info
    assert info["version"] != "0.1.0"  # Should be custom version


def test_endpoints_have_tags():
    """Test that endpoints are tagged."""
    response = client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]

    # Check that /items GET has tags
    assert "/items" in paths
    assert "get" in paths["/items"]
    assert "tags" in paths["/items"]["get"]
    assert "items" in paths["/items"]["get"]["tags"]


def test_endpoints_have_summaries():
    """Test that endpoints have summaries or descriptions."""
    response = client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]

    # Check POST /items has summary or description
    assert "/items" in paths
    assert "post" in paths["/items"]
    post_endpoint = paths["/items"]["post"]

    has_summary = "summary" in post_endpoint and len(post_endpoint.get("summary", "")) > 0
    has_description = "description" in post_endpoint and len(post_endpoint.get("description", "")) > 0

    assert has_summary or has_description, "POST /items should have summary or description"


def test_list_items_works():
    """Test that list items endpoint works."""
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_create_item_works():
    """Test that create item endpoint works."""
    item = {"name": "Test Item", "price": 19.99}
    response = client.post("/items", json=item)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item["name"]
    assert data["price"] == item["price"]


def test_get_item_works():
    """Test that get item endpoint works."""
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "price" in data
