# Redis Implementation for Rate Limiting

## Why This Matters

On mobile, rate limiting is someone else's problem -- the backend returns 429, and your app handles it. Now you are the backend developer, and you need rate limiting that works across multiple server instances. A Python dictionary works for one server, but the moment you scale to two servers behind a load balancer, each server has its own counter and a user gets 2x the rate limit.

Redis solves this because it is a shared, fast, atomic data store. Every server checks the same Redis instance, so rate limits are consistent regardless of which server handles the request.

## Why Redis for Rate Limiting

```
Without Redis (per-server counters):

Server A: user_123 → 50 requests  ← Thinks user is under limit
Server B: user_123 → 50 requests  ← Also thinks user is under limit
                                   ← User actually made 100 requests!

With Redis (shared counter):

Server A ──┐
            ├──→ Redis: user_123 → 100 requests ← Correctly enforced
Server B ──┘
```

**Three reasons Redis wins for rate limiting:**
1. **Atomic operations** -- INCR, ZADD, and pipelines prevent race conditions
2. **Speed** -- Sub-millisecond operations add negligible latency to requests
3. **Expiry** -- Built-in key TTL handles cleanup automatically

## Token Bucket with Redis

The token bucket stores two values per key: current token count and last refill timestamp.

```python
import time
import redis.asyncio as redis


class TokenBucketLimiter:
    """
    Token bucket rate limiter backed by Redis.

    Uses a Redis hash to store bucket state:
    - tokens: current token count (float)
    - last_refill: timestamp of last refill calculation
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        capacity: int = 10,
        refill_rate: float = 1.0,
    ):
        self.redis = redis_client
        self.capacity = capacity          # Max tokens in bucket
        self.refill_rate = refill_rate    # Tokens added per second

    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed. Consumes one token if yes."""
        bucket_key = f"bucket:{key}"
        now = time.time()

        # Use pipeline for atomic read
        bucket = await self.redis.hgetall(bucket_key)

        if not bucket:
            # First request: initialize bucket with capacity - 1
            await self.redis.hset(bucket_key, mapping={
                "tokens": str(self.capacity - 1),
                "last_refill": str(now),
            })
            await self.redis.expire(bucket_key, 3600)
            return True

        # Parse current state
        tokens = float(bucket[b"tokens"])
        last_refill = float(bucket[b"last_refill"])

        # Calculate tokens to add based on elapsed time
        elapsed = now - last_refill
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)

        if tokens < 1:
            return False  # No tokens available

        # Consume one token and update state
        await self.redis.hset(bucket_key, mapping={
            "tokens": str(tokens - 1),
            "last_refill": str(now),
        })
        return True
```

**Redis data structure used:** Hash (`HSET`, `HGETALL`)
- Key: `bucket:{identifier}`
- Fields: `tokens` (float), `last_refill` (float timestamp)

## Sliding Window with Sorted Sets

The sliding window uses Redis sorted sets to track individual request timestamps.

```python
import time
import redis.asyncio as redis


class SlidingWindowLimiter:
    """
    Sliding window rate limiter using Redis sorted sets.

    Each request is stored as a member with its timestamp as the score.
    Old entries outside the window are cleaned up on each check.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if request is allowed.

        Returns:
            (allowed: bool, remaining: int) -- whether allowed and
            how many requests remain in the window.
        """
        now = time.time()
        window_start = now - self.window_seconds
        sorted_set_key = f"sw:{key}"

        # Atomic pipeline: clean, add, count, expire
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(sorted_set_key, 0, window_start)  # Remove old
        pipe.zadd(sorted_set_key, {str(now): now})               # Add current
        pipe.zcard(sorted_set_key)                                # Count
        pipe.expire(sorted_set_key, self.window_seconds)          # Auto-cleanup
        results = await pipe.execute()

        request_count = results[2]
        allowed = request_count <= self.max_requests
        remaining = max(0, self.max_requests - request_count)

        if not allowed:
            # Remove the request we just added (it should not count)
            await self.redis.zrem(sorted_set_key, str(now))
            remaining = 0

        return allowed, remaining
```

**Redis data structure used:** Sorted Set (`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`)
- Key: `sw:{identifier}`
- Members: request timestamps (as strings)
- Scores: request timestamps (as floats)

### How Sorted Sets Work for Rate Limiting

```
Sorted Set: sw:user_123

Score (timestamp)    Member
──────────────────   ──────
1709001200.123       "1709001200.123"
1709001201.456       "1709001201.456"
1709001202.789       "1709001202.789"
                     ↑
                     Each request adds an entry

ZREMRANGEBYSCORE: removes entries older than (now - window)
ZCARD: counts remaining entries = requests in current window
```

## Pipeline for Atomicity

**Critical warning:** Never do a read-check-increment without a pipeline or Lua script.

```python
# WRONG: Race condition between read and write
count = await redis.get(key)       # Thread A reads: 9
count = await redis.get(key)       # Thread B reads: 9
if int(count) < limit:             # Both threads: 9 < 10
    await redis.incr(key)          # Thread A increments: 10
    await redis.incr(key)          # Thread B increments: 11 ← OVER LIMIT!

# RIGHT: Atomic pipeline
pipe = redis.pipeline()
pipe.incr(key)                     # Atomic increment
pipe.expire(key, window)           # Set expiry
results = await pipe.execute()
count = results[0]                 # Read the result AFTER increment
if count > limit:
    return False                   # Correctly rejected
```

**Lua script alternative** for complex logic:

```python
# Lua script runs atomically on Redis server
SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)

if count < limit then
    redis.call('ZADD', key, now, tostring(now))
    redis.call('EXPIRE', key, window)
    return {1, limit - count - 1}
else
    return {0, 0}
end
"""
```

## Key Expiry for Auto-Cleanup

Always set expiry on rate limit keys to prevent Redis memory from growing unbounded:

```python
# Token bucket: expire after inactivity
await redis.expire(bucket_key, 3600)  # Clean up after 1 hour of inactivity

# Sliding window: expire after window duration
await redis.expire(sorted_set_key, window_seconds)  # Clean up when window passes

# Fixed window: expire after window duration
current = await redis.incr(window_key)
if current == 1:
    await redis.expire(window_key, window_seconds)
```

**Without expiry:** Old keys accumulate. A server with 100,000 unique users per day would accumulate millions of dead keys.

## Comparison: Token Bucket vs Sliding Window in Redis

| Aspect | Token Bucket (Hash) | Sliding Window (Sorted Set) |
|--------|--------------------|-----------------------------|
| Redis ops per check | 2 (HGETALL + HSET) | 4 (ZREMRANGEBYSCORE + ZADD + ZCARD + EXPIRE) |
| Memory per key | ~100 bytes (2 fields) | ~50 bytes per request in window |
| Burst handling | Allows bursts up to capacity | Strict -- no bursts |
| Accuracy | Approximate (time-based refill) | Exact (per-request tracking) |
| Best for | User-facing APIs, high traffic | Billing, strict compliance |

## Key Takeaways

1. **Use Redis pipelines** for atomicity -- never read-check-write in separate commands
2. **Sorted sets** are perfect for sliding windows -- `ZADD`, `ZREMRANGEBYSCORE`, and `ZCARD` give you precise counting
3. **Hash maps** are ideal for token buckets -- store tokens and last_refill in two fields
4. **Always set key expiry** to prevent unbounded memory growth
5. **Choose your algorithm** based on burst tolerance and precision requirements
6. **Race conditions** are the most common rate limiting bug -- atomic operations or Lua scripts prevent them
