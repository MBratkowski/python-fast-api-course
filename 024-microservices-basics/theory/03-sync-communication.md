# Synchronous Communication

## Why This Matters

On mobile, you make HTTP calls to a single backend. In a microservices architecture, services also make HTTP calls -- to each other. The Order Service needs user details, so it calls the User Service. This is synchronous communication: the caller waits for a response before continuing.

The critical difference from mobile HTTP calls is that you are now calling services on an internal network with different reliability expectations. You must handle timeouts, retries, and service unavailability -- because in microservices, the service you call **will** go down at some point.

## Service-to-Service HTTP Calls with httpx

**Always use httpx.AsyncClient** for async FastAPI services. Never use the `requests` library in async code -- it blocks the event loop.

```python
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Simulated order database
orders_db = {
    1: {"id": 1, "user_id": 42, "total": 99.99, "status": "completed"},
    2: {"id": 2, "user_id": 7, "total": 249.50, "status": "pending"},
}

USER_SERVICE_URL = "http://user-service:8001"


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Get order with enriched user data from User Service."""
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Call User Service to get user details
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USER_SERVICE_URL}/users/{order['user_id']}",
                timeout=5.0,  # ALWAYS set a timeout
            )
            response.raise_for_status()
            user = response.json()
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="User service timed out",
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                user = {"name": "Unknown User"}
            else:
                raise HTTPException(
                    status_code=502,
                    detail="User service error",
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="User service unavailable",
            )

    return {
        "order": order,
        "user": user,
    }
```

## Timeout Handling

**Rule: ALWAYS set a timeout on service-to-service calls.**

Without a timeout, a slow downstream service can consume all your connections:

```
Without timeout:

Request → Order Service → User Service (hanging...)
Request → Order Service → User Service (hanging...)
Request → Order Service → User Service (hanging...)
... all connections consumed, Order Service is now down too!
```

```python
# WRONG: No timeout -- will hang forever if User Service is slow
response = await client.get(f"{url}/users/{user_id}")

# RIGHT: 5-second timeout
response = await client.get(f"{url}/users/{user_id}", timeout=5.0)

# RIGHT: Different timeouts for different operations
timeout = httpx.Timeout(
    connect=2.0,    # Time to establish connection
    read=5.0,       # Time to read response
    write=5.0,      # Time to send request
    pool=10.0,      # Time to wait for connection from pool
)
response = await client.get(f"{url}/users/{user_id}", timeout=timeout)
```

## Error Handling

Three types of errors to handle in service-to-service calls:

```python
import httpx

async def call_service(client: httpx.AsyncClient, url: str) -> dict | None:
    """Make a service call with comprehensive error handling."""
    try:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException:
        # Service is too slow -- timeout exceeded
        # Action: Return default/cached data or raise 504
        print(f"Timeout calling {url}")
        return None

    except httpx.HTTPStatusError as e:
        # Service returned an error status code (4xx, 5xx)
        # Action: Handle based on status code
        print(f"HTTP error {e.response.status_code} from {url}")
        if e.response.status_code == 404:
            return None  # Resource not found -- handle gracefully
        raise  # Re-raise for unexpected errors

    except httpx.RequestError as e:
        # Network error -- service is down, DNS failure, connection refused
        # Action: Return default data or raise 502
        print(f"Request error calling {url}: {e}")
        return None
```

## Retry with Exponential Backoff

For transient failures, retry with increasing delays:

```python
import asyncio
import random
import httpx


async def call_with_retry(
    client: httpx.AsyncClient,
    url: str,
    max_retries: int = 3,
) -> httpx.Response:
    """Call a service with exponential backoff retry."""
    last_exception = None

    for attempt in range(max_retries):
        try:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            return response

        except (httpx.TimeoutException, httpx.RequestError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
                continue

        except httpx.HTTPStatusError as e:
            # Only retry on 5xx (server errors), not 4xx (client errors)
            if e.response.status_code >= 500 and attempt < max_retries - 1:
                last_exception = e
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
                continue
            raise  # Don't retry 4xx errors

    raise last_exception  # All retries exhausted
```

## Circuit Breaker Concept

When a service is consistently failing, stop calling it temporarily to let it recover:

```
Circuit Breaker States:

CLOSED (normal):
  All requests pass through
  Track failure count
  If failures > threshold → OPEN

OPEN (failing):
  All requests fail immediately (no actual call)
  Start timer
  After timeout → HALF-OPEN

HALF-OPEN (testing):
  Allow one request through
  If success → CLOSED
  If failure → OPEN
```

```python
import time
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple circuit breaker for service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0

    def can_execute(self) -> bool:
        """Check if a request should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True  # Allow one test request
            return False

        # HALF_OPEN: allow the test request
        return True

    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

## Using httpx.ASGITransport for Testing

In tests (and exercises), you can call a FastAPI app without running a server:

```python
import httpx
from fastapi import FastAPI

# "Remote" service (in production, this runs on a different server)
user_service = FastAPI()


@user_service.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}


# Call it using ASGITransport (no server needed)
async def test_service_call():
    transport = httpx.ASGITransport(app=user_service)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/users/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Alice"
```

This is the pattern used in all Module 024 exercises. In production, you would replace `ASGITransport` with a real base URL.

## Anti-Pattern: Using requests in Async Code

```python
# WRONG: blocks the async event loop
import requests  # synchronous library

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    # This blocks ALL other requests while waiting for response!
    response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}")
    return response.json()

# RIGHT: use httpx AsyncClient
import httpx

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    # Non-blocking -- other requests can be processed while waiting
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            timeout=5.0,
        )
        return response.json()
```

## Key Takeaways

1. **Use httpx.AsyncClient** for all service-to-service HTTP calls in async FastAPI -- never use `requests`
2. **ALWAYS set a timeout** -- without one, a slow service can bring down your entire system
3. **Handle three error types**: timeout (504), HTTP errors (check status code), network errors (502)
4. **Retry only transient failures** -- retry 5xx and timeouts, never retry 4xx
5. **Circuit breakers** prevent cascading failures by stopping calls to a consistently failing service
6. **Use ASGITransport** in tests to call FastAPI apps without running servers
