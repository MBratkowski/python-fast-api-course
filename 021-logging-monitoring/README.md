# Module 021: Logging and Monitoring

## Why This Module?

On iOS, you use `os.Logger` or `OSLog` to write structured log messages that show up in Console.app. On Android, `Logcat` and `Timber` give you tagged, leveled logging out of the box. Both platforms give you crash reporting through Crashlytics or Sentry. You already understand why logging matters -- you've debugged production crashes by reading logs and stack traces.

Backend logging is the same concept with higher stakes. Your FastAPI server handles thousands of concurrent requests. When something goes wrong, you can't attach a debugger -- you need logs. But not just any logs. You need structured, machine-parseable logs with request tracing so you can follow a single request through your entire system.

This module teaches you how to build a production logging and monitoring setup for FastAPI.

## What You'll Learn

- Python's built-in logging module: loggers, handlers, formatters, and log levels
- Structured logging with structlog for JSON output that machines can parse
- Request tracing middleware that assigns a unique ID to every request
- Error tracking concepts with Sentry (theory only -- no DSN required)
- Application metrics with Prometheus (theory only -- no infrastructure required)
- Health check endpoints with liveness and readiness probes

## Mobile Developer Context

You already know logging. This module translates your mobile logging knowledge to the backend.

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Logging framework | `os.Logger` / `OSLog` | `Logcat` / `Timber` | `logging` / `structlog` |
| Structured logging | `os_log` with format strings | Timber custom tree + JSON | structlog `JSONRenderer` |
| Request tracing | URLSession task identifiers | OkHttp Interceptor | Middleware + `X-Request-ID` |
| Crash reporting | Crashlytics / Sentry | Crashlytics / Sentry | Sentry SDK |
| Performance metrics | Firebase Performance | Firebase Performance | Prometheus + `/metrics` |

**Key Difference from Mobile:**
- On mobile, the OS collects crash logs and analytics automatically. On the backend, you configure everything yourself -- log format, destinations, retention, and alerting.

## Prerequisites

- [ ] Python basics and virtual environments (Module 001)
- [ ] FastAPI fundamentals: routes, middleware, dependencies (Modules 003-005)
- [ ] Understanding of HTTP headers (Module 002)

## Installation

```bash
# structlog is the only new dependency for this module
pip install structlog>=25.5.0
```

## Topics

### Theory
1. **Python Logging** -- stdlib `logging` module: loggers, handlers, formatters, log levels
2. **Structured Logging** -- structlog with JSON output, processor chains, contextvars
3. **Request Tracing** -- Middleware that assigns UUID to every request for log correlation
4. **Error Tracking with Sentry** -- Error aggregation, stack traces, breadcrumbs (theory only)
5. **Prometheus Metrics** -- Metric types, auto-instrumentation, `/metrics` endpoint (theory only)
6. **Health Checks** -- Liveness and readiness probes for Kubernetes-style deployments

### Exercises
1. **Logging Configuration** -- Configure stdlib logging with handlers and formatters
2. **Structured Logs** -- Set up structlog with JSON output and request tracing
3. **Health Endpoint** -- Build `/health/live` and `/health/ready` endpoints

### Project
Build comprehensive logging and monitoring for a FastAPI application.

## Time Estimate

- Theory: ~90 minutes
- Exercises: ~45 minutes
- Project: ~90 minutes

## Example

```python
import logging
import structlog
from uuid import uuid4
from fastapi import FastAPI, Request

# Configure structured logging with JSON output
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()
logger.info("user_created", user_id=42, email="alice@example.com")
# Output: {"user_id": 42, "email": "alice@example.com", "event": "user_created", "level": "info", "timestamp": "2026-03-08T12:00:00Z"}
```
