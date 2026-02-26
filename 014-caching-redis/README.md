# Module 014: Caching with Redis

## Why This Module?

Reduce database load and speed up responses. Redis is the go-to caching solution for Python APIs.

## What You'll Learn

- Redis fundamentals
- Caching strategies
- Cache invalidation
- Session storage
- Rate limiting with Redis
- Redis data structures

## Topics

### Theory
1. Why Cache?
2. Redis Setup & CLI
3. Caching Patterns (Cache-aside, Write-through)
4. TTL & Expiration
5. Cache Invalidation Strategies
6. Redis Data Structures

### Project
Add caching layer to your API for frequently accessed data.

## Example

```python
import redis.asyncio as redis
from functools import wraps

redis_client = redis.from_url("redis://localhost:6379")

def cache(ttl: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache first
            cached = await redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Compute and cache
            result = await func(*args, **kwargs)
            await redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache(ttl=300)
async def get_user(user_id: int) -> dict:
    return await db.fetch_user(user_id)
```
