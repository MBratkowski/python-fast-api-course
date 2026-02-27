# Exception Handling in Async Code

## Why This Matters

Async code fails too: network timeouts, API errors, database failures. You need to catch errors, retry operations, and handle partial failures gracefully.

Like error handling in Swift async/await, Kotlin coroutines with supervisorScope, or Dart zone error handling.

## Basic Exception Handling

```python
import asyncio
import httpx

async def fetch_user(user_id: int):
    """Fetch user from API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.example.com/users/{user_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
        return None
    except httpx.TimeoutException:
        print("Request timed out")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def main():
    user = await fetch_user(1)
    if user:
        print(f"User: {user['name']}")
    else:
        print("Failed to fetch user")

asyncio.run(main())
```

## Exceptions in gather()

**Default behavior: first exception cancels others:**

```python
async def task_ok(name: str):
    await asyncio.sleep(1)
    return f"{name} OK"

async def task_error(name: str):
    await asyncio.sleep(0.5)
    raise ValueError(f"{name} failed")

async def main():
    try:
        results = await asyncio.gather(
            task_ok("A"),
            task_error("B"),
            task_ok("C")
        )
    except ValueError as e:
        print(f"Error: {e}")
        # Tasks A and C are cancelled!

asyncio.run(main())

# Output:
# Error: B failed
```

**With `return_exceptions=True`: collect all results:**

```python
async def main():
    results = await asyncio.gather(
        task_ok("A"),
        task_error("B"),
        task_ok("C"),
        return_exceptions=True  # Don't raise, return exceptions
    )

    # results = ["A OK", ValueError("B failed"), "C OK"]

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i} failed: {result}")
        else:
            print(f"Task {i} succeeded: {result}")

asyncio.run(main())

# Output:
# Task 0 succeeded: A OK
# Task 1 failed: B failed
# Task 2 succeeded: C OK
```

## Mobile Platform Comparison

**Swift (throwing async functions):**

```swift
func fetchData() async throws -> Data {
    try await urlSession.data(from: url)
}

// Catch errors
do {
    let data = try await fetchData()
} catch {
    print("Error: \(error)")
}

// Multiple tasks
async let result1 = fetchData1()
async let result2 = fetchData2()
let (data1, data2) = try await (result1, result2)
// First error cancels all
```

**Kotlin (supervisorScope vs coroutineScope):**

```kotlin
// coroutineScope: first error cancels all
coroutineScope {
    val data1 = async { fetchData1() }
    val data2 = async { fetchData2() }  // If this fails, data1 is cancelled
    listOf(data1, data2).awaitAll()
}

// supervisorScope: errors don't cancel siblings
supervisorScope {
    val data1 = async { fetchData1() }
    val data2 = async { fetchData2() }  // If this fails, data1 continues
    listOf(data1, data2).awaitAll()
}
```

**Dart (zone error handling):**

```dart
await runZonedGuarded(() async {
  await Future.wait([
    fetchData1(),
    fetchData2(),
  ]);
}, (error, stackTrace) {
  print('Error: $error');
});
```

**Python (gather with return_exceptions):**

```python
# First error stops all
results = await asyncio.gather(task1(), task2())

# Collect all errors
results = await asyncio.gather(
    task1(),
    task2(),
    return_exceptions=True
)
```

## TaskGroup with Exception Groups (Python 3.11+)

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
            tg.create_task(task_error("C"))
            tg.create_task(task_ok("D"))
    except* ValueError as eg:  # Exception group
        print(f"Caught {len(eg.exceptions)} errors:")
        for exc in eg.exceptions:
            print(f"  - {exc}")

asyncio.run(main())

# Output:
# Caught 2 errors:
#   - B failed
#   - C failed
```

**`except*` syntax** catches exception groups (multiple errors).

## Timeout Handling

**asyncio.wait_for():**

```python
import asyncio

async def slow_task():
    await asyncio.sleep(5)
    return "Done"

async def main():
    try:
        result = await asyncio.wait_for(slow_task(), timeout=2.0)
        print(result)
    except asyncio.TimeoutError:
        print("Task timed out after 2s")

asyncio.run(main())

# Output:
# Task timed out after 2s
```

**asyncio.timeout() context manager (Python 3.11+):**

```python
async def main():
    try:
        async with asyncio.timeout(2.0):
            result = await slow_task()
            print(result)
    except TimeoutError:
        print("Task timed out after 2s")

asyncio.run(main())
```

## Retry Logic

```python
import asyncio
import httpx

async def fetch_with_retry(url: str, max_retries: int = 3):
    """Fetch with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise

            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

async def main():
    try:
        data = await fetch_with_retry("https://api.example.com/data")
        print(f"Success: {data}")
    except Exception as e:
        print(f"Failed after retries: {e}")

asyncio.run(main())
```

## Cancellation Handling

```python
import asyncio

async def long_task():
    """Task that can be cancelled."""
    try:
        print("Task starting")
        await asyncio.sleep(10)
        print("Task finished")
    except asyncio.CancelledError:
        print("Task was cancelled")
        # Cleanup code here
        raise  # Re-raise to propagate cancellation

async def main():
    task = asyncio.create_task(long_task())

    await asyncio.sleep(1)  # Let it start

    task.cancel()  # Cancel the task

    try:
        await task
    except asyncio.CancelledError:
        print("Main: task was cancelled")

asyncio.run(main())

# Output:
# Task starting
# Task was cancelled
# Main: task was cancelled
```

## Partial Success Pattern

```python
import asyncio

async def fetch_data(id: int):
    """Fetch data that might fail."""
    await asyncio.sleep(0.1)
    if id % 3 == 0:
        raise ValueError(f"ID {id} failed")
    return f"Data {id}"

async def fetch_all_with_fallback(ids: list[int]):
    """Fetch all, collect successes and failures."""
    tasks = [fetch_data(id) for id in ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = []
    failures = []

    for id, result in zip(ids, results):
        if isinstance(result, Exception):
            failures.append((id, result))
        else:
            successes.append(result)

    return successes, failures

async def main():
    ids = list(range(1, 11))
    successes, failures = await fetch_all_with_fallback(ids)

    print(f"Successes: {len(successes)}")
    print(f"Failures: {len(failures)}")

    for id, error in failures:
        print(f"  ID {id} failed: {error}")

asyncio.run(main())

# Output:
# Successes: 7
# Failures: 3
#   ID 3 failed: ID 3 failed
#   ID 6 failed: ID 6 failed
#   ID 9 failed: ID 9 failed
```

## Fallback Values

```python
async def fetch_with_fallback(url: str, fallback: dict):
    """Fetch data with fallback on error."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=2.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}. Using fallback.")
        return fallback

async def main():
    data = await fetch_with_fallback(
        "https://api.example.com/data",
        fallback={"status": "unavailable"}
    )
    print(data)

asyncio.run(main())
```

## Circuit Breaker Pattern

```python
import asyncio
from datetime import datetime, timedelta

class CircuitBreaker:
    """Circuit breaker for failing services."""

    def __init__(self, failure_threshold: int = 3, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, coro):
        """Call coroutine through circuit breaker."""
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await coro
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.failures >= self.failure_threshold:
                self.state = "open"

            raise

async def unreliable_api():
    """API that fails often."""
    await asyncio.sleep(0.1)
    raise Exception("API failed")

async def main():
    breaker = CircuitBreaker(failure_threshold=3)

    for i in range(5):
        try:
            await breaker.call(unreliable_api())
        except Exception as e:
            print(f"Attempt {i + 1}: {e}, State: {breaker.state}")

asyncio.run(main())

# Output:
# Attempt 1: API failed, State: closed
# Attempt 2: API failed, State: closed
# Attempt 3: API failed, State: open
# Attempt 4: Circuit breaker is OPEN, State: open
# Attempt 5: Circuit breaker is OPEN, State: open
```

## Key Takeaways

1. **Use try/except** around await calls just like sync code
2. **gather() with return_exceptions=True** collects all errors
3. **TaskGroup** (Python 3.11+) uses exception groups (`except*`)
4. **asyncio.wait_for()** adds timeout to any coroutine
5. **Retry with exponential backoff** for transient failures
6. **Handle CancelledError** for cleanup during cancellation
7. **Partial success pattern** separates successes from failures
8. **Circuit breaker** protects against failing services
9. **Like mobile error handling** — Swift throws, Kotlin supervisorScope, Dart zones
