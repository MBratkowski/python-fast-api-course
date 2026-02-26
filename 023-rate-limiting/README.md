# Module 023: Rate Limiting

## Why This Module?

Protect your API from abuse. Rate limiting prevents DoS attacks and ensures fair usage.

## What You'll Learn

- Rate limiting algorithms
- Redis-based rate limiting
- Per-user and per-IP limits
- API quotas
- Retry-After headers
- Graceful degradation

## Topics

### Theory
1. Rate Limiting Algorithms (Token Bucket, Sliding Window)
2. Redis-Based Implementation
3. Per-User vs Per-IP Limiting
4. Monthly Quotas
5. Response Headers
6. Client-Side Handling

### Project
Implement rate limiting for your API.

## Example

```python
from fastapi import Request, HTTPException
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379")

async def rate_limit(
    request: Request,
    limit: int = 100,
    window: int = 60
):
    """Limit requests per IP per minute."""
    key = f"rate_limit:{request.client.host}"

    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, window)

    if current > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(window)}
        )

# Use as dependency
@app.get("/api/data")
async def get_data(_: None = Depends(rate_limit)):
    return {"data": "value"}

# Or per-user limits
async def user_rate_limit(
    current_user: User = Depends(get_current_user)
):
    key = f"rate_limit:user:{current_user.id}"
    # ... same logic
```
