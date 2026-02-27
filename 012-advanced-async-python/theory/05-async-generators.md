# Async Generators

## Why This Matters

Stream data one chunk at a time instead of loading everything into memory. Like Swift's `AsyncSequence`, Kotlin's `Flow`, or Dart's `Stream` — process large datasets incrementally.

Perfect for: paginated APIs, large files, database cursors, real-time feeds.

## Regular Generators (Sync)

```python
def count_up_to(n: int):
    """Sync generator."""
    for i in range(1, n + 1):
        yield i  # Produces values one at a time

for num in count_up_to(5):
    print(num)

# Output: 1, 2, 3, 4, 5
```

**Generator = function with `yield`** that produces values lazily.

## Async Generators

```python
import asyncio

async def async_count_up_to(n: int):
    """Async generator."""
    for i in range(1, n + 1):
        await asyncio.sleep(0.1)  # Simulate async work
        yield i  # Produces values one at a time

async def main():
    async for num in async_count_up_to(5):
        print(num)

asyncio.run(main())

# Output: 1, 2, 3, 4, 5 (with 0.1s delay each)
```

**Async generator = `async def` with `yield`** that produces values asynchronously.

## Mobile Platform Comparison

**Swift (AsyncSequence):**

```swift
func fetchPages() -> AsyncStream<[Item]> {
    AsyncStream { continuation in
        Task {
            for page in 1...10 {
                let items = await fetchPage(page)
                continuation.yield(items)
            }
            continuation.finish()
        }
    }
}

for await page in fetchPages() {
    print(page)
}
```

**Kotlin (Flow):**

```kotlin
fun fetchPages(): Flow<List<Item>> = flow {
    for (page in 1..10) {
        val items = fetchPage(page)
        emit(items)
    }
}

fetchPages().collect { page ->
    println(page)
}
```

**Dart (Stream):**

```dart
Stream<List<Item>> fetchPages() async* {
  for (var page = 1; page <= 10; page++) {
    final items = await fetchPage(page);
    yield items;
  }
}

await for (var page in fetchPages()) {
  print(page);
}
```

**Python (Async Generator):**

```python
async def fetch_pages():
    for page in range(1, 11):
        items = await fetch_page(page)
        yield items

async for page in fetch_pages():
    print(page)
```

## Practical Example: Paginated API

```python
import httpx

async def fetch_users_paginated():
    """Fetch users page by page."""
    page = 1
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                "https://api.example.com/users",
                params={"page": page, "limit": 10}
            )
            data = response.json()

            if not data["users"]:
                break  # No more pages

            yield data["users"]  # Yield one page at a time
            page += 1

async def main():
    total_users = 0

    async for page in fetch_users_paginated():
        total_users += len(page)
        print(f"Got {len(page)} users (total: {total_users})")

asyncio.run(main())

# Output:
# Got 10 users (total: 10)
# Got 10 users (total: 20)
# Got 5 users (total: 25)
```

**Benefits:**
- Don't load all users into memory
- Start processing immediately
- Cancel early if needed

## Reading Large Files

```python
import aiofiles

async def read_lines(filename: str):
    """Read file line by line."""
    async with aiofiles.open(filename, "r") as f:
        async for line in f:
            yield line.strip()

async def main():
    async for line in read_lines("large_file.txt"):
        if "error" in line.lower():
            print(line)

asyncio.run(main())
```

## Database Cursor (Streaming Results)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def fetch_users_stream(session: AsyncSession):
    """Stream users from database."""
    result = await session.stream(select(User))

    async for user in result.scalars():
        yield user

async def main(session: AsyncSession):
    async for user in fetch_users_stream(session):
        print(f"Processing user {user.id}")
        # Process one user at a time
```

## Async Generator with Cleanup

```python
from contextlib import asynccontextmanager
import httpx

async def api_stream(url: str):
    """Stream data from API with automatic cleanup."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            for item in response.json()["items"]:
                yield item
        finally:
            print("Cleanup: client closed")

async def main():
    async for item in api_stream("https://api.example.com/stream"):
        print(item)
        if item["id"] == 5:
            break  # Early exit — cleanup still runs

asyncio.run(main())
```

## Transforming Streams

**Filter:**

```python
async def filter_async(agen, predicate):
    """Filter async generator."""
    async for item in agen:
        if predicate(item):
            yield item

async def numbers():
    for i in range(10):
        yield i

async def main():
    async for even in filter_async(numbers(), lambda x: x % 2 == 0):
        print(even)  # 0, 2, 4, 6, 8

asyncio.run(main())
```

**Map:**

```python
async def map_async(agen, func):
    """Map async generator."""
    async for item in agen:
        yield await func(item) if asyncio.iscoroutinefunction(func) else func(item)

async def numbers():
    for i in range(5):
        yield i

async def square(x):
    await asyncio.sleep(0.1)
    return x * x

async def main():
    async for result in map_async(numbers(), square):
        print(result)  # 0, 1, 4, 9, 16

asyncio.run(main())
```

## Buffering Results

```python
async def fetch_data():
    """Fetch data items one at a time."""
    for i in range(10):
        await asyncio.sleep(0.1)
        yield f"Item {i}"

async def buffer(agen, size: int):
    """Buffer async generator results."""
    buffer = []
    async for item in agen:
        buffer.append(item)
        if len(buffer) >= size:
            yield buffer
            buffer = []

    if buffer:
        yield buffer

async def main():
    async for batch in buffer(fetch_data(), 3):
        print(f"Batch: {batch}")

asyncio.run(main())

# Output:
# Batch: ['Item 0', 'Item 1', 'Item 2']
# Batch: ['Item 3', 'Item 4', 'Item 5']
# Batch: ['Item 6', 'Item 7', 'Item 8']
# Batch: ['Item 9']
```

## Real-World: Streaming API Aggregator

```python
import httpx

async def fetch_from_apis(api_urls: list[str]):
    """Fetch from multiple APIs, yield results as they arrive."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in api_urls]

        for coro in asyncio.as_completed(tasks):
            response = await coro
            data = response.json()

            for item in data["items"]:
                yield item

async def main():
    apis = [
        "https://api1.example.com/data",
        "https://api2.example.com/data",
        "https://api3.example.com/data"
    ]

    async for item in fetch_from_apis(apis):
        print(f"Got: {item}")
        # Process items as soon as any API returns

asyncio.run(main())
```

## Async Generator vs gather()

**gather() — load all:**

```python
async def fetch_all_pages():
    """Load all pages into memory."""
    pages = await asyncio.gather(
        *[fetch_page(i) for i in range(1, 101)]
    )
    return pages  # 100 pages in memory

async def main():
    pages = await fetch_all_pages()
    for page in pages:
        process(page)
```

**Async generator — stream:**

```python
async def fetch_pages_stream():
    """Stream pages one at a time."""
    for i in range(1, 101):
        page = await fetch_page(i)
        yield page  # Only 1 page in memory

async def main():
    async for page in fetch_pages_stream():
        process(page)
```

**Use async generators when:**
- Data is too large for memory
- You want to start processing immediately
- You might not need all data (early exit)

## Key Takeaways

1. **Async generators = `async def` + `yield`** for streaming data
2. **Consume with `async for`** not regular `for`
3. **Perfect for paginated APIs** and large datasets
4. **Like mobile streams** — AsyncSequence (Swift), Flow (Kotlin), Stream (Dart)
5. **One item at a time** — memory efficient
6. **Can transform** with filter, map, buffer
7. **Cleanup runs even on early exit** (finally block)
8. **Use over gather()** when you don't need all data at once
