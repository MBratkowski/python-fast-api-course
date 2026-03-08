"""
Exercise 2: Structured Logging with structlog

In this exercise, you'll configure structlog for JSON output and implement
request tracing middleware for FastAPI.

Your tasks:
1. Implement configure_structlog() that sets up structlog with:
   - JSONRenderer for JSON output
   - TimeStamper for ISO timestamps
   - add_log_level processor
   - contextvars support

2. Implement create_tracing_middleware() that returns a FastAPI middleware function:
   - Clears contextvars at the start of each request
   - Generates a UUID4 request ID
   - Binds request_id to structlog context
   - Adds X-Request-ID to the response headers

Mobile analogy: This is like setting up Firebase Analytics with structured events
and adding a session ID to every event automatically.

Prerequisites: pip install structlog

Run: pytest 021-logging-monitoring/exercises/02_structured_logs.py -v
"""

import json
import logging
from uuid import uuid4

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


# ============= TODO 1: Configure structlog =============
# Set up structlog with:
# - merge_contextvars processor (for request-scoped data)
# - add_log_level processor
# - TimeStamper with fmt="iso"
# - JSONRenderer as the final processor
#
# Use structlog.make_filtering_bound_logger(logging.INFO) as wrapper_class
# Use structlog.PrintLoggerFactory() as logger_factory
#
# Hints:
# - structlog.configure() accepts processors as a list
# - Processors run in order; JSONRenderer must be last
# - merge_contextvars enables bind_contextvars() to work


def configure_structlog() -> None:
    """Configure structlog with JSON output and contextvars support."""
    # TODO: Implement this function
    pass


# ============= TODO 2: Create tracing middleware =============
# Return a middleware function that:
# 1. Calls clear_contextvars() to reset context
# 2. Generates a request_id using str(uuid4())
# 3. Calls bind_contextvars(request_id=request_id)
# 4. Calls next (response = await call_next(request))
# 5. Adds X-Request-ID header to the response
# 6. Returns the response
#
# Hints:
# - The middleware function signature is:
#   async def middleware(request: Request, call_next)
# - Use response.headers["X-Request-ID"] = request_id
# - Return the response at the end


def create_tracing_middleware():
    """Create a FastAPI middleware function for request tracing.

    Returns:
        An async middleware function compatible with app.middleware("http")
    """
    # TODO: Implement this function
    # Return an async function with signature:
    #   async def middleware(request: Request, call_next):
    pass


# ============= TESTS (do not modify below) =============


def _make_app() -> FastAPI:
    """Create a test FastAPI app with tracing middleware."""
    configure_structlog()

    app = FastAPI()

    middleware_fn = create_tracing_middleware()
    if middleware_fn is not None:
        app.middleware("http")(middleware_fn)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "hello"}

    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        logger = structlog.get_logger()
        logger.info("fetching_user", user_id=user_id)
        return {"id": user_id, "name": "Alice"}

    return app


class TestStructlogConfig:
    """Tests for structlog configuration."""

    def test_configure_runs_without_error(self):
        """configure_structlog should not raise any exceptions."""
        configure_structlog()

    def test_json_output(self):
        """Logs should be valid JSON after configuration."""
        configure_structlog()

        with structlog.testing.capture_logs() as captured:
            logger = structlog.get_logger()
            logger.info("test_event", key="value")

        assert len(captured) >= 1, (
            "No logs captured. Make sure configure_structlog() "
            "sets up structlog correctly."
        )
        event = captured[0]
        assert event["event"] == "test_event", (
            f"Expected event 'test_event', got {event.get('event')}"
        )
        assert event.get("key") == "value", (
            "Structured key-value pairs should be preserved in the log event."
        )

    def test_log_level_present(self):
        """Log entries should include the log level."""
        configure_structlog()

        with structlog.testing.capture_logs() as captured:
            logger = structlog.get_logger()
            logger.info("level_test")

        assert len(captured) >= 1, "No logs captured."
        event = captured[0]
        assert "log_level" in event, (
            "Log entries should include 'log_level'. "
            "Add structlog.processors.add_log_level to your processor chain."
        )
        assert event["log_level"] == "info", (
            f"Expected log_level 'info', got '{event.get('log_level')}'"
        )


class TestTracingMiddleware:
    """Tests for request tracing middleware."""

    def test_middleware_not_none(self):
        """create_tracing_middleware should return a callable."""
        middleware = create_tracing_middleware()
        assert middleware is not None, (
            "create_tracing_middleware should return a middleware function, not None."
        )
        assert callable(middleware), (
            "create_tracing_middleware should return a callable function."
        )

    def test_request_id_in_response_header(self):
        """Response should include X-Request-ID header."""
        app = _make_app()
        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert "x-request-id" in response.headers, (
            "Response should include X-Request-ID header. "
            "Set response.headers['X-Request-ID'] = request_id in your middleware."
        )

    def test_request_id_is_uuid_format(self):
        """X-Request-ID should be a valid UUID format."""
        app = _make_app()
        client = TestClient(app)
        response = client.get("/test")

        request_id = response.headers.get("x-request-id", "")
        # UUID4 format: 8-4-4-4-12 hex characters
        parts = request_id.split("-")
        assert len(parts) == 5, (
            f"X-Request-ID should be UUID format (8-4-4-4-12). Got: {request_id!r}"
        )

    def test_unique_request_ids(self):
        """Each request should get a unique request ID."""
        app = _make_app()
        client = TestClient(app)

        ids = set()
        for _ in range(5):
            response = client.get("/test")
            request_id = response.headers.get("x-request-id", "")
            ids.add(request_id)

        assert len(ids) == 5, (
            f"Each request should get a unique ID. Got {len(ids)} unique IDs for 5 requests."
        )

    def test_endpoint_still_works(self):
        """Middleware should not break the endpoint response."""
        app = _make_app()
        client = TestClient(app)
        response = client.get("/users/42")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 42
        assert data["name"] == "Alice"
