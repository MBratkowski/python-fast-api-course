# Project: Product Catalog API

## Overview

Build a complete product catalog API with filtering, pagination, sorting, and full CRUD operations. This project combines all concepts from Module 004: path parameters, query parameters, request headers, response models, and status codes.

## Requirements

Create a `product_api.py` file with the following endpoints:

### 1. List Products (GET /products)

Supports filtering, pagination, and sorting:

**Query Parameters:**
- `category: str | None` - Filter by category
- `min_price: float | None` - Minimum price filter
- `max_price: float | None` - Maximum price filter
- `skip: int = 0` - Number of items to skip (pagination)
- `limit: int = 10` - Maximum items to return (max 100)
- `sort_by: str = "name"` - Sort field (name, price, created_at)
- `order: str = "asc"` - Sort order (asc, desc)

**Response:**
```json
{
  "products": [
    {"id": 1, "name": "Laptop", "category": "electronics", "price": 999.99, "in_stock": true},
    ...
  ],
  "total": 50,
  "skip": 0,
  "limit": 10
}
```

### 2. Get Single Product (GET /products/{product_id})

**Response:** Product object or 404 if not found

### 3. Create Product (POST /products)

**Request Body:**
```json
{
  "name": "New Product",
  "category": "electronics",
  "price": 299.99,
  "in_stock": true
}
```

**Response:** Created product with generated ID (201 status)

### 4. Update Product (PUT /products/{product_id})

**Request Body:** Full product data (all fields required)

**Response:** Updated product or 404 if not found

### 5. Partial Update (PATCH /products/{product_id})

**Request Body:** Partial product data (only fields to update)

**Response:** Updated product or 404 if not found

### 6. Delete Product (DELETE /products/{product_id})

**Response:** 204 No Content on success, 404 if not found

## Starter Template

```python
"""
Product Catalog API

A complete REST API with filtering, pagination, sorting, and CRUD operations.
Run: uvicorn product_api:app --reload
Test: pytest product_api.py -v
"""

from fastapi import FastAPI, Query, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime

app = FastAPI(title="Product Catalog API")

# ============= MODELS =============

class ProductBase(BaseModel):
    """Base product fields."""
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    in_stock: bool = True


class ProductCreate(ProductBase):
    """Schema for creating products."""
    pass


class ProductUpdate(ProductBase):
    """Schema for full update (PUT)."""
    pass


class ProductPartialUpdate(BaseModel):
    """Schema for partial update (PATCH) - all fields optional."""
    name: str | None = None
    category: str | None = None
    price: float | None = None
    in_stock: bool | None = None


class ProductResponse(ProductBase):
    """Schema for product responses."""
    id: int
    created_at: str


class ProductListResponse(BaseModel):
    """Schema for list endpoint response."""
    products: list[ProductResponse]
    total: int
    skip: int
    limit: int


# ============= DATA =============

# In-memory database (use a dict for easy CRUD)
products_db: dict[int, dict] = {
    1: {
        "id": 1,
        "name": "Laptop",
        "category": "electronics",
        "price": 999.99,
        "in_stock": True,
        "created_at": "2026-01-01T10:00:00Z"
    },
    2: {
        "id": 2,
        "name": "Wireless Mouse",
        "category": "electronics",
        "price": 29.99,
        "in_stock": True,
        "created_at": "2026-01-05T12:00:00Z"
    },
    3: {
        "id": 3,
        "name": "Office Chair",
        "category": "furniture",
        "price": 199.99,
        "in_stock": True,
        "created_at": "2026-01-10T09:00:00Z"
    },
    4: {
        "id": 4,
        "name": "Standing Desk",
        "category": "furniture",
        "price": 399.99,
        "in_stock": False,
        "created_at": "2026-01-15T14:00:00Z"
    },
    5: {
        "id": 5,
        "name": "USB-C Hub",
        "category": "electronics",
        "price": 49.99,
        "in_stock": True,
        "created_at": "2026-01-20T11:00:00Z"
    },
    6: {
        "id": 6,
        "name": "Desk Lamp",
        "category": "furniture",
        "price": 39.99,
        "in_stock": True,
        "created_at": "2026-01-25T16:00:00Z"
    },
    7: {
        "id": 7,
        "name": "Mechanical Keyboard",
        "category": "electronics",
        "price": 129.99,
        "in_stock": True,
        "created_at": "2026-02-01T10:00:00Z"
    },
    8: {
        "id": 8,
        "name": "Monitor Stand",
        "category": "furniture",
        "price": 29.99,
        "in_stock": False,
        "created_at": "2026-02-05T13:00:00Z"
    },
}

next_id = 9  # For generating new IDs


# ============= ENDPOINTS =============

@app.get("/products", response_model=ProductListResponse)
async def list_products(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    sort_by: str = "name",
    order: str = "asc"
):
    """
    List products with filtering, pagination, and sorting.

    TODO: Implement filtering, sorting, and pagination logic.
    """
    pass


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    Get single product by ID.

    TODO: Return product or raise 404 if not found.
    """
    pass


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    """
    Create new product.

    TODO: Generate ID, add to database, return created product.
    """
    pass


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductUpdate):
    """
    Update entire product (all fields required).

    TODO: Update product or raise 404 if not found.
    """
    pass


@app.patch("/products/{product_id}", response_model=ProductResponse)
async def partial_update_product(product_id: int, product: ProductPartialUpdate):
    """
    Partially update product (only provided fields).

    TODO: Update only provided fields or raise 404 if not found.
    """
    pass


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int):
    """
    Delete product.

    TODO: Delete product or raise 404 if not found. Return None.
    """
    pass


# ============= TESTS (Optional) =============
# Uncomment to test with pytest

# client = TestClient(app)
#
# def test_list_products():
#     response = client.get("/products")
#     assert response.status_code == 200
#     data = response.json()
#     assert "products" in data
#     assert "total" in data
#
# def test_filter_by_category():
#     response = client.get("/products?category=electronics")
#     assert response.status_code == 200
#     data = response.json()
#     for product in data["products"]:
#         assert product["category"] == "electronics"
#
# def test_create_product():
#     new_product = {
#         "name": "Test Product",
#         "category": "test",
#         "price": 99.99,
#         "in_stock": True
#     }
#     response = client.post("/products", json=new_product)
#     assert response.status_code == 201
#     data = response.json()
#     assert "id" in data
#
# def test_get_product():
#     response = client.get("/products/1")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == 1
#
# def test_delete_product():
#     response = client.delete("/products/1")
#     assert response.status_code == 204
```

## Success Criteria

- [ ] List endpoint supports filtering by category, price range
- [ ] List endpoint supports pagination (skip/limit)
- [ ] List endpoint supports sorting by name, price, created_at
- [ ] Get endpoint returns product or 404
- [ ] Create endpoint returns 201 with generated ID
- [ ] Update (PUT) endpoint requires all fields
- [ ] Partial update (PATCH) endpoint updates only provided fields
- [ ] Delete endpoint returns 204 on success, 404 if not found
- [ ] All endpoints use appropriate status codes
- [ ] Response models filter out any internal fields

## Testing

Run the API:
```bash
uvicorn product_api:app --reload
```

Visit the auto-generated docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Test with curl:
```bash
# List products
curl http://localhost:8000/products

# Filter by category
curl "http://localhost:8000/products?category=electronics"

# Get single product
curl http://localhost:8000/products/1

# Create product
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "New Item", "category": "test", "price": 19.99, "in_stock": true}'

# Delete product
curl -X DELETE http://localhost:8000/products/1
```

## Stretch Goals

1. **Add search by name** - `?search=laptop` filters products by name substring
2. **Add response headers** - Include `X-Total-Count` header with total product count
3. **Add category endpoint** - `GET /categories` returns list of all unique categories
4. **Add stock management** - `POST /products/{id}/restock` to mark product as in stock
5. **Add validation** - Prevent duplicate product names
6. **Add sorting validation** - Return 400 if `sort_by` field is invalid
