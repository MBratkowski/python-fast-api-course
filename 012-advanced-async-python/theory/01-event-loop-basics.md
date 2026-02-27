# Event Loop Basics

## Why This Matters

Understanding the event loop is like understanding the main thread in mobile development. It's the foundation of async Python — the engine that runs your async code.

Think of it like iOS's main run loop or Android's Looper: a single-threaded loop that processes tasks one at a time, switching between them when they're waiting.

## What is the Event Loop?

The event loop is a **single-threaded** loop that:
1. Runs one coroutine at a time
2. When a coroutine waits (`await`), switches to another coroutine
3. Returns to the first coroutine when its wait is complete

**It's NOT parallel execution** — it's **concurrent execution on one thread**.

**ASCII visualization:**

```
Time →
Thread: [Task A runs...] [waits for I/O] [Task B runs...] [waits] [Task A continues] [done]
                          ↓                              ↓
                    Switch to Task B              Switch to Task A
```

## Event Loop vs Threads

| Concept | Threads (Parallel) | Event Loop (Concurrent) |
|---------|-------------------|------------------------|
| Execution | Multiple tasks run simultaneously | One task runs at a time |
| Switching | OS preemptively switches | Tasks voluntarily yield with `await` |
| Resource usage | High (each thread has stack) | Low (shared stack) |
| Complexity | Race conditions, locks | No race conditions |
| Best for | CPU-intensive work | I/O-intensive work (APIs, databases) |

**Mobile Parallel:**

| Platform | Event Loop Equivalent |
|----------|----------------------|
| **Swift** | `MainActor` runs on main thread's run loop |
| **Kotlin** | `Dispatchers.Main` backed by Android Looper |
| **Dart** | Single-threaded event loop (isolates for parallelism) |
| **Python** | `asyncio` event loop (threads for parallelism) |

## Coroutines vs Functions

**Synchronous function:** Runs to completion without yielding.

```python
def sync_function():
    result = do_work()  # Blocks until complete
    return result
```

**Coroutine (async function):** Can yield control while waiting.

```python
async def async_function():
    result = await do_async_work()  # Yields control while waiting
    return result
```

**Key difference:** `await` says "I'm waiting, run other tasks".

## Running Async Code

**Top-level entry point:**

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# Start the event loop
asyncio.run(main())
```

`asyncio.run()`:
1. Creates an event loop
2. Runs `main()` coroutine
3. Closes the loop when done

**You can only call `asyncio.run()` once** — it's the entry point.

## await: The Key to Async

`await` tells the event loop "I'm waiting for this, run other tasks".

```python
import asyncio
import time

async def task(name: str, delay: float):
    """Simulate async work."""
    print(f"{name} starting")
    await asyncio.sleep(delay)  # Yields control during sleep
    print(f"{name} done after {delay}s")

async def main():
    # Sequential: 1s + 2s = 3s total
    await task("A", 1)
    await task("B", 2)

    # Concurrent: max(1s, 2s) = 2s total
    await asyncio.gather(
        task("A", 1),
        task("B", 2)
    )

asyncio.run(main())
```

**Without `await`:** You get a coroutine object (not executed).

```python
async def get_data():
    return 42

result = get_data()  # This is a coroutine object, NOT 42!
print(result)  # <coroutine object get_data at 0x...>

result = await get_data()  # Now it runs and returns 42
print(result)  # 42
```

## Async vs Sync Functions

```python
import asyncio
import requests  # Sync HTTP library
import httpx     # Async HTTP library

# Sync function (blocks the thread)
def fetch_sync(url: str) -> str:
    response = requests.get(url)
    return response.text

# Async function (yields during I/O)
async def fetch_async(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

# Can't mix them
async def main():
    # ❌ Wrong: sync function blocks the event loop
    data = fetch_sync("https://example.com")

    # ✅ Right: async function yields during I/O
    data = await fetch_async("https://example.com")
```

**Rule:** In async code, use async libraries (httpx, aiofiles, asyncpg) — not sync libraries (requests, open, psycopg2).

## The Event Loop Lifecycle

```python
import asyncio

async def task():
    print("Task running")
    await asyncio.sleep(0.1)
    print("Task done")

# Method 1: asyncio.run (recommended)
asyncio.run(task())

# Method 2: Manual loop management (advanced)
loop = asyncio.get_event_loop()
loop.run_until_complete(task())
loop.close()
```

**Always use `asyncio.run()`** unless you have a specific reason not to.

## Comparison: Mobile Threads vs Python Event Loop

**Swift (GCD):**

```swift
// Main queue (like event loop)
DispatchQueue.main.async {
    // Runs on main thread
}

// Background queue (parallel)
DispatchQueue.global().async {
    // Runs on background thread
}
```

**Kotlin (Coroutines):**

```kotlin
// Main dispatcher (like event loop)
withContext(Dispatchers.Main) {
    // Runs on main thread
}

// IO dispatcher (thread pool)
withContext(Dispatchers.IO) {
    // Runs on background thread
}
```

**Dart (Event loop):**

```dart
// All async code runs on event loop
Future<String> fetchData() async {
  return await http.get(url);
}
```

**Python (asyncio):**

```python
# All async code runs on event loop
async def fetch_data():
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

## When the Event Loop Blocks

**Blocking the loop (bad):**

```python
import asyncio
import time

async def bad_task():
    print("Starting")
    time.sleep(2)  # ❌ Blocks the entire event loop!
    print("Done")

async def good_task():
    print("Starting")
    await asyncio.sleep(2)  # ✅ Yields control during wait
    print("Done")
```

**Symptoms of a blocked loop:**
- Other tasks don't run
- API requests timeout
- UI becomes unresponsive

**Solution:** Use async versions of blocking operations.

## Creating Tasks

```python
import asyncio

async def background_task():
    """Runs in background."""
    await asyncio.sleep(2)
    print("Background task done")

async def main():
    # Create task (starts immediately)
    task = asyncio.create_task(background_task())

    # Do other work
    print("Doing other work...")
    await asyncio.sleep(1)
    print("Other work done")

    # Wait for background task
    await task

asyncio.run(main())

# Output:
# Doing other work...
# Other work done
# Background task done
```

## Key Takeaways

1. **Event loop is single-threaded** — one task runs at a time
2. **Concurrency, not parallelism** — tasks take turns, don't run simultaneously
3. **`await` yields control** to the event loop
4. **`asyncio.run()`** starts the event loop (entry point)
5. **Use async libraries** (httpx, not requests) in async code
6. **Don't block the loop** — use `await asyncio.sleep()` not `time.sleep()`
7. **`async def` creates coroutines** that must be awaited
8. **Like mobile main threads** — Swift MainActor, Kotlin Dispatchers.Main, Dart event loop
