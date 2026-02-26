"""
Exercise 2: Optional and Required Parameters

Handle optional and required parameters in path, query, and headers.
Run: pytest 004-request-response/exercises/02_optional_required.py -v
"""

from fastapi import FastAPI, Query, Header, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

# Simulated data
PRODUCTS = [
    {"id": 1, "name": "Laptop", "category": "electronics", "price": 999.99},
    {"id": 2, "name": "Chair", "category": "furniture", "price": 199.99},
    {"id": 3, "name": "Desk", "category": "furniture", "price": 299.99},
    {"id": 4, "name": "Phone", "category": "electronics", "price": 699.99},
    {"id": 5, "name": "Lamp", "category": "furniture", "price": 49.99},
]


# Exercise 2.1: Required query parameter
# TODO: Implement GET /search endpoint
# - q: str (REQUIRED - no default value)
# - Return {"query": q, "results": [list of products where q appears in name]}
# - Search should be case-insensitive
# - If q is not provided, FastAPI returns 422 automatically
@app.get("/search")
async def search(q: str):
    """Search products by query (required parameter)."""
    pass  # TODO: Implement


# Exercise 2.2: Optional filters with None defaults
# TODO: Implement GET /products endpoint
# - category: str | None = None (optional filter)
# - min_price: float | None = None (optional minimum price filter)
# - max_price: float | None = None (optional maximum price filter)
# - Return {"products": [...], "filters": {...}}
# - Apply filters only if provided (not None)
# - If no filters, return all products
@app.get("/products")
async def filter_products(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None
):
    """Filter products by optional criteria."""
    pass  # TODO: Implement


# Exercise 2.3: Headers - optional and required
# TODO: Implement GET /api/data endpoint
# - x_request_id: str | None from Header (optional)
# - authorization: str from Header (REQUIRED)
# - Return {"request_id": x_request_id, "authenticated": True}
# - If authorization header is missing, FastAPI returns 422
# - If authorization doesn't start with "Bearer ", raise HTTPException 401
@app.get("/api/data")
async def get_data(
    x_request_id: Annotated[str | None, Header()] = None,
    authorization: Annotated[str, Header()]
):
    """API endpoint requiring authorization header."""
    pass  # TODO: Implement


# Pydantic model for feedback
class Feedback(BaseModel):
    message: str
    email: str | None = None
    rating: int | None = None


# Exercise 2.4: Request body with optional fields
# TODO: Implement POST /feedback endpoint
# - Accept Feedback model as request body
# - message: required field
# - email: optional field
# - rating: optional field
# - Return {"status": "received", "feedback": feedback}
# - Validate that if rating is provided, it's between 1-5
@app.post("/feedback")
async def submit_feedback(feedback: Feedback):
    """Submit feedback with optional email and rating."""
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 004-request-response/exercises/02_optional_required.py -v

client = TestClient(app)

def test_search_with_query():
    """Test search with required query parameter."""
    response = client.get("/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "laptop"
    assert len(data["results"]) > 0
    # Check that "laptop" appears in at least one result
    assert any("laptop" in item["name"].lower() for item in data["results"])

def test_search_case_insensitive():
    """Test that search is case-insensitive."""
    response = client.get("/search?q=CHAIR")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    assert any("chair" in item["name"].lower() for item in data["results"])

def test_search_missing_query():
    """Test that missing q parameter returns 422."""
    response = client.get("/search")
    assert response.status_code == 422  # Required parameter missing

def test_filter_products_no_filters():
    """Test filtering products with no filters applied."""
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) == len(PRODUCTS)
    assert data["filters"]["category"] is None
    assert data["filters"]["min_price"] is None
    assert data["filters"]["max_price"] is None

def test_filter_products_by_category():
    """Test filtering products by category."""
    response = client.get("/products?category=electronics")
    assert response.status_code == 200
    data = response.json()
    assert data["filters"]["category"] == "electronics"
    # All returned products should be electronics
    for product in data["products"]:
        assert product["category"] == "electronics"

def test_filter_products_by_price_range():
    """Test filtering products by price range."""
    response = client.get("/products?min_price=100&max_price=500")
    assert response.status_code == 200
    data = response.json()
    assert data["filters"]["min_price"] == 100.0
    assert data["filters"]["max_price"] == 500.0
    # All products should be in price range
    for product in data["products"]:
        assert 100.0 <= product["price"] <= 500.0

def test_filter_products_combined():
    """Test combining multiple filters."""
    response = client.get("/products?category=furniture&min_price=100")
    assert response.status_code == 200
    data = response.json()
    # All products should match both filters
    for product in data["products"]:
        assert product["category"] == "furniture"
        assert product["price"] >= 100.0

def test_api_data_with_auth():
    """Test API endpoint with required authorization header."""
    response = client.get(
        "/api/data",
        headers={"Authorization": "Bearer token123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["request_id"] is None  # Optional header not provided

def test_api_data_with_request_id():
    """Test API endpoint with optional request ID header."""
    response = client.get(
        "/api/data",
        headers={
            "Authorization": "Bearer token123",
            "X-Request-ID": "req-abc-123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "req-abc-123"

def test_api_data_missing_auth():
    """Test that missing authorization header returns 422."""
    response = client.get("/api/data")
    assert response.status_code == 422  # Required header missing

def test_api_data_invalid_auth():
    """Test that invalid authorization format returns 401."""
    response = client.get(
        "/api/data",
        headers={"Authorization": "InvalidFormat"}
    )
    assert response.status_code == 401

def test_feedback_required_only():
    """Test submitting feedback with required field only."""
    response = client.post(
        "/feedback",
        json={"message": "Great product!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    assert data["feedback"]["message"] == "Great product!"
    assert data["feedback"]["email"] is None
    assert data["feedback"]["rating"] is None

def test_feedback_with_email():
    """Test submitting feedback with optional email."""
    response = client.post(
        "/feedback",
        json={
            "message": "Good service",
            "email": "user@example.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"]["email"] == "user@example.com"

def test_feedback_with_rating():
    """Test submitting feedback with optional rating."""
    response = client.post(
        "/feedback",
        json={
            "message": "Excellent!",
            "rating": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"]["rating"] == 5

def test_feedback_missing_message():
    """Test that missing required message field returns 422."""
    response = client.post(
        "/feedback",
        json={"email": "user@example.com"}
    )
    assert response.status_code == 422  # Required field missing

def test_feedback_invalid_rating():
    """Test that invalid rating is caught by validation."""
    response = client.post(
        "/feedback",
        json={
            "message": "Test",
            "rating": 10  # Should be 1-5
        }
    )
    # This test depends on your validation implementation
    # Could be 422 (Pydantic validation) or 400 (custom validation)
    assert response.status_code in [400, 422]
