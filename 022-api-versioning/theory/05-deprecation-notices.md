# Deprecation Notices

## Why This Matters

On iOS, when Apple deprecates an API, you see a compiler warning: "UIWebView was deprecated in iOS 12.0." On Android, `@Deprecated` annotations do the same thing. These warnings give you time to migrate before the API is removed.

Backend APIs need the same mechanism. When you release v2 of your API, v1 doesn't disappear immediately. You deprecate it: you announce that v1 will stop working on a specific date, and you tell consumers where to find v2. HTTP has standardized headers for exactly this purpose.

## The Deprecation Headers

Three headers communicate API deprecation:

### 1. Deprecation Header

Indicates that the endpoint is deprecated:

```
Deprecation: true
```

Or with a date when it was deprecated:

```
Deprecation: Sat, 01 Mar 2026 00:00:00 GMT
```

### 2. Sunset Header (RFC 8594)

Specifies when the endpoint will stop working:

```
Sunset: Sun, 01 Jun 2026 00:00:00 GMT
```

After this date, the endpoint may return 410 Gone or stop responding entirely.

### 3. Link Header

Points to the successor version:

```
Link: </v2/users/42>; rel="successor-version"
```

This tells the client exactly where to find the replacement endpoint.

## FastAPI Implementation

### Basic Deprecation Headers

```python
from fastapi import FastAPI, APIRouter, Response

app = FastAPI()

v1_router = APIRouter(prefix="/v1", tags=["v1 (deprecated)"])
v2_router = APIRouter(prefix="/v2", tags=["v2"])


@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int, response: Response):
    """Get user (DEPRECATED -- use v2 instead)."""

    # Add deprecation headers
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sun, 01 Jun 2026 00:00:00 GMT"
    response.headers["Link"] = f'</v2/users/{user_id}>; rel="successor-version"'

    return {"id": user_id, "name": "Alice"}


@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    """Get user (current version)."""
    return {
        "data": {"id": user_id, "name": "Alice", "email": "alice@example.com"},
        "meta": {"version": "2.0"},
    }


app.include_router(v1_router)
app.include_router(v2_router)
```

**Response from v1:**
```
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sun, 01 Jun 2026 00:00:00 GMT
Link: </v2/users/42>; rel="successor-version"
Content-Type: application/json

{"id": 42, "name": "Alice"}
```

### Deprecation Middleware for Entire Router

Instead of adding headers to each endpoint, use a middleware or dependency:

```python
from fastapi import Depends, Response
from datetime import datetime


def deprecation_headers(sunset_date: str, successor_prefix: str = "/v2"):
    """Create a dependency that adds deprecation headers."""

    async def add_headers(response: Response):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = sunset_date

    return add_headers


# Apply to entire v1 router
v1_router = APIRouter(
    prefix="/v1",
    tags=["v1 (deprecated)"],
    dependencies=[Depends(deprecation_headers(
        sunset_date="Sun, 01 Jun 2026 00:00:00 GMT",
    ))],
)
```

Now every endpoint on `v1_router` automatically includes deprecation headers.

### Per-Endpoint Link Header

The `Link` header needs the specific successor URL, so it's best added per-endpoint:

```python
@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int, response: Response):
    response.headers["Link"] = f'</v2/users/{user_id}>; rel="successor-version"'
    return {"id": user_id, "name": "Alice"}


@v1_router.get("/orders/{order_id}")
async def get_order_v1(order_id: int, response: Response):
    response.headers["Link"] = f'</v2/orders/{order_id}>; rel="successor-version"'
    return {"id": order_id, "total": 99.99}
```

## Logging Deprecated Endpoint Usage

Track which consumers still use deprecated endpoints so you know when it's safe to remove them:

```python
import structlog

logger = structlog.get_logger()


@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int, response: Response):
    # Log deprecated usage for tracking
    logger.warning(
        "deprecated_endpoint_called",
        endpoint="/v1/users/{user_id}",
        successor="/v2/users/{user_id}",
        sunset_date="2026-06-01",
    )

    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sun, 01 Jun 2026 00:00:00 GMT"
    response.headers["Link"] = f'</v2/users/{user_id}>; rel="successor-version"'

    return {"id": user_id, "name": "Alice"}
```

In your log aggregator, you can then query for `deprecated_endpoint_called` events to see:
- How many requests still hit v1
- Which endpoints are most used
- Whether usage is declining over time

## Deprecation Timeline Best Practices

A typical deprecation timeline:

```
Month 0:  Release v2. V1 continues working normally.
          Announce v2 in documentation.

Month 1:  Add Deprecation headers to v1 endpoints.
          Set Sunset date 6 months out.
          Begin logging deprecated usage.

Month 3:  Send reminder to API consumers.
          Review usage logs -- are consumers migrating?

Month 5:  Send final warning.
          Consider returning a deprecation warning in the response body.

Month 6:  Sunset date reached.
          Return 410 Gone on v1 endpoints.
          Or redirect to v2 with 301 Moved Permanently.
```

### After Sunset: Return 410 Gone

```python
from fastapi import HTTPException


@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    raise HTTPException(
        status_code=410,
        detail={
            "message": "API v1 has been sunset. Use v2 instead.",
            "successor": f"/v2/users/{user_id}",
            "documentation": "https://docs.example.com/migration-guide",
        },
    )
```

## Client-Side Handling

Mobile apps should watch for deprecation headers:

```swift
// iOS/Swift
if let deprecation = response.value(forHTTPHeaderField: "Deprecation"),
   deprecation == "true" {
    // Log warning, show migration notice
    logger.warning("API endpoint is deprecated")

    if let sunset = response.value(forHTTPHeaderField: "Sunset") {
        logger.warning("Endpoint will be removed on: \(sunset)")
    }
}
```

```kotlin
// Android/Kotlin
response.header("Deprecation")?.let { deprecation ->
    if (deprecation == "true") {
        Timber.w("API endpoint is deprecated")
        response.header("Sunset")?.let { sunset ->
            Timber.w("Endpoint will be removed on: $sunset")
        }
    }
}
```

This is why deprecation headers matter -- they let clients react programmatically.

## Key Takeaways

1. **Use three headers for deprecation:** `Deprecation: true` to flag it, `Sunset` for the removal date, `Link` for the successor.
2. **The Sunset header is an RFC standard (RFC 8594).** It's not a custom header -- it's an official HTTP specification.
3. **Log deprecated endpoint usage.** Track which consumers still use old endpoints to plan the sunset safely.
4. **Give consumers time.** A 3-6 month deprecation window is standard. Announce early, remind often.
5. **After sunset, return 410 Gone.** Don't just silently drop the endpoint -- tell clients what happened and where to go.
6. **Mobile apps should check for deprecation headers.** Just like compiler warnings for deprecated iOS/Android APIs, HTTP deprecation headers let clients react before it's too late.
