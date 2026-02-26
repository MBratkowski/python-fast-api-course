# Module 024: Microservices Basics

## Why This Module?

As systems grow, you may need to split into multiple services. Learn the fundamentals of distributed systems.

## What You'll Learn

- Microservices vs Monolith
- Service communication (HTTP, gRPC)
- API Gateway pattern
- Service discovery
- Distributed transactions
- Event-driven architecture

## Topics

### Theory
1. When to Use Microservices
2. Service Boundaries
3. Synchronous Communication (HTTP/gRPC)
4. Asynchronous Communication (Message Queues)
5. API Gateway Pattern
6. Data Consistency Challenges

### Project
Split a monolith into two communicating services.

## Example

```python
# Service A - User Service
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}

# Service B - Order Service (calls User Service)
import httpx

USER_SERVICE_URL = "http://user-service:8000"

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = await db.get_order(order_id)

    # Call User Service
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{USER_SERVICE_URL}/users/{order.user_id}"
        )
        user = user_response.json()

    return {
        "order": order,
        "user": user
    }

# Event-driven alternative
from redis import Redis

redis = Redis()

# Service A publishes
redis.publish("user_created", json.dumps({"id": 1, "name": "Alice"}))

# Service B subscribes
pubsub = redis.pubsub()
pubsub.subscribe("user_created")
```
