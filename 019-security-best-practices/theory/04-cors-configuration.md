# CORS Configuration

## Why This Matters

On mobile, you never think about CORS. Your app makes HTTP requests to any server, and the OS does not restrict cross-origin calls. But when your API is consumed by a web frontend running in a browser, CORS becomes critical. Browsers enforce the Same-Origin Policy: JavaScript on `https://frontend.com` cannot make requests to `https://api.backend.com` unless the API explicitly allows it via CORS headers.

Think of CORS as the server-side equivalent of App Transport Security (ATS) on iOS or Network Security Configuration on Android. On mobile, the OS restricts which servers your app can talk to. With CORS, the browser restricts which servers a web page can talk to -- and your API must cooperate by sending the right headers.

## What Is CORS?

**Cross-Origin Resource Sharing (CORS)** is a security mechanism enforced by web browsers. It prevents malicious websites from making unauthorized API requests using a logged-in user's credentials.

### The Same-Origin Policy

Two URLs have the same origin if they share the same:
- **Protocol:** `https` vs `http`
- **Host:** `api.example.com` vs `example.com`
- **Port:** `:443` vs `:8000`

| Request from | Request to | Same origin? |
|-------------|------------|-------------|
| `https://myapp.com` | `https://myapp.com/api` | Yes |
| `https://myapp.com` | `https://api.myapp.com` | No (different subdomain) |
| `http://localhost:3000` | `http://localhost:8000` | No (different port) |
| `https://myapp.com` | `http://myapp.com` | No (different protocol) |

### Why This Exists

Without CORS, a malicious website could:
1. User visits `https://evil.com` while logged into `https://mybank.com`
2. JavaScript on `evil.com` sends `fetch("https://mybank.com/api/transfer", {method: "POST", credentials: "include"})`
3. The browser sends the user's authentication cookies automatically
4. Money transferred without the user's knowledge

CORS prevents step 2 by requiring `mybank.com` to explicitly allow requests from `evil.com`.

## FastAPI CORSMiddleware

FastAPI provides CORS support through Starlette's `CORSMiddleware`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "https://admin.myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,  # Cache preflight response for 10 minutes
)
```

### Configuration Options

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `allow_origins` | Which origins can make requests | `["https://myapp.com"]` |
| `allow_credentials` | Allow cookies/auth headers | `True` or `False` |
| `allow_methods` | Allowed HTTP methods | `["GET", "POST"]` |
| `allow_headers` | Allowed request headers | `["Authorization"]` |
| `expose_headers` | Response headers visible to JS | `["X-Total-Count"]` |
| `max_age` | Preflight cache duration (seconds) | `600` |

## The Critical Rule: No Wildcard with Credentials

This is the most important CORS rule to remember:

```python
# INVALID: Browser will REJECT this configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # Wildcard
    allow_credentials=True,       # With credentials
)
```

**Why?** The CORS specification explicitly forbids `Access-Control-Allow-Origin: *` when `Access-Control-Allow-Credentials: true`. Browsers will block the response entirely. This is not a FastAPI limitation -- it is enforced by every browser.

**The fix:** List specific origins when using credentials:

```python
# VALID: Specific origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://admin.myapp.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Preflight Requests

For "non-simple" requests (POST with JSON, requests with custom headers like `Authorization`), browsers send a **preflight request** before the actual request:

```
1. Browser sends:    OPTIONS /api/users  (preflight)
2. Server responds:  200 OK with CORS headers
3. Browser sends:    POST /api/users     (actual request)
4. Server responds:  201 Created with data
```

The preflight checks if the server allows the actual request. If the CORS headers are missing or wrong, the browser never sends the actual request.

**What triggers a preflight:**
- HTTP methods other than GET, HEAD, POST
- POST with `Content-Type: application/json` (not `multipart/form-data`)
- Custom headers like `Authorization`
- Any request with `credentials: include`

FastAPI's CORSMiddleware handles preflight requests automatically.

## Development vs. Production Origins

```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    origins = [
        "http://localhost:3000",     # React dev server
        "http://localhost:5173",     # Vite dev server
        "http://127.0.0.1:3000",
    ]
else:
    origins = [
        "https://myapp.com",
        "https://admin.myapp.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### When Wildcard IS Acceptable

If your API is truly public (no authentication, no cookies), wildcard is fine:

```python
# Public API -- no credentials needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Any origin can access
    allow_credentials=False,       # No cookies or auth headers
    allow_methods=["GET"],         # Read-only
)
```

Examples: public weather API, currency exchange rates, open data APIs.

## Debugging CORS Issues

### Common Error Messages

**Browser console:** `Access to fetch at 'https://api.example.com' from origin 'https://myapp.com' has been blocked by CORS policy`

**Troubleshooting checklist:**
1. Is the origin in `allow_origins`? (Check exact match including protocol and port)
2. Is the HTTP method in `allow_methods`?
3. Are custom headers in `allow_headers`? (especially `Authorization` and `Content-Type`)
4. Are you using `allow_origins=["*"]` with `allow_credentials=True`? (this is invalid)
5. Is the middleware added to the FastAPI app? (check ordering -- CORS middleware should be added first)

### Testing CORS in Your API

```python
from fastapi.testclient import TestClient

def test_cors_allows_configured_origin(client: TestClient):
    """Preflight request from allowed origin should succeed."""
    response = client.options(
        "/api/users",
        headers={
            "Origin": "https://myapp.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://myapp.com"

def test_cors_blocks_unknown_origin(client: TestClient):
    """Preflight from unknown origin should not include CORS headers."""
    response = client.options(
        "/api/users",
        headers={
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers
```

## Key Takeaways

1. **CORS is a browser security feature** -- it does not affect mobile apps or server-to-server requests
2. **Never use `allow_origins=["*"]` with `allow_credentials=True`** -- browsers reject this combination
3. **List specific origins** in production (e.g., `["https://myapp.com"]`)
4. **Use environment-based configuration** to separate development and production origins
5. **Include `Authorization` in `allow_headers`** if your API uses JWT authentication
6. **FastAPI handles preflight automatically** through `CORSMiddleware` -- you just configure it correctly
