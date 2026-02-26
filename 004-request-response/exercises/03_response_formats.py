"""
Exercise 3: Response Formats and Status Codes

Return different response formats and use appropriate status codes.
Run: pytest 004-request-response/exercises/03_response_formats.py -v
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

# Response model
class ItemResponse(BaseModel):
    """Response model for item data."""
    id: int
    name: str
    price: float
    in_stock: bool


# Simulated database
ITEMS_DB = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": True, "internal_cost": 500.0},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "in_stock": True, "internal_cost": 15.0},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "in_stock": False, "internal_cost": 40.0},
}


# Exercise 3.1: GET endpoint with response_model
# TODO: Implement GET /items/{item_id} endpoint
# - Use response_model=ItemResponse to filter response fields
# - Look up item in ITEMS_DB
# - If not found, raise HTTPException with 404 and detail "Item not found"
# - Return item data (internal_cost should be filtered out by response_model)
@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get item by ID with filtered response."""
    pass  # TODO: Implement


# Exercise 3.2: POST endpoint with 201 status code
# TODO: Implement POST /items endpoint
# - Accept ItemResponse model as request body (reuse for simplicity)
# - Set status_code=201 in decorator
# - In real app would save to database, here just return the created item
# - Return the created item with its data
@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemResponse):
    """Create new item and return 201 status."""
    pass  # TODO: Implement


# Exercise 3.3: DELETE endpoint with 204 status code
# TODO: Implement DELETE /items/{item_id} endpoint
# - Set status_code=204 in decorator
# - Look up item in ITEMS_DB
# - If not found, raise HTTPException with 404
# - If found, delete from ITEMS_DB (simulate deletion)
# - Return None (204 means no content in response body)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete item and return 204 status."""
    pass  # TODO: Implement


# Exercise 3.4: Endpoint that raises 404 with custom detail
# TODO: Implement GET /items/{item_id}/stock endpoint
# - Look up item in ITEMS_DB
# - If not found, raise HTTPException with:
#   - status_code=404
#   - detail=f"Item {item_id} not found"
# - If found, return {"item_id": item_id, "in_stock": item["in_stock"]}
@app.get("/items/{item_id}/stock")
async def get_item_stock(item_id: int):
    """Get item stock status with custom 404 handling."""
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 004-request-response/exercises/03_response_formats.py -v

client = TestClient(app)

def test_get_item_success():
    """Test getting item with response_model filtering."""
    response = client.get("/items/1")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99
    assert data["in_stock"] is True

    # response_model should filter out internal_cost
    assert "internal_cost" not in data

def test_get_item_not_found():
    """Test getting non-existent item returns 404."""
    response = client.get("/items/999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_get_item_filters_internal_fields():
    """Test that response_model filters internal fields."""
    response = client.get("/items/2")
    assert response.status_code == 200
    data = response.json()

    # Public fields
    assert "id" in data
    assert "name" in data
    assert "price" in data
    assert "in_stock" in data

    # Internal field filtered out
    assert "internal_cost" not in data

def test_create_item_status_code():
    """Test POST endpoint returns 201 Created status."""
    new_item = {
        "id": 10,
        "name": "New Product",
        "price": 49.99,
        "in_stock": True
    }

    response = client.post("/items", json=new_item)
    assert response.status_code == 201  # Created status

    data = response.json()
    assert data["id"] == 10
    assert data["name"] == "New Product"

def test_create_item_response_model():
    """Test POST endpoint uses response_model."""
    new_item = {
        "id": 11,
        "name": "Another Product",
        "price": 99.99,
        "in_stock": False
    }

    response = client.post("/items", json=new_item)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "price" in data
    assert "in_stock" in data

def test_delete_item_success():
    """Test deleting existing item returns 204."""
    # First verify item exists
    get_response = client.get("/items/1")
    assert get_response.status_code == 200

    # Delete the item
    delete_response = client.delete("/items/1")
    assert delete_response.status_code == 204

    # 204 means no content in response body
    assert delete_response.text == ""

def test_delete_item_not_found():
    """Test deleting non-existent item returns 404."""
    response = client.delete("/items/999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_delete_item_no_content():
    """Test that 204 response has no content."""
    # Use item 2 for deletion test
    response = client.delete("/items/2")
    assert response.status_code == 204

    # Response body should be empty
    assert response.content == b""

def test_get_stock_success():
    """Test getting stock status for existing item."""
    response = client.get("/items/1/stock")
    assert response.status_code == 200

    data = response.json()
    assert "item_id" in data
    assert "in_stock" in data
    assert data["item_id"] == 1

def test_get_stock_not_found():
    """Test getting stock for non-existent item returns 404."""
    response = client.get("/items/999/stock")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "999" in data["detail"]  # Custom detail includes item_id

def test_get_stock_out_of_stock():
    """Test getting stock status for out-of-stock item."""
    response = client.get("/items/3/stock")
    assert response.status_code == 200

    data = response.json()
    assert data["item_id"] == 3
    assert data["in_stock"] is False

def test_response_status_codes():
    """Test that correct status codes are used for different operations."""
    # GET: 200 OK
    get_resp = client.get("/items/1")
    assert get_resp.status_code == 200

    # POST: 201 Created
    post_resp = client.post("/items", json={
        "id": 20,
        "name": "Test",
        "price": 10.0,
        "in_stock": True
    })
    assert post_resp.status_code == 201

    # DELETE: 204 No Content
    delete_resp = client.delete("/items/2")
    assert delete_resp.status_code == 204

    # GET not found: 404 Not Found
    not_found_resp = client.get("/items/999")
    assert not_found_resp.status_code == 404
