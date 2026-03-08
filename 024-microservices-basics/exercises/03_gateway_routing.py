"""
Exercise 3: API Gateway Routing

Build an API gateway that routes requests to backend services based
on URL prefix. The gateway is the single entry point -- clients
talk to it, and it forwards requests to the right service.

Run: pytest 024-microservices-basics/exercises/03_gateway_routing.py -v

Requirements: pip install fastapi httpx pytest pytest-asyncio
"""

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI, HTTPException


# ============= BACKEND SERVICES (PROVIDED) =============
# These simulate separate services running on different ports.
# In production, each would be a separate deployment.

user_service = FastAPI()
product_service = FastAPI()


@user_service.get("/users/{user_id}")
async def get_user(user_id: int):
    """User Service endpoint."""
    users = {
        1: {"id": 1, "name": "Alice", "role": "admin"},
        2: {"id": 2, "name": "Bob", "role": "user"},
    }
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_service.get("/users")
async def list_users():
    """List all users."""
    return [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
    ]


@product_service.get("/products/{product_id}")
async def get_product(product_id: int):
    """Product Service endpoint."""
    products = {
        1: {"id": 1, "name": "Laptop", "price": 999.99},
        2: {"id": 2, "name": "Keyboard", "price": 79.99},
    }
    product = products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@product_service.get("/products")
async def list_products():
    """List all products."""
    return [
        {"id": 1, "name": "Laptop", "price": 999.99},
        {"id": 2, "name": "Keyboard", "price": 79.99},
    ]


# ============= API GATEWAY (IMPLEMENT THIS) =============

gateway = FastAPI()


# TODO: Exercise 3.1
# Create a service registry that maps service names to their FastAPI apps.
# This simulates what would be service URLs in production.
#
# The registry should map:
#   "users" → user_service (the FastAPI app)
#   "products" → product_service (the FastAPI app)
#
# In production, this would map to URLs like:
#   "users" → "http://user-service:8001"
#   "products" → "http://product-service:8002"

# TODO: Define SERVICE_REGISTRY as a dict mapping service names to FastAPI apps
# SERVICE_REGISTRY = {
#     "users": ...,
#     "products": ...,
# }


# TODO: Exercise 3.2
# Implement the gateway route that forwards requests to backend services.
#
# The gateway should:
# 1. Extract the service name from the URL (first path segment)
# 2. Look up the service in SERVICE_REGISTRY
# 3. If service not found: raise HTTPException(status_code=404, detail="Service not found")
# 4. Build the backend path from the remaining URL segments
#    Example: GET /users/1 → service="users", path="users/1"
# 5. Use httpx.ASGITransport(app=service_app) to forward the request
# 6. Forward with httpx.AsyncClient and return the backend's JSON response
# 7. If the backend returns an error status, forward that status code
#
# Route pattern: "/{service_name}/{path:path}"
# This captures: GET /users/1 → service_name="users", path="1"
#                GET /users → service_name="users", path=""
#                GET /products/search → service_name="products", path="search"

@gateway.get("/{service_name}/{path:path}")
async def route_request(service_name: str, path: str):
    """
    Route GET requests to the appropriate backend service.

    Maps URL prefix to backend service:
    - /users/* → User Service
    - /products/* → Product Service
    - /unknown/* → 404

    The path after the service name is forwarded to the backend.
    Example: GET /users/1 → User Service GET /users/1
    """
    # TODO: Implement
    # 1. Look up service_name in SERVICE_REGISTRY
    # 2. If not found: raise HTTPException(status_code=404, detail="Service not found")
    # 3. Create transport: httpx.ASGITransport(app=service_app)
    # 4. Create client: httpx.AsyncClient(transport=transport, base_url="http://test")
    # 5. Forward request: await client.get(f"/{service_name}/{path}", timeout=5.0)
    # 6. If response status >= 400: raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Backend error"))
    # 7. Return response.json()
    pass


# TODO: Exercise 3.3
# Handle the case where no path is provided after the service name.
# Example: GET /users → should forward to User Service GET /users

@gateway.get("/{service_name}")
async def route_request_no_path(service_name: str):
    """
    Route GET requests without a sub-path.

    Example: GET /users → forward to User Service GET /users
    """
    # TODO: Implement (same logic as route_request but path is empty)
    # Hint: Forward to f"/{service_name}" on the backend
    pass


# ============= TESTS =============
# Run with: pytest 024-microservices-basics/exercises/03_gateway_routing.py -v


@pytest.mark.asyncio
async def test_route_to_user_service():
    """GET /users/1 through gateway should return user data from User Service."""
    transport = httpx.ASGITransport(app=gateway)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/users/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_route_to_product_service():
    """GET /products/1 through gateway should return product data from Product Service."""
    transport = httpx.ASGITransport(app=gateway)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/products/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99


@pytest.mark.asyncio
async def test_unknown_service_returns_404():
    """GET /unknown/1 through gateway should return 404."""
    transport = httpx.ASGITransport(app=gateway)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/unknown/1")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_backend_404_forwarded():
    """When backend returns 404, gateway should forward 404."""
    transport = httpx.ASGITransport(app=gateway)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/users/999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_users_through_gateway():
    """GET /users through gateway should list all users."""
    transport = httpx.ASGITransport(app=gateway)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_products_through_gateway():
    """GET /products through gateway should list all products."""
    transport = httpx.ASGITransport(app=gateway)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/products")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_different_users_through_gateway():
    """Gateway should correctly route to different user IDs."""
    transport = httpx.ASGITransport(app=gateway)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response_1 = await client.get("/users/1")
        response_2 = await client.get("/users/2")

    assert response_1.json()["name"] == "Alice"
    assert response_2.json()["name"] == "Bob"
