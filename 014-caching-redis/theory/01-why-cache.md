# Why Cache?

## Why This Matters

On mobile, you cache images and API responses to avoid re-downloading them. `NSCache` keeps recent images in memory so scrolling through a feed stays smooth. `URLCache` stores HTTP responses so the app loads instantly on launch.

Backend caching solves the same problem at a different scale. Instead of caching for one user on one device, you're caching for **thousands of users across multiple servers**. A single cached database query can save millions of database reads per day.

## The Speed Gap

Here's why caching matters -- the latency difference between data sources:

| Data Source | Typical Latency | Relative Speed |
|-------------|----------------|----------------|
| L1 CPU cache | ~0.5 ns | Reference |
| RAM | ~100 ns | 200x slower |
| Redis (local) | ~0.5 ms | 1,000,000x slower than L1, but... |
| PostgreSQL query | ~5 ms | 10x slower than Redis |
| External API call | ~100 ms | 200x slower than Redis |
| Cold database query (no index) | ~500 ms | 1000x slower than Redis |

**The key insight**: Redis at ~0.5ms is 10x faster than a database query at ~5ms. For a high-traffic endpoint hit 1000 times/second, caching turns 5 seconds of database time into 0.5 seconds of Redis time -- freeing your database for writes.

## Where Caching Fits

```
Client Request
     │
     ▼
┌─────────────┐
│  API Server  │
│              │──→ Check Redis Cache ──→ HIT? Return cached data (fast)
│              │                    │
│              │                    └──→ MISS? Query Database (slow)
│              │                              │
│              │                              ├──→ Store result in Redis
│              │                              └──→ Return data
└─────────────┘
```

## Cache Hit vs Cache Miss

- **Cache Hit**: Data found in Redis. Return immediately (~0.5ms)
- **Cache Miss**: Data not in Redis. Fetch from database (~5ms), store in Redis, return

The **hit rate** is the percentage of requests served from cache. A 90% hit rate means 9 out of 10 requests skip the database entirely.

```python
# Pseudocode for cache-aside pattern
async def get_user(user_id: int):
    # 1. Check cache (fast)
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return cached  # Cache HIT

    # 2. Cache miss -- fetch from database (slow)
    user = await db.get_user(user_id)

    # 3. Store in cache for next time
    await redis.setex(f"user:{user_id}", 3600, user)

    return user
```

## What to Cache

### Good Candidates for Caching

| Data Type | Why Cache It | Example TTL |
|-----------|-------------|-------------|
| User profiles | Read frequently, change rarely | 1 hour |
| Product listings | Same data served to many users | 15 minutes |
| Configuration/settings | Almost never changes | 24 hours |
| API responses (external) | Expensive external calls | 5 minutes |
| Computed aggregations | Expensive to calculate | 1 hour |
| Session data | Read on every request | Until logout |

### Poor Candidates for Caching

| Data Type | Why Not Cache | Better Approach |
|-----------|--------------|-----------------|
| Real-time stock prices | Changes every second | WebSocket stream |
| One-time-use tokens | Used once, then invalid | Database only |
| Large files/blobs | Redis is in-memory (expensive) | Object storage (S3) |
| Frequently mutated data | Cache invalidation overhead too high | Direct database reads |

## Benefits of Caching

1. **Lower latency**: Responses are faster (0.5ms vs 5ms+)
2. **Reduced database load**: Fewer queries hit the database
3. **Cost reduction**: Database connections and compute are expensive
4. **Higher throughput**: Serve more requests per second
5. **Resilience**: Cache can serve stale data if database is temporarily down

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Redis |
|---------|-----------|----------------|--------------|
| Purpose | Smooth UI, offline support | Smooth UI, offline support | Fast responses, reduce DB load |
| Scope | Single device | Single device | All servers |
| Eviction | Memory pressure (automatic) | Manual or LRU | Configurable policy |
| TTL | Limited (`URLCache`) | Limited (custom) | Built-in (`SETEX`, `EXPIRE`) |
| Hit/miss tracking | Custom implementation | Custom implementation | Redis `INFO stats` |
| Cache warming | On app launch | On app launch | On server start or first request |

## The Two Hard Problems

Phil Karlton famously said:

> "There are only two hard things in Computer Science: cache invalidation and naming things."

**Cache invalidation** -- knowing when to remove or update cached data -- is the primary challenge. You'll learn strategies for this in the upcoming theory files. For now, remember:

- **Stale data is the main risk** of caching
- **TTL is your safety net** -- cached data expires automatically
- **Active invalidation** -- deleting cache on write -- keeps data fresh

## Key Takeaways

- Caching stores frequently accessed data in fast memory (Redis) instead of querying the database
- Redis is ~10x faster than PostgreSQL for simple lookups
- Cache-aside pattern: check cache first, fall back to database, store result
- Good cache candidates: read-heavy, slowly-changing data (user profiles, product listings)
- Bad cache candidates: real-time data, one-time tokens, large blobs
- Cache invalidation (keeping cached data fresh) is the hardest part
- Mobile parallel: Redis is like `NSCache`/`LruCache`, but shared across all servers and with built-in TTL
