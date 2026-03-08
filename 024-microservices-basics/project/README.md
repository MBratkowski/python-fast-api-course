# Project: Split a Monolith into Two Services

## Overview

Take a monolithic FastAPI application (users + orders in one app) and split it into two independently running services that communicate via HTTP calls and Redis events.

## Starter Monolith

```python
"""
Monolithic API -- Users and Orders in one application.

Your task: Split this into user_service and order_service.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Monolith API")

# --- Shared Database (in-memory for simplicity) ---

users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "tier": "pro"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "tier": "free"},
}

orders_db = {}
next_order_id = 1


# --- Models ---

class OrderCreate(BaseModel):
    user_id: int
    product: str
    total: float


# --- User Endpoints ---

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users")
async def list_users():
    return list(users_db.values())


# --- Order Endpoints (directly access users_db) ---

@app.post("/orders")
async def create_order(order: OrderCreate):
    global next_order_id

    # PROBLEM: Directly accesses user data (tight coupling)
    user = users_db.get(order.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    new_order = {
        "id": next_order_id,
        "user_id": order.user_id,
        "user_name": user["name"],  # Directly reads user data
        "product": order.product,
        "total": order.total,
        "status": "created",
    }
    orders_db[next_order_id] = new_order
    next_order_id += 1
    return new_order


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # PROBLEM: Directly accesses user data
    user = users_db.get(order["user_id"])
    return {"order": order, "user": user}


@app.get("/orders")
async def list_orders(user_id: int | None = None):
    if user_id:
        return [o for o in orders_db.values() if o["user_id"] == user_id]
    return list(orders_db.values())
```

## Requirements

### Service Separation
- [ ] Create `user_service` as an independent FastAPI app with its own data store
- [ ] Create `order_service` as an independent FastAPI app with its own data store
- [ ] Each service should have a health check endpoint: `GET /health` returning `{"status": "healthy", "service": "user_service"}` (or `"order_service"`)

### HTTP Communication
- [ ] Order Service calls User Service via httpx.AsyncClient to get user details
- [ ] Use httpx.ASGITransport for testing (no running servers needed)
- [ ] Handle User Service errors gracefully (timeout, 404, 502)
- [ ] Set timeout of 5 seconds on all cross-service calls

### Event-Driven Communication
- [ ] When an order is created, publish an `order_created` event to Redis pub/sub
- [ ] When an order is cancelled, publish an `order_cancelled` event
- [ ] Event format: `{"event_type": "...", "timestamp": "...", "payload": {...}}`
- [ ] Use fakeredis for testing

### Simple API Gateway
- [ ] Create a gateway app that routes `/users/*` to User Service and `/orders/*` to Order Service
- [ ] Gateway provides a single entry point for clients

### Testing
- [ ] Test each service independently
- [ ] Test cross-service communication using ASGITransport
- [ ] Test event publishing and receiving
- [ ] Test gateway routing

## Success Criteria

1. **No shared data access**: Order Service never directly reads User data -- always calls User Service API
2. **HTTP calls work**: Order endpoints return enriched data with user details from User Service
3. **Events published**: Creating/cancelling orders publishes events to Redis channels
4. **Gateway routes correctly**: All requests through gateway reach the right service
5. **Health checks**: Each service reports its health independently
6. **Error handling**: Service unavailability is handled gracefully (502, not 500)
7. **Self-contained tests**: All tests run without Docker or running servers

## Architecture Diagram

```
                        ┌──────────────┐
    Client ────────────→│  API Gateway │
                        │  (FastAPI)   │
                        └──────┬───────┘
                               │
                    ┌──────────┼──────────┐
                    │                     │
             ┌──────┴──────┐       ┌──────┴──────┐
             │ User Service│       │Order Service │
             │  (FastAPI)  │◄─HTTP─│  (FastAPI)   │
             │             │       │              │
             │ users_db    │       │ orders_db    │
             └─────────────┘       └──────┬───────┘
                                          │
                                    Redis Pub/Sub
                                   (order events)
```

## Testing Tips

- Use `httpx.ASGITransport(app=service)` to test services without running them
- Use `fakeredis.aioredis.FakeRedis()` for Redis pub/sub testing
- Test services independently first, then test integration
- Mock time for event timestamp verification
