# Request Headers

## Why This Matters

When your mobile app makes an API request, it sends metadata in headers: authentication tokens, content type, user agent, etc. You've been setting these headers in URLSession or OkHttp - now you'll read them on the backend to authenticate users, check request formats, and make routing decisions.

## What are Request Headers?

Headers are key-value pairs sent in the HTTP request before the body. They contain metadata about the request:

```
GET /api/users HTTP/1.1
Host: api.example.com
Authorization: Bearer token123
Content-Type: application/json
User-Agent: MyApp/1.0
Accept: application/json
```

## Reading Headers in FastAPI

Use the `Header()` function from `fastapi`:

```python
from fastapi import FastAPI, Header
from typing import Annotated

app = FastAPI()

@app.get("/")
async def read_root(
    user_agent: Annotated[str | None, Header()] = None
):
    """
    Reads the User-Agent header.
    Header name is converted: User-Agent → user_agent
    """
    return {"user_agent": user_agent}
```

**Automatic name conversion:**
- HTTP headers use hyphens: `User-Agent`, `Content-Type`, `X-Request-ID`
- Python variables can't have hyphens
- FastAPI converts automatically: `User-Agent` → `user_agent`

## Common Headers

### Authorization Header

```python
@app.get("/me")
async def get_current_user(
    authorization: Annotated[str | None, Header()] = None
):
    """
    Reads Authorization: Bearer token123
    authorization will be "Bearer token123"
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"error": "Unauthorized"}

    token = authorization.replace("Bearer ", "")
    return {"token": token}
```

Better approach with alias:

```python
@app.get("/me")
async def get_current_user(
    auth_token: Annotated[str, Header(alias="Authorization")]
):
    """
    Use alias to keep variable name clean.
    auth_token reads from Authorization header.
    """
    return {"token": auth_token}
```

### Content-Type Header

```python
@app.post("/data")
async def receive_data(
    content_type: Annotated[str | None, Header()] = None
):
    """
    Reads Content-Type header.
    content_type will be "application/json", "application/xml", etc.
    """
    if content_type != "application/json":
        return {"error": "Only JSON is supported"}

    return {"content_type": content_type}
```

### Accept Header

```python
@app.get("/data")
async def send_data(
    accept: Annotated[str | None, Header()] = None
):
    """
    Reads Accept header to determine response format.
    accept might be "application/json", "application/xml", "*/*"
    """
    if accept == "application/xml":
        return {"format": "XML would be sent here"}

    return {"format": "json"}
```

### User-Agent Header

```python
@app.get("/stats")
async def track_request(
    user_agent: Annotated[str | None, Header()] = None
):
    """
    Reads User-Agent to track which clients are using the API.
    user_agent might be "MyApp/1.0 (iOS 17.0)", "Mozilla/5.0..."
    """
    return {
        "user_agent": user_agent,
        "platform": "iOS" if "iOS" in (user_agent or "") else "other"
    }
```

## Custom Headers

APIs often use custom headers prefixed with `X-`:

```python
@app.get("/data")
async def get_data(
    x_request_id: Annotated[str | None, Header()] = None,
    x_api_version: Annotated[str | None, Header()] = None,
    x_client_platform: Annotated[str | None, Header()] = None
):
    """
    Custom headers for request tracking, API versioning, and analytics.

    Request headers:
    X-Request-ID: abc-123
    X-API-Version: 2.0
    X-Client-Platform: ios
    """
    return {
        "request_id": x_request_id,
        "api_version": x_api_version,
        "platform": x_client_platform
    }
```

## Required vs Optional Headers

```python
# Required header (no default value)
@app.get("/secure")
async def secure_endpoint(
    authorization: Annotated[str, Header()]
):
    """
    authorization is REQUIRED.
    Missing header → 422 Unprocessable Entity
    """
    return {"authorized": True}

# Optional header with default
@app.get("/track")
async def track(
    x_request_id: Annotated[str, Header()] = "auto-generated-id"
):
    """
    x_request_id is OPTIONAL.
    If not provided, uses default value.
    """
    return {"request_id": x_request_id}

# Optional nullable header
@app.get("/info")
async def info(
    x_debug: Annotated[str | None, Header()] = None
):
    """
    x_debug is OPTIONAL and nullable.
    If not provided, is None.
    """
    return {"debug_mode": x_debug is not None}
```

## Header Validation

Add validation constraints to headers:

```python
from fastapi import Header
from typing import Annotated

@app.get("/data")
async def get_data(
    x_api_key: Annotated[
        str,
        Header(
            min_length=32,
            max_length=64,
            description="API key for authentication"
        )
    ]
):
    """
    x_api_key must be between 32-64 characters.
    Invalid length → 422 with error details
    """
    return {"authenticated": True}
```

## Multiple Header Values

Some headers can have multiple values:

```python
@app.get("/data")
async def get_data(
    accept_language: Annotated[list[str] | None, Header()] = None
):
    """
    Request might have:
    Accept-Language: en-US
    Accept-Language: fr-FR

    accept_language will be ["en-US", "fr-FR"]
    """
    return {"languages": accept_language}
```

## Case Sensitivity

HTTP headers are case-insensitive:
- `Authorization`, `authorization`, `AUTHORIZATION` are all the same
- FastAPI converts to lowercase with underscores

```python
@app.get("/test")
async def test(
    x_custom_header: Annotated[str | None, Header()] = None
):
    """
    All these request headers map to x_custom_header:
    - X-Custom-Header
    - x-custom-header
    - X-CUSTOM-HEADER
    """
    return {"header": x_custom_header}
```

## Header Defaults and Conversion

```python
@app.get("/settings")
async def get_settings(
    x_enable_cache: Annotated[bool, Header()] = True,
    x_max_age: Annotated[int, Header()] = 300
):
    """
    Headers are automatically converted based on type hints:
    X-Enable-Cache: true → x_enable_cache: bool = True
    X-Max-Age: 300 → x_max_age: int = 300
    """
    return {
        "cache_enabled": x_enable_cache,
        "cache_max_age": x_max_age
    }
```

## Mobile Developer Context

| Mobile Code | FastAPI Headers |
|-------------|-----------------|
| `request.setValue("Bearer token", forHTTPHeaderField: "Authorization")` | `authorization: Annotated[str, Header()]` |
| `request.addValue("application/json", forHTTPHeaderField: "Content-Type")` | `content_type: Annotated[str, Header()]` |
| Read response headers | Set response headers (covered in next module) |
| Retrofit `@Header` annotation | FastAPI `Header()` function |

## Security Note

**Never log or expose sensitive headers:**
- Authorization tokens
- API keys
- Session cookies
- Authentication credentials

```python
# BAD - Don't do this
@app.get("/debug")
async def debug(
    authorization: Annotated[str | None, Header()] = None
):
    return {"auth_header": authorization}  # ❌ Exposes token

# GOOD - Validate without exposing
@app.get("/secure")
async def secure(
    authorization: Annotated[str | None, Header()] = None
):
    if not authorization:
        return {"error": "Unauthorized"}

    # Validate token (don't return it)
    is_valid = validate_token(authorization)
    return {"authenticated": is_valid}  # ✅ Safe
```

## Key Takeaways

1. **Use `Header()` to read request headers** - automatic name conversion (hyphen → underscore)
2. **Headers are case-insensitive** - `Authorization` = `authorization`
3. **Common headers:** `authorization`, `content_type`, `user_agent`, `accept`
4. **Custom headers often start with `X-`** - `X-Request-ID`, `X-API-Key`
5. **Make headers optional with `| None`** - required headers error without default
6. **Type hints enable automatic conversion** - string → int, bool, etc.
7. **Never log or return sensitive headers** - tokens, API keys, passwords
