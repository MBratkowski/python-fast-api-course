# Project: Caching Layer for REST API

## Overview

Build a caching layer for a product catalog API using Redis. You'll implement cache-aside reads, invalidation on mutations, configurable TTL per entity type, and a cache statistics endpoint.

This project uses **real Redis via Docker Compose** (unlike the exercises which used fakeredis). You'll connect to Redis, manage the connection lifecycle with FastAPI lifespan, and see caching behavior in a production-like setup.

## What You'll Build

A FastAPI application with:
- Product CRUD endpoints with Redis caching
- Cache-aside pattern on all GET endpoints
- Automatic cache invalidation on POST/PUT/DELETE
- Configurable TTL per entity type
- A `/cache/stats` endpoint showing hit rate and key count

## Requirements

### Infrastructure

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: products
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
```

### Dependencies

```bash
pip install fastapi uvicorn redis sqlalchemy psycopg2-binary
```

### Functional Requirements

1. **GET /products/{id}** -- Cache-aside: check Redis, fall back to DB, cache result
2. **GET /products/** -- Cache-aside for list queries with pagination
3. **POST /products/** -- Create product, invalidate list caches
4. **PUT /products/{id}** -- Update product, invalidate specific entry + list caches
5. **DELETE /products/{id}** -- Delete product, invalidate specific entry + list caches
6. **GET /cache/stats** -- Return cache hit/miss counts, hit rate, total keys

### Non-Functional Requirements

- Redis connection managed via FastAPI lifespan (not `on_event`)
- Connection pooling with `redis.asyncio.from_url()`
- All cache keys follow pattern: `product:{id}` or `products:list:page:{n}`
- TTL: 30 minutes for individual products, 5 minutes for list queries
- `decode_responses=True` on Redis client

## Starter Template

```python
"""Product Catalog API with Redis Caching Layer."""
import json
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel

# ============= Configuration =============

REDIS_URL = "redis://localhost:6379/0"
PRODUCT_TTL = 1800      # 30 minutes
LIST_TTL = 300           # 5 minutes

# ============= Schemas =============

class ProductCreate(BaseModel):
    name: str
    price: float
    category: str

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    category: str | None = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str

# ============= Redis Lifecycle =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """TODO: Create Redis connection on startup, close on shutdown."""
    # TODO: Set up app.state.redis using redis.from_url()
    # TODO: Initialize cache stats counters
    yield
    # TODO: Close Redis connection

app = FastAPI(lifespan=lifespan)

# ============= Dependencies =============

async def get_redis(request: Request) -> redis.Redis:
    """TODO: Return Redis client from app state."""
    pass

async def get_db():
    """TODO: Return database session."""
    pass

# ============= Cache Helpers =============

async def cache_get(r: redis.Redis, key: str) -> dict | None:
    """TODO: Get from cache, track hit/miss stats."""
    # Increment hit or miss counter in Redis
    pass

async def cache_set(r: redis.Redis, key: str, data: dict, ttl: int) -> None:
    """TODO: Store in cache with TTL."""
    pass

async def cache_invalidate(r: redis.Redis, *keys: str) -> None:
    """TODO: Delete one or more cache keys."""
    pass

async def invalidate_product_lists(r: redis.Redis) -> None:
    """TODO: Invalidate all cached product list queries."""
    # Use SCAN to find keys matching "products:list:*"
    pass

# ============= Endpoints =============

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    r: redis.Redis = Depends(get_redis),
    db=Depends(get_db)
):
    """TODO: Implement cache-aside for single product."""
    pass

@app.get("/products/", response_model=list[ProductResponse])
async def list_products(
    page: int = 1,
    per_page: int = 20,
    r: redis.Redis = Depends(get_redis),
    db=Depends(get_db)
):
    """TODO: Implement cache-aside for product list."""
    pass

@app.post("/products/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    r: redis.Redis = Depends(get_redis),
    db=Depends(get_db)
):
    """TODO: Create product and invalidate list caches."""
    pass

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    r: redis.Redis = Depends(get_redis),
    db=Depends(get_db)
):
    """TODO: Update product and invalidate caches."""
    pass

@app.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    r: redis.Redis = Depends(get_redis),
    db=Depends(get_db)
):
    """TODO: Delete product and invalidate caches."""
    pass

@app.get("/cache/stats")
async def cache_stats(r: redis.Redis = Depends(get_redis)):
    """TODO: Return cache statistics."""
    # Read hit/miss counters from Redis
    # Calculate hit rate
    # Count total cached keys
    pass
```

## Success Criteria

- [ ] GET endpoints return cached data on second request (verify with response time or log)
- [ ] PUT/DELETE endpoints clear the cache for the modified product
- [ ] POST/PUT/DELETE endpoints clear list caches (so list queries get fresh data)
- [ ] Cache stats endpoint shows accurate hit/miss counts
- [ ] Redis connection is properly set up in lifespan and closed on shutdown
- [ ] All cache keys have TTL set (no keys without expiration)
- [ ] Application works correctly even if Redis is down (graceful fallback to DB)

## Testing Your Implementation

```bash
# Start services
docker-compose up -d

# Run the API
uvicorn main:app --reload

# Test cache-aside
curl http://localhost:8000/products/1       # Cache miss (DB query)
curl http://localhost:8000/products/1       # Cache hit (from Redis)

# Test invalidation
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Widget"}'
curl http://localhost:8000/products/1       # Cache miss (invalidated, fresh from DB)

# Check stats
curl http://localhost:8000/cache/stats
```

## Stretch Goals

1. **HTTP Cache Headers**: Add `ETag` and `Cache-Control` headers to responses so clients can cache too
2. **Cache Warming**: Pre-populate cache on startup with the most popular products
3. **Redis Pub/Sub**: Use Redis pub/sub to notify other API instances when cache is invalidated (for multi-server deployments)
4. **Cache Decorator**: Build a `@cached(ttl=300)` decorator that automatically caches endpoint responses
5. **Metrics Dashboard**: Add Prometheus metrics for cache hit rate, latency, and key count

## Hints

- Use `redis.asyncio.from_url()` with `decode_responses=True` for the async client
- Track hits/misses using Redis `INCR` on counter keys (`cache:hits`, `cache:misses`)
- Use `SCAN` (not `KEYS`) to find keys matching a pattern in production
- Wrap Redis calls in try/except to handle connection failures gracefully
- Use `pipeline()` when invalidating multiple keys for efficiency
