# Module 012: Advanced Async Python

## Why This Module?

Go deeper into async programming. Handle concurrent database queries, external API calls, and optimize performance.

## What You'll Learn

- asyncio in depth
- Concurrent operations (gather, wait)
- Async context managers
- Async generators
- Semaphores & rate limiting
- Error handling in async code

## Topics

### Theory
1. asyncio Event Loop
2. gather() vs wait() vs as_completed()
3. Semaphores for Concurrency Limits
4. Async Context Managers
5. Async Generators & Streaming
6. Exception Handling Patterns

### Project
Build an API that aggregates data from multiple external services concurrently.

## Example

```python
import asyncio
from asyncio import Semaphore

# Limit concurrent requests
semaphore = Semaphore(10)

async def fetch_with_limit(url: str):
    async with semaphore:
        async with httpx.AsyncClient() as client:
            return await client.get(url)

async def fetch_all(urls: list[str]) -> list[dict]:
    tasks = [fetch_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r.json() for r in results if not isinstance(r, Exception)]
```
