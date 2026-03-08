# Client-Side Handling of Rate Limits

## Why This Matters

As a mobile developer, this is the other side of the conversation. You have built the rate limiter on the backend -- now you need to understand how mobile clients should handle the 429 responses you send. This knowledge makes you a better API designer because you will build rate limiting that is easy for clients to work with.

When your iOS or Android app receives a 429 from an API you call, the wrong response is to immediately retry. The right response is to read the `Retry-After` header, back off, queue pending requests, and show the user a helpful message.

## Handling 429 Responses

### The Wrong Way

```python
# DO NOT do this -- retry storm
async def fetch_data_bad(client, url):
    while True:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        # Immediately retrying makes the problem worse!
```

### The Right Way

```python
import asyncio
import httpx


async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    max_retries: int = 3,
) -> dict | None:
    """Fetch with proper 429 handling and exponential backoff."""
    for attempt in range(max_retries):
        response = await client.get(url)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:
            # Read Retry-After header
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                wait_time = int(retry_after)
            else:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt

            print(f"Rate limited. Waiting {wait_time}s before retry...")
            await asyncio.sleep(wait_time)
            continue

        # Other errors -- do not retry
        response.raise_for_status()

    return None  # All retries exhausted
```

## Exponential Backoff

Exponential backoff increases the wait time between retries exponentially. This prevents the "thundering herd" problem where all rate-limited clients retry at the same time.

```
Attempt 1: wait 1 second
Attempt 2: wait 2 seconds
Attempt 3: wait 4 seconds
Attempt 4: wait 8 seconds
...with random jitter to spread retries
```

```python
import random
import asyncio


def calculate_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
) -> float:
    """
    Calculate exponential backoff delay with optional jitter.

    Args:
        attempt: Current retry attempt (0-indexed)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        jitter: Add randomness to prevent thundering herd
    """
    delay = min(base_delay * (2 ** attempt), max_delay)

    if jitter:
        # Full jitter: random value between 0 and calculated delay
        delay = random.uniform(0, delay)

    return delay


# Usage
for attempt in range(5):
    delay = calculate_backoff(attempt)
    print(f"Attempt {attempt}: wait {delay:.1f}s")
    # Attempt 0: wait 0.7s  (random 0-1)
    # Attempt 1: wait 1.3s  (random 0-2)
    # Attempt 2: wait 2.8s  (random 0-4)
    # Attempt 3: wait 5.1s  (random 0-8)
    # Attempt 4: wait 12.4s (random 0-16)
```

## Reading Rate Limit Headers Proactively

Smart clients read rate limit headers on every response, not just 429s:

```python
import httpx


class RateLimitAwareClient:
    """HTTP client that proactively respects rate limits."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.remaining = None
        self.reset_at = None

    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            # Pre-check: if we know we are out of requests, wait
            if self.remaining is not None and self.remaining <= 0:
                import time
                now = time.time()
                if self.reset_at and self.reset_at > now:
                    wait = self.reset_at - now
                    print(f"Proactively waiting {wait:.0f}s (no remaining requests)")
                    await asyncio.sleep(wait)

            response = await client.request(method, path, **kwargs)

            # Update rate limit state from headers
            if "X-RateLimit-Remaining" in response.headers:
                self.remaining = int(response.headers["X-RateLimit-Remaining"])
            if "X-RateLimit-Reset" in response.headers:
                self.reset_at = int(response.headers["X-RateLimit-Reset"])

            return response
```

## Request Queuing During Rate Limit

When rate limited, queue requests instead of dropping them:

```python
import asyncio
from collections import deque


class RequestQueue:
    """Queue requests during rate limiting and process when allowed."""

    def __init__(self):
        self.queue: deque = deque()
        self.is_rate_limited = False
        self.retry_after = 0

    async def enqueue(self, coro):
        """Add a request to the queue."""
        if self.is_rate_limited:
            future = asyncio.get_event_loop().create_future()
            self.queue.append((coro, future))
            return await future
        return await coro

    async def process_queue(self):
        """Process queued requests after rate limit window passes."""
        if self.retry_after > 0:
            await asyncio.sleep(self.retry_after)

        self.is_rate_limited = False
        while self.queue:
            coro, future = self.queue.popleft()
            try:
                result = await coro
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

    def on_rate_limited(self, retry_after: int):
        """Called when a 429 is received."""
        self.is_rate_limited = True
        self.retry_after = retry_after
        # Start processing queue after retry_after seconds
        asyncio.create_task(self.process_queue())
```

## User-Friendly Messages

Never show raw HTTP errors to users. Map 429 responses to helpful messages:

```python
def get_user_message(status_code: int, headers: dict) -> str:
    """Convert HTTP error to user-friendly message."""
    if status_code == 429:
        retry_after = headers.get("Retry-After", "60")
        minutes = int(retry_after) // 60
        seconds = int(retry_after) % 60

        if minutes > 0:
            return f"You're making requests too quickly. Please wait {minutes} minute(s) and try again."
        return f"You're making requests too quickly. Please wait {seconds} seconds and try again."

    if status_code == 503:
        return "The service is temporarily unavailable. Please try again in a moment."

    return "Something went wrong. Please try again later."
```

## Mobile Platform Patterns

### iOS (Swift) -- URLSession Retry

```swift
// How iOS apps handle 429 from your API
func fetchData() async throws -> Data {
    var request = URLRequest(url: apiURL)
    let (data, response) = try await URLSession.shared.data(for: request)

    if let httpResponse = response as? HTTPURLResponse,
       httpResponse.statusCode == 429 {
        let retryAfter = httpResponse.value(forHTTPHeaderField: "Retry-After")
        let delay = TimeInterval(retryAfter ?? "5") ?? 5.0
        try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
        return try await fetchData()  // Retry after waiting
    }

    return data
}
```

### Android (Kotlin) -- Retrofit/OkHttp Interceptor

```kotlin
// How Android apps handle 429 from your API
class RateLimitInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())

        if (response.code == 429) {
            val retryAfter = response.header("Retry-After")?.toLongOrNull() ?: 5L
            Thread.sleep(retryAfter * 1000)
            response.close()
            return chain.proceed(chain.request())  // Retry after waiting
        }

        return response
    }
}
```

### Python (httpx) -- Backend Calling Another API

```python
import httpx
import asyncio


async def call_external_api(url: str) -> dict:
    """Call an external API with proper rate limit handling."""
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            response = await client.get(url)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "5"))
                await asyncio.sleep(retry_after)
                continue

            response.raise_for_status()

    raise Exception("Max retries exceeded")
```

## Design Guidelines for API Builders

As the API builder, make rate limiting easy for clients:

1. **Always include `Retry-After` on 429s** -- do not make clients guess
2. **Include rate limit headers on all responses** -- let clients monitor proactively
3. **Use seconds for `Retry-After`** -- simpler than HTTP-date format
4. **Return JSON error body** -- not just a status code
5. **Document your limits** -- publish rate limits in API documentation
6. **Use consistent limits** -- same limit behavior across all endpoints of the same type

## Key Takeaways

1. **Read `Retry-After`** headers on 429 responses -- never retry immediately
2. **Use exponential backoff with jitter** when `Retry-After` is not provided
3. **Read rate limit headers proactively** on every response to avoid hitting limits
4. **Queue requests** during rate limiting instead of dropping them
5. **Show user-friendly messages** -- never expose raw HTTP errors
6. **Design your API for client convenience** -- include headers, JSON errors, and documentation
