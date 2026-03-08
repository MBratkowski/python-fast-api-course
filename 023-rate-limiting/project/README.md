# Project: Implement Rate Limiting for an API

## Overview

Add comprehensive rate limiting to a FastAPI application. You will implement multiple rate limiting algorithms, per-user limits with tier support, rate limit response headers, and monthly quota tracking -- all backed by Redis.

## Requirements

### Core Rate Limiting
- [ ] Implement a **token bucket** rate limiter for burst-friendly endpoints (e.g., `GET /items`)
- [ ] Implement a **sliding window** rate limiter for strict endpoints (e.g., `POST /payments`)
- [ ] Both limiters should use Redis (fakeredis for testing) for distributed state

### Per-User Limits
- [ ] Extract user identity from JWT tokens (use PyJWT)
- [ ] Apply per-user rate limits with independent counters per user
- [ ] Support tier-based limits:
  - Free tier: 60 requests/minute, 1,000 requests/month
  - Pro tier: 300 requests/minute, 50,000 requests/month
  - Enterprise tier: 1,000 requests/minute, unlimited monthly
- [ ] Fall back to IP-based limiting for unauthenticated requests (30 requests/minute)

### Response Headers
- [ ] Include `X-RateLimit-Limit` on every response
- [ ] Include `X-RateLimit-Remaining` on every response
- [ ] Include `X-RateLimit-Reset` (Unix timestamp) on every response
- [ ] Include `Retry-After` (seconds) on 429 responses
- [ ] Return 429 status code with JSON error body when rate limited

### Monthly Quotas
- [ ] Track monthly API usage per user with Redis counters
- [ ] Implement quota percentage warnings (return warning level in response when > 80%)
- [ ] Monthly counters should auto-expire at the end of each month
- [ ] Provide a `GET /api/quota` endpoint returning current usage stats

## Starter Template

```python
"""
Rate-Limited API Application

Run: uvicorn project:app --reload --port 8000
Test: pytest 023-rate-limiting/project/ -v
"""

import time
from contextlib import asynccontextmanager
from enum import Enum

import jwt
import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel


# ============= Configuration =============

SECRET_KEY = "your-secret-key-for-testing"
ALGORITHM = "HS256"


class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_RATE_LIMITS = {
    UserTier.FREE: {"per_minute": 60, "monthly": 1_000},
    UserTier.PRO: {"per_minute": 300, "monthly": 50_000},
    UserTier.ENTERPRISE: {"per_minute": 1_000, "monthly": None},  # Unlimited
}

ANONYMOUS_RATE_LIMIT = 30  # per minute


# ============= Models =============

class QuotaResponse(BaseModel):
    used: int
    limit: int | None
    remaining: int | None
    percentage: float
    warning: str  # "ok", "warning", "critical", "exceeded"
    tier: str


# ============= Redis Setup =============

redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    # Use fakeredis for development/testing
    import fakeredis.aioredis
    redis_client = fakeredis.aioredis.FakeRedis()
    yield
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)


# ============= TODO: Implement Rate Limiters =============

# 1. TokenBucketLimiter class (for GET endpoints)
# 2. SlidingWindowLimiter class (for POST/PUT/DELETE endpoints)
# 3. MonthlyQuotaTracker class
# 4. Rate limit middleware or dependency that adds headers
# 5. JWT user extraction with tier lookup
# 6. /api/quota endpoint


# ============= Endpoints =============

@app.get("/items")
async def list_items():
    """Burst-friendly endpoint (token bucket)."""
    return {"items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """Burst-friendly endpoint (token bucket)."""
    return {"item": {"id": item_id, "name": f"Item {item_id}"}}


@app.post("/payments")
async def create_payment():
    """Strict endpoint (sliding window)."""
    return {"payment": {"id": 1, "status": "created"}}


@app.get("/api/quota")
async def get_quota():
    """Return current user's quota status."""
    # TODO: Implement quota status endpoint
    pass
```

## Success Criteria

1. **Token bucket works**: GET endpoints allow bursts up to capacity, then throttle
2. **Sliding window works**: POST endpoints have strict per-second rate limiting
3. **Per-user independence**: Rate limiting user A does not affect user B
4. **Tier enforcement**: Free users have lower limits than Pro users
5. **Headers on every response**: All four rate limit headers are present
6. **429 format**: Rate limited responses include JSON body with Retry-After header
7. **Monthly quotas**: Usage is tracked and warning levels are returned
8. **Quota endpoint**: `GET /api/quota` returns current usage statistics

## Testing Tips

- Use `fakeredis.aioredis.FakeRedis()` for all Redis operations
- Mock `time.time()` to control timing without real delays
- Use `TestClient` for endpoint tests
- Test each rate limiter independently before integration
- Verify rate limit headers are present on both 200 and 429 responses
