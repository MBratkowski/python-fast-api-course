# Project: Async Data Aggregation Pipeline

## Overview

Build an async data aggregation pipeline that fetches data from multiple APIs concurrently, handles errors gracefully, implements rate limiting with semaphores, and reports metrics. This project combines everything you learned about async Python.

**Goal**: Create a production-ready async pipeline that can fetch from 10+ APIs concurrently, handle partial failures, respect rate limits, and clean up resources properly.

## Requirements

### 1. API Aggregator Class

Create `APIAggregator` class using async context manager pattern:

**Structure:**
```python
class APIAggregator:
    async def __aenter__(self):
        # Setup: create HTTP client, initialize metrics
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup: close HTTP client, log metrics
        pass

    async def fetch(self, url: str) -> dict:
        # Fetch from single API with error handling
        pass

    async def aggregate(self, urls: list[str]) -> dict:
        # Fetch from all APIs concurrently with rate limiting
        pass
```

**Features:**
- Use `httpx.AsyncClient` for HTTP requests
- Implement rate limiting with `asyncio.Semaphore`
- Track metrics (success count, failure count, total time)
- Proper cleanup in `__aexit__`

### 2. Concurrent Fetching

**Fetch from multiple APIs concurrently:**
- Accept list of API URLs
- Use `asyncio.gather()` with `return_exceptions=True`
- Limit concurrent requests with semaphore (configurable, default 5)
- Return both successes and failures

**Example:**
```python
async with APIAggregator(concurrency_limit=5) as agg:
    result = await agg.aggregate([
        "https://api.example.com/users",
        "https://api.example.com/posts",
        "https://api.example.com/comments"
    ])
```

### 3. Error Handling

**Handle failures gracefully:**
- HTTP errors (404, 500, etc.)
- Timeout errors (set timeout to 5 seconds)
- Network errors (connection failed)
- Collect partial results (don't fail entire pipeline on one error)

**Separate successes from failures:**
```python
{
    "successes": [
        {"url": "...", "data": {...}},
        {"url": "...", "data": {...}}
    ],
    "failures": [
        {"url": "...", "error": "404 Not Found"},
        {"url": "...", "error": "Timeout"}
    ]
}
```

### 4. Rate Limiting

**Use semaphore to limit concurrent requests:**
- Configurable limit (default: 5 concurrent requests)
- Prevent overwhelming target APIs
- Track max concurrent execution

**Example:**
```python
# Only 5 requests run at a time, even with 50 URLs
async with APIAggregator(concurrency_limit=5) as agg:
    result = await agg.aggregate(list_of_50_urls)
```

### 5. Metrics Collection

**Track and report metrics:**
- Total requests attempted
- Successful requests count
- Failed requests count
- Total execution time
- Average response time
- Max concurrent requests

**Return metrics with results:**
```python
{
    "successes": [...],
    "failures": [...],
    "metrics": {
        "total_requests": 50,
        "successful": 45,
        "failed": 5,
        "total_time": 10.5,
        "avg_response_time": 0.21,
        "max_concurrent": 5
    }
}
```

### 6. Retry Logic (Stretch Goal)

**Retry failed requests with exponential backoff:**
- Retry up to 3 times for transient failures (5xx errors, timeouts)
- Don't retry permanent failures (4xx errors)
- Exponential backoff: 1s, 2s, 4s
- Track retry attempts in metrics

## Starter Template

```python
"""
Async Data Aggregation Pipeline
TODO: Build production-ready async pipeline with error handling and rate limiting
"""

import asyncio
import time
from contextlib import asynccontextmanager
import httpx

class APIAggregator:
    """Async API aggregator with rate limiting and error handling."""

    def __init__(self, concurrency_limit: int = 5, timeout: float = 5.0):
        """
        Initialize aggregator.

        Args:
            concurrency_limit: Max concurrent requests
            timeout: Request timeout in seconds
        """
        self.concurrency_limit = concurrency_limit
        self.timeout = timeout
        self.client = None
        self.semaphore = None
        self.metrics = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "total_time": 0,
            "max_concurrent": 0
        }

    async def __aenter__(self):
        """Setup: create HTTP client and semaphore."""
        # TODO: Implement
        # - Create httpx.AsyncClient
        # - Create asyncio.Semaphore with concurrency_limit
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup: close HTTP client, log metrics."""
        # TODO: Implement
        # - Close self.client
        # - Log self.metrics
        pass

    async def fetch(self, url: str) -> dict:
        """
        Fetch data from a single URL with error handling.

        Args:
            url: API endpoint URL

        Returns:
            dict with "url" and either "data" or "error"
        """
        # TODO: Implement
        # - Use semaphore to limit concurrency
        # - Use httpx client to GET url with timeout
        # - Handle httpx.HTTPStatusError, httpx.TimeoutException
        # - Update metrics
        # - Return {"url": url, "data": response.json()} on success
        # - Return {"url": url, "error": str(error)} on failure
        pass

    async def aggregate(self, urls: list[str]) -> dict:
        """
        Fetch from all URLs concurrently.

        Args:
            urls: List of API endpoint URLs

        Returns:
            dict with "successes", "failures", and "metrics"
        """
        # TODO: Implement
        # - Record start time
        # - Use asyncio.gather() with return_exceptions=True
        # - Separate successes from failures
        # - Calculate metrics (total_time, avg_response_time)
        # - Return results with metrics
        pass

# ============= Usage Example =============

async def main():
    """Example usage of APIAggregator."""
    urls = [
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/users/2",
        "https://jsonplaceholder.typicode.com/users/3",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/invalid",  # Will fail
    ]

    async with APIAggregator(concurrency_limit=3) as agg:
        result = await agg.aggregate(urls)

        print(f"Successful: {len(result['successes'])}")
        print(f"Failed: {len(result['failures'])}")
        print(f"Metrics: {result['metrics']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Success Criteria

- [ ] `APIAggregator` implements async context manager protocol
- [ ] Fetches from multiple APIs concurrently
- [ ] Rate limiting works (respects concurrency limit)
- [ ] Handles errors gracefully (partial failures don't break pipeline)
- [ ] Returns both successes and failures
- [ ] Collects and reports metrics
- [ ] HTTP client is properly closed
- [ ] Works with real APIs (test with jsonplaceholder.typicode.com)
- [ ] Tests pass with `pytest tests/ -v`

## Testing Your Implementation

```python
import pytest

@pytest.mark.asyncio
async def test_aggregator_basic():
    """Test basic aggregation."""
    urls = [
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/users/2"
    ]

    async with APIAggregator() as agg:
        result = await agg.aggregate(urls)

    assert len(result["successes"]) == 2
    assert len(result["failures"]) == 0

@pytest.mark.asyncio
async def test_aggregator_with_failures():
    """Test handling failures."""
    urls = [
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/invalid/404"
    ]

    async with APIAggregator() as agg:
        result = await agg.aggregate(urls)

    assert len(result["successes"]) == 1
    assert len(result["failures"]) == 1

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test concurrency limit."""
    urls = [f"https://jsonplaceholder.typicode.com/users/{i}" for i in range(1, 11)]

    async with APIAggregator(concurrency_limit=3) as agg:
        result = await agg.aggregate(urls)

    # Max concurrent should not exceed 3
    assert result["metrics"]["max_concurrent"] <= 3
```

## Stretch Goals

1. **Retry logic**: Retry failed requests with exponential backoff (max 3 retries)
2. **Async generator**: Use async generator to yield results as they arrive
3. **Progress reporting**: Add progress callback that reports completion percentage
4. **Caching**: Cache successful responses (simple dict cache with TTL)
5. **Response validation**: Validate response schema with Pydantic
6. **Batching**: Process URLs in batches (e.g., 100 URLs → 10 batches of 10)
7. **Circuit breaker**: Stop calling failing APIs after N consecutive failures
8. **Streaming responses**: Handle streaming JSON responses (large datasets)

## Resources

- [httpx documentation](https://www.python-httpx.org/)
- [asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO](https://realpython.com/async-io-python/)
- [jsonplaceholder.typicode.com](https://jsonplaceholder.typicode.com/) (free fake API for testing)
