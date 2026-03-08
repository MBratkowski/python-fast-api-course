# Project: Comprehensive Logging and Monitoring

## Overview

Add full observability to a FastAPI application using structured logging, request tracing, and health check endpoints. By the end, every request will be traceable through your logs, and your application will report its health status to infrastructure tooling.

This project ties together everything from Module 021 -- Python logging, structlog, request tracing middleware, and health checks.

## Requirements

### 1. Structured Logging Configuration
- [ ] Configure structlog with JSON output (`JSONRenderer`)
- [ ] Include `add_log_level`, `TimeStamper(fmt="iso")`, and `merge_contextvars` processors
- [ ] Use `ConsoleRenderer` in development mode, `JSONRenderer` in production mode
- [ ] Switch based on an environment variable (e.g., `ENVIRONMENT=production`)

### 2. Request Tracing Middleware
- [ ] Assign a UUID4 request ID to every incoming request
- [ ] Accept client-provided `X-Request-ID` header (use it if present, generate if not)
- [ ] Bind `request_id`, `method`, and `path` to structlog context
- [ ] Return `X-Request-ID` in the response headers
- [ ] Log `request_started` and `request_completed` events with status code and duration

### 3. Structured Log Events
- [ ] Log a structured event for user login: `event="user_login"`, `user_id`, `ip_address`
- [ ] Log a structured event for resource creation: `event="resource_created"`, `resource_type`, `resource_id`
- [ ] Log a structured event for errors: `event="operation_failed"`, `operation`, `error`, `exc_info`
- [ ] All events should automatically include `request_id` from the tracing middleware

### 4. Health Check Endpoints
- [ ] `GET /health/live` returns `{"status": "alive"}` with HTTP 200
- [ ] `GET /health/ready` checks database and cache connectivity
- [ ] Return HTTP 200 with `{"status": "ready", "checks": {...}}` when all healthy
- [ ] Return HTTP 503 with `{"status": "not_ready", "checks": {...}}` when any unhealthy
- [ ] Include timeout on dependency checks (3 second max)

### 5. Tests
- [ ] Test that logs are valid JSON in production mode
- [ ] Test that request ID appears in response headers
- [ ] Test that each request gets a unique request ID
- [ ] Test liveness endpoint returns 200
- [ ] Test readiness endpoint returns 200 when healthy, 503 when unhealthy

## Starter Template

Create the following file structure:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app with middleware
│   ├── logging_config.py # structlog configuration
│   ├── middleware.py      # Request tracing middleware
│   ├── health.py          # Health check endpoints
│   └── routes.py          # Sample routes with structured logging
└── tests/
    ├── __init__.py
    ├── test_logging.py    # Logging output tests
    ├── test_tracing.py    # Request ID tests
    └── test_health.py     # Health endpoint tests
```

### main.py

```python
import os
from fastapi import FastAPI
from app.logging_config import configure_logging
from app.middleware import add_tracing_middleware
from app.health import router as health_router
from app.routes import router as api_router


def create_app() -> FastAPI:
    # Configure logging based on environment
    env = os.getenv("ENVIRONMENT", "development")
    configure_logging(json_output=(env == "production"))

    app = FastAPI(title="Observability Demo")

    # Add request tracing
    add_tracing_middleware(app)

    # Include routers
    app.include_router(health_router)
    app.include_router(api_router)

    return app


app = create_app()
```

## Success Criteria

When complete, you should be able to:

1. Start the app and see structured log output for every request
2. Filter logs by `request_id` to trace a single request
3. Hit `/health/live` and get a 200 response
4. Hit `/health/ready` and see dependency check results
5. Run `pytest` and have all tests pass
6. Switch between development (colorful console) and production (JSON) log output

## Stretch Goals

- Add Sentry integration (requires a free Sentry account and DSN)
- Add `prometheus-fastapi-instrumentator` for automatic metrics collection
- Add a custom processor that filters out sensitive fields (password, token)
- Track request duration in the tracing middleware and log it with `request_completed`
