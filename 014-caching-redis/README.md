# Module 014: Caching with Redis

## Why This Module?

Learn server-side caching to make your API fast. Caching stores frequently accessed data in memory so your endpoints skip expensive database queries. A cached response can be 10x faster than hitting the database every time.

## What You'll Learn

- Why caching matters and where it fits in the request lifecycle
- Redis setup with Docker and connection management
- Caching patterns: cache-aside, write-through, read-through
- TTL (Time-To-Live) and expiration strategies
- Cache invalidation: the hardest problem in computer science
- Redis data structures beyond simple key-value

## Mobile Developer Context

You've used in-memory caching on mobile: `NSCache` (iOS), `LruCache` (Android), image caching with libraries like Kingfisher or Coil. Mobile caches live in the app's process memory and disappear when the app is killed.

Server-side caching with Redis is fundamentally different: **the cache is an external service shared across all API instances**. Multiple servers read and write the same cache, making it a coordination point for your entire backend.

**Caching Across Platforms:**

| Concept | iOS/Swift | Android/Kotlin | Python/Redis |
|---------|-----------|----------------|--------------|
| In-memory cache | `NSCache` | `LruCache` | `redis.Redis` (external) |
| Disk cache | `URLCache` | `DiskLruCache` | Redis persistence (RDB/AOF) |
| TTL/expiry | `NSCache.countLimit` | `ExpiringMap` (third-party) | `SETEX` / `EXPIRE` (built-in) |
| Cache eviction | Automatic (memory pressure) | Manual or LRU | `maxmemory-policy allkeys-lru` |
| Shared across instances | No (single device) | No (single device) | Yes (all servers share Redis) |
| Survives app restart | `URLCache` (disk) | `DiskLruCache` | Yes (Redis persistence) |

**Key Differences from Mobile:**

1. **External service**: Redis runs as a separate process (often Docker container), not in your app's memory
2. **Shared state**: All API instances share the same Redis cache -- invalidation affects everyone
3. **Network hop**: Cache access involves a network call (~0.5ms vs ~0ns for in-memory)
4. **Explicit management**: You control TTL, eviction, and invalidation -- no OS memory pressure handling
5. **Rich data structures**: Redis supports strings, hashes, sets, sorted sets, lists -- not just key-value

## Topics

### Theory
1. Why Cache?
2. Redis Setup and Connection
3. Caching Patterns
4. TTL and Expiration
5. Cache Invalidation
6. Redis Data Structures

### Exercises
1. Basic Caching (with fakeredis)
2. TTL Management
3. Cache Invalidation

### Project
Add a caching layer to an API with cache-aside pattern, invalidation on mutations, and configurable TTL.

## Example

```python
import json
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Redis connection lifecycle."""
    app.state.redis = redis.from_url(
        "redis://localhost:6379",
        decode_responses=True
    )
    yield
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    cache = app.state.redis
    cache_key = f"user:{user_id}"

    # Check cache first
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)  # Cache hit: ~0.5ms

    # Cache miss: fetch from database (~5ms)
    user = await fetch_user_from_db(user_id)

    # Store in cache with 1-hour TTL
    await cache.setex(cache_key, 3600, json.dumps(user))

    return user
```

## Quick Assessment

Before starting this module, ask yourself:
- Have you used `NSCache` (iOS) or `LruCache` (Android)?
- Do you understand why reading from memory is faster than querying a database?
- Have you dealt with stale data in mobile caches?

If yes, you're ready. The concepts are the same -- the tools are just different.

## Time Estimate

6-8 hours total:
- Theory: 2-3 hours
- Exercises: 2-3 hours
- Project: 2-3 hours

## Key Differences from Mobile

1. **External service**: Redis is not in your app's memory -- it's a separate server
2. **Shared across instances**: All API servers share the same cache (unlike per-device mobile caches)
3. **Explicit TTL**: You set expiration times explicitly (no automatic memory pressure eviction)
4. **Cache invalidation**: When data changes, you must explicitly delete cached values
5. **Rich data types**: Redis supports hashes, sets, sorted sets, lists -- far beyond simple key-value
