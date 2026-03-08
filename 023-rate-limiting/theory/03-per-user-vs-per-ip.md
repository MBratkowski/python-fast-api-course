# Per-User vs Per-IP Rate Limiting

## Why This Matters

On mobile, the app store enforces rate limits per developer account -- your personal API key has one quota, your company's key has another. This is per-user rate limiting. But when you build a backend, you also need to handle unauthenticated requests where you have no user identity -- only an IP address.

Choosing the right rate limit key determines who gets throttled. Get it wrong, and you either block legitimate users sharing an IP (a corporate office behind NAT) or fail to limit an attacker using multiple accounts.

## Rate Limit Keys

The "key" is the identifier used to track request counts. Different keys serve different purposes:

### 1. IP Address

```python
from fastapi import Request

def get_rate_limit_key_ip(request: Request) -> str:
    """Rate limit by client IP address."""
    client_host = request.client.host
    return f"rl:ip:{client_host}"
```

**When to use:** Unauthenticated endpoints (login, registration, public APIs)
**Pros:** Works without authentication, catches unauthenticated abuse
**Cons:** Shared IPs (NAT, corporate offices) affect all users behind them

```
Corporate office (1 public IP: 203.0.113.50)

User A ──┐
User B ──┼──→ NAT ──→ 203.0.113.50 ──→ Your API
User C ──┘
                      ↑
              All three users share one rate limit!
              50 requests from User A = 50 fewer for Users B and C
```

### 2. Authenticated User ID

```python
from fastapi import Depends
from your_app.auth import get_current_user, User

def get_rate_limit_key_user(
    current_user: User = Depends(get_current_user),
) -> str:
    """Rate limit by authenticated user ID."""
    return f"rl:user:{current_user.id}"
```

**When to use:** Authenticated endpoints where each user should have independent limits
**Pros:** Fair per-user limits, supports tier-based quotas
**Cons:** Requires authentication, does not protect login/registration endpoints

### 3. API Key

```python
from fastapi import Header, HTTPException

def get_rate_limit_key_api(
    x_api_key: str = Header(...),
) -> str:
    """Rate limit by API key."""
    # Validate API key exists in database (omitted for brevity)
    return f"rl:apikey:{x_api_key}"
```

**When to use:** Third-party API access, developer platform APIs
**Pros:** Per-application limits, easy to revoke/change
**Cons:** API keys can be shared or stolen

### 4. Combined Keys

```python
def get_rate_limit_key_combined(
    request: Request,
    current_user: User | None = None,
) -> str:
    """Use user ID if authenticated, otherwise fall back to IP."""
    if current_user:
        return f"rl:user:{current_user.id}"
    return f"rl:ip:{request.client.host}"
```

## Tier-Based Per-User Limits

Different users can have different rate limits based on their subscription tier:

```python
from enum import Enum


class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# Rate limits per tier (requests per hour)
TIER_LIMITS = {
    UserTier.FREE: 100,
    UserTier.PRO: 1_000,
    UserTier.ENTERPRISE: 10_000,
}


async def check_user_rate_limit(
    redis_client,
    user_id: int,
    user_tier: UserTier,
    limiter,
) -> bool:
    """Apply tier-based rate limit for authenticated user."""
    limit = TIER_LIMITS[user_tier]
    key = f"rl:user:{user_id}"
    return await limiter.is_allowed(key, limit)
```

### FastAPI Dependency for Tier-Based Limits

```python
from fastapi import Depends, HTTPException, Request


async def rate_limit_dependency(
    request: Request,
    current_user: User = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """FastAPI dependency that enforces per-user rate limits."""
    limit = TIER_LIMITS.get(current_user.tier, TIER_LIMITS[UserTier.FREE])
    key = f"rl:user:{current_user.id}"

    allowed, remaining = await sliding_window_check(
        redis_client, key, limit, window=3600
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Upgrade your plan for higher limits.",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "Retry-After": "60",
            },
        )

    # Store remaining count for response headers (middleware will add them)
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_limit = limit
```

## Extracting User Identity from JWT

```python
import jwt
from fastapi import Request, HTTPException


async def get_user_id_from_request(request: Request) -> int | None:
    """Extract user ID from JWT token if present."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


async def flexible_rate_limit(request: Request, redis_client):
    """Rate limit by user ID if authenticated, otherwise by IP."""
    user_id = await get_user_id_from_request(request)

    if user_id:
        key = f"rl:user:{user_id}"
        limit = 1000  # Authenticated users get more requests
    else:
        key = f"rl:ip:{request.client.host}"
        limit = 100   # Anonymous users get fewer requests

    # Apply rate limit check...
```

## Strategy Guide

| Endpoint Type | Recommended Key | Why |
|--------------|-----------------|-----|
| Login / Registration | IP address | No auth available yet |
| Public data (read-only) | IP address | Low risk, simple |
| Authenticated CRUD | User ID | Fair per-user limits |
| Admin endpoints | User ID + stricter limits | Protect sensitive operations |
| Third-party API | API key | Per-application tracking |
| File uploads | User ID + endpoint-specific | Expensive operations need separate limits |

## Mobile Analogy

This is exactly like how mobile app stores handle developer quotas:

- **Apple App Store Connect API**: Rate limits per API key (your developer account), not per IP. Multiple team members sharing a key share the quota.
- **Google Play Developer API**: Per-project quotas in Google Cloud Console. Different projects (apps) have independent limits.
- **Firebase**: Per-project limits with tier upgrades (Spark free tier vs Blaze pay-as-you-go).

Your backend works the same way -- identify the caller, look up their tier, and apply the appropriate limit.

## Key Takeaways

1. **IP-based** limiting is for unauthenticated endpoints -- but beware of shared IPs behind NAT
2. **User-based** limiting is fairer and supports tier differentiation (free/pro/enterprise)
3. **Always fall back** to IP-based limiting when no user identity is available
4. **Tier-based limits** let you monetize API access -- free users get lower limits
5. **Extract user identity** from JWT tokens to apply per-user limits in middleware
6. **Use different limits** for different endpoint types -- file uploads need stricter limits than reads
