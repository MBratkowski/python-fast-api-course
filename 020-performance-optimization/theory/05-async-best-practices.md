# Async Best Practices

## Why This Matters

On iOS, you use Grand Central Dispatch or Swift's async/await to keep heavy work off the main thread so the UI stays responsive. On Android, you use Kotlin coroutines with `Dispatchers.IO` for network and disk operations and `Dispatchers.Main` for UI updates. The goal is the same: don't block the thread that handles user interactions.

FastAPI works the same way, but the "main thread" is the asyncio event loop. If you block the event loop with synchronous code (like a slow database query or a CPU-heavy calculation), every other request waiting on that event loop stalls. Understanding when to use `async def` vs `def` in FastAPI is the difference between an API that handles 1000 concurrent requests and one that falls over at 50.

## When Async Helps (and When It Does Not)

| Workload Type | Example | Async Benefit | Recommendation |
|---------------|---------|--------------|----------------|
| I/O-bound (network) | HTTP calls, database queries | High -- event loop handles other requests while waiting | Use `async def` |
| I/O-bound (disk) | File reads/writes | Medium -- depends on library | Use `async def` with async libraries |
| CPU-bound | Image processing, data parsing | None -- blocks the event loop | Use `def` or `run_in_executor` |
| Mixed | Query + process results | Depends on ratio | Profile to decide |

**The rule:** Async helps when your code spends most of its time *waiting* (for a network response, database query, or file read). It does NOT help when your code spends most of its time *computing* (number crunching, parsing, image processing).

## FastAPI: async def vs def

FastAPI handles `async def` and `def` endpoints differently:

```python
from fastapi import FastAPI

app = FastAPI()


# Async endpoint -- runs directly on the event loop
@app.get("/async")
async def async_endpoint():
    result = await some_async_database_query()
    return {"data": result}


# Sync endpoint -- FastAPI runs this in a thread pool automatically
@app.get("/sync")
def sync_endpoint():
    result = some_sync_database_query()
    return {"data": result}
```

**How FastAPI handles each:**

| Declaration | Execution | Blocks Event Loop? | Concurrent Handling |
|-------------|-----------|-------------------|-------------------|
| `async def` | Directly on event loop | Only if you use sync code inside | Yes, via `await` |
| `def` | In a separate thread pool | No (it's in its own thread) | Yes, via threading |

**When to use `async def`:**
- All I/O operations inside use `await` (async database driver, httpx, aiofiles)
- You want maximum throughput for I/O-bound work

**When to use `def`:**
- You call synchronous libraries (requests, synchronous SQLAlchemy)
- The endpoint does CPU-bound work
- You're unsure -- `def` is the safer default

## The Common Mistake: Blocking the Event Loop

This is the single most dangerous async pitfall:

```python
import time

# WRONG: Blocks the event loop for 5 seconds
# Every other request on this event loop waits
@app.get("/bad")
async def bad_endpoint():
    time.sleep(5)  # Synchronous sleep in async function!
    return {"status": "done"}


# RIGHT: Async sleep yields control back to the event loop
@app.get("/good")
async def good_endpoint():
    await asyncio.sleep(5)  # Other requests proceed during this wait
    return {"status": "done"}
```

**Other blocking calls to watch for in async endpoints:**

```python
# BAD -- these block the event loop in async def:
import requests
response = requests.get("https://api.example.com")  # Use httpx instead

import sqlalchemy
session.execute(select(User))  # Use async SQLAlchemy instead

open("large_file.txt").read()  # Use aiofiles instead

time.sleep(1)  # Use asyncio.sleep instead

hash_password(password)  # CPU-bound, use run_in_executor
```

**Mobile analogy:** This is exactly like calling `URLSession.dataTask` synchronously on the main thread in iOS -- the UI freezes. Or doing a Room database query on the main thread in Android -- you get an ANR (Application Not Responding).

## Using run_in_executor for CPU-bound Work

When you need CPU-bound work in an async endpoint, offload it to a thread pool:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)


@app.get("/cpu-heavy")
async def cpu_heavy_endpoint():
    loop = asyncio.get_event_loop()

    # Run CPU-bound function in thread pool
    result = await loop.run_in_executor(executor, expensive_calculation, data)
    return {"result": result}


def expensive_calculation(data):
    """CPU-bound work that would block the event loop."""
    # Heavy computation here...
    return processed_data
```

**Mobile analogy:** This is like dispatching work to `DispatchQueue.global(qos: .background)` on iOS, or using `Dispatchers.Default` in Kotlin coroutines.

## asyncio.gather for Concurrent I/O

When you need to make multiple independent I/O calls, run them concurrently:

```python
import asyncio
import httpx


@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int):
    # Sequential -- takes sum of all call times
    # user = await get_user(user_id)        # 100ms
    # posts = await get_posts(user_id)      # 200ms
    # notifications = await get_notifications(user_id)  # 150ms
    # Total: 450ms

    # Concurrent -- takes time of the slowest call
    user, posts, notifications = await asyncio.gather(
        get_user(user_id),          # 100ms
        get_posts(user_id),         # 200ms
        get_notifications(user_id), # 150ms
    )
    # Total: 200ms (the slowest one)

    return {
        "user": user,
        "posts": posts,
        "notifications": notifications,
    }
```

**Mobile analogy:** This is like using `async let` in Swift concurrency or `coroutineScope { launch { ... } }` in Kotlin to run multiple network calls in parallel.

### Error handling with gather

```python
# By default, if one task fails, gather cancels the rest and raises
try:
    user, posts = await asyncio.gather(
        get_user(user_id),
        get_posts(user_id),
    )
except Exception as e:
    # One of the calls failed
    logger.error("Dashboard fetch failed: %s", e)
    raise HTTPException(status_code=500)

# Or: return exceptions instead of raising
results = await asyncio.gather(
    get_user(user_id),
    get_posts(user_id),
    return_exceptions=True,  # Returns exception objects instead of raising
)
for result in results:
    if isinstance(result, Exception):
        logger.error("One call failed: %s", result)
```

## Async Database Sessions with SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Async engine (note the asyncpg driver)
async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/mydb")

# Async session factory
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# FastAPI dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Async endpoint using async session
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

## Sync vs Async Performance Comparison

| Scenario | Sync `def` | Async `def` (correct) | Async `def` (blocking) |
|----------|-----------|----------------------|----------------------|
| 10 concurrent DB queries (50ms each) | 500ms (sequential in thread) | 50ms (concurrent await) | 500ms (blocks event loop) |
| 100 concurrent requests | ~100 threads | 1 thread, all concurrent | 1 thread, all sequential |
| CPU-bound (100ms computation) | 100ms (fine in thread) | 100ms (blocks event loop!) | 100ms (blocks event loop) |
| Memory per connection | ~8MB per thread | ~1KB per coroutine | ~1KB per coroutine |

## Decision Framework

```
Is the endpoint I/O-bound?
├── Yes: Do you have async libraries for all I/O?
│   ├── Yes → Use `async def` with `await`
│   └── No → Use `def` (FastAPI runs it in thread pool)
└── No (CPU-bound):
    ├── Short computation (< 10ms) → Either `def` or `async def` is fine
    └── Long computation (> 10ms) → Use `def` or `run_in_executor`
```

## Key Takeaways

1. **`async def` is not automatically faster.** It only helps when you actually `await` I/O operations. Misuse makes things worse.
2. **Never call sync I/O in an `async def` endpoint.** This blocks the event loop and serializes all requests. Use `def` instead, or use async libraries.
3. **Use `def` when unsure.** FastAPI automatically runs sync endpoints in a thread pool, so they never block the event loop.
4. **Use `asyncio.gather()` for concurrent I/O.** When you need data from multiple sources, fetch them in parallel instead of sequentially.
5. **Use `run_in_executor()` for CPU-bound work** in async endpoints. This offloads the work to a thread pool while keeping the event loop free.
6. **Async database access requires an async driver.** Use `asyncpg` for PostgreSQL (not `psycopg2`), and `AsyncSession` from SQLAlchemy.
