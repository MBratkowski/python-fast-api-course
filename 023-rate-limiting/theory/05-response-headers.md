# Rate Limit Response Headers

## Why This Matters

When your iOS app calls an API and gets rate limited, how does it know when to retry? The answer is HTTP headers. Standard rate limit headers tell clients exactly how many requests they have left, when the window resets, and how long to wait after a 429 response.

As a backend developer, you must include these headers so mobile clients can implement smart retry logic instead of blindly hammering your API.

## Standard Rate Limit Headers

There are four headers that well-behaved APIs include on every response (not just 429s):

| Header | Description | Example Value |
|--------|-------------|---------------|
| `X-RateLimit-Limit` | Maximum requests allowed in the window | `100` |
| `X-RateLimit-Remaining` | Requests remaining in current window | `67` |
| `X-RateLimit-Reset` | Unix timestamp when the window resets | `1709001260` |
| `Retry-After` | Seconds to wait (only on 429 responses) | `30` |

```
Normal response (200 OK):

HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 67
X-RateLimit-Reset: 1709001260

{"data": {"id": 1, "name": "Alice"}}

Rate limited response (429):

HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1709001260
Retry-After: 30

{"detail": "Rate limit exceeded. Try again in 30 seconds."}
```

## Adding Headers via FastAPI Middleware

The most effective approach is middleware that adds headers to every response:

```python
import time
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """Add rate limit headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # These values are set by the rate limit check dependency
        if hasattr(request.state, "rate_limit_info"):
            info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset"])

        return response


app = FastAPI()
app.add_middleware(RateLimitHeaderMiddleware)
```

### Setting Rate Limit Info in a Dependency

```python
from fastapi import Depends, HTTPException, Request
import time


async def rate_limit_check(
    request: Request,
    redis_client=Depends(get_redis),
    current_user=Depends(get_current_user_optional),
):
    """Check rate limit and store info for header middleware."""
    key = f"rl:user:{current_user.id}" if current_user else f"rl:ip:{request.client.host}"
    limit = 1000 if current_user else 100

    # Check using sliding window limiter (from previous theory)
    allowed, remaining = await sliding_window_check(
        redis_client, key, limit, window=60
    )

    # Calculate reset time (end of current 60-second window)
    now = time.time()
    reset_at = int(now) + 60 - (int(now) % 60)

    # Store for middleware to add to response headers
    request.state.rate_limit_info = {
        "limit": limit,
        "remaining": remaining,
        "reset": reset_at,
    }

    if not allowed:
        retry_after = reset_at - int(now)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_at),
                "Retry-After": str(retry_after),
            },
        )
```

## Adding Headers via Response Object

For per-endpoint control, add headers directly on the Response:

```python
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/api/items")
async def list_items(
    response: Response,
    rate_info: dict = Depends(get_rate_limit_info),
):
    """Endpoint with rate limit headers set directly."""
    response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])

    return {"items": [{"id": 1}, {"id": 2}]}
```

## 429 Too Many Requests

The HTTP 429 status code signals that the client has sent too many requests. Always include a JSON body explaining the situation:

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def raise_rate_limit_error(
    limit: int,
    reset_at: int,
    retry_after: int,
) -> None:
    """Raise a properly formatted 429 error."""
    raise HTTPException(
        status_code=429,
        detail={
            "error": "rate_limit_exceeded",
            "message": f"Rate limit of {limit} requests exceeded. "
                       f"Try again in {retry_after} seconds.",
            "limit": limit,
            "retry_after": retry_after,
            "reset_at": reset_at,
        },
        headers={
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_at),
            "Retry-After": str(retry_after),
        },
    )
```

### Custom Exception Handler for 429s

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    """Custom 429 handler with consistent JSON format."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": str(exc.detail) if hasattr(exc, "detail") else "Too many requests",
            "type": "rate_limit_exceeded",
        },
        headers=getattr(exc, "headers", {}),
    )
```

## Header Values Explained

### X-RateLimit-Reset: Unix Timestamp

The reset header tells the client exactly when the current window ends:

```python
import time

# For a 60-second fixed window:
now = int(time.time())
window_seconds = 60
reset_at = now + window_seconds - (now % window_seconds)

# For a sliding window (always 60 seconds from now):
reset_at = now + window_seconds

# For token bucket (time until one token refills):
tokens_needed = 1
refill_rate = 1.0  # tokens per second
reset_at = now + int(tokens_needed / refill_rate)
```

### Retry-After: Seconds to Wait

Only sent on 429 responses. Tells the client the minimum wait time:

```python
# Simple: wait until window resets
retry_after = reset_at - int(time.time())

# With jitter (prevents thundering herd):
import random
retry_after = reset_at - int(time.time()) + random.randint(0, 5)
```

## Complete Middleware Example

```python
import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Complete rate limiting middleware with headers."""

    def __init__(self, app, redis_client, default_limit=100, window=60):
        super().__init__(app)
        self.redis = redis_client
        self.default_limit = default_limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        key = f"rl:{request.client.host}"
        now = int(time.time())
        reset_at = now + self.window - (now % self.window)

        # Increment counter
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window)
        results = await pipe.execute()
        current = results[0]

        remaining = max(0, self.default_limit - current)

        if current > self.default_limit:
            from fastapi.responses import JSONResponse
            retry_after = reset_at - now
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={
                    "X-RateLimit-Limit": str(self.default_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(retry_after),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.default_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        return response
```

## Key Takeaways

1. **Include rate limit headers on every response** -- not just 429s -- so clients can proactively manage their request rate
2. **Use standard header names** (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`) for client compatibility
3. **`Retry-After` is only for 429 responses** -- it tells the client the minimum wait time
4. **Use middleware for global headers** and dependencies for per-endpoint customization
5. **Always return a JSON body with 429** -- include the error type, message, and retry information
6. **Add jitter to `Retry-After`** to prevent thundering herd when many clients retry simultaneously
