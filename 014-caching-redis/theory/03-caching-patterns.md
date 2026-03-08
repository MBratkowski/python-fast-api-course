# Caching Patterns

## Why This Matters

On mobile, caching patterns are straightforward: check `NSCache` or `LruCache`, fetch from network if not found, store the result. You don't think much about it because the cache serves one user on one device.

Backend caching is more nuanced because the cache serves many users across multiple server instances. Different read/write patterns call for different caching strategies. Picking the wrong pattern leads to stale data, inconsistent reads, or wasted cache space.

This file covers the three main caching patterns you'll encounter: cache-aside (most common), write-through, and read-through. Most backends use cache-aside for 90% of use cases.

## Pattern 1: Cache-Aside (Look-Aside)

The most common pattern. Your application code manages both the cache and the database explicitly.

**Flow:**
1. Application checks cache
2. On miss: fetch from database
3. Store result in cache
4. Return data

```
Client Request
     │
     ▼
Application Code
     │
     ├──→ GET from Redis ──→ HIT? Return data
     │                  │
     │                  └──→ MISS
     │                        │
     ├──→ SELECT from Database │
     │                        │
     ├──→ SET in Redis ◄──────┘
     │
     ▼
Return Response
```

### Implementation

```python
import json
import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request, HTTPException

# Assume redis client is set up via lifespan (see 02-redis-setup.md)

async def get_user_cached(
    user_id: int,
    cache: redis.Redis,
    db  # your database session
) -> dict:
    """Cache-aside pattern for user lookup."""
    cache_key = f"user:{user_id}"

    # Step 1: Check cache
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)  # Cache HIT

    # Step 2: Cache miss -- fetch from database
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 3: Store in cache with TTL
    user_data = {"id": user.id, "name": user.name, "email": user.email}
    await cache.setex(cache_key, 3600, json.dumps(user_data))  # 1 hour TTL

    return user_data
```

### When to Use Cache-Aside

- Read-heavy workloads (read:write ratio > 10:1)
- Data that changes infrequently (user profiles, product listings)
- When you need fine-grained control over what gets cached

### Pros and Cons

| Pros | Cons |
|------|------|
| Simple to understand and implement | Application manages both cache and DB |
| Only caches data that's actually requested | Cache miss has extra latency (cache check + DB + cache write) |
| Works with any database | Data can be stale until TTL expires or manually invalidated |
| Resilient: if Redis fails, app still works (just slower) | Cold cache problem on startup |

## Pattern 2: Write-Through

Data is written to cache AND database simultaneously. The cache is always up-to-date.

**Flow:**
1. Application writes to cache
2. Cache writes to database (or application writes to both)
3. Read always hits cache (guaranteed fresh)

```python
async def update_user_write_through(
    user_id: int,
    update_data: dict,
    cache: redis.Redis,
    db
) -> dict:
    """Write-through: update both cache and DB."""
    # Step 1: Update database
    user = await db.update_user(user_id, update_data)

    # Step 2: Update cache immediately (always in sync)
    cache_key = f"user:{user_id}"
    user_data = {"id": user.id, "name": user.name, "email": user.email}
    await cache.setex(cache_key, 3600, json.dumps(user_data))

    return user_data
```

### When to Use Write-Through

- When data consistency between cache and DB is critical
- When reads vastly outnumber writes
- Configuration data, user settings

### Pros and Cons

| Pros | Cons |
|------|------|
| Cache is always consistent with DB | Every write has double latency (cache + DB) |
| No stale data | Caches data that may never be read |
| Simple read path (always from cache) | More complex write path |

## Pattern 3: Read-Through

Similar to cache-aside, but the cache itself handles fetching from the database on a miss. The application only talks to the cache.

```python
class ReadThroughCache:
    """Cache that automatically fetches from DB on miss."""

    def __init__(self, cache: redis.Redis, db, ttl: int = 3600):
        self.cache = cache
        self.db = db
        self.ttl = ttl

    async def get_user(self, user_id: int) -> dict | None:
        cache_key = f"user:{user_id}"

        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Cache miss -- fetch and store automatically
        user = await self.db.get_user(user_id)
        if user:
            user_data = {"id": user.id, "name": user.name, "email": user.email}
            await self.cache.setex(cache_key, self.ttl, json.dumps(user_data))
            return user_data

        return None
```

### When to Use Read-Through

- When you want to abstract caching from business logic
- When the same pattern applies to many entity types
- Libraries like `dogpile.cache` implement this pattern

## Pattern Comparison

| Feature | Cache-Aside | Write-Through | Read-Through |
|---------|-------------|---------------|--------------|
| Who manages cache? | Application | Application (both sides) | Cache layer |
| Data freshness | Stale until TTL/invalidation | Always fresh | Stale until TTL/invalidation |
| Write latency | Normal (DB only) | Higher (DB + cache) | Normal (DB only) |
| Read latency (hit) | Fast | Fast | Fast |
| Read latency (miss) | Slow (cache + DB + cache write) | N/A (always cached on write) | Slow (same as cache-aside) |
| Complexity | Low | Medium | Medium |
| Most common? | Yes (90%+ of backends) | Sometimes | Rarely (usually via library) |

## Building a Reusable Cache Helper

For real applications, wrap the cache-aside pattern in a reusable helper:

```python
import json
from typing import Callable, TypeVar
import redis.asyncio as redis

T = TypeVar("T")


async def cache_or_fetch(
    cache: redis.Redis,
    key: str,
    fetch_fn: Callable,
    ttl: int = 3600
) -> dict | None:
    """
    Generic cache-aside helper.

    Usage:
        user = await cache_or_fetch(
            cache, f"user:{user_id}",
            lambda: db.get_user(user_id),
            ttl=3600
        )
    """
    # Check cache
    cached = await cache.get(key)
    if cached:
        return json.loads(cached)

    # Fetch from source
    result = await fetch_fn()
    if result is None:
        return None

    # Store in cache
    data = result if isinstance(result, dict) else result.__dict__
    await cache.setex(key, ttl, json.dumps(data))

    return data
```

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Redis |
|---------|-----------|----------------|--------------|
| Default pattern | Cache-aside (NSCache) | Cache-aside (LruCache) | Cache-aside (explicit) |
| HTTP caching | URLCache (automatic) | OkHttp cache (automatic) | Manual with Redis |
| Write-through | Core Data + NSCache | Room + LruCache | Application manages both |
| Cache abstraction | NSCache protocol | Cache interface | Custom helper or library |
| Automatic loading | NSCache (no auto-load) | LruCache `create()` | Read-through pattern |

## Key Takeaways

- **Cache-aside** is the default pattern for most backends -- application checks cache, falls back to DB, stores result
- **Write-through** keeps cache always fresh but adds write latency -- use for critical consistency needs
- **Read-through** abstracts the caching logic -- useful for reusable cache layers
- Most production systems use **cache-aside for reads** combined with **explicit invalidation on writes**
- Build a reusable `cache_or_fetch` helper to avoid duplicating cache-aside logic across endpoints
- Mobile parallel: `NSCache` and `LruCache` are essentially cache-aside -- check cache first, fetch if missing
