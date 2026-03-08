# Redis Setup and Connection

## Why This Matters

On mobile, caching just works out of the box. `NSCache` is a single line of code. `LruCache` takes a size limit and you're done. There's no server to install, no connection to manage, no pooling to configure.

Backend caching with Redis requires infrastructure setup. Redis is a separate server process that your API connects to over the network. Getting the setup right -- Docker, connection pooling, lifecycle management -- is the foundation for everything else in this module.

Think of it like setting up a backend database (you did this in Module 006 with PostgreSQL). The same pattern applies: Docker container, client library, connection management.

## Installing Redis with Docker Compose

Redis runs as a separate service. The simplest way to run it locally is Docker Compose.

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  redis_data:
```

```bash
# Start Redis
docker-compose up -d redis

# Verify it's running
docker-compose exec redis redis-cli ping
# Output: PONG

# Interactive Redis CLI
docker-compose exec redis redis-cli
```

## The redis-py Library

Python's official Redis client is `redis-py`. It supports both synchronous and asynchronous operations.

```bash
pip install redis>=5.0.0
```

**Important**: Do NOT install `aioredis` separately. It was merged into `redis-py` in version 4.2+. The `redis.asyncio` module provides all async functionality.

### Synchronous Client

```python
import redis

# Create client with connection pooling (automatic)
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# Basic operations
r.set("name", "FastAPI Course")
value = r.get("name")
print(value)  # "FastAPI Course"

# Set with TTL (seconds)
r.setex("temp_key", 60, "expires in 1 minute")

# Check TTL remaining
ttl = r.ttl("temp_key")
print(f"Expires in {ttl} seconds")
```

### Asynchronous Client

```python
import redis.asyncio as redis

# Async client -- same API, async methods
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

async def example():
    await r.set("name", "FastAPI Course")
    value = await r.get("name")
    print(value)  # "FastAPI Course"

    await r.close()
```

## Connection Pooling

Redis connections are TCP sockets. Creating a new connection per request is wasteful and can exhaust file descriptors under load.

```python
import redis

# from_url() creates a connection pool automatically
# Default pool: max 10 connections
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# Explicit pool configuration
pool = redis.ConnectionPool.from_url(
    "redis://localhost:6379/0",
    max_connections=20,
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)
```

### Async Connection Pool

```python
import redis.asyncio as redis

# Async pool
pool = redis.ConnectionPool.from_url(
    "redis://localhost:6379/0",
    max_connections=20,
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)

async def example():
    await r.set("key", "value")
    await r.aclose()  # Close pool when done
```

## FastAPI Integration with Lifespan

Use FastAPI's `lifespan` context manager (not the deprecated `on_event`) to manage the Redis connection lifecycle.

```python
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create Redis connection on startup, close on shutdown."""
    app.state.redis = redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True
    )
    yield
    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)


async def get_redis(request: Request) -> redis.Redis:
    """Dependency to get Redis client from app state."""
    return request.app.state.redis


@app.get("/items/{item_id}")
async def get_item(
    item_id: int,
    cache: redis.Redis = Depends(get_redis)
):
    cached = await cache.get(f"item:{item_id}")
    if cached:
        return {"item": cached, "source": "cache"}

    # Simulate DB fetch
    item = f"Item {item_id}"
    await cache.setex(f"item:{item_id}", 3600, item)
    return {"item": item, "source": "database"}
```

### Why Lifespan, Not on_event?

```python
# DEPRECATED -- don't use
@app.on_event("startup")
async def startup():
    app.state.redis = redis.from_url(...)

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()

# CURRENT -- use lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.from_url(...)
    yield
    await app.state.redis.aclose()
```

The `lifespan` approach is cleaner because setup and teardown are in the same function, making it impossible to forget cleanup.

## Redis URL Format

```
redis://[[username:]password@]host[:port][/database]
```

| URL | Description |
|-----|-------------|
| `redis://localhost:6379/0` | Local Redis, database 0 |
| `redis://localhost:6379/1` | Local Redis, database 1 |
| `redis://:mypassword@redis.example.com:6379/0` | Remote with password |
| `rediss://redis.example.com:6380/0` | TLS-encrypted connection |

Redis has 16 databases by default (0-15). Use different databases for different purposes (e.g., 0 for cache, 1 for Celery broker).

## decode_responses Parameter

```python
# Without decode_responses (default) -- returns bytes
r = redis.from_url("redis://localhost:6379/0")
value = r.get("key")
# value = b"hello" (bytes)

# With decode_responses=True -- returns strings
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
value = r.get("key")
# value = "hello" (str)
```

**Always use `decode_responses=True`** unless you're storing binary data. It saves you from calling `.decode()` everywhere.

## Verifying the Connection

```python
import redis

r = redis.from_url("redis://localhost:6379/0")

# Ping test
try:
    response = r.ping()
    print(f"Redis connected: {response}")  # True
except redis.ConnectionError:
    print("Cannot connect to Redis")
```

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Redis |
|---------|-----------|----------------|--------------|
| Setup | `NSCache()` (zero config) | `LruCache(maxSize)` (one line) | Docker + `redis.from_url()` |
| Client library | Built into Foundation | Built into Android SDK | `pip install redis` |
| Connection | In-process (automatic) | In-process (automatic) | TCP socket (needs pooling) |
| Lifecycle | Tied to app lifecycle | Tied to app lifecycle | `lifespan` context manager |
| Configuration | Cache size, cost limit | Max size in bytes/entries | URL, pool size, TTL defaults |
| Multiple instances | No (single app) | No (single app) | Yes (shared across servers) |

## Key Takeaways

- Redis runs as a separate service -- install via Docker Compose for local development
- Use `redis-py` (not `aioredis`) for both sync and async operations
- `redis.asyncio` provides the async client -- import `redis.asyncio as redis`
- Always use `from_url()` with connection pooling (it handles pooling automatically)
- Use FastAPI `lifespan` context manager for connection lifecycle (not `on_event`)
- Set `decode_responses=True` to get strings instead of bytes
- Redis URLs follow the format: `redis://host:port/database`
