# Module 023: Rate Limiting

## Why This Module?

As a mobile developer, you have seen rate limiting from the client side -- Apple's App Store Connect API returns 429 responses when you hit their limits, and Google's APIs enforce per-project quotas. But you have never had to implement the server side of this protection.

Without rate limiting, a single user (or bot) can overwhelm your API, starving every other user. A misconfigured mobile app retrying in a tight loop can unintentionally DDoS your server. Rate limiting is not optional for production APIs -- it is essential infrastructure.

This module teaches you to implement rate limiting algorithms from scratch using Redis, giving you deep understanding of how token buckets and sliding windows actually work -- not just how to configure a library.

## What You'll Learn

- Rate limiting algorithms: fixed window, sliding window, token bucket, leaky bucket
- Redis-based implementation with atomic operations for thread safety
- Per-user and per-IP rate limit strategies with independent counters
- Monthly quota tracking with tier-based limits (free/pro/enterprise)
- Standard rate limit response headers (X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After)
- Client-side handling of 429 responses with exponential backoff

## Mobile Developer Context

**Rate Limiting Across Platforms:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Rate limit response | URLSession handles 429 | Retrofit/OkHttp interceptor | FastAPI middleware + 429 response |
| Retry logic | URLSession retry policies | OkHttp retry interceptor | Client reads Retry-After header |
| Per-user limits | API key in request header | API key in request header | Extract user from JWT, rate limit per user |
| Quota tracking | App Store Connect API quotas | Google API Console quotas | Redis counters with monthly expiry |

## Prerequisites

Before starting, you should be comfortable with:
- [ ] Redis basics and data structures (Module 014)
- [ ] JWT authentication (Module 009)
- [ ] FastAPI middleware and dependencies (Modules 003-005)
- [ ] fakeredis for self-contained testing (Module 014)

## Topics

### Theory
1. Rate Limiting Algorithms -- Token bucket, sliding window, fixed window, leaky bucket
2. Redis Implementation -- Atomic operations with Redis for rate limiting
3. Per-User vs Per-IP -- Different rate limit keys and tier-based limits
4. Monthly Quotas -- Long-term usage tracking and quota tiers
5. Response Headers -- Standard rate limit headers and 429 responses
6. Client-Side Handling -- How mobile clients should handle rate limits

### Exercises
1. Token Bucket -- Implement a token bucket rate limiter with fakeredis
2. Sliding Window -- Implement a sliding window rate limiter with sorted sets
3. Per-User Limits -- Combine rate limiting with user identification

### Project
Implement comprehensive rate limiting for a FastAPI application.

## Time Estimate

- Theory: ~90 minutes
- Exercises: ~75 minutes
- Project: ~90 minutes

## Note

This module implements rate limiting algorithms from scratch using Redis. For the slowapi library approach (simpler but less flexible), see Module 019: Security Best Practices. Requires the `fakeredis` package (already installed from Module 014).

## Example

```python
import time
import redis.asyncio as redis


class TokenBucketLimiter:
    """Token bucket rate limiter using Redis."""

    def __init__(self, redis_client, capacity: int = 10, refill_rate: float = 1.0):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second

    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under the rate limit."""
        bucket_key = f"bucket:{key}"
        now = time.time()

        # Get current bucket state
        pipe = self.redis.pipeline()
        pipe.hgetall(bucket_key)
        results = await pipe.execute()
        bucket = results[0]

        if not bucket:
            # New bucket: use one token, store state
            await self.redis.hset(bucket_key, mapping={
                "tokens": str(self.capacity - 1),
                "last_refill": str(now),
            })
            await self.redis.expire(bucket_key, 3600)
            return True

        tokens = float(bucket[b"tokens"])
        last_refill = float(bucket[b"last_refill"])

        # Refill tokens based on elapsed time
        elapsed = now - last_refill
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)

        if tokens < 1:
            return False  # No tokens available

        # Consume one token
        await self.redis.hset(bucket_key, mapping={
            "tokens": str(tokens - 1),
            "last_refill": str(now),
        })
        return True
```
