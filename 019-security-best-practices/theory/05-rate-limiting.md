# Rate Limiting

## Why This Matters

On mobile, you manage API quotas to avoid exceeding rate limits set by backend services -- throttling requests, implementing exponential backoff, caching responses. Now you are on the other side: setting those limits to protect your server.

Without rate limiting, your API is vulnerable to:
- **Brute force attacks:** An attacker tries thousands of passwords per second on your login endpoint
- **Denial of Service (DoS):** A single client floods your API with requests, overwhelming the server
- **Resource abuse:** A bot scrapes all your data by hitting list endpoints repeatedly
- **Cost attacks:** If your API calls paid services (email, SMS, AI), unlimited requests drain your budget

Rate limiting is the API equivalent of the bouncer at a club: everyone can come in, but not all at once.

## slowapi: Rate Limiting for FastAPI

`slowapi` is the most popular rate limiting library for FastAPI. It is based on `flask-limiter` and uses a decorator pattern to set limits per endpoint.

### Setup

```bash
pip install slowapi
```

```python
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter using client IP as the key
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Basic Usage: Decorator Pattern

```python
@app.get("/api/items")
@limiter.limit("30/minute")
async def list_items(request: Request):
    """Allow 30 requests per minute per IP."""
    return {"items": [...]}

@app.post("/api/items")
@limiter.limit("10/minute")
async def create_item(request: Request):
    """Allow 10 creates per minute per IP (more restrictive)."""
    return {"id": 1, "name": "New Item"}
```

**Important:** The `request: Request` parameter is required for slowapi to identify the client. Without it, rate limiting will not work.

### Rate Limit String Format

| Format | Meaning |
|--------|---------|
| `"10/minute"` | 10 requests per minute |
| `"100/hour"` | 100 requests per hour |
| `"5/second"` | 5 requests per second |
| `"1000/day"` | 1000 requests per day |
| `"10/minute;100/hour"` | Both limits apply (10/min AND 100/hour) |

### Different Limits for Different Endpoints

Apply stricter limits to sensitive endpoints:

```python
# Authentication endpoints -- strict limits
@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    """5 login attempts per minute prevents brute force."""
    ...

@app.post("/auth/register")
@limiter.limit("3/minute")
async def register(request: Request, user_data: UserCreate):
    """3 registrations per minute prevents spam accounts."""
    ...

@app.post("/auth/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request: Request, email: str):
    """3 password resets per hour prevents email flooding."""
    ...

# Public read endpoints -- relaxed limits
@app.get("/api/posts")
@limiter.limit("60/minute")
async def list_posts(request: Request):
    """60 reads per minute is reasonable for browsing."""
    ...

# Resource-intensive endpoints -- moderate limits
@app.post("/api/search")
@limiter.limit("20/minute")
async def search(request: Request, query: str):
    """Search is expensive -- limit to 20/minute."""
    ...
```

### The 429 Response

When a client exceeds the rate limit, slowapi returns a `429 Too Many Requests` response:

```json
{
  "error": "Rate limit exceeded: 5 per 1 minute"
}
```

Headers included in the response:

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1709856000
Retry-After: 45
```

Your mobile client should check for 429 and implement backoff:

```swift
// iOS example of handling 429
if response.statusCode == 429 {
    let retryAfter = response.headers["Retry-After"]
    // Wait and retry
}
```

### Storage Backends

By default, slowapi uses in-memory storage. For production with multiple server processes, use Redis:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory (development, single process)
limiter = Limiter(key_func=get_remote_address)

# Redis (production, multiple processes)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/0",
)
```

### Custom Key Functions

Rate limit by user instead of IP (useful when users share IPs or use VPNs):

```python
from fastapi import Request

def get_user_key(request: Request) -> str:
    """Rate limit by authenticated user, fall back to IP."""
    # Check for auth token in header
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        # Extract user ID from token (simplified)
        return f"user:{auth[7:20]}"
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_key)
```

## Rate Limiting Strategy Guide

| Endpoint Type | Recommended Limit | Reasoning |
|--------------|-------------------|-----------|
| Login | 5/minute | Prevent brute force |
| Registration | 3/minute | Prevent spam accounts |
| Password reset | 3/hour | Prevent email flooding |
| Public list endpoints | 60/minute | Normal browsing speed |
| Public detail endpoints | 120/minute | Higher for individual reads |
| Authenticated writes | 30/minute | Moderate for legitimate use |
| Search | 20/minute | Search is expensive |
| File upload | 5/minute | Uploads consume storage |
| Admin endpoints | 120/minute | Admins need higher limits |

## Complete Example

```python
from fastapi import FastAPI, Request, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    return {"token": "..."}

@app.get("/api/posts")
@limiter.limit("60/minute")
async def list_posts(request: Request):
    return {"posts": []}

@app.post("/api/posts")
@limiter.limit("10/minute")
async def create_post(request: Request):
    return {"id": 1}
```

## Key Takeaways

1. **Rate limiting prevents abuse** -- brute force, DoS, scraping, and cost attacks
2. **Use slowapi** with the `@limiter.limit()` decorator for per-endpoint configuration
3. **Apply stricter limits** to authentication endpoints (5/minute) than to read endpoints (60/minute)
4. **The `request: Request` parameter is required** for slowapi to work
5. **Use Redis storage** in production when running multiple server processes
6. **Return 429 Too Many Requests** with `Retry-After` headers so clients know when to retry
7. **Mobile analogy:** You have been the client implementing backoff; now you set the limits
