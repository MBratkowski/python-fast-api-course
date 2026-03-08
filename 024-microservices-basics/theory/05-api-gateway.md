# API Gateway

## Why This Matters

On mobile, your app talks to one backend URL. But in a microservices architecture, there might be 5, 10, or 50 different services. Should your mobile app know about all of them? Absolutely not. An API gateway sits between clients and services, providing a single entry point that routes requests to the right backend service.

This is the same pattern as a Coordinator or Router in iOS, or Navigation Component in Android -- a central point that decides where to send the user (or request).

## What an API Gateway Does

```
Without Gateway:
                                    ┌──────────────┐
Mobile App ──→ http://users:8001 ──→│ User Service │
           ──→ http://orders:8002──→│ Order Service│
           ──→ http://products:8003→│ Product Svc  │
           ──→ http://payments:8004→│ Payment Svc  │

   Client needs to know every service URL!
   Client handles auth for each service!
   Every service exposed to the internet!


With Gateway:
                                         ┌──────────────┐
Mobile App ──→ http://api.example.com ──→│  API Gateway  │
               (one URL)                 │               │
                                         │ /users/* ──→ User Service
                                         │ /orders/* ─→ Order Service
                                         │ /products/*→ Product Svc
                                         │ /payments/*→ Payment Svc
                                         └──────────────┘

   Client knows one URL!
   Gateway handles auth once!
   Services are internal only!
```

### Gateway Responsibilities

| Responsibility | Description |
|---------------|-------------|
| **Routing** | Route `/users/*` to User Service, `/orders/*` to Order Service |
| **Authentication** | Verify JWT once at the gateway, pass user info to services |
| **Rate limiting** | Apply rate limits at the gateway (Module 023) |
| **Request aggregation** | Combine data from multiple services into one response |
| **Load balancing** | Distribute requests across service instances |
| **SSL termination** | Handle HTTPS at the gateway, use HTTP internally |

## Simple Gateway with FastAPI

```python
import httpx
from fastapi import FastAPI, Request, HTTPException

gateway = FastAPI()

# Service registry: maps URL prefixes to backend service URLs
SERVICE_REGISTRY = {
    "users": "http://user-service:8001",
    "orders": "http://order-service:8002",
    "products": "http://product-service:8003",
}


@gateway.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service_name: str, path: str, request: Request):
    """Route requests to the appropriate backend service."""
    # Look up service URL
    service_url = SERVICE_REGISTRY.get(service_name)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    # Build target URL
    target_url = f"{service_url}/{path}"

    # Forward the request
    async with httpx.AsyncClient() as client:
        try:
            # Forward with same method, headers, and body
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={
                    key: value
                    for key, value in request.headers.items()
                    if key.lower() not in ("host", "content-length")
                },
                content=await request.body(),
                timeout=10.0,
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timed out")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Service unavailable")

    # Return the service's response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )
```

## Routing Based on URL Prefix

The gateway inspects the first path segment to determine which service to call:

```python
# Request: GET /users/42
# → Route to: http://user-service:8001/42

# Request: POST /orders
# → Route to: http://order-service:8002/

# Request: GET /products/search?q=laptop
# → Route to: http://product-service:8003/search?q=laptop
```

### With Query Parameters

```python
from fastapi import Request
from urllib.parse import urlencode

@gateway.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service_name: str, path: str, request: Request):
    service_url = SERVICE_REGISTRY.get(service_name)
    if not service_url:
        raise HTTPException(status_code=404, detail="Unknown service")

    # Preserve query parameters
    target_url = f"{service_url}/{path}"
    if request.query_params:
        target_url += f"?{request.query_params}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            content=await request.body(),
            timeout=10.0,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
    )
```

## Request Aggregation

Sometimes a client needs data from multiple services. Instead of making the client call each service, the gateway aggregates responses:

```python
@gateway.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int):
    """
    Aggregate data from multiple services into a single dashboard response.
    Client makes one request; gateway makes three.
    """
    async with httpx.AsyncClient() as client:
        # Call multiple services in parallel
        import asyncio

        user_task = client.get(
            f"{SERVICE_REGISTRY['users']}/{user_id}",
            timeout=5.0,
        )
        orders_task = client.get(
            f"{SERVICE_REGISTRY['orders']}/?user_id={user_id}",
            timeout=5.0,
        )

        user_response, orders_response = await asyncio.gather(
            user_task, orders_task,
            return_exceptions=True,
        )

    # Build aggregated response
    dashboard = {}

    if isinstance(user_response, httpx.Response) and user_response.status_code == 200:
        dashboard["user"] = user_response.json()
    else:
        dashboard["user"] = None

    if isinstance(orders_response, httpx.Response) and orders_response.status_code == 200:
        dashboard["recent_orders"] = orders_response.json()
    else:
        dashboard["recent_orders"] = []

    return dashboard
```

## Gateway with Authentication

Authenticate at the gateway so backend services do not need to:

```python
import jwt
from fastapi import Request, HTTPException


async def verify_auth(request: Request) -> dict | None:
    """Verify JWT token at the gateway."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Routes that require authentication
PROTECTED_PREFIXES = {"orders", "payments"}


@gateway.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_with_auth(service_name: str, path: str, request: Request):
    """Gateway with authentication check."""
    # Check if this service requires authentication
    if service_name in PROTECTED_PREFIXES:
        user = await verify_auth(request)
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication required")

    # Route to service (same as before)
    service_url = SERVICE_REGISTRY.get(service_name)
    if not service_url:
        raise HTTPException(status_code=404, detail="Unknown service")

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{service_url}/{path}",
            content=await request.body(),
            timeout=10.0,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
    )
```

## Testing with ASGITransport

Test the gateway by mounting backend services with ASGITransport:

```python
import httpx
from fastapi import FastAPI

# Backend services
user_service = FastAPI()
product_service = FastAPI()


@user_service.get("/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}


@product_service.get("/{product_id}")
async def get_product(product_id: int):
    return {"id": product_id, "name": "Widget"}


# In tests, replace SERVICE_REGISTRY URLs with ASGITransport
async def test_gateway_routing():
    # Mount services as transports
    user_transport = httpx.ASGITransport(app=user_service)
    product_transport = httpx.ASGITransport(app=product_service)

    # Test calling through gateway logic
    async with httpx.AsyncClient(
        transport=user_transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/1")
        assert response.json()["name"] == "Alice"
```

## Key Takeaways

1. **API gateway provides a single entry point** -- clients talk to one URL, not every service directly
2. **Route based on URL prefix** -- `/users/*` goes to User Service, `/orders/*` to Order Service
3. **Authenticate once at the gateway** -- backend services trust the gateway's auth check
4. **Aggregate responses** to reduce client round trips -- gateway calls multiple services and combines results
5. **Always set timeouts** on forwarded requests -- a slow service should not block the gateway
6. **Use httpx.AsyncClient** for request forwarding -- it handles async I/O efficiently
