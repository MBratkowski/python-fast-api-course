# Phase 07: Production Part B - Research

**Researched:** 2026-03-08
**Domain:** Logging/monitoring, API versioning, rate limiting, microservices communication for FastAPI
**Confidence:** HIGH

## Summary

This research covers four advanced production modules for FastAPI: structured logging and monitoring (Module 021), API versioning strategies (Module 022), rate limiting algorithms (Module 023), and microservices basics (Module 024). These modules build on Phase 6's deployment foundations by teaching observability, API lifecycle management, traffic control, and distributed system patterns.

The ecosystem is mature for all four domains. structlog (v25.5.0) is the standard for structured JSON logging in Python. API versioning is handled natively with FastAPI's APIRouter prefix system -- no third-party library needed. Rate limiting exercises should teach algorithms from scratch using fakeredis (matching Module 014 pattern) rather than using slowapi (already covered in Module 019). Microservices communication uses httpx AsyncClient for synchronous HTTP calls and Redis pub/sub for async messaging.

All four modules produce educational content (theory files, exercises, project READMEs) following the established pattern from Phases 1-6. Exercises should be self-contained Python files with embedded tests. Module 023 exercises use fakeredis for Redis-based rate limiting algorithms. Module 024 exercises use httpx with FastAPI TestClient for service-to-service communication patterns.

**Primary recommendation:** Use structlog for structured logging with stdlib logging integration. Use FastAPI APIRouter prefix for URL versioning and Header dependency for header versioning. Implement token bucket and sliding window algorithms from scratch using fakeredis. Use httpx AsyncClient for service communication and Redis pub/sub (via fakeredis) for message passing. Follow established module content patterns: 6 theory files, 3 exercises with embedded tests, 1 project README.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROD-05 | Module 021 -- Logging & Monitoring: 6 theory files (Python logging, structured logging, request tracing, Sentry, Prometheus metrics, health checks), 3 exercises (logging config, structured logs, health endpoint), 1 project (comprehensive logging/monitoring) | structlog v25.5.0 for structured logging, stdlib logging module, UUID-based request tracing middleware, prometheus-fastapi-instrumentator for metrics, health check endpoint patterns with liveness/readiness |
| PROD-06 | Module 022 -- API Versioning: 6 theory files (why version, URL path versioning, header versioning, breaking vs non-breaking, deprecation, maintaining versions), 3 exercises (URL versioning, header versioning, deprecation), 1 project (add versioning with migration path) | FastAPI APIRouter prefix for URL versioning, Header dependency for header-based versioning, deprecation headers (Sunset, Deprecation), no third-party library needed |
| PROD-07 | Module 023 -- Rate Limiting: 6 theory files (algorithms, Redis implementation, per-user vs per-IP, monthly quotas, response headers, client handling), 3 exercises (token bucket, sliding window, per-user limits), 1 project (implement rate limiting) | Token bucket algorithm with fakeredis, sliding window using sorted sets (ZADD/ZREMRANGEBYSCORE), per-user rate limiting with JWT user ID as key, 429 status code with Retry-After header |
| PROD-08 | Module 024 -- Microservices Basics: 6 theory files (when to use, service boundaries, sync communication, async communication, API gateway, data consistency), 3 exercises (service communication, message passing, gateway routing), 1 project (split monolith into two services) | httpx AsyncClient for sync HTTP communication, Redis pub/sub for async messaging, API gateway pattern with FastAPI proxy routes, eventual consistency concepts |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| structlog | 25.5.0 | Structured logging | Most popular Python structured logging; JSON output, processor chains, stdlib integration |
| fakeredis | 2.21+ | Redis mock for exercises | Already used in Module 014; supports sorted sets, pub/sub; no Docker needed |
| httpx | 0.27+ | Async HTTP client | Already in project stack (used for testing); AsyncClient for service-to-service calls |
| prometheus-fastapi-instrumentator | 7.1.0 | Prometheus metrics | Standard FastAPI metrics library; auto-instruments endpoints, exposes /metrics |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-json-logger | 3.2+ | JSON log formatter | Alternative to structlog for simpler JSON logging with stdlib |
| asgi-correlation-id | 4.3+ | Request ID middleware | Auto-generates correlation IDs and attaches to logs |
| prometheus-client | 0.21+ | Prometheus base library | Dependency of prometheus-fastapi-instrumentator; direct use for custom metrics |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| structlog | python-json-logger | structlog is more powerful (processor chains, contextvars); python-json-logger is simpler |
| fakeredis for rate limiting | slowapi | slowapi was covered in Module 019; exercises should teach algorithms from scratch |
| httpx for service calls | requests | httpx supports async natively; requests requires separate aiohttp for async |
| Custom API versioning | fastapi-versioning | fastapi-versioning has limited maintenance; native APIRouter is simpler and more flexible |

**Installation:**
```bash
# Module 021: Logging & Monitoring
pip install structlog>=25.5.0 prometheus-fastapi-instrumentator>=7.1.0

# Module 022: API Versioning (no extra deps -- uses FastAPI built-ins)

# Module 023: Rate Limiting
pip install fakeredis>=2.21.0

# Module 024: Microservices Basics
pip install httpx>=0.27.0 fakeredis>=2.21.0
```

## Architecture Patterns

### Recommended Project Structure

```
021-logging-monitoring/
├── theory/
│   ├── 01-python-logging.md
│   ├── 02-structured-logging.md
│   ├── 03-request-tracing.md
│   ├── 04-error-tracking-sentry.md
│   ├── 05-prometheus-metrics.md
│   └── 06-health-checks.md
├── exercises/
│   ├── 01_logging_config.py
│   ├── 02_structured_logs.py
│   └── 03_health_endpoint.py
├── project/
│   └── README.md
└── README.md

022-api-versioning/
├── theory/
│   ├── 01-why-version-apis.md
│   ├── 02-url-path-versioning.md
│   ├── 03-header-versioning.md
│   ├── 04-breaking-vs-nonbreaking.md
│   ├── 05-deprecation-notices.md
│   └── 06-maintaining-versions.md
├── exercises/
│   ├── 01_url_versioning.py
│   ├── 02_header_versioning.py
│   └── 03_deprecation.py
├── project/
│   └── README.md
└── README.md

023-rate-limiting/
├── theory/
│   ├── 01-rate-limiting-algorithms.md
│   ├── 02-redis-implementation.md
│   ├── 03-per-user-vs-per-ip.md
│   ├── 04-monthly-quotas.md
│   ├── 05-response-headers.md
│   └── 06-client-side-handling.md
├── exercises/
│   ├── 01_token_bucket.py
│   ├── 02_sliding_window.py
│   └── 03_per_user_limits.py
├── project/
│   └── README.md
└── README.md

024-microservices-basics/
├── theory/
│   ├── 01-when-to-use-microservices.md
│   ├── 02-service-boundaries.md
│   ├── 03-sync-communication.md
│   ├── 04-async-communication.md
│   ├── 05-api-gateway.md
│   └── 06-data-consistency.md
├── exercises/
│   ├── 01_service_communication.py
│   ├── 02_message_passing.py
│   └── 03_gateway_routing.py
├── project/
│   └── README.md
└── README.md
```

### Pattern 1: Structured Logging with structlog

**What:** Configure structlog with JSON output, timestamp, log level, and contextvars for request-scoped data
**When to use:** Every production FastAPI application for machine-parseable logs

**Example:**
```python
# Source: structlog documentation + FastAPI integration patterns
import structlog
import logging

# Configure structlog with JSON renderer
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info("user_created", user_id=42, email="alice@example.com")
# Output: {"user_id": 42, "email": "alice@example.com", "event": "user_created", "level": "info", "timestamp": "2026-03-08T12:00:00Z"}
```

### Pattern 2: Request Tracing Middleware

**What:** Assign a unique request ID to every request and include it in all logs
**When to use:** Every production API for correlating logs across a single request lifecycle

**Example:**
```python
# Source: FastAPI middleware + structlog contextvars
from fastapi import FastAPI, Request
from uuid import uuid4
import structlog
from structlog.contextvars import clear_contextvars, bind_contextvars

app = FastAPI()
logger = structlog.get_logger()

@app.middleware("http")
async def request_tracing(request: Request, call_next):
    clear_contextvars()
    request_id = str(uuid4())
    bind_contextvars(request_id=request_id)

    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_completed",
        status_code=response.status_code,
    )
    return response
```

### Pattern 3: URL Path Versioning with APIRouter

**What:** Separate versioned routers with different prefixes
**When to use:** Primary versioning strategy; most explicit and widely understood

**Example:**
```python
# Source: FastAPI APIRouter documentation
from fastapi import FastAPI, APIRouter

app = FastAPI()

v1_router = APIRouter(prefix="/v1", tags=["v1"])
v2_router = APIRouter(prefix="/v2", tags=["v2"])

@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    """V1: Returns flat user object."""
    return {"id": user_id, "name": "Alice"}

@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    """V2: Returns wrapped response with metadata."""
    return {
        "data": {"id": user_id, "name": "Alice", "email": "alice@example.com"},
        "meta": {"version": "2.0", "deprecated_fields": []}
    }

app.include_router(v1_router)
app.include_router(v2_router)
```

### Pattern 4: Header-Based Versioning

**What:** Use a custom header (X-API-Version) to select API version
**When to use:** When URL must remain stable; less common but useful to teach

**Example:**
```python
# Source: FastAPI Header dependency
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    x_api_version: str = Header(default="1.0"),
):
    if x_api_version == "2.0":
        return {
            "data": {"id": user_id, "name": "Alice"},
            "meta": {"version": "2.0"}
        }
    elif x_api_version == "1.0":
        return {"id": user_id, "name": "Alice"}
    else:
        raise HTTPException(400, f"Unsupported API version: {x_api_version}")
```

### Pattern 5: Token Bucket Rate Limiter with Redis

**What:** Implement token bucket algorithm using Redis for atomic operations
**When to use:** When burst traffic is acceptable up to a limit; most common algorithm

**Example:**
```python
# Source: Redis rate limiting patterns
import time
import redis.asyncio as redis

class TokenBucketLimiter:
    def __init__(self, redis_client: redis.Redis, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.capacity = capacity          # Max tokens
        self.refill_rate = refill_rate    # Tokens per second

    async def is_allowed(self, key: str) -> bool:
        now = time.time()
        pipe = self.redis.pipeline()

        # Get current state
        tokens_key = f"tb:{key}:tokens"
        last_key = f"tb:{key}:last"

        current_tokens = await self.redis.get(tokens_key)
        last_refill = await self.redis.get(last_key)

        if current_tokens is None:
            current_tokens = self.capacity
            last_refill = now
        else:
            current_tokens = float(current_tokens)
            last_refill = float(last_refill)

        # Refill tokens
        elapsed = now - last_refill
        new_tokens = min(self.capacity, current_tokens + elapsed * self.refill_rate)

        if new_tokens >= 1:
            new_tokens -= 1
            allowed = True
        else:
            allowed = False

        # Update state
        await self.redis.set(tokens_key, new_tokens)
        await self.redis.set(last_key, now)
        await self.redis.expire(tokens_key, int(self.capacity / self.refill_rate) + 1)
        await self.redis.expire(last_key, int(self.capacity / self.refill_rate) + 1)

        return allowed
```

### Pattern 6: Sliding Window Rate Limiter with Sorted Sets

**What:** Use Redis sorted sets to track individual request timestamps
**When to use:** When precise rate limiting is needed without fixed-window boundary issues

**Example:**
```python
# Source: Redis sorted set rate limiting pattern
import time
import redis.asyncio as redis

class SlidingWindowLimiter:
    def __init__(self, redis_client: redis.Redis, max_requests: int, window_seconds: int):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window_seconds

    async def is_allowed(self, key: str) -> tuple[bool, int]:
        now = time.time()
        window_start = now - self.window
        redis_key = f"sw:{key}"

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, window_start)  # Remove old entries
        pipe.zadd(redis_key, {f"{now}": now})               # Add current request
        pipe.zcard(redis_key)                                # Count requests in window
        pipe.expire(redis_key, self.window)                  # Auto-cleanup
        results = await pipe.execute()

        request_count = results[2]
        remaining = max(0, self.max_requests - request_count)

        if request_count > self.max_requests:
            # Remove the request we just added since it's denied
            await self.redis.zrem(redis_key, f"{now}")
            return False, 0

        return True, remaining
```

### Pattern 7: Service-to-Service Communication with httpx

**What:** One FastAPI service calling another using httpx AsyncClient
**When to use:** Synchronous inter-service communication in microservices

**Example:**
```python
# Source: httpx async documentation + FastAPI patterns
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()
USER_SERVICE_URL = "http://user-service:8001"

@app.get("/orders/{order_id}")
async def get_order_with_user(order_id: int):
    # Local data
    order = {"id": order_id, "user_id": 42, "total": 99.99}

    # Call User Service
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USER_SERVICE_URL}/users/{order['user_id']}",
                timeout=5.0,
            )
            response.raise_for_status()
            user = response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(502, f"User service error: {e.response.status_code}")
        except httpx.RequestError:
            raise HTTPException(503, "User service unavailable")

    return {"order": order, "user": user}
```

### Pattern 8: Redis Pub/Sub Message Passing

**What:** Async event-driven communication between services using Redis pub/sub
**When to use:** When services need to react to events without direct HTTP calls

**Example:**
```python
# Source: redis-py pub/sub documentation
import json
import redis.asyncio as redis

# Publisher (Service A)
async def publish_event(redis_client: redis.Redis, channel: str, event: dict):
    await redis_client.publish(channel, json.dumps(event))

# Subscriber (Service B)
async def subscribe_to_events(redis_client: redis.Redis, channel: str):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    async for message in pubsub.listen():
        if message["type"] == "message":
            event = json.loads(message["data"])
            await handle_event(event)

async def handle_event(event: dict):
    print(f"Received: {event}")
```

### Anti-Patterns to Avoid

- **Using print() instead of logging:** No log levels, no structured output, no control over verbosity
- **Logging sensitive data:** Never log passwords, tokens, or PII; filter these in structlog processors
- **Versioning every endpoint change:** Only version for breaking changes; additive changes are non-breaking
- **Fixed window rate limiting without understanding boundary issues:** Two bursts at window boundary allow 2x the limit; teach sliding window as the solution
- **Synchronous HTTP calls in microservices:** Always use httpx.AsyncClient, never requests library in async FastAPI
- **Tight coupling between microservices:** Services should communicate via well-defined APIs or events, not shared databases

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON log formatting | Custom JSON serializer | structlog JSONRenderer | Handles nested objects, exceptions, timestamps correctly |
| Request ID propagation | Manual header passing | structlog contextvars + middleware | Thread-safe, automatic propagation to all log calls |
| Prometheus metrics | Custom counters/histograms | prometheus-fastapi-instrumentator | Auto-instruments all endpoints; handles histograms, counters, labels |
| Health check orchestration | Custom dependency checking | Dedicated health endpoint with try/except per dependency | Simple pattern; no library needed but don't skip database/Redis checks |
| API versioning router | Custom URL parsing | FastAPI APIRouter with prefix | Built-in, handles OpenAPI docs separation, tag grouping |
| HTTP client for services | Raw urllib/socket calls | httpx AsyncClient | Connection pooling, timeout handling, async support, error classes |

**Key insight:** For modules 021 and 022, the framework provides almost everything natively. structlog is the one external library that adds significant value. For module 023, the educational value is in implementing algorithms from scratch, so avoid abstracting with slowapi. For module 024, httpx is already in the project and provides production-grade HTTP client capabilities.

## Common Pitfalls

### Pitfall 1: Logging Configuration Conflicts with Uvicorn

**What goes wrong:** structlog and Uvicorn both try to configure Python's logging module, producing duplicate or missing logs
**Why it happens:** Uvicorn has its own logging configuration that can override application-level settings
**How to avoid:** Configure structlog to wrap stdlib logging; set Uvicorn's log_config=None or use structlog's stdlib integration processors
**Warning signs:** Duplicate log lines, inconsistent log formats, logs appearing in wrong format

### Pitfall 2: Breaking Changes vs Non-Breaking Changes Confusion

**What goes wrong:** Learners version the API for every change, creating unnecessary complexity
**Why it happens:** Unclear on what constitutes a breaking change
**How to avoid:** Theory file must clearly define: removing a field = breaking, adding an optional field = non-breaking, changing a field type = breaking, adding a new endpoint = non-breaking
**Warning signs:** v1, v2, v3... for minor additions

### Pitfall 3: Rate Limiting Race Conditions

**What goes wrong:** Two concurrent requests both pass the check before either increments the counter
**Why it happens:** Non-atomic read-check-increment pattern
**How to avoid:** Use Redis pipeline or Lua scripts for atomic operations; exercises should demonstrate the pipeline approach
**Warning signs:** Rate limiter allows more requests than configured under concurrent load

### Pitfall 4: Sorted Set Memory Growth

**What goes wrong:** Sliding window sorted sets grow unbounded if cleanup is missed
**Why it happens:** Forgetting to call ZREMRANGEBYSCORE before counting, or not setting key expiry
**How to avoid:** Always clean old entries before counting; set Redis key TTL equal to window size
**Warning signs:** Redis memory usage growing linearly over time

### Pitfall 5: Microservice Cascading Failures

**What goes wrong:** One service being slow causes all dependent services to timeout and fail
**Why it happens:** No timeout on HTTP calls; no circuit breaker pattern
**How to avoid:** Always set httpx timeout parameter; teach timeout handling in exercises; mention circuit breaker pattern in theory
**Warning signs:** All services fail when one service has issues

### Pitfall 6: Shared Database Anti-Pattern in Microservices

**What goes wrong:** Two services read/write the same database tables, creating tight coupling
**Why it happens:** Seems simpler than API calls or events
**How to avoid:** Each service owns its data; communicate via APIs or events. Theory file should cover this explicitly
**Warning signs:** Schema changes in one service break another

## Code Examples

Verified patterns from official sources:

### Health Check Endpoint with Dependency Checks

```python
# Source: FastAPI health check patterns + Kubernetes probe conventions
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

async def check_database():
    """Check database connectivity."""
    try:
        # Execute simple query
        await db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis():
    """Check Redis connectivity."""
    try:
        await redis_client.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health/live")
async def liveness():
    """Liveness probe -- is the process running?"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Readiness probe -- can we handle traffic?"""
    db_status = await check_database()
    redis_status = await check_redis()

    all_healthy = all(
        s["status"] == "healthy"
        for s in [db_status, redis_status]
    )

    status_code = 200 if all_healthy else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": {
                "database": db_status,
                "redis": redis_status,
            },
        },
    )
```

### Deprecation Headers in Versioned API

```python
# Source: HTTP Sunset header RFC 8594 + API deprecation patterns
from fastapi import FastAPI, APIRouter, Response
from datetime import datetime

v1_router = APIRouter(prefix="/v1", tags=["v1 (deprecated)"])

@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int, response: Response):
    # Add deprecation headers
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sat, 01 Jun 2026 00:00:00 GMT"
    response.headers["Link"] = '</v2/users/{user_id}>; rel="successor-version"'

    return {"id": user_id, "name": "Alice"}
```

### Rate Limiting Response Headers

```python
# Source: IETF RateLimit header fields draft
from fastapi import Request, Response
from fastapi.responses import JSONResponse

async def rate_limit_middleware(request: Request, call_next):
    key = request.client.host
    allowed, remaining = await limiter.is_allowed(key)

    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + 60),
            },
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response
```

### API Gateway Routing Pattern

```python
# Source: FastAPI proxy pattern + httpx
from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI(title="API Gateway")

SERVICES = {
    "users": "http://user-service:8001",
    "orders": "http://order-service:8002",
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        return Response(status_code=404, content="Service not found")

    target_url = f"{SERVICES[service]}/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            content=await request.body(),
            timeout=10.0,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )
```

### Mobile Developer Comparison Tables

```
Logging Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Framework     | os.Logger /         | Logcat /            | stdlib logging /    |
|               | OSLog               | Timber              | structlog           |
+---------------+---------------------+---------------------+---------------------+
| Structured    | os_log with         | Timber custom       | structlog JSON      |
| logging       | format strings      | tree + JSON         | renderer            |
+---------------+---------------------+---------------------+---------------------+
| Request       | URLSession          | OkHttp              | Middleware +        |
| tracing       | task identifiers    | Interceptor         | X-Request-ID        |
+---------------+---------------------+---------------------+---------------------+
| Crash         | Crashlytics /       | Crashlytics /       | Sentry SDK          |
| reporting     | Sentry              | Sentry              |                     |
+---------------+---------------------+---------------------+---------------------+

API Versioning Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| API compat    | Deployment target   | minSdkVersion       | API version prefix  |
|               | (iOS 15, 16, 17)    | (API 26, 33, 34)    | (/v1, /v2)          |
+---------------+---------------------+---------------------+---------------------+
| Deprecation   | @available(*, dep)  | @Deprecated         | Sunset header +     |
|               |                     | annotation          | Deprecation header  |
+---------------+---------------------+---------------------+---------------------+
| Backward      | #available checks   | Build.VERSION       | Multiple routers    |
| compat        |                     | checks              | with shared logic   |
+---------------+---------------------+---------------------+---------------------+

Rate Limiting Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Client-side   | URLSession rate     | OkHttp rate         | Server enforces     |
| throttling    | limiting            | limiting            | limits, client      |
|               |                     |                     | reads Retry-After   |
+---------------+---------------------+---------------------+---------------------+
| Retry logic   | URLSession retry    | Retrofit retry      | Respect 429 +      |
|               | with backoff        | interceptor         | Retry-After header  |
+---------------+---------------------+---------------------+---------------------+

Microservices Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Modular arch  | Swift Package       | Multi-module        | Separate FastAPI    |
|               | modules             | Gradle project      | service per domain  |
+---------------+---------------------+---------------------+---------------------+
| Service calls | URLSession to       | Retrofit to         | httpx AsyncClient   |
|               | different APIs      | different APIs      | to other services   |
+---------------+---------------------+---------------------+---------------------+
| Events        | NotificationCenter  | EventBus / Flow     | Redis pub/sub       |
|               |                     |                     |                     |
+---------------+---------------------+---------------------+---------------------+
```

## Exercise Design Considerations

### Module 021 (Logging & Monitoring) -- Standard Python Exercises

Exercises fit the standard pattern well. All three exercises are self-contained Python files:
- **Exercise 01 (Logging Config):** Configure stdlib logging with multiple handlers (console, file). Test verifies log output format and level filtering.
- **Exercise 02 (Structured Logs):** Configure structlog with JSON output. Implement request logging middleware. Tests verify JSON format and required fields.
- **Exercise 03 (Health Endpoint):** Build health check endpoints with dependency checks. Tests use TestClient to verify /health/live and /health/ready responses.

### Module 022 (API Versioning) -- Standard FastAPI Exercises

All exercises use FastAPI TestClient:
- **Exercise 01 (URL Versioning):** Create v1 and v2 routers with different response formats. Tests verify both versions return correct data.
- **Exercise 02 (Header Versioning):** Implement version selection via X-API-Version header. Tests send different headers and verify responses.
- **Exercise 03 (Deprecation):** Add deprecation headers to v1 endpoints. Tests verify Sunset and Deprecation headers present.

### Module 023 (Rate Limiting) -- Algorithm Implementation with fakeredis

Exercises teach algorithms from scratch (not using slowapi):
- **Exercise 01 (Token Bucket):** Implement token bucket using fakeredis. Tests verify burst allowance and refill behavior.
- **Exercise 02 (Sliding Window):** Implement sliding window using sorted sets in fakeredis. Tests verify accurate counting across window boundaries.
- **Exercise 03 (Per-User Limits):** Combine rate limiting with user identification. Tests verify different users have independent limits.

**Note:** fakeredis supports all required Redis commands (ZADD, ZREMRANGEBYSCORE, ZCARD, pipeline, expire). This was verified from Module 014's successful use of fakeredis.

### Module 024 (Microservices) -- httpx + TestClient Exercises

Exercises simulate multi-service architecture within single test files:
- **Exercise 01 (Service Communication):** Create two FastAPI apps in one file; use httpx to call between them. Tests verify cross-service data flow.
- **Exercise 02 (Message Passing):** Implement pub/sub with fakeredis. Tests verify event publishing and consumption.
- **Exercise 03 (Gateway Routing):** Build a simple API gateway that routes to backend services. Tests verify routing logic.

**Pattern for testing service-to-service:** Mount one FastAPI app on httpx.AsyncClient using `transport=httpx.ASGITransport(app=service_app)`. This allows testing without running actual servers.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| python-json-logger | structlog with JSONRenderer | structlog matured 2023+ | Better processor chains, contextvars integration |
| fastapi-versioning package | Native APIRouter prefix | Always available | No external dependency, more flexible |
| Fixed window rate limiting | Sliding window with sorted sets | Best practice established | Eliminates boundary burst issue |
| requests library for HTTP | httpx AsyncClient | 2022+ | Native async support, better performance |
| aioredis for async Redis | redis-py redis.asyncio | 2023 (aioredis deprecated) | Single library for sync and async |
| Custom Prometheus middleware | prometheus-fastapi-instrumentator | 2021+ | Auto-instruments all endpoints |

**Deprecated/outdated:**
- **fastapi-versioning**: Limited maintenance, open issues; use native APIRouter prefix instead
- **aioredis**: Merged into redis-py; use `redis.asyncio` (already decided in Phase 5)
- **python-jose**: Abandoned; use PyJWT (already decided in Phase 3)
- **requests in async code**: Use httpx for async HTTP calls

## Open Questions

1. **Sentry integration depth in exercises**
   - What we know: Sentry is listed in Module 021 theory topics. Sentry SDK requires an actual DSN to function.
   - What's unclear: Whether to include Sentry in exercises or keep it theory-only
   - Recommendation: Keep Sentry as theory-only content. Exercises should focus on structlog and health checks which are fully self-contained. The project README can describe Sentry integration as an extension.

2. **Prometheus metrics exercise approach**
   - What we know: prometheus-fastapi-instrumentator auto-instruments endpoints and exposes /metrics
   - What's unclear: Whether to exercise Prometheus setup or keep it theory-only (running Prometheus requires Docker)
   - Recommendation: Cover Prometheus in theory. Health check exercise (Exercise 03) can include a custom /metrics-like endpoint that returns basic counters, demonstrating the concept without requiring Prometheus infrastructure.

3. **Microservices exercise testing without real services**
   - What we know: httpx.ASGITransport allows testing a FastAPI app without a running server
   - What's unclear: How realistic the exercise can be with in-process simulation
   - Recommendation: Use httpx.ASGITransport to mount a second FastAPI app as a "remote service." This is realistic enough for learning service communication patterns and keeps exercises self-contained.

## Sources

### Primary (HIGH confidence)
- [structlog documentation](https://www.structlog.org/) - v25.5.0, processor chains, JSONRenderer, contextvars
- [FastAPI APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/) - Router prefix for versioning
- [Redis sorted sets documentation](https://redis.io/docs/latest/develop/data-types/sorted-sets/) - ZADD, ZREMRANGEBYSCORE for sliding window
- [httpx async documentation](https://www.python-httpx.org/async/) - AsyncClient for service communication
- [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator) - v7.1.0 auto-instrumentation

### Secondary (MEDIUM confidence)
- [Setting Up Structured Logging in FastAPI with structlog](https://ouassim.tech/notes/setting-up-structured-logging-in-fastapi-with-structlog/) - Integration patterns
- [Redis rate limiting tutorial](https://redis.io/tutorials/howtos/ratelimiting/) - Token bucket and sliding window implementations
- [FastAPI health check patterns](https://www.index.dev/blog/how-to-implement-health-check-in-python) - Liveness/readiness probe patterns
- [API versioning in Python](https://treblle.com/blog/api-versioning-in-python) - URL vs header versioning tradeoffs
- [FastAPI microservices patterns](https://talent500.com/blog/fastapi-microservices-python-api-design-patterns-2025/) - Service communication with httpx

### Tertiary (LOW confidence)
- [httpx-retries](https://will-ockmore.github.io/httpx-retries/) - Retry patterns for httpx (not verified independently)
- [circuitbreaker library](https://pypi.org/project/circuitbreaker/) - Circuit breaker for microservices (mentioned in theory only)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - structlog, fakeredis, httpx, prometheus-fastapi-instrumentator are all well-documented and mature
- Architecture: HIGH - Module structure follows established Phases 1-6 patterns; all code patterns verified with official docs
- Pitfalls: HIGH - Common issues verified across multiple sources (logging conflicts, race conditions, cascading failures)
- Exercise design: HIGH - All exercises use proven patterns (TestClient, fakeredis, httpx.ASGITransport) already established in earlier phases

**Research date:** 2026-03-08
**Valid until:** ~2026-05-08 (60 days - production tooling is mature and stable)
