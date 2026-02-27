# Async Context Managers

## Why This Matters

Resources need cleanup: close database connections, close HTTP clients, release locks. In async code, cleanup must be async too.

Async context managers (`async with`) are like Swift's `defer` in async functions, Kotlin's `use` extension, or Dart's `try/finally` — but integrated with the event loop.

## The Problem: Async Cleanup

```python
import httpx

# ❌ Wrong: sync context manager with async code
async def fetch_data():
    client = httpx.AsyncClient()
    response = await client.get("https://api.example.com/data")
    await client.aclose()  # Manual cleanup (easy to forget!)
    return response.json()

# ✅ Right: async context manager
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
    # client.aclose() called automatically
```

## Async Context Manager Protocol

**Sync context manager:**

```python
class FileManager:
    def __enter__(self):
        self.file = open("data.txt", "w")
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

with FileManager() as f:
    f.write("data")
```

**Async context manager:**

```python
class AsyncFileManager:
    async def __aenter__(self):
        # Async setup
        self.file = await async_open("data.txt", "w")
        return self.file

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Async cleanup
        await self.file.aclose()

async with AsyncFileManager() as f:
    await f.write("data")
```

**Key difference:** `__aenter__` and `__aexit__` are `async def`.

## Mobile Platform Comparison

**Swift (defer):**

```swift
func fetchData() async throws -> Data {
    let client = HTTPClient()
    defer { await client.close() }  // Cleanup

    return try await client.get(url)
}
```

**Kotlin (use extension):**

```kotlin
suspend fun fetchData(): Data {
    return HttpClient().use { client ->
        client.get(url)
    }  // Cleanup happens automatically
}
```

**Dart (try/finally):**

```dart
Future<Data> fetchData() async {
  final client = HttpClient();
  try {
    return await client.get(url);
  } finally {
    await client.close();  // Cleanup
  }
}
```

**Python (async with):**

```python
async def fetch_data():
    async with httpx.AsyncClient() as client:
        return await client.get(url)
    # Cleanup happens automatically
```

## Built-in Async Context Managers

**httpx.AsyncClient:**

```python
import httpx

async def fetch():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

**aiofiles (async file I/O):**

```python
import aiofiles

async def read_file():
    async with aiofiles.open("data.txt", "r") as f:
        content = await f.read()
        return content
```

**SQLAlchemy async session:**

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def query_user(session_factory):
    async with session_factory() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
```

## Creating Custom Async Context Managers

**Method 1: Class with `__aenter__` and `__aexit__`:**

```python
import asyncio

class AsyncTimer:
    """Measure async operation time."""

    async def __aenter__(self):
        self.start = asyncio.get_event_loop().time()
        print("Timer started")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed = asyncio.get_event_loop().time() - self.start
        print(f"Timer stopped: {elapsed:.2f}s")

async def main():
    async with AsyncTimer():
        await asyncio.sleep(1.5)

asyncio.run(main())

# Output:
# Timer started
# Timer stopped: 1.50s
```

**Method 2: @asynccontextmanager decorator (easier):**

```python
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def async_timer():
    """Measure async operation time."""
    start = asyncio.get_event_loop().time()
    print("Timer started")

    yield  # Code runs here

    elapsed = asyncio.get_event_loop().time() - start
    print(f"Timer stopped: {elapsed:.2f}s")

async def main():
    async with async_timer():
        await asyncio.sleep(1.5)

asyncio.run(main())
```

## Practical Example: Database Transaction

```python
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def transaction(session: AsyncSession):
    """Async transaction context manager."""
    try:
        yield session
        await session.commit()
        print("Transaction committed")
    except Exception as e:
        await session.rollback()
        print(f"Transaction rolled back: {e}")
        raise

async def create_user(session_factory, name: str):
    async with session_factory() as session:
        async with transaction(session):
            user = User(name=name)
            session.add(user)
            # Automatically commits on success
            # Automatically rolls back on error
```

## Nested Async Context Managers

```python
import httpx
import aiofiles

async def fetch_and_save(url: str, filename: str):
    """Fetch data and save to file."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        async with aiofiles.open(filename, "w") as f:
            await f.write(response.text)
```

## Error Handling

**Cleanup runs even on error:**

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def resource():
    print("Setup")
    try:
        yield
    finally:
        print("Cleanup (always runs)")

async def main():
    try:
        async with resource():
            print("Using resource")
            raise ValueError("Something failed")
    except ValueError:
        print("Caught error")

asyncio.run(main())

# Output:
# Setup
# Using resource
# Cleanup (always runs)
# Caught error
```

## Async Lock Context Manager

```python
import asyncio

lock = asyncio.Lock()

async def protected_operation(id: int):
    """Only one task can run this at a time."""
    async with lock:
        print(f"Task {id} acquired lock")
        await asyncio.sleep(1)
        print(f"Task {id} releasing lock")

async def main():
    await asyncio.gather(
        protected_operation(1),
        protected_operation(2),
        protected_operation(3)
    )

asyncio.run(main())

# Output:
# Task 1 acquired lock
# Task 1 releasing lock
# Task 2 acquired lock
# Task 2 releasing lock
# Task 3 acquired lock
# Task 3 releasing lock
```

## API Client with Connection Pooling

```python
from contextlib import asynccontextmanager
import httpx

class APIClient:
    """Reusable API client with connection pooling."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def get(self, path: str):
        return await self._client.get(path)

    async def post(self, path: str, data: dict):
        return await self._client.post(path, json=data)

async def main():
    async with APIClient("https://api.example.com") as client:
        users = await client.get("/users")
        posts = await client.get("/posts")
        # Connection pool reused for both requests
    # Client closed automatically

asyncio.run(main())
```

## When to Use Async Context Managers

**Use when:**
- Resource needs async cleanup (close, flush, commit)
- Setup requires async operation (open connection, acquire lock)
- You want guaranteed cleanup (even on error)

**Common use cases:**
- HTTP clients (httpx.AsyncClient)
- Database sessions (AsyncSession)
- File I/O (aiofiles)
- Locks and semaphores (asyncio.Lock)
- Custom resource management

## Key Takeaways

1. **Async context managers ensure cleanup** in async code
2. **Use `async with`** not `with` for async resources
3. **`__aenter__` and `__aexit__`** are async methods
4. **@asynccontextmanager decorator** is easier than class
5. **Cleanup runs even on error** (like finally block)
6. **Like Swift defer, Kotlin use, Dart try/finally** but async-aware
7. **Built-in examples:** httpx.AsyncClient, aiofiles, AsyncSession
8. **Always preferred over manual cleanup** (less error-prone)
