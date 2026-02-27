# Semaphores for Rate Limiting

## Why This Matters

You have 1000 tasks to run concurrently. Do you run all 1000 at once and crash the server? Or limit to 10 at a time?

Semaphores control concurrency — like DispatchSemaphore in Swift, Semaphore in Kotlin coroutines, or custom limiters in Dart. They prevent overwhelming resources (APIs, databases, connections).

## The Problem: Too Much Concurrency

```python
import asyncio
import httpx

async def fetch_data(id: int):
    """Fetch data from API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/data/{id}")
        return response.json()

async def main():
    # ❌ Problem: 1000 concurrent requests!
    results = await asyncio.gather(
        *[fetch_data(i) for i in range(1000)]
    )
    # This will:
    # - Overwhelm the API (rate limit errors)
    # - Open 1000 connections (memory issues)
    # - Hit file descriptor limits

asyncio.run(main())
```

## The Solution: Semaphores

```python
import asyncio

# Semaphore with limit of 10
semaphore = asyncio.Semaphore(10)

async def fetch_data(id: int):
    """Fetch data with concurrency limit."""
    async with semaphore:
        # Only 10 tasks can run this code at once
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.example.com/data/{id}")
            return response.json()

async def main():
    # ✅ Solution: Max 10 concurrent requests
    results = await asyncio.gather(
        *[fetch_data(i) for i in range(1000)]
    )
    # This will:
    # - Limit to 10 concurrent requests
    # - Process all 1000 in batches
    # - Respect rate limits

asyncio.run(main())
```

**How it works:**
1. Semaphore has a counter (starts at 10)
2. `async with semaphore:` decrements counter
3. When counter hits 0, other tasks wait
4. When task exits, counter increments
5. Waiting tasks resume

## Mobile Platform Comparison

**Swift (DispatchSemaphore):**

```swift
let semaphore = DispatchSemaphore(value: 10)

func fetchData(id: Int) async -> Data {
    semaphore.wait()
    defer { semaphore.signal() }

    // Fetch data
    return data
}
```

**Kotlin (Semaphore):**

```kotlin
val semaphore = Semaphore(10)

suspend fun fetchData(id: Int): Data {
    semaphore.acquire()
    try {
        // Fetch data
        return data
    } finally {
        semaphore.release()
    }
}
```

**Dart (Custom limiter):**

```dart
// Dart doesn't have built-in semaphores
// Use packages like 'async' or custom implementation
```

**Python (asyncio.Semaphore):**

```python
semaphore = asyncio.Semaphore(10)

async def fetch_data(id: int):
    async with semaphore:
        # Fetch data
        return data
```

**Always use `async with`** — it guarantees release even on exceptions.

## Practical Example: Rate-Limited API Calls

```python
import asyncio
import httpx
import time

async def fetch_user(user_id: int, semaphore: asyncio.Semaphore):
    """Fetch user with rate limiting."""
    async with semaphore:
        print(f"Fetching user {user_id}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://jsonplaceholder.typicode.com/users/{user_id}"
            )
            return response.json()

async def main():
    # Limit to 5 concurrent requests
    semaphore = asyncio.Semaphore(5)

    start = time.time()

    # Fetch 20 users (will process in batches of 5)
    users = await asyncio.gather(
        *[fetch_user(i, semaphore) for i in range(1, 21)]
    )

    elapsed = time.time() - start
    print(f"Fetched {len(users)} users in {elapsed:.1f}s")
    print(f"Batches: {len(users) / 5} = 4 batches")

asyncio.run(main())
```

## Before/After Comparison

**Without semaphore (100 concurrent):**

```python
async def main():
    # All 100 run at once
    results = await asyncio.gather(
        *[fetch_data(i) for i in range(100)]
    )
    # Outcome:
    # - 100 connections opened
    # - API returns 429 Too Many Requests
    # - Some requests fail
```

**With semaphore (10 concurrent):**

```python
semaphore = asyncio.Semaphore(10)

async def fetch_data(id: int):
    async with semaphore:
        return await actually_fetch(id)

async def main():
    # Only 10 run at a time
    results = await asyncio.gather(
        *[fetch_data(i) for i in range(100)]
    )
    # Outcome:
    # - 10 connections at a time
    # - All requests succeed
    # - Takes 10x longer but reliable
```

## Tracking Concurrent Execution

```python
import asyncio

class TrackedSemaphore:
    """Semaphore that tracks active tasks."""

    def __init__(self, limit: int):
        self.semaphore = asyncio.Semaphore(limit)
        self.active = 0
        self.max_active = 0

    async def __aenter__(self):
        await self.semaphore.acquire()
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.active -= 1
        self.semaphore.release()

async def task(id: int, semaphore: TrackedSemaphore):
    async with semaphore:
        print(f"Task {id}: {semaphore.active} active")
        await asyncio.sleep(0.1)

async def main():
    semaphore = TrackedSemaphore(5)

    await asyncio.gather(
        *[task(i, semaphore) for i in range(20)]
    )

    print(f"Max concurrent: {semaphore.max_active}")

asyncio.run(main())
```

## Database Connection Pool

Common use case: limit database connections.

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Create engine with connection pool
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=10,
    max_overflow=0
)

# Semaphore to match pool size
db_semaphore = asyncio.Semaphore(10)

async def query_user(user_id: int):
    """Query user with connection limiting."""
    async with db_semaphore:
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one()

async def main():
    # Can process 100 users, but only 10 DB connections at once
    users = await asyncio.gather(
        *[query_user(i) for i in range(100)]
    )

asyncio.run(main())
```

## Semaphore with Error Handling

```python
import asyncio

semaphore = asyncio.Semaphore(5)

async def risky_task(id: int):
    """Task that might fail."""
    async with semaphore:
        if id % 10 == 0:
            raise ValueError(f"Task {id} failed")
        await asyncio.sleep(0.1)
        return f"Task {id} OK"

async def main():
    results = await asyncio.gather(
        *[risky_task(i) for i in range(20)],
        return_exceptions=True
    )

    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    print(f"Successes: {len(successes)}")
    print(f"Failures: {len(failures)}")

asyncio.run(main())
```

**Semaphore is released even when exception occurs** (thanks to `async with`).

## Choosing Semaphore Limits

| Resource | Recommended Limit |
|----------|------------------|
| External API calls | 5-20 (depends on API rate limits) |
| Database connections | Match pool size (e.g., 10) |
| File I/O | 50-100 (OS file descriptor limits) |
| HTTP client connections | 100-500 (depends on server) |

**Too low:** Slow processing (under-utilized resources)  
**Too high:** Rate limit errors, connection exhaustion  
**Just right:** Fast processing without overwhelming resources

## Key Takeaways

1. **Semaphores limit concurrency** to N tasks at a time
2. **Use `async with semaphore:`** — never manual acquire/release
3. **Prevents overwhelming resources** (APIs, databases, connections)
4. **Choose limit based on resource** (API: 10, DB: pool size, files: 100)
5. **Semaphore is released on error** (thanks to context manager)
6. **Like mobile semaphores** — DispatchSemaphore (Swift), Semaphore (Kotlin)
7. **Common pattern:** Wrap resource access in semaphore-protected function
