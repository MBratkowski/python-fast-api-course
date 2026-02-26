# Async Python Basics

## Why This Matters

You know async/await from mobile - waiting for network calls without blocking the UI. Backend is the same: handle many requests concurrently without blocking.

## The Concept

```
Synchronous:     Request 1 ████████░░░░░░░░ Request 2 ████████░░░░░░░░
                          DB wait           DB wait

Asynchronous:    Request 1 ██░░░░░░██░░░░░░
                 Request 2 ░░██░░░░░░██░░░░
                          (concurrent)
```

## Basic Syntax

```python
import asyncio

# Async function (coroutine)
async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(1)  # Simulate DB/API call
    return {"id": user_id, "name": "Alice"}

# Call with await
async def main():
    user = await fetch_user(1)
    print(user)

# Run the async function
asyncio.run(main())
```

## Concurrent Execution

Run multiple async operations at once:

```python
import asyncio

async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(1)
    return {"id": user_id}

async def main():
    # Sequential: 3 seconds
    user1 = await fetch_user(1)
    user2 = await fetch_user(2)
    user3 = await fetch_user(3)

    # Concurrent: 1 second
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
    print(users)  # [{"id": 1}, {"id": 2}, {"id": 3}]

asyncio.run(main())
```

## FastAPI Async Endpoints

FastAPI handles async natively:

```python
from fastapi import FastAPI

app = FastAPI()

# Async endpoint
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await fetch_from_database(user_id)
    return user

# Sync endpoint (also works, FastAPI handles it)
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

## When to Use Async

**Use async for**:
- Database queries
- HTTP requests to other services
- File I/O
- Any waiting operation

**Use sync for**:
- CPU-intensive work (calculations)
- Simple operations with no I/O

## Common Async Libraries

```python
# HTTP client
import httpx

async def call_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# Database (async SQLAlchemy)
from sqlalchemy.ext.asyncio import AsyncSession

async def get_users(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()
```

## Error Handling

```python
import asyncio

async def fetch_with_timeout(user_id: int) -> dict | None:
    try:
        return await asyncio.wait_for(
            fetch_user(user_id),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        return None
```

## Key Takeaways

1. **`async def`** defines a coroutine
2. **`await`** pauses until the operation completes
3. **`asyncio.gather()`** runs multiple operations concurrently
4. **FastAPI** handles both async and sync endpoints
5. Use async for I/O, sync for CPU-bound work
