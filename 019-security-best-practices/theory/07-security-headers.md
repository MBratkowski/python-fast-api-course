# Security Headers

## Why This Matters

On mobile, the OS provides security features automatically -- iOS enforces ATS (App Transport Security) to require HTTPS, Android blocks cleartext traffic by default. On the server, you must explicitly add security headers to your HTTP responses. These headers tell browsers how to handle your content securely: prevent clickjacking, block MIME type sniffing, enforce HTTPS, and restrict what scripts can run.

Security headers are a defense-in-depth measure. They do not replace authentication, authorization, or input validation -- but they add an extra layer that mitigates entire categories of attacks. Many security audits and compliance standards (SOC 2, PCI DSS) require them.

## Essential Security Headers

### X-Content-Type-Options: nosniff

Prevents browsers from "sniffing" the MIME type of a response. Without this, a browser might execute a file as JavaScript even if the server sends it as `text/plain`.

```
X-Content-Type-Options: nosniff
```

**Why it matters:** An attacker uploads a file named `photo.jpg` that is actually JavaScript. Without `nosniff`, the browser might execute it.

### X-Frame-Options: DENY

Prevents your pages from being embedded in iframes on other sites. This blocks **clickjacking** attacks where a malicious site overlays your UI with invisible frames.

```
X-Frame-Options: DENY
```

| Value | Meaning |
|-------|---------|
| `DENY` | Cannot be embedded in any iframe |
| `SAMEORIGIN` | Can only be embedded by same-origin pages |

For APIs, `DENY` is almost always correct. APIs should not be rendered in iframes.

### Strict-Transport-Security (HSTS)

Forces browsers to use HTTPS for all future requests to your domain. Once a browser sees this header, it will never make an HTTP request to your site -- even if the user types `http://`.

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

| Directive | Meaning |
|-----------|---------|
| `max-age=31536000` | Remember this for 1 year (in seconds) |
| `includeSubDomains` | Apply to all subdomains too |

**Warning:** Only add HSTS when you are sure HTTPS is properly configured. Once set, browsers will refuse HTTP for the specified duration.

### Content-Security-Policy (CSP)

Controls which resources (scripts, styles, images) the browser is allowed to load. This is the most powerful defense against XSS attacks.

```
Content-Security-Policy: default-src 'self'
```

For APIs that only return JSON, a restrictive CSP is appropriate:

```
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
```

| Directive | Purpose |
|-----------|---------|
| `default-src 'self'` | Only allow resources from same origin |
| `default-src 'none'` | Block all resources (strictest for APIs) |
| `frame-ancestors 'none'` | Prevent embedding (modern replacement for X-Frame-Options) |

### X-XSS-Protection

Enables the browser's built-in XSS filter. While modern browsers have deprecated this in favor of CSP, it is still useful for older browsers:

```
X-XSS-Protection: 1; mode=block
```

## Implementing Security Headers in FastAPI

### Custom Middleware with BaseHTTPMiddleware

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Restrict resource loading
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )

        # Prevent referrer leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Control browser features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        return response

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
```

### Using the secure Library

The `secure` library provides pre-configured security header bundles:

```bash
pip install secure
```

```python
import secure
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Create secure headers with defaults
secure_headers = secure.Secure()

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        secure_headers.set_headers(response)
        return response

app = FastAPI()
app.add_middleware(SecureHeadersMiddleware)
```

### Custom vs. secure Library

| Approach | Pros | Cons |
|----------|------|------|
| Custom middleware | Full control, no dependency, easy to understand | Must know all headers |
| `secure` library | Good defaults, less code, maintained | Extra dependency, less visible |

**Recommendation for learning:** Start with custom middleware so you understand each header. In production, either approach works.

## Middleware Ordering

When combining multiple middlewares, order matters. FastAPI processes middleware in reverse order of addition (last added = first to run):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS first (runs after security headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Add security headers second (runs first, applies to all responses)
app.add_middleware(SecurityHeadersMiddleware)
```

## Verifying Your Headers

### Using curl

```bash
# Check response headers
curl -I https://your-api.com/api/health

# Expected output includes:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
```

### Using Tests

```python
from fastapi.testclient import TestClient

def test_security_headers_present(client: TestClient):
    """Every response should include security headers."""
    response = client.get("/api/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "max-age=" in response.headers["Strict-Transport-Security"]
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
```

## Headers Summary

| Header | Value | Protects Against |
|--------|-------|------------------|
| `X-Content-Type-Options` | `nosniff` | MIME type confusion attacks |
| `X-Frame-Options` | `DENY` | Clickjacking |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | HTTP downgrade attacks |
| `Content-Security-Policy` | `default-src 'none'` | XSS, code injection |
| `X-XSS-Protection` | `1; mode=block` | Reflected XSS (legacy) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Referrer leakage |
| `Permissions-Policy` | `camera=(), microphone=()` | Unauthorized feature access |

## Key Takeaways

1. **Security headers are defense-in-depth** -- they add protection on top of authentication and validation
2. **Use `BaseHTTPMiddleware`** to apply headers to every response automatically
3. **`X-Content-Type-Options: nosniff`** and **`X-Frame-Options: DENY`** are the minimum for any API
4. **Add HSTS only when HTTPS is properly configured** -- it cannot be easily undone
5. **CSP with `default-src 'none'`** is appropriate for JSON APIs that do not serve HTML
6. **Test that headers are present** in your API tests -- middleware configuration can break silently
7. **Mobile analogy:** Security headers are your server's App Transport Security (ATS) -- configuring how clients interact with your server securely
