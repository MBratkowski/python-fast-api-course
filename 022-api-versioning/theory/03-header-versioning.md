# Header-Based Versioning

## Why This Matters

URL path versioning (`/v1/users`, `/v2/users`) is the most common approach, but it changes the URL for every version. Some teams prefer keeping URLs stable and using a custom HTTP header to select the API version. This is header-based versioning.

**Mobile analogy:** On iOS, `URLRequest` lets you add custom headers to every request. On Android, `OkHttp` interceptors can inject headers automatically. If your mobile app already uses custom headers for feature flags or configuration, header-based versioning feels natural.

Header versioning is less common than URL versioning, but it's important to understand because you'll encounter it in the wild.

## The Pattern

```
# Default: v1 response
GET /users/1 HTTP/1.1
Host: api.example.com

# Explicit v1
GET /users/1 HTTP/1.1
Host: api.example.com
X-API-Version: 1.0

# Request v2
GET /users/1 HTTP/1.1
Host: api.example.com
X-API-Version: 2.0
```

Same URL, different response based on the header value.

## FastAPI Implementation

FastAPI's `Header()` dependency makes this straightforward:

```python
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

USERS_DB = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}


@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    x_api_version: str = Header(default="1.0"),
):
    """Get a user. Version is selected via X-API-Version header."""

    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if x_api_version == "1.0":
        # V1: flat response
        return {"id": user["id"], "name": user["name"]}

    elif x_api_version == "2.0":
        # V2: wrapped response with metadata
        return {
            "data": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            },
            "meta": {"version": "2.0"},
        }

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported API version: {x_api_version}. Supported: 1.0, 2.0",
        )
```

### How FastAPI Handles Header Names

FastAPI automatically converts `X-API-Version` to the Python parameter `x_api_version`:

- HTTP header: `X-API-Version: 2.0`
- Python parameter: `x_api_version: str`
- FastAPI converts hyphens to underscores and lowercases

You can also use the `alias` parameter for clarity:

```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    api_version: str = Header(default="1.0", alias="X-API-Version"),
):
    # Now the parameter is called api_version instead of x_api_version
    ...
```

## Default Version Behavior

Always provide a default version for when the header is missing:

```python
# Good: defaults to v1 when header is missing
x_api_version: str = Header(default="1.0")

# Bad: required header -- forces all clients to send it
x_api_version: str = Header()  # 422 if header missing
```

**The rule:** When the `X-API-Version` header is absent, return the oldest supported version (usually 1.0). This ensures backward compatibility -- existing clients that don't send the header continue working.

## Extracting Version Logic

For cleaner code, create a dependency that extracts and validates the version:

```python
from fastapi import Depends, Header, HTTPException

SUPPORTED_VERSIONS = {"1.0", "2.0"}


async def get_api_version(
    x_api_version: str = Header(default="1.0"),
) -> str:
    """Dependency that extracts and validates the API version."""
    if x_api_version not in SUPPORTED_VERSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported API version: {x_api_version}. "
                   f"Supported versions: {', '.join(sorted(SUPPORTED_VERSIONS))}",
        )
    return x_api_version


@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    version: str = Depends(get_api_version),
):
    user = get_user_from_db(user_id)

    if version == "1.0":
        return format_v1(user)
    elif version == "2.0":
        return format_v2(user)
```

## URL Versioning vs Header Versioning

| Aspect | URL Path (`/v1/users`) | Header (`X-API-Version: 1.0`) |
|--------|----------------------|-------------------------------|
| **Visibility** | Version is in the URL | Hidden in headers |
| **Browser testing** | Easy -- paste URL | Hard -- need curl or API client |
| **Caching** | Works with URL-based caches | Requires `Vary: X-API-Version` header |
| **API documentation** | Separate docs per version | One endpoint with version notes |
| **Routing** | Separate routers | Single endpoint with branching |
| **Client adoption** | Change URL | Add header |
| **Discovery** | Self-documenting | Need documentation |

### When to Use URL Versioning (Default Choice)

- Public APIs with external consumers
- When you want explicit, discoverable versioning
- When different versions have significantly different endpoints
- When you want Swagger docs separated by version

### When to Use Header Versioning

- Internal APIs where you control all clients
- When URLs must remain stable (contractual or organizational requirements)
- When version differences are small (same endpoints, slightly different responses)
- When using content negotiation patterns

**Recommendation:** Start with URL path versioning. It's more explicit, more widely understood, and easier to test. Use header versioning only when you have a specific reason.

## Caching with Header Versioning

If you use header versioning with HTTP caching, you must include the `Vary` header:

```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    x_api_version: str = Header(default="1.0"),
    response: Response = None,
):
    # Tell caches that the response varies by API version
    response.headers["Vary"] = "X-API-Version"

    if x_api_version == "1.0":
        return {"id": user_id, "name": "Alice"}
    elif x_api_version == "2.0":
        return {"data": {"id": user_id, "name": "Alice"}, "meta": {"version": "2.0"}}
```

Without `Vary`, a cache might serve a v1 response to a v2 client (or vice versa) because the URL is the same.

## Hybrid Approach

Some APIs use both strategies:

```python
from fastapi import FastAPI, APIRouter, Header

app = FastAPI()

# Major versions via URL
v1_router = APIRouter(prefix="/v1", tags=["v1"])
v2_router = APIRouter(prefix="/v2", tags=["v2"])

# Minor versions via header within v2
@v2_router.get("/users/{user_id}")
async def get_user_v2(
    user_id: int,
    x_api_minor: str = Header(default="0"),
):
    user = get_user_from_db(user_id)
    response = format_v2(user)

    if x_api_minor == "1":
        # V2.1 adds avatar URL
        response["data"]["avatar_url"] = user.get("avatar_url")

    return response
```

This gives you the clarity of URL versioning for major changes and the flexibility of header versioning for minor tweaks.

## Key Takeaways

1. **Header versioning uses `X-API-Version` header** to select the API version. FastAPI's `Header()` dependency makes it easy.
2. **Always provide a default version.** When the header is missing, return the oldest supported version for backward compatibility.
3. **Return 400 for unsupported versions.** Don't silently default -- tell the client which versions are supported.
4. **URL versioning is preferred for most cases.** Header versioning is useful when URLs must stay stable or version differences are small.
5. **Include `Vary: X-API-Version`** when using header versioning with HTTP caching.
6. **Extract version logic into a dependency.** Use `Depends(get_api_version)` to keep endpoint code clean.
