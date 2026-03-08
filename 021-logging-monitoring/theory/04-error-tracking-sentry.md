# Error Tracking with Sentry

## Why This Matters

On both iOS and Android, Crashlytics is the standard for crash reporting. You add the SDK, and every unhandled exception is captured, grouped, and reported with a stack trace, device info, and breadcrumbs. You don't write any error-handling code -- the SDK intercepts crashes automatically.

Sentry does the same thing for backend applications. It captures exceptions, groups them by root cause, tracks which deploy introduced them, and sends alerts when error rates spike. If Crashlytics is your mobile crash reporter, Sentry is your backend crash reporter.

**Note:** This topic is theory only. Sentry requires a DSN (Data Source Name) from a Sentry account, so exercises focus on structlog and health checks instead. Understanding what Sentry does will help you set it up when you deploy your first production API.

## What Sentry Does

Sentry is an error tracking platform that:

1. **Captures unhandled exceptions** -- every crash is logged with a full stack trace
2. **Groups similar errors** -- "NullPointerException in auth.py line 42" isn't 1,000 separate issues, it's one issue that happened 1,000 times
3. **Tracks breadcrumbs** -- the sequence of events leading up to the error (HTTP requests, database queries, log messages)
4. **Monitors performance** -- tracks transaction durations and identifies slow endpoints
5. **Sends alerts** -- notifies your team via Slack, email, or PagerDuty when new errors appear or error rates spike

**Mobile analogy:**

| Feature | Crashlytics | Sentry (Backend) |
|---------|-------------|-------------------|
| Crash capture | Automatic for unhandled exceptions | Automatic for unhandled exceptions |
| Grouping | By stack trace | By stack trace + fingerprint |
| Breadcrumbs | User actions, network calls | HTTP requests, DB queries, log entries |
| User context | Firebase user ID | Custom user ID from auth |
| Releases | App version tracking | Deploy version tracking |
| Alerts | Firebase alerts | Slack, email, PagerDuty |

## FastAPI Integration

### Installation

```bash
pip install sentry-sdk[fastapi]
```

### Basic Setup

```python
import sentry_sdk
from fastapi import FastAPI

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",  # Your Sentry DSN
    traces_sample_rate=0.1,   # Sample 10% of transactions for performance monitoring
    profiles_sample_rate=0.1, # Sample 10% for profiling
    environment="production", # Separate dev/staging/production errors
    release="myapp@1.2.0",   # Track which release introduced errors
)

app = FastAPI()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # If this raises an exception, Sentry captures it automatically
    user = await user_service.get(user_id)
    return user
```

That's it. Any unhandled exception in your FastAPI routes is now captured and sent to Sentry with:
- Full stack trace
- Request URL, method, headers, and body
- Environment variables (filtered for secrets)
- Python version and package versions

### Adding User Context

```python
from fastapi import Request
import sentry_sdk


@app.middleware("http")
async def sentry_user_context(request: Request, call_next):
    """Attach authenticated user info to Sentry events."""
    user = getattr(request.state, "user", None)
    if user:
        sentry_sdk.set_user({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        })
    else:
        sentry_sdk.set_user(None)

    return await call_next(request)
```

**Mobile analogy:** This is like `Crashlytics.setUserId(user.id)` on iOS or `Firebase.crashlytics.setUserId(user.id)` on Android.

### Manual Error Capture

Sometimes you handle an error gracefully but still want to report it:

```python
import sentry_sdk
from fastapi import HTTPException


@app.post("/payments")
async def create_payment(payment: PaymentCreate):
    try:
        result = await payment_gateway.charge(payment)
        return result
    except PaymentDeclinedError as e:
        # Handle gracefully (return 400 to client)
        # But still report to Sentry for tracking
        sentry_sdk.capture_exception(e)
        raise HTTPException(400, detail="Payment declined")
```

### Breadcrumbs

Sentry automatically captures breadcrumbs -- a timeline of events leading up to an error:

```python
import sentry_sdk

# Add custom breadcrumb
sentry_sdk.add_breadcrumb(
    category="payment",
    message=f"Attempting charge for order {order_id}",
    level="info",
    data={"order_id": order_id, "amount": amount},
)
```

The breadcrumb trail shows up in the Sentry error report:

```
10:00:00 - HTTP GET /orders/42             (auto-captured)
10:00:01 - SQL SELECT * FROM orders        (auto-captured)
10:00:01 - Attempting charge for order 42   (custom breadcrumb)
10:00:02 - HTTP POST payment-gateway.com   (auto-captured)
10:00:03 - ERROR: ConnectionTimeout        (the crash)
```

## Performance Monitoring

Sentry also tracks request performance:

```python
sentry_sdk.init(
    dsn="...",
    traces_sample_rate=0.1,  # Sample 10% of requests
)

# Sentry automatically creates transactions for each FastAPI request
# and measures duration of each endpoint
```

The Sentry dashboard shows:
- **P50/P95/P99 response times** per endpoint
- **Slowest transactions** ranked by duration
- **Database query performance** within each transaction
- **Throughput** (requests per minute)

## Configuration Best Practices

```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn="...",

    # Only sample a percentage of transactions for performance
    # 1.0 = 100% (development only), 0.1 = 10% (production)
    traces_sample_rate=0.1,

    # Tag the environment so you can filter
    environment="production",

    # Track which deploy introduced errors
    release="myapp@1.2.0",

    # Don't send PII (emails, usernames) unless explicitly set
    send_default_pii=False,

    # Capture INFO+ log messages as breadcrumbs
    integrations=[
        LoggingIntegration(
            level=logging.INFO,        # Capture as breadcrumbs
            event_level=logging.ERROR,  # Send as events
        ),
    ],

    # Filter out noisy errors
    before_send=filter_events,
)


def filter_events(event, hint):
    """Filter out known noisy errors."""
    if "exc_info" in hint:
        exc_type, exc_value, _ = hint["exc_info"]
        # Don't report 404s to Sentry
        if isinstance(exc_value, HTTPException) and exc_value.status_code == 404:
            return None
    return event
```

## DSN Security

The DSN (Data Source Name) is a URL that tells the SDK where to send events:

```
https://examplePublicKey@o0.ingest.sentry.io/0
```

**Never hardcode the DSN.** Use environment variables:

```python
import os
import sentry_sdk

dsn = os.getenv("SENTRY_DSN")
if dsn:
    sentry_sdk.init(dsn=dsn)
```

In production, set `SENTRY_DSN` in your deployment environment. In development, leave it unset and Sentry simply won't initialize.

## Key Takeaways

1. **Sentry is Crashlytics for the backend.** It captures unhandled exceptions, groups them, and tracks error rates across deploys.
2. **The FastAPI integration is automatic.** Install `sentry-sdk[fastapi]`, call `sentry_sdk.init()`, and every unhandled exception is captured with full context.
3. **Use `set_user()` to attach user context.** This lets you find all errors for a specific user, just like `Crashlytics.setUserId()` on mobile.
4. **Breadcrumbs show the timeline.** They capture the sequence of events leading to an error -- HTTP requests, database queries, and custom events.
5. **Performance monitoring tracks latency.** Sentry measures P50/P95/P99 response times and identifies slow endpoints without separate APM tooling.
6. **Never hardcode the DSN.** Use `SENTRY_DSN` environment variable. When unset, Sentry does nothing -- safe for development.
