# Cache Invalidation

## Why This Matters

Phil Karlton famously said: "There are only two hard things in Computer Science: cache invalidation and naming things."

On mobile, cache invalidation is usually simple: pull-to-refresh clears the cache, or the OS evicts entries under memory pressure. You rarely think about it because one user on one device means one cache to manage.

Backend cache invalidation is harder because: (1) multiple servers share the same cache, (2) any write must invalidate the right cache entries, and (3) forgetting to invalidate means users see stale data. Getting this wrong is how bugs like "I updated my profile but it still shows the old name" happen.

## The Core Problem

```
Timeline:
  T=0  User reads profile    → cached in Redis as user:42
  T=5  User updates email    → written to database
  T=10 User reads profile    → Redis still has old email (STALE!)
  T=60 TTL expires           → Redis deletes old data
  T=61 User reads profile    → cache miss → fresh data from DB
```

Between T=5 and T=60, the user sees stale data. Cache invalidation strategies reduce or eliminate this window.

## Strategy 1: TTL-Based (Passive)

The simplest strategy. Data expires automatically after a set time. You accept some staleness in exchange for zero invalidation logic.

```python
# Set with TTL -- expires in 15 minutes
await cache.setex("product:100", 900, json.dumps(product_data))

# Data might be up to 15 minutes stale -- acceptable for product listings
# No invalidation code needed
```

**When to use:** Data where staleness is acceptable (product catalogs, aggregated stats, external API responses).

**When NOT to use:** Data where staleness causes bugs (user profile shown to the user, inventory counts for checkout).

## Strategy 2: Explicit Delete on Write (Active)

Delete the cached entry whenever the underlying data changes. The next read triggers a cache miss and fetches fresh data.

```python
import json
import redis.asyncio as redis


class UserService:
    def __init__(self, db, cache: redis.Redis):
        self.db = db
        self.cache = cache

    async def get_user(self, user_id: int) -> dict:
        """Read with cache-aside."""
        cache_key = f"user:{user_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        user = await self.db.get_user(user_id)
        if user:
            await self.cache.setex(cache_key, 3600, json.dumps(user))
        return user

    async def update_user(self, user_id: int, data: dict) -> dict:
        """Write with cache invalidation."""
        # 1. Update database
        user = await self.db.update_user(user_id, data)

        # 2. Invalidate cache (delete, don't update)
        await self.cache.delete(f"user:{user_id}")

        return user

    async def delete_user(self, user_id: int) -> None:
        """Delete with cache invalidation."""
        await self.db.delete_user(user_id)
        await self.cache.delete(f"user:{user_id}")
```

### Why Delete, Not Update?

```python
# BAD: Update cache on write (write-through)
async def update_user(self, user_id: int, data: dict):
    user = await self.db.update_user(user_id, data)
    await self.cache.setex(f"user:{user_id}", 3600, json.dumps(user))
    # Problem: race condition if two concurrent updates happen
    # DB might have version B, but cache stored version A

# GOOD: Delete cache on write (invalidate)
async def update_user(self, user_id: int, data: dict):
    user = await self.db.update_user(user_id, data)
    await self.cache.delete(f"user:{user_id}")
    # Next read gets fresh data from DB -- no race condition
```

Deleting is safer than updating because it avoids race conditions between concurrent writes.

## Strategy 3: Tag-Based Invalidation

Group related cache keys so you can invalidate them together. Useful when one change affects multiple cached entries.

```python
class TaggedCache:
    """Cache with tag-based invalidation."""

    def __init__(self, cache: redis.Redis):
        self.cache = cache

    async def set_with_tags(
        self,
        key: str,
        value: str,
        ttl: int,
        tags: list[str]
    ):
        """Store value and register it under tags."""
        # Store the value
        await self.cache.setex(key, ttl, value)

        # Register key under each tag
        for tag in tags:
            await self.cache.sadd(f"tag:{tag}", key)

    async def invalidate_tag(self, tag: str):
        """Delete all keys associated with a tag."""
        tag_key = f"tag:{tag}"

        # Get all keys in this tag group
        keys = await self.cache.smembers(tag_key)

        if keys:
            # Delete all cached values
            await self.cache.delete(*keys)

        # Delete the tag set itself
        await self.cache.delete(tag_key)


# Usage example
tagged_cache = TaggedCache(cache)

# Cache a user's orders (tagged with both user and orders)
await tagged_cache.set_with_tags(
    "orders:user:42",
    json.dumps(orders),
    ttl=1800,
    tags=["user:42", "orders"]
)

# Cache the order count (also tagged)
await tagged_cache.set_with_tags(
    "order_count:user:42",
    "5",
    ttl=1800,
    tags=["user:42", "orders"]
)

# When a new order is placed: invalidate all order-related caches
await tagged_cache.invalidate_tag("orders")

# When a user is deleted: invalidate everything for that user
await tagged_cache.invalidate_tag("user:42")
```

## Consistent Key Naming

Consistent cache key patterns make invalidation predictable:

```python
# Pattern: entity_type:entity_id
"user:42"
"product:100"
"order:789"

# Pattern: entity_type:entity_id:sub_resource
"user:42:orders"
"user:42:preferences"
"product:100:reviews"

# Pattern: list with filters
"products:category:electronics:page:1"
"users:role:admin"
```

**Rules:**
1. Use lowercase
2. Use colons as separators
3. Start with the entity type
4. Include the ID
5. Be consistent across the codebase

```python
def cache_key(entity: str, entity_id: int, *parts: str) -> str:
    """Generate consistent cache keys."""
    key = f"{entity}:{entity_id}"
    if parts:
        key += ":" + ":".join(parts)
    return key

# Usage
cache_key("user", 42)            # "user:42"
cache_key("user", 42, "orders")  # "user:42:orders"
cache_key("product", 100)        # "product:100"
```

## Invalidation on CRUD Operations

Always invalidate on create, update, and delete. This is the most important rule.

```python
class CachedProductService:
    def __init__(self, db, cache: redis.Redis):
        self.db = db
        self.cache = cache
        self.ttl = 1800  # 30 minutes

    async def get_product(self, product_id: int) -> dict | None:
        """READ: Cache-aside."""
        key = f"product:{product_id}"
        cached = await self.cache.get(key)
        if cached:
            return json.loads(cached)

        product = await self.db.get_product(product_id)
        if product:
            await self.cache.setex(key, self.ttl, json.dumps(product))
        return product

    async def create_product(self, data: dict) -> dict:
        """CREATE: Invalidate list caches."""
        product = await self.db.create_product(data)
        # New product affects list queries
        await self._invalidate_product_lists()
        return product

    async def update_product(self, product_id: int, data: dict) -> dict:
        """UPDATE: Invalidate specific entry and lists."""
        product = await self.db.update_product(product_id, data)
        await self.cache.delete(f"product:{product_id}")
        await self._invalidate_product_lists()
        return product

    async def delete_product(self, product_id: int) -> None:
        """DELETE: Invalidate specific entry and lists."""
        await self.db.delete_product(product_id)
        await self.cache.delete(f"product:{product_id}")
        await self._invalidate_product_lists()

    async def _invalidate_product_lists(self):
        """Delete all cached product list queries."""
        # Use SCAN to find matching keys (don't use KEYS in production)
        async for key in self.cache.scan_iter("products:*"):
            await self.cache.delete(key)
```

## Invalidation Patterns Summary

| Strategy | Freshness | Complexity | Use Case |
|----------|-----------|------------|----------|
| TTL-only | Eventual (up to TTL) | None | Reference data, external APIs |
| Delete on write | Immediate (next read) | Low | Single entity caches |
| Tag-based | Immediate (next read) | Medium | Related entity groups |
| TTL + delete on write | Immediate + safety net | Low | Most production caches |

**Recommended default**: Combine TTL with explicit delete on write. TTL handles edge cases where invalidation is missed. Explicit delete handles the common case.

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Redis |
|---------|-----------|----------------|--------------|
| Automatic expiry | Memory pressure | LRU eviction | TTL (explicit) |
| Manual invalidation | `removeObject(forKey:)` | `remove(key)` | `cache.delete(key)` |
| Clear all | `removeAllObjects()` | `evictAll()` | `cache.flushdb()` |
| Group invalidation | Not built-in | Not built-in | Tag-based + SCAN |
| Stale-while-revalidate | URLCache (HTTP) | OkHttp (HTTP) | Custom implementation |
| Consistency guarantee | Single device (easy) | Single device (easy) | Multiple servers (hard) |

## Key Takeaways

- Cache invalidation means removing stale data when the underlying source changes
- **Always invalidate on create, update, and delete** -- this is the most important rule
- Use **delete (not update)** on write to avoid race conditions
- Combine **TTL + explicit delete**: TTL is the safety net, delete handles the fast path
- Use **consistent key naming** (`entity:id`) to make invalidation predictable
- **Tag-based invalidation** lets you group related keys and invalidate them together
- Never use `KEYS *` in production -- use `SCAN` for pattern-based deletion
- Mobile parallel: `removeObject(forKey:)` (iOS) / `remove(key)` (Android) is equivalent to `cache.delete(key)`
