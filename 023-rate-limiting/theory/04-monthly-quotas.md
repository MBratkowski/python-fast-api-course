# Monthly Quotas

## Why This Matters

On mobile, you have worked with APIs that have monthly quotas -- Google Maps gives you a certain number of API calls per month, Firebase has monthly limits on reads and writes, and Apple's CloudKit has per-app quotas. As a backend developer, you now need to implement this same concept.

Rate limiting handles short-term burst protection (100 requests per minute). Monthly quotas handle long-term usage caps (10,000 API calls per month). They solve different problems and often work together.

## Rate Limiting vs Quotas

```
Rate Limiting (short-term):
├── "Max 100 requests per minute"
├── Protects against bursts and DDoS
├── Resets every minute/hour
└── Same limit for same tier

Quotas (long-term):
├── "Max 10,000 requests per month"
├── Controls total usage over billing period
├── Resets monthly (billing cycle)
└── Tied to subscription tier
```

| Aspect | Rate Limiting | Monthly Quotas |
|--------|--------------|----------------|
| Time window | Seconds to hours | Month (billing period) |
| Purpose | Burst protection | Usage caps |
| Reset | Automatic (window passes) | Calendar-based (monthly) |
| Counter type | Short-lived (auto-expire) | Long-lived (monthly expire) |
| User message | "Slow down" | "Upgrade your plan" |

## Redis Counters for Monthly Quotas

Use `INCR` with `EXPIREAT` to create counters that reset at the start of each month:

```python
import time
from datetime import datetime, timezone
import calendar
import redis.asyncio as redis


async def check_monthly_quota(
    redis_client: redis.Redis,
    user_id: int,
    monthly_limit: int,
) -> tuple[bool, int, int]:
    """
    Check if user is within their monthly quota.

    Returns:
        (allowed: bool, used: int, remaining: int)
    """
    now = datetime.now(timezone.utc)

    # Key includes year-month so it naturally separates months
    quota_key = f"quota:{user_id}:{now.year}:{now.month:02d}"

    # Increment usage counter
    current_usage = await redis_client.incr(quota_key)

    # Set expiry on first use (expire at end of month)
    if current_usage == 1:
        # Calculate seconds until end of month
        last_day = calendar.monthrange(now.year, now.month)[1]
        end_of_month = datetime(
            now.year, now.month, last_day, 23, 59, 59,
            tzinfo=timezone.utc,
        )
        ttl = int((end_of_month - now).total_seconds())
        await redis_client.expire(quota_key, ttl)

    remaining = max(0, monthly_limit - current_usage)
    allowed = current_usage <= monthly_limit

    if not allowed:
        # Decrement since we should not count rejected requests
        await redis_client.decr(quota_key)

    return allowed, current_usage, remaining
```

## Quota Tiers

```python
from enum import Enum
from dataclasses import dataclass


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class QuotaConfig:
    monthly_requests: int
    rate_limit_per_minute: int
    max_file_uploads: int


QUOTA_TIERS: dict[PlanTier, QuotaConfig] = {
    PlanTier.FREE: QuotaConfig(
        monthly_requests=1_000,
        rate_limit_per_minute=10,
        max_file_uploads=50,
    ),
    PlanTier.PRO: QuotaConfig(
        monthly_requests=50_000,
        rate_limit_per_minute=100,
        max_file_uploads=500,
    ),
    PlanTier.ENTERPRISE: QuotaConfig(
        monthly_requests=1_000_000,
        rate_limit_per_minute=1_000,
        max_file_uploads=10_000,
    ),
}
```

## Tracking Usage Across Multiple Endpoints

Track different quotas for different resource types:

```python
async def check_endpoint_quota(
    redis_client: redis.Redis,
    user_id: int,
    endpoint_type: str,
    tier: PlanTier,
) -> tuple[bool, int]:
    """
    Track usage per endpoint type within the monthly quota.

    endpoint_type: "api_calls", "file_uploads", "exports"
    """
    now = datetime.now(timezone.utc)
    quota_key = f"quota:{user_id}:{endpoint_type}:{now.year}:{now.month:02d}"

    config = QUOTA_TIERS[tier]

    # Map endpoint types to their specific limits
    limits = {
        "api_calls": config.monthly_requests,
        "file_uploads": config.max_file_uploads,
    }

    limit = limits.get(endpoint_type, config.monthly_requests)

    current = await redis_client.incr(quota_key)
    if current == 1:
        last_day = calendar.monthrange(now.year, now.month)[1]
        end_of_month = datetime(
            now.year, now.month, last_day, 23, 59, 59,
            tzinfo=timezone.utc,
        )
        ttl = int((end_of_month - now).total_seconds())
        await redis_client.expire(quota_key, ttl)

    remaining = max(0, limit - current)
    return current <= limit, remaining
```

## Quota Percentage Warnings

Alert users before they hit their limit:

```python
async def get_quota_status(
    redis_client: redis.Redis,
    user_id: int,
    tier: PlanTier,
) -> dict:
    """
    Get current quota usage with warning levels.

    Returns status dict with usage percentage and warning level.
    """
    now = datetime.now(timezone.utc)
    quota_key = f"quota:{user_id}:api_calls:{now.year}:{now.month:02d}"
    config = QUOTA_TIERS[tier]

    current_usage = await redis_client.get(quota_key)
    used = int(current_usage) if current_usage else 0
    limit = config.monthly_requests
    percentage = (used / limit) * 100 if limit > 0 else 0

    # Determine warning level
    if percentage >= 100:
        warning = "exceeded"
    elif percentage >= 90:
        warning = "critical"    # Send email alert
    elif percentage >= 80:
        warning = "warning"     # Show in-app warning
    else:
        warning = "ok"

    return {
        "used": used,
        "limit": limit,
        "remaining": max(0, limit - used),
        "percentage": round(percentage, 1),
        "warning": warning,
        "tier": tier.value,
        "resets_at": f"{now.year}-{now.month + 1:02d}-01T00:00:00Z"
        if now.month < 12
        else f"{now.year + 1}-01-01T00:00:00Z",
    }
```

### Usage in a FastAPI Endpoint

```python
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()


@app.get("/api/quota")
async def get_my_quota(
    current_user: User = Depends(get_current_user),
    redis_client = Depends(get_redis),
):
    """Return current user's quota status."""
    status = await get_quota_status(
        redis_client, current_user.id, current_user.tier
    )
    return {"data": status}


# Example response:
# {
#     "data": {
#         "used": 8500,
#         "limit": 10000,
#         "remaining": 1500,
#         "percentage": 85.0,
#         "warning": "warning",
#         "tier": "pro",
#         "resets_at": "2024-04-01T00:00:00Z"
#     }
# }
```

## Combined Rate Limiting and Quotas

In production, use both together:

```python
async def combined_check(
    redis_client: redis.Redis,
    user_id: int,
    tier: PlanTier,
    rate_limiter: SlidingWindowLimiter,
) -> None:
    """Check both rate limit and monthly quota. Raise HTTPException if either fails."""
    config = QUOTA_TIERS[tier]

    # Check 1: Short-term rate limit (per minute)
    rate_key = f"rl:user:{user_id}"
    rate_allowed, rate_remaining = await rate_limiter.is_allowed(rate_key)
    if not rate_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down.",
            headers={"Retry-After": "60"},
        )

    # Check 2: Monthly quota
    quota_allowed, quota_used, quota_remaining = await check_monthly_quota(
        redis_client, user_id, config.monthly_requests
    )
    if not quota_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly quota exceeded ({config.monthly_requests} requests). "
                   f"Upgrade to {PlanTier.PRO.value} for higher limits.",
            headers={"Retry-After": "86400"},  # Try again tomorrow
        )
```

## Key Takeaways

1. **Rate limiting and quotas solve different problems** -- use both together in production
2. **Include year-month in the Redis key** so counters naturally separate by billing period
3. **Use EXPIREAT or EXPIRE** so old quota keys are automatically cleaned up
4. **Warn users at 80% and 90%** of their quota -- do not surprise them at 100%
5. **Track usage per endpoint type** for fine-grained quota control
6. **Tier-based quotas** are a natural monetization strategy for API products
