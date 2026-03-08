# Structured Logging

## Why This Matters

On mobile, when you send analytics events to Firebase Analytics or Amplitude, you don't send raw strings. You send structured events: `event_name: "purchase_completed"`, `parameters: { "item_id": 42, "price": 9.99, "currency": "USD" }`. Each event is a dictionary of typed key-value pairs that the analytics platform can query, filter, and aggregate.

Backend logging should work the same way. Instead of:

```
2026-03-08 12:00:00 INFO User 42 logged in from 192.168.1.1
```

You want:

```json
{"event": "user_login", "user_id": 42, "ip": "192.168.1.1", "level": "info", "timestamp": "2026-03-08T12:00:00Z"}
```

The first format is for humans reading a terminal. The second format is for machines that ingest, index, and query millions of log lines. In production, machines read your logs far more than humans do.

## The Problem with Unstructured Logs

```python
import logging

logger = logging.getLogger(__name__)

# Unstructured -- good luck parsing this at scale
logger.info(f"User {user_id} logged in from {ip_address} using {browser}")
logger.info(f"Order {order_id} created for user {user_id}, total: ${total}")
logger.error(f"Payment failed for order {order_id}: {error_message}")
```

These messages are readable in a terminal, but try to answer these questions across 10 million log lines:

- How many logins happened in the last hour?
- Which users had payment failures?
- What's the average order total?

You'd need regex or string parsing -- fragile and slow.

## structlog: Structured Logging for Python

`structlog` is the standard library for structured logging in Python. It produces JSON output that log aggregators (Datadog, ELK Stack, CloudWatch) can query directly.

### Installation

```bash
pip install structlog>=25.5.0
```

### Basic Configuration

```python
import logging
import structlog


def configure_structlog() -> None:
    """Configure structlog with JSON output."""
    structlog.configure(
        processors=[
            # Merge context variables (from contextvars)
            structlog.contextvars.merge_contextvars,
            # Add the log level to the event dict
            structlog.processors.add_log_level,
            # Add ISO timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Render stack info if present
            structlog.processors.StackInfoRenderer(),
            # Format exception info
            structlog.processors.format_exc_info,
            # Render everything as JSON
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### Usage

```python
import structlog

logger = structlog.get_logger()

# Structured log -- each keyword becomes a JSON field
logger.info("user_login", user_id=42, ip="192.168.1.1")
# Output: {"event": "user_login", "user_id": 42, "ip": "192.168.1.1", "level": "info", "timestamp": "2026-03-08T12:00:00Z"}

logger.warning("rate_limit_exceeded", user_id=42, endpoint="/api/users", limit=100)
# Output: {"event": "rate_limit_exceeded", "user_id": 42, "endpoint": "/api/users", "limit": 100, "level": "warning", "timestamp": "..."}

logger.error("payment_failed", order_id=789, error="Card declined", amount=99.99)
# Output: {"event": "payment_failed", "order_id": 789, "error": "Card declined", "amount": 99.99, "level": "error", "timestamp": "..."}
```

**Mobile analogy:** This is exactly like Firebase Analytics events. Each log call is like `Analytics.logEvent("user_login", parameters: ["user_id": 42])`.

## Understanding Processor Chains

Processors are functions that transform the log event dictionary before it's rendered. They form a pipeline:

```
Log call
  |
  v
merge_contextvars    --> adds request_id, user_id from context
  |
  v
add_log_level        --> adds "level": "info"
  |
  v
TimeStamper          --> adds "timestamp": "2026-03-08T12:00:00Z"
  |
  v
StackInfoRenderer    --> adds stack trace if requested
  |
  v
format_exc_info      --> formats exception info if present
  |
  v
JSONRenderer         --> converts dict to JSON string
  |
  v
Output: {"event": "...", "level": "...", "timestamp": "...", ...}
```

Each processor receives the event dictionary, modifies it, and passes it to the next processor. The last processor (`JSONRenderer`) converts the dictionary to the final output string.

### Writing a Custom Processor

```python
def add_app_version(logger, method_name, event_dict):
    """Add application version to every log entry."""
    event_dict["app_version"] = "2.1.0"
    return event_dict


# Add to processor chain (before JSONRenderer)
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_app_version,  # Custom processor
        structlog.processors.JSONRenderer(),
    ],
    # ... rest of config
)
```

## Context Variables (contextvars)

The most powerful structlog feature is `contextvars` integration. You can bind data to the current execution context, and it automatically appears in every log call within that context.

```python
from structlog.contextvars import bind_contextvars, clear_contextvars

# At the start of a request:
clear_contextvars()
bind_contextvars(request_id="abc-123", user_id=42)

# Later, anywhere in your code during that request:
logger.info("processing_order", order_id=789)
# Output includes request_id and user_id automatically:
# {"event": "processing_order", "order_id": 789, "request_id": "abc-123", "user_id": 42, "level": "info", ...}
```

This is how request tracing works -- you bind a unique request ID at the start of the request, and every log entry within that request includes it. We'll cover this in detail in the next topic.

**Mobile analogy:** This is similar to setting user properties in Firebase Analytics. Once you set `Analytics.setUserId("42")`, every subsequent event includes that user ID automatically.

## Integrating structlog with stdlib logging

If your application uses libraries that log via Python's standard `logging` module, you can route those logs through structlog:

```python
import logging
import structlog


def configure_structlog_with_stdlib() -> None:
    """Configure structlog to also capture stdlib logging output."""

    # Configure structlog's own output
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

    # Route stdlib logging through structlog's formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
```

Now both `structlog.get_logger()` and `logging.getLogger()` produce the same JSON format.

## Development vs Production Output

In development, JSON is hard to read. Use `ConsoleRenderer` for colorful, human-readable output:

```python
import sys
import structlog


def configure_structlog(json_output: bool = True) -> None:
    """Configure structlog with environment-appropriate output."""

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_output:
        # Production: JSON for machine parsing
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: colorful console output
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Usage:
# configure_structlog(json_output=os.getenv("ENVIRONMENT") == "production")
```

## Key Takeaways

1. **Structured logs are dictionaries, not strings.** Every field is a key-value pair that log aggregators can query and filter.
2. **structlog is the standard.** It produces JSON output, supports processor chains for extensibility, and integrates with Python's stdlib `logging`.
3. **Processors form a pipeline.** Each processor transforms the event dictionary. Put custom processors before `JSONRenderer`.
4. **contextvars provides request-scoped data.** Bind data once at request start, and it appears in every log call during that request.
5. **Use `ConsoleRenderer` in development, `JSONRenderer` in production.** Same processors, different final renderer based on environment.
6. **Don't reinvent structured logging.** Just like you use Firebase Analytics instead of building your own analytics SDK, use structlog instead of formatting JSON strings manually.
