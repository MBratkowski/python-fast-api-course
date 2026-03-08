# TTL and Expiration

## Why This Matters

On mobile, `NSCache` evicts entries automatically under memory pressure. You don't set explicit timeouts -- the OS decides when to drop cached data. Android's `LruCache` evicts the least-recently-used entry when the cache is full.

Server-side caching with Redis requires you to set explicit expiration times. Without TTL (Time-To-Live), cached data lives forever, consuming memory and becoming increasingly stale. TTL is your safety net against both stale data and memory exhaustion.

## What Is TTL?

TTL (Time-To-Live) is the number of seconds before a cached key automatically expires and is deleted by Redis.

```python
import redis

r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# Set a key with 60-second TTL
r.setex("session:abc123", 60, "user_data_here")

# Check remaining TTL
ttl = r.ttl("session:abc123")
print(f"Expires in {ttl} seconds")  # Expires in ~60 seconds

# After 60 seconds...
value = r.get("session:abc123")
print(value)  # None (expired and deleted)
```

## Setting TTL

### At Write Time (Recommended)

```python
# SETEX: Set value with TTL in one atomic command
r.setex("user:42", 3600, '{"name": "Alice"}')  # 1 hour

# SET with EX parameter (same effect)
r.set("user:42", '{"name": "Alice"}', ex=3600)  # 1 hour

# SET with PX parameter (milliseconds)
r.set("user:42", '{"name": "Alice"}', px=3600000)  # 1 hour in ms
```

### After Write

```python
# Set TTL on an existing key
r.set("user:42", '{"name": "Alice"}')
r.expire("user:42", 3600)  # Set 1-hour TTL

# Set absolute expiration time
from datetime import datetime, timedelta
expires_at = datetime.now() + timedelta(hours=1)
r.expireat("user:42", expires_at)
```

### Remove TTL (Make Persistent)

```python
# Remove TTL -- key will never expire
r.persist("user:42")

# Check if key has TTL
ttl = r.ttl("user:42")
# -1 means no TTL (persistent)
# -2 means key doesn't exist
# Positive number = seconds remaining
```

## Choosing TTL Values

Different data types need different TTL values. The right TTL balances freshness against cache hit rate.

| Data Type | Suggested TTL | Rationale |
|-----------|--------------|-----------|
| User session | 30 minutes | Security: limit session lifetime |
| User profile | 1 hour | Changes infrequently, read often |
| Product listing | 15 minutes | Balance freshness with performance |
| Configuration/settings | 24 hours | Rarely changes |
| External API response | 5 minutes | Reduce API calls, accept some staleness |
| Search results | 10 minutes | Results change as data is added |
| Dashboard aggregations | 1 hour | Expensive to compute, okay if slightly stale |
| Feature flags | 5 minutes | Short TTL for quick propagation of changes |

### The TTL Tradeoff

```
Short TTL (seconds)                    Long TTL (hours/days)
├── Fresher data                       ├── Higher cache hit rate
├── More DB queries                    ├── Fewer DB queries
├── Lower cache hit rate               ├── Data might be stale
└── Higher database load               └── Lower database load
```

**Rule of thumb**: Start with a 1-hour TTL, then adjust based on how fresh the data needs to be and how often it changes.

## Sliding Expiration

Reset the TTL every time a key is accessed, keeping frequently-accessed data alive longer.

```python
async def get_with_sliding_ttl(
    cache: redis.Redis,
    key: str,
    ttl: int = 3600
) -> str | None:
    """Get value and refresh TTL on access."""
    value = await cache.get(key)
    if value:
        # Reset TTL -- key stays alive while being accessed
        await cache.expire(key, ttl)
    return value
```

**Use sliding expiration for:**
- User sessions (keep active sessions alive)
- Rate limiting windows
- Any data that should expire only when unused

**Avoid sliding expiration for:**
- Data with strict freshness requirements (always use fixed TTL)
- Data that must expire regardless of access pattern

## Memory Management

Redis stores everything in memory. Without TTL and eviction policies, Redis will eventually run out of memory.

### Max Memory Configuration

```
# redis.conf or docker-compose command
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Eviction Policies

| Policy | Behavior | When to Use |
|--------|----------|-------------|
| `noeviction` | Reject writes when full | When you can't lose any cached data |
| `allkeys-lru` | Evict least recently used key | General caching (most common) |
| `volatile-lru` | Evict LRU among keys with TTL | Mix of cache and persistent keys |
| `allkeys-random` | Evict random key | When all keys have equal value |
| `volatile-ttl` | Evict keys closest to expiration | When short TTL = less important |

**Recommended default**: `allkeys-lru` -- Redis behaves like `LruCache` on Android, evicting the least recently used entries when memory is full.

## Anti-Pattern: Caching Without TTL

```python
# BAD: No TTL -- data lives forever
await cache.set("user:42", json.dumps(user_data))
# If user updates their profile, cache serves stale data indefinitely
# If 100,000 users are cached, Redis memory grows without bound

# GOOD: Always set TTL
await cache.setex("user:42", 3600, json.dumps(user_data))
# Stale data expires automatically after 1 hour
# Memory is reclaimed as keys expire
```

**Every cached key should have a TTL.** Even if you actively invalidate on writes, TTL is your safety net for edge cases where invalidation fails.

## Monitoring TTL

```python
import redis

r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

def inspect_key(key: str):
    """Check a key's type, value, and TTL."""
    key_type = r.type(key)
    ttl = r.ttl(key)
    value = r.get(key) if key_type == "string" else f"[{key_type}]"

    if ttl == -1:
        print(f"{key}: {value} (no TTL -- persistent)")
    elif ttl == -2:
        print(f"{key}: does not exist")
    else:
        print(f"{key}: {value} (expires in {ttl}s)")
```

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Redis |
|---------|-----------|----------------|--------------|
| Expiration mechanism | Memory pressure (automatic) | LRU eviction (automatic) | TTL (explicit, per-key) |
| Set expiry | `NSCache.totalCostLimit` | `LruCache(maxSize)` | `setex(key, ttl, value)` |
| Sliding expiry | Not built-in | Not built-in | `expire(key, ttl)` on read |
| Memory limit | System-managed | `maxSize` in constructor | `maxmemory` config |
| Eviction policy | System decides | LRU only | 6+ policies available |
| Check remaining time | Not available | Not available | `ttl(key)` returns seconds |

## Key Takeaways

- **Always set TTL** on cached keys -- it prevents stale data and memory exhaustion
- Use `setex()` to set value and TTL atomically (preferred over separate `set` + `expire`)
- Choose TTL based on data freshness needs: sessions (30 min), profiles (1 hr), config (24 hr)
- **Sliding expiration** resets TTL on access -- good for sessions, bad for strict freshness
- Configure `maxmemory` and `maxmemory-policy` (use `allkeys-lru` as default)
- TTL is your safety net even when you actively invalidate -- covers edge cases
- Mobile parallel: TTL is like `NSCache` memory pressure eviction, but you control the timing explicitly
