# Module 024: Microservices Basics

## Why This Module?

As a mobile developer, you have worked with modular architectures -- Swift Package modules on iOS, multi-module Gradle projects on Android. You know how to split a large app into smaller, focused modules. Microservices apply the same principle to backend systems: instead of one monolithic server, you split functionality into independently deployable services.

But microservices are not always the right choice. Many successful companies started with monoliths and only decomposed when they needed independent scaling or team autonomy. This module teaches you when microservices make sense, how services communicate, and the challenges of distributed systems -- so you can make informed architectural decisions.

## What You'll Learn

- When to use microservices vs staying with a monolith
- How to identify service boundaries using domain-driven design concepts
- Synchronous service-to-service communication with httpx AsyncClient
- Asynchronous event-driven communication with Redis pub/sub
- API gateway pattern for routing and aggregation
- Data consistency challenges in distributed systems (CAP theorem, sagas)

## Mobile Developer Context

**Distributed Systems Across Platforms:**

| Concept | iOS (Swift) | Android (Kotlin) | Backend (Microservices) |
|---------|-------------|-------------------|------------------------|
| Modularity | Swift Package modules | Gradle multi-module | Separate services |
| Communication | NotificationCenter, Combine | EventBus, SharedFlow | HTTP calls, Redis pub/sub |
| API surface | Public module interface | Module public API | REST endpoints |
| Data isolation | Module-scoped storage | Module-scoped database | Database per service |
| Routing | Coordinator/Router pattern | Navigation component | API gateway |

**Key Insight:** The architectural principles are the same -- loose coupling, high cohesion, clear interfaces. The difference is that microservices run in separate processes (or machines), so communication goes over the network instead of function calls.

## Prerequisites

Before starting, you should be comfortable with:
- [ ] FastAPI routing and endpoints (Modules 003-005)
- [ ] httpx for HTTP requests (Module 011, testing)
- [ ] Redis basics and pub/sub (Module 014)
- [ ] Async Python (Module 012)

## Topics

### Theory
1. When to Use Microservices -- Monolith vs microservices tradeoffs
2. Service Boundaries -- Domain-driven design for finding boundaries
3. Synchronous Communication -- HTTP service-to-service calls with httpx
4. Asynchronous Communication -- Event-driven architecture with Redis pub/sub
5. API Gateway -- Routing, auth, and request aggregation
6. Data Consistency -- CAP theorem, eventual consistency, saga pattern

### Exercises
1. Service Communication -- Cross-service HTTP calls with httpx and ASGITransport
2. Message Passing -- Redis pub/sub event-driven messaging
3. Gateway Routing -- API gateway that routes to backend services

### Project
Split a monolith into two communicating services.

## Time Estimate

- Theory: ~120 minutes
- Exercises: ~90 minutes
- Project: ~120 minutes

## Note

All exercises simulate multi-service architectures within single test files using `httpx.ASGITransport` to mount FastAPI apps as "remote services" -- no Docker or running servers required. Requires `httpx` and `fakeredis` packages (both already installed from earlier modules).

## Example

```python
import httpx
from fastapi import FastAPI

# Two services in one file (for testing/learning)
user_service = FastAPI()
order_service = FastAPI()


@user_service.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}


@order_service.get("/orders/{order_id}")
async def get_order(order_id: int):
    # Call user_service using ASGITransport (no running server needed)
    transport = httpx.ASGITransport(app=user_service)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/users/{order_id}")
        user = response.json()

    return {
        "order": {"id": order_id, "total": 99.99},
        "user": user,
    }
```
