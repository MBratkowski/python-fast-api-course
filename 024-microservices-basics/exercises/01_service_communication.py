"""
Exercise 1: Service-to-Service HTTP Communication

Simulate cross-service HTTP calls using httpx.ASGITransport.
The Order Service calls the User Service to enrich order data
with user details -- without running actual servers.

Run: pytest 024-microservices-basics/exercises/01_service_communication.py -v

Requirements: pip install fastapi httpx pytest pytest-asyncio
"""

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI, HTTPException


# ============= USER SERVICE (PROVIDED) =============
# This is the "remote" service. In production it runs on a separate server.
# In this exercise, we mount it with ASGITransport.

user_service = FastAPI()

_users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
}


@user_service.get("/users/{user_id}")
async def get_user(user_id: int):
    """Return user details by ID."""
    user = _users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============= ORDER SERVICE (IMPLEMENT THIS) =============

order_service = FastAPI()

_orders_db = {
    101: {"id": 101, "user_id": 1, "product": "Laptop", "total": 999.99},
    102: {"id": 102, "user_id": 2, "product": "Keyboard", "total": 79.99},
    103: {"id": 103, "user_id": 999, "product": "Mouse", "total": 29.99},  # User doesn't exist
}


# TODO: Exercise 1.1
# Implement the get_order endpoint that:
# 1. Looks up the order in _orders_db by order_id
# 2. If order not found: raise HTTPException(status_code=404, detail="Order not found")
# 3. Calls the User Service to get user details for the order's user_id
#    - Use httpx.AsyncClient with ASGITransport to call user_service
#    - transport = httpx.ASGITransport(app=user_service)
#    - base_url = "http://test" (required but not actually used for ASGITransport)
#    - Set timeout=5.0
# 4. If User Service returns 404: set user to {"name": "Unknown User"}
# 5. If User Service has a network/timeout error: raise HTTPException(status_code=502, detail="User service unavailable")
# 6. Return: {"order": order_data, "user": user_data}

@order_service.get("/orders/{order_id}")
async def get_order(order_id: int):
    """
    Get order with enriched user data from User Service.

    Returns order details combined with user information
    fetched from the User Service via HTTP.
    """
    # TODO: Implement
    # 1. Look up order in _orders_db
    # 2. Create httpx.ASGITransport(app=user_service)
    # 3. Use async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
    # 4. Call client.get(f"/users/{order['user_id']}", timeout=5.0)
    # 5. Handle response.status_code == 404 → user = {"name": "Unknown User"}
    # 6. Handle httpx.RequestError → raise HTTPException(502)
    # 7. Return {"order": order, "user": user}
    pass


# ============= TESTS =============
# Run with: pytest 024-microservices-basics/exercises/01_service_communication.py -v


@pytest.mark.asyncio
async def test_get_order_with_user_details():
    """Order endpoint should return order with user details from User Service."""
    transport = httpx.ASGITransport(app=order_service)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/orders/101")

    assert response.status_code == 200
    data = response.json()
    assert data["order"]["id"] == 101
    assert data["order"]["product"] == "Laptop"
    assert data["user"]["name"] == "Alice"
    assert data["user"]["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_get_order_different_user():
    """Should fetch correct user for each order."""
    transport = httpx.ASGITransport(app=order_service)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/orders/102")

    assert response.status_code == 200
    data = response.json()
    assert data["order"]["product"] == "Keyboard"
    assert data["user"]["name"] == "Bob"


@pytest.mark.asyncio
async def test_order_not_found():
    """Should return 404 for non-existent order."""
    transport = httpx.ASGITransport(app=order_service)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/orders/999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_not_found_graceful_handling():
    """Should handle missing user gracefully (not crash)."""
    transport = httpx.ASGITransport(app=order_service)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Order 103 has user_id=999 which doesn't exist in user_service
        response = await client.get("/orders/103")

    assert response.status_code == 200
    data = response.json()
    assert data["order"]["id"] == 103
    assert data["user"]["name"] == "Unknown User"


@pytest.mark.asyncio
async def test_response_structure():
    """Response should have both 'order' and 'user' keys."""
    transport = httpx.ASGITransport(app=order_service)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/orders/101")

    data = response.json()
    assert "order" in data, "Response should have 'order' key"
    assert "user" in data, "Response should have 'user' key"
    assert "id" in data["order"], "Order should have 'id'"
    assert "total" in data["order"], "Order should have 'total'"
    assert "name" in data["user"], "User should have 'name'"
