# Module 012: Advanced Async Python

## Why This Module?

Master async concurrency patterns for high-performance APIs. Learn asyncio's event loop, concurrent execution with gather/wait, rate limiting with semaphores, and structured error handling.

## What You'll Learn

- Event loop fundamentals and how async really works
- Concurrent execution with asyncio.gather() and asyncio.wait()
- Structured concurrency with TaskGroup (Python 3.11+)
- Rate limiting with semaphores
- Async context managers for resource cleanup
- Async generators for streaming data
- Exception handling in async code

## Mobile Developer Context

You've used async patterns in mobile development: GCD/structured concurrency (Swift), coroutines/Dispatchers (Kotlin), Futures/Streams (Dart). Python's asyncio is the same concept with different syntax.

**Async Patterns Across Platforms:**

| Concept | Swift | Kotlin | Dart | Python |
|---------|-------|--------|------|--------|
| Async function | `async func` | `suspend fun` | `Future<T>` / `async` | `async def` |
| Await result | `await` | `await` | `await` | `await` |
| Run concurrently | `async let` / `withTaskGroup` | `async { }` / `awaitAll()` | `Future.wait()` | `asyncio.gather()` |
| Event loop | `MainActor` | `Dispatchers.Main` | Event loop | `asyncio.run()` |
| Semaphore | `DispatchSemaphore` | `Semaphore` | Custom limiters | `asyncio.Semaphore` |
| Context manager | `defer` | `use` | `try/finally` | `async with` |
| Stream/Generator | `AsyncSequence` | `Flow` | `Stream` | `async for` / `async def` with `yield` |

**Key Differences:**
- Python uses a single-threaded event loop (like Dart, unlike Swift/Kotlin)
- `asyncio.gather()` is like `async let` in Swift or `awaitAll()` in Kotlin
- Python's `async with` replaces Swift's `defer` and Kotlin's `use` for cleanup
- Async generators (`async def` + `yield`) are like Swift's `AsyncSequence` or Kotlin's `Flow`

## Topics

### Theory
1. Event Loop Basics
2. gather(), wait(), and as_completed()
3. Semaphores for Rate Limiting
4. Async Context Managers
5. Async Generators
6. Exception Handling in Async Code

### Exercises
1. Concurrent Execution with gather()
2. Rate Limiting with Semaphores
3. Error Handling in Async Code

### Project
Async data aggregation pipeline with concurrent API calls, error handling, and rate limiting.

## Example

```python
import asyncio
import httpx

async def fetch_user(user_id: int) -> dict:
    """Fetch user from API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()

async def main():
    """Fetch 10 users concurrently."""
    # Sequential: 10 seconds (1 second each)
    users = []
    for user_id in range(1, 11):
        user = await fetch_user(user_id)
        users.append(user)

    # Concurrent: ~1 second (all at once)
    users = await asyncio.gather(
        *[fetch_user(user_id) for user_id in range(1, 11)]
    )

    print(f"Fetched {len(users)} users")

# Run the async function
asyncio.run(main())
```

## Quick Assessment

Before starting this module, ask yourself:
- Have you used async/await in Swift, Kotlin, or Dart?
- Do you understand the difference between concurrency and parallelism?
- Have you written background tasks in mobile apps?

If yes, you're ready. The concepts are identical — you're just learning Python's syntax.

## Time Estimate

6-8 hours total:
- Theory: 2-3 hours
- Exercises: 2-3 hours
- Project: 2-3 hours

## Key Differences from Mobile Async

1. **Single-threaded**: Python's event loop runs on one thread (like Dart), not multiple threads (like Swift/Kotlin)
2. **Explicit event loop**: You call `asyncio.run()` to start the loop (mobile frameworks handle this)
3. **Context managers**: Python uses `async with` for cleanup (Swift uses `defer`, Kotlin uses `use`)
4. **TaskGroup**: Python 3.11+ has structured concurrency like Swift's `withTaskGroup`
5. **No async by default**: You must explicitly use `async def` and `await` (Swift/Kotlin have better defaults)

## Why This Matters for APIs

**Without async:** Your API handles one request at a time. While waiting for a database query or external API call, the server is idle.

**With async:** Your API handles many requests concurrently. While one request waits for the database, another request is processed.

**Real-world impact:**
- Sync API: 10 requests/second
- Async API: 1000+ requests/second

That's why FastAPI is built on async Python — it's designed for high-performance APIs.
