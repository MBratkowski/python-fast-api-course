# Request Tracing

## Why This Matters

On iOS, when you make a network request using `URLSession`, each task gets a unique `taskIdentifier`. If something goes wrong, you can find that specific request in your logs by its identifier. On Android, OkHttp interceptors let you tag and log every request-response cycle with a correlation ID.

Backend request tracing is the same idea at a larger scale. Your FastAPI server handles hundreds of requests per second. When a user reports "the app is slow" or "I got an error," you need to find their specific request among thousands of log lines. A request ID makes this possible.

The pattern: assign a unique UUID to every incoming request, attach it to every log message during that request, and return it in a response header so the client can reference it.

## The Problem Without Request IDs

Without request tracing, your logs look like this:

```
INFO  Processing order
INFO  Fetching user from database
ERROR Database timeout
INFO  Processing order
INFO  Sending email notification
INFO  Fetching user from database
```

Which "Processing order" caused the "Database timeout"? You can't tell. Multiple requests interleave their log messages.

With request tracing:

```json
{"event": "processing_order", "request_id": "a1b2c3", "order_id": 42}
{"event": "fetching_user", "request_id": "d4e5f6", "user_id": 7}
{"event": "database_timeout", "request_id": "a1b2c3", "query": "SELECT ..."}
{"event": "processing_order", "request_id": "d4e5f6", "order_id": 99}
{"event": "sending_email", "request_id": "d4e5f6", "to": "alice@example.com"}
{"event": "fetching_user", "request_id": "a1b2c3", "user_id": 42}
```

Now you can filter by `request_id: "a1b2c3"` and see the full lifecycle of that specific request.

## The Complete Implementation

Request tracing in FastAPI requires three things:
1. A middleware that generates a unique ID for each request
2. structlog's `contextvars` to bind the ID so all logs include it
3. A response header (`X-Request-ID`) so clients can reference it

### Step 1: The Middleware

```python
from uuid import uuid4
from fastapi import FastAPI, Request
import structlog
from structlog.contextvars import clear_contextvars, bind_contextvars

app = FastAPI()
logger = structlog.get_logger()


@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    """Assign a unique request ID to every request."""

    # Clear any leftover context from the previous request
    clear_contextvars()

    # Generate a unique request ID (or use one from the client)
    request_id = request.headers.get("X-Request-ID", str(uuid4()))

    # Bind to structlog context -- every log call in this request
    # will automatically include request_id
    bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    logger.info("request_started")

    # Process the request
    response = await call_next(request)

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    logger.info("request_completed", status_code=response.status_code)

    return response
```

### Step 2: Using It in Route Handlers

Once the middleware binds the request ID, every `structlog.get_logger()` call in any code that runs during that request will automatically include the `request_id`:

```python
import structlog

logger = structlog.get_logger()


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    logger.info("fetching_order", order_id=order_id)
    # Output: {"event": "fetching_order", "order_id": 42, "request_id": "a1b2c3", "method": "GET", "path": "/orders/42", ...}

    order = await order_service.get(order_id)

    logger.info("order_found", order_id=order_id, total=order.total)
    # Output: {"event": "order_found", "order_id": 42, "total": 99.99, "request_id": "a1b2c3", ...}

    return order
```

You don't pass `request_id` manually -- `contextvars` handles it automatically. This works across function calls, service layers, and even database queries, as long as they run in the same async context.

### Step 3: Client-Side Usage

The `X-Request-ID` response header lets clients reference specific requests:

```
# Request
GET /orders/42 HTTP/1.1
Host: api.example.com

# Response
HTTP/1.1 200 OK
X-Request-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Content-Type: application/json

{"id": 42, "total": 99.99}
```

**Mobile analogy:** When you get a support ticket saying "the app crashed at 3pm," you look up the crash in Crashlytics by its crash ID. The `X-Request-ID` serves the same purpose -- the mobile app can include it in error reports: "Request a1b2c3 failed."

## Accepting Client-Provided Request IDs

Sometimes the client (your mobile app) wants to set the request ID:

```python
@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    clear_contextvars()

    # Use client-provided ID if present, otherwise generate one
    request_id = request.headers.get("X-Request-ID") or str(uuid4())

    bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response
```

This is useful when the mobile app generates its own correlation ID and sends it with the request. You can then trace a single user action from the mobile app all the way through the backend.

## Adding More Context

You can bind additional context at any point during the request:

```python
from structlog.contextvars import bind_contextvars


async def authenticate(token: str):
    user = await verify_token(token)
    # Add user context to all subsequent logs
    bind_contextvars(user_id=user.id, user_role=user.role)
    return user
```

Now every log entry after authentication includes `user_id` and `user_role`:

```json
{"event": "fetching_order", "request_id": "a1b2c3", "user_id": 42, "user_role": "admin", "order_id": 789}
```

## Request Tracing Across Services

In a microservices architecture, the request ID follows the request across service boundaries:

```
Mobile App                    API Gateway              Order Service              User Service
    |                            |                         |                          |
    |-- GET /orders/42 --------->|                         |                          |
    |   X-Request-ID: abc-123    |                         |                          |
    |                            |-- GET /orders/42 ------>|                          |
    |                            |   X-Request-ID: abc-123 |                          |
    |                            |                         |-- GET /users/7 --------->|
    |                            |                         |   X-Request-ID: abc-123  |
    |                            |                         |<-- 200 ------------------|
    |                            |<-- 200 ----------------|                          |
    |<-- 200 --------------------|                         |                          |
```

Each service forwards the `X-Request-ID` header. You can search for `request_id: "abc-123"` across all services and see the complete request flow.

## Complete Middleware with Timing

A production-ready middleware that also tracks request duration:

```python
import time
from uuid import uuid4
from fastapi import FastAPI, Request
import structlog
from structlog.contextvars import clear_contextvars, bind_contextvars

app = FastAPI()
logger = structlog.get_logger()


@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    """Trace every request with a unique ID and measure duration."""
    clear_contextvars()

    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    start_time = time.perf_counter()

    bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown",
    )

    logger.info("request_started")

    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed")
        raise

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        "request_completed",
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    response.headers["X-Request-ID"] = request_id
    return response
```

## Key Takeaways

1. **Every request needs a unique ID.** Use `uuid4()` to generate one, or accept a client-provided `X-Request-ID` header.
2. **Use structlog contextvars for automatic propagation.** Bind the request ID once in middleware, and it appears in every log entry for that request.
3. **Always call `clear_contextvars()` first.** This prevents data from a previous request leaking into the current one.
4. **Return `X-Request-ID` in the response.** Clients can use it for support tickets, debugging, and end-to-end tracing.
5. **Forward the request ID across services.** In a microservices architecture, the same request ID should flow through every service the request touches.
6. **Add timing to your middleware.** Request duration is one of the most useful metrics for diagnosing performance issues.
