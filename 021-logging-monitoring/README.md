# Module 021: Logging & Monitoring

## Why This Module?

When things break in production, logs are your lifeline. Learn structured logging and monitoring.

## What You'll Learn

- Python logging module
- Structured logging (JSON)
- Request tracing
- Error tracking (Sentry)
- Metrics & alerting
- Health checks

## Topics

### Theory
1. Python logging Configuration
2. Structured Logging
3. Request ID Tracing
4. Error Tracking with Sentry
5. Prometheus Metrics
6. Health Check Endpoints

### Project
Add comprehensive logging and monitoring to your API.

## Example

```python
import logging
import structlog
from uuid import uuid4
from fastapi import Request

# Structured logging setup
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())
    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    response = await call_next(request)

    logger.info(
        "request_completed",
        request_id=request_id,
        status_code=response.status_code,
    )
    return response

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": await check_db(),
        "redis": await check_redis(),
    }
```
