# gather(), wait(), and as_completed()

## Why This Matters

You need to fetch data from 10 APIs. Do you wait for each one sequentially (slow) or fetch all 10 concurrently (fast)?

This is like `async let` in Swift, `awaitAll()` in Kotlin, or `Future.wait()` in Dart — running multiple async operations concurrently and collecting results.

## asyncio.gather(): Run All Concurrently

`gather()` runs multiple coroutines concurrently and returns all results.

```python
import asyncio
import httpx

async def fetch_user(user_id: int) -> dict:
    """Fetch user from API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
        return response.json()

async def main():
    # Sequential: slow (10 requests × ~200ms = 2s)
    users = []
    for user_id in range(1, 11):
        user = await fetch_user(user_id)
        users.append(user)

    # Concurrent: fast (10 requests at once = ~200ms)
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
        fetch_user(4),
        fetch_user(5)
    )

    # Even better: use list comprehension
    users = await asyncio.gather(
        *[fetch_user(user_id) for user_id in range(1, 11)]
    )

    print(f"Fetched {len(users)} users")

asyncio.run(main())
```

**Key points:**
- Returns results in the **same order** as input
- Waits for **all** coroutines to complete
- If one fails, raises exception immediately (unless `return_exceptions=True`)

## Timing Comparison

```python
import asyncio
import time

async def task(name: str, delay: float):
    """Simulate async work."""
    await asyncio.sleep(delay)
    return f"{name} done"

async def sequential():
    """Run tasks one by one."""
    start = time.time()

    result1 = await task("A", 1.0)
    result2 = await task("B", 1.0)
    result3 = await task("C", 1.0)

    elapsed = time.time() - start
    print(f"Sequential: {elapsed:.1f}s")  # ~3.0s

async def concurrent():
    """Run tasks concurrently."""
    start = time.time()

    results = await asyncio.gather(
        task("A", 1.0),
        task("B", 1.0),
        task("C", 1.0)
    )

    elapsed = time.time() - start
    print(f"Concurrent: {elapsed:.1f}s")  # ~1.0s

asyncio.run(sequential())
asyncio.run(concurrent())
```

**Output:**
```
Sequential: 3.0s
Concurrent: 1.0s
```

## Mobile Platform Comparison

**Swift (async let):**

```swift
async func fetchUsers() async -> [User] {
    async let user1 = fetchUser(1)
    async let user2 = fetchUser(2)
    async let user3 = fetchUser(3)

    return await [user1, user2, user3]
}
```

**Kotlin (awaitAll):**

```kotlin
suspend fun fetchUsers(): List<User> {
    return coroutineScope {
        listOf(
            async { fetchUser(1) },
            async { fetchUser(2) },
            async { fetchUser(3) }
        ).awaitAll()
    }
}
```

**Dart (Future.wait):**

```dart
Future<List<User>> fetchUsers() async {
  return Future.wait([
    fetchUser(1),
    fetchUser(2),
    fetchUser(3),
  ]);
}
```

**Python (asyncio.gather):**

```python
async def fetch_users() -> list[User]:
    return await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
```

## Error Handling with gather()

**Default: first exception stops everything:**

```python
async def task_ok():
    await asyncio.sleep(1)
    return "OK"

async def task_error():
    await asyncio.sleep(0.5)
    raise ValueError("Something failed")

async def main():
    try:
        results = await asyncio.gather(
            task_ok(),
            task_error(),
            task_ok()
        )
    except ValueError as e:
        print(f"Error: {e}")
        # Other tasks are cancelled!

asyncio.run(main())
```

**With `return_exceptions=True`: collect all results:**

```python
async def main():
    results = await asyncio.gather(
        task_ok(),
        task_error(),
        task_ok(),
        return_exceptions=True
    )

    # results = ["OK", ValueError("Something failed"), "OK"]

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i} failed: {result}")
        else:
            print(f"Task {i} succeeded: {result}")

asyncio.run(main())
```

## asyncio.wait(): More Control

`wait()` gives more control over completion:

```python
import asyncio

async def task(name: str, delay: float):
    await asyncio.sleep(delay)
    return name

async def main():
    tasks = [
        asyncio.create_task(task("A", 1.0)),
        asyncio.create_task(task("B", 2.0)),
        asyncio.create_task(task("C", 3.0))
    ]

    # Wait for all to complete
    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    # Wait for first to complete
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # Wait for first exception
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # Extract results
    for task in done:
        result = task.result()  # or task.exception() if it failed
        print(result)

asyncio.run(main())
```

**When to use:**
- `gather()`: You want all results in order (most common)
- `wait()`: You want control over completion order or timeouts

## asyncio.as_completed(): Process Results as They Arrive

```python
import asyncio

async def fetch(url: str, delay: float):
    """Simulate fetching with variable delay."""
    await asyncio.sleep(delay)
    return f"Data from {url}"

async def main():
    urls = [
        ("api1.com", 2.0),
        ("api2.com", 1.0),
        ("api3.com", 3.0)
    ]

    # Create coroutines
    coros = [fetch(url, delay) for url, delay in urls]

    # Process results as they complete
    for coro in asyncio.as_completed(coros):
        result = await coro
        print(f"Got: {result}")

asyncio.run(main())

# Output (as they complete):
# Got: Data from api2.com  (after 1s)
# Got: Data from api1.com  (after 2s)
# Got: Data from api3.com  (after 3s)
```

**Use case:** Show results progressively (like a progress bar).

## TaskGroup: Structured Concurrency (Python 3.11+)

`TaskGroup` is the modern, safer way to run concurrent tasks:

```python
import asyncio

async def task(name: str, delay: float):
    await asyncio.sleep(delay)
    return f"{name} done"

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(task("A", 1.0))
        task2 = tg.create_task(task("B", 2.0))
        task3 = tg.create_task(task("C", 1.5))

    # All tasks complete when exiting the context manager
    print(task1.result())
    print(task2.result())
    print(task3.result())

asyncio.run(main())
```

**Benefits:**
- Automatic cleanup (like Swift's `withTaskGroup`)
- Exception groups for multiple failures
- Ensures all tasks finish before continuing

**Comparison to Swift:**

```swift
// Swift's withTaskGroup
await withTaskGroup(of: String.self) { group in
    group.addTask { await task("A", 1.0) }
    group.addTask { await task("B", 2.0) }
    group.addTask { await task("C", 1.5) }

    for await result in group {
        print(result)
    }
}
```

**Comparison to Kotlin:**

```kotlin
// Kotlin's coroutineScope
coroutineScope {
    val task1 = async { task("A", 1.0) }
    val task2 = async { task("B", 2.0) }
    val task3 = async { task("C", 1.5) }

    listOf(task1, task2, task3).awaitAll()
}
```

## Error Handling with TaskGroup

```python
import asyncio

async def task_ok(name: str):
    await asyncio.sleep(1)
    return f"{name} OK"

async def task_error(name: str):
    await asyncio.sleep(0.5)
    raise ValueError(f"{name} failed")

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task_ok("A"))
            tg.create_task(task_error("B"))
            tg.create_task(task_ok("C"))
    except* ValueError as eg:  # Exception group
        print(f"Caught {len(eg.exceptions)} errors:")
        for exc in eg.exceptions:
            print(f"  - {exc}")

asyncio.run(main())
```

**Exception groups (`except*`)** let you handle multiple failures.

## Choosing the Right Tool

| Tool | Best For |
|------|----------|
| **gather()** | Run multiple tasks, get all results in order |
| **wait()** | Fine control over completion order |
| **as_completed()** | Process results progressively as they arrive |
| **TaskGroup** | Structured concurrency with automatic cleanup (Python 3.11+) |

## Key Takeaways

1. **gather() runs tasks concurrently** and returns results in order
2. **Sequential vs concurrent**: 3 × 1s = 3s vs max(1s) = 1s
3. **return_exceptions=True** collects errors instead of raising
4. **wait() gives more control** over completion order
5. **as_completed() processes results** as they arrive
6. **TaskGroup is the modern way** (Python 3.11+) — like Swift's withTaskGroup
7. **Use gather() for most cases** — it's simple and works well
8. **Like mobile async patterns** — async let (Swift), awaitAll (Kotlin), Future.wait (Dart)
