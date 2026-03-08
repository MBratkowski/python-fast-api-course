# Rate Limiting Algorithms

## Why This Matters

On iOS, you have used `URLSession` with rate limiting -- when Apple's API returns a 429, your app backs off. On Android, OkHttp interceptors handle retry logic transparently. But you have never had to decide **how** to count requests and **when** to reject them.

Rate limiting protects your API from three threats: malicious attacks (DDoS), misbehaving clients (tight retry loops), and unfair usage (one user consuming all resources). The algorithm you choose determines how strictly you enforce limits and how you handle bursts of traffic.

Understanding these algorithms gives you the ability to pick the right strategy for each endpoint -- burst-friendly for user-facing APIs, strict for expensive operations.

## Why Rate Limit?

1. **Prevent abuse** -- Stop bots and attackers from overwhelming your API
2. **Ensure fairness** -- No single user should consume all available capacity
3. **Protect resources** -- Database connections, CPU, and memory are finite
4. **Cost control** -- Prevent runaway costs from excessive API calls
5. **Stability** -- Keep the service responsive under heavy load

## Algorithm Overview

### 1. Fixed Window

The simplest approach: count requests in fixed time windows (e.g., per minute).

```
Window: 12:00:00 - 12:00:59  |  Window: 12:01:00 - 12:01:59
                              |
  ████████░░  (8/10 used)     |  ██░░░░░░░░  (2/10 used)
                              |
         boundary ────────────┘
```

**How it works:**
- Divide time into fixed windows (e.g., 1-minute intervals)
- Count requests in the current window
- Reject when count exceeds limit

```python
import time

def fixed_window_check(redis_client, key: str, limit: int, window: int) -> bool:
    """Fixed window rate limiter."""
    # Window key changes every `window` seconds
    window_key = f"fw:{key}:{int(time.time()) // window}"

    current = redis_client.incr(window_key)
    if current == 1:
        redis_client.expire(window_key, window)

    return current <= limit
```

**Pros:** Simple, low memory (one counter per window)
**Cons:** Boundary burst problem -- a user can make 2x the limit across a window boundary

```
The Boundary Burst Problem:
                              |
Window 1        Window 2      |
          ████████████████████|
          10 reqs    10 reqs  |
          (last 10s) (first 10s)
                              |
= 20 requests in 20 seconds, but limit is 10/minute!
```

### 2. Sliding Window

Fixes the boundary burst problem by tracking individual request timestamps.

```
                 60-second sliding window
    ◄────────────────────────────────────►
    │                                    │
────┼──x──x──x──x──x──x──x──x──────────┼────
    │  1  2  3  4  5  6  7  8           now
    │                                    │
    Requests in window: 8/10 ── ALLOWED
```

**How it works:**
- Store each request timestamp in a sorted set
- Remove timestamps older than the window
- Count remaining entries
- Reject if count exceeds limit

```python
import time

async def sliding_window_check(
    redis_client, key: str, limit: int, window: int
) -> tuple[bool, int]:
    """Sliding window rate limiter using sorted sets."""
    now = time.time()
    window_start = now - window

    pipe = redis_client.pipeline()
    # Remove old entries
    pipe.zremrangebyscore(f"sw:{key}", 0, window_start)
    # Add current request
    pipe.zadd(f"sw:{key}", {str(now): now})
    # Count entries in window
    pipe.zcard(f"sw:{key}")
    # Set expiry for cleanup
    pipe.expire(f"sw:{key}", window)
    results = await pipe.execute()

    request_count = results[2]
    allowed = request_count <= limit
    remaining = max(0, limit - request_count)

    return allowed, remaining
```

**Pros:** Precise, no boundary burst problem
**Cons:** More memory (stores each timestamp), more Redis operations

### 3. Token Bucket

The most flexible algorithm. Tokens accumulate over time, and each request consumes a token. Allows controlled bursts.

```
Bucket capacity: 5 tokens
Refill rate: 1 token/second

Time 0:   [*][*][*][*][*]  5 tokens (full)
           ↓ 3 requests arrive at once
Time 0+:  [*][*][ ][ ][ ]  2 tokens left (burst allowed!)
           ↓ 2 seconds pass, 2 tokens refill
Time 2:   [*][*][*][*][ ]  4 tokens
           ↓ 1 request
Time 2+:  [*][*][*][ ][ ]  3 tokens
```

**How it works:**
- Bucket starts full (capacity = max tokens)
- Each request removes one token
- Tokens refill at a constant rate
- Request denied if no tokens available

```python
import time

class TokenBucket:
    def __init__(self, redis_client, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second

    async def is_allowed(self, key: str) -> bool:
        bucket_key = f"tb:{key}"
        now = time.time()

        bucket = await self.redis.hgetall(bucket_key)

        if not bucket:
            # First request: full bucket minus one token
            await self.redis.hset(bucket_key, mapping={
                "tokens": str(self.capacity - 1),
                "last_refill": str(now),
            })
            await self.redis.expire(bucket_key, 3600)
            return True

        tokens = float(bucket["tokens"])
        last_refill = float(bucket["last_refill"])

        # Calculate refilled tokens
        elapsed = now - last_refill
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)

        if tokens < 1:
            return False

        # Consume token
        await self.redis.hset(bucket_key, mapping={
            "tokens": str(tokens - 1),
            "last_refill": str(now),
        })
        return True
```

**Pros:** Allows bursts up to capacity, smooth average rate, flexible
**Cons:** Slightly more complex, requires storing bucket state

### 4. Leaky Bucket

Requests enter a queue and are processed at a fixed rate. Like water dripping from a bucket.

```
    Incoming requests (variable rate)
         │ │ │ │ │ │
         ▼ ▼ ▼ ▼ ▼ ▼
    ┌───────────────────┐
    │ ░░░░░░░░░░░░░░░░░ │ ← Queue (bucket)
    │ ░░░░░░░░░░░░░░░░░ │
    └────────┬──────────┘
             │
             ▼ (constant drip rate)
        Processed at fixed rate
```

**How it works:**
- Requests added to a queue (the bucket)
- Queue has a maximum size (bucket capacity)
- Requests processed at a constant rate (the leak)
- If queue is full, new requests are rejected

**Pros:** Smooth, predictable output rate
**Cons:** Adds latency (queuing), more complex to implement

## Algorithm Comparison

| Algorithm | Burst Handling | Memory | Precision | Complexity |
|-----------|---------------|--------|-----------|------------|
| Fixed Window | Allows 2x burst at boundary | Low (1 counter) | Low | Simple |
| Sliding Window | No burst at boundary | High (per-request) | High | Medium |
| Token Bucket | Controlled bursts | Medium (2 values) | Medium | Medium |
| Leaky Bucket | No bursts (queued) | Medium | High | High |

## When to Use Each

- **Fixed Window**: Internal APIs with simple needs, logging/monitoring
- **Sliding Window**: Public APIs requiring precise limiting, billing endpoints
- **Token Bucket**: User-facing APIs where bursts are acceptable (page loads, scrolling)
- **Leaky Bucket**: APIs feeding downstream systems with strict rate requirements

## Mobile Analogy

Think of rate limiting like iOS App Transport Security (ATS) or Android Network Security Config -- they enforce rules about how your app communicates. Rate limiting enforces rules about how **often** clients can communicate.

Just as `URLSession` on iOS handles rate limit responses automatically with `waitsForConnectivity`, your backend rate limiter tells clients when to back off. The difference: on mobile you **react** to rate limits, on the backend you **enforce** them.

## Key Takeaways

1. **Fixed window** is simple but has the boundary burst problem -- use only for non-critical limits
2. **Sliding window** with Redis sorted sets gives precise per-second accuracy
3. **Token bucket** is the most practical for APIs -- it allows natural traffic bursts while enforcing average rates
4. **Choose based on your needs**: burst tolerance, precision requirements, and implementation complexity
5. **Redis is essential** for distributed rate limiting -- in-memory counters only work for single-server deployments
