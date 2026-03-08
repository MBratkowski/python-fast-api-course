"""
Exercise 2: Sliding Window Rate Limiter

Implement a sliding window rate limiter using Redis sorted sets.
The sliding window precisely tracks individual request timestamps
and counts requests within a moving time window.

Run: pytest 023-rate-limiting/exercises/02_sliding_window.py -v

Requirements: pip install fakeredis pytest pytest-asyncio
"""

import time
from unittest.mock import patch

import fakeredis.aioredis
import pytest
import pytest_asyncio


# ============= SLIDING WINDOW LIMITER (IMPLEMENT THIS) =============

class SlidingWindowLimiter:
    """
    Sliding window rate limiter using Redis sorted sets.

    How it works:
    - Each request timestamp is stored in a sorted set (score = timestamp)
    - On each check, remove timestamps older than the window
    - Count remaining entries to determine if under the limit

    Redis commands used:
    - ZREMRANGEBYSCORE: remove entries outside the window
    - ZADD: add current request timestamp
    - ZCARD: count entries in the set
    - EXPIRE: set key expiry for cleanup
    """

    def __init__(self, redis_client, max_requests: int = 10, window_seconds: int = 60):
        """
        Args:
            redis_client: Redis (or fakeredis) async client
            max_requests: Maximum requests allowed in the window
            window_seconds: Size of the sliding window in seconds
        """
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if a request is allowed under the rate limit.

        Returns:
            (allowed: bool, remaining: int) -- whether the request is allowed
            and how many requests remain in the current window.

        Steps:
        1. Build sorted set key: f"sw:{key}"
        2. Get current time with time.time()
        3. Calculate window_start = now - window_seconds
        4. Use a Redis pipeline (self.redis.pipeline()) to execute atomically:
           a. ZREMRANGEBYSCORE(key, 0, window_start) -- remove old entries
           b. ZADD(key, {str(now): now}) -- add current request
           c. ZCARD(key) -- count entries
           d. EXPIRE(key, window_seconds) -- set expiry
        5. Execute pipeline and get results
        6. request_count = results[2] (ZCARD result)
        7. If request_count > max_requests:
           - Remove the entry we just added (ZREM)
           - Return (False, 0)
        8. Otherwise:
           - remaining = max_requests - request_count
           - Return (True, remaining)

        Hint: Pipeline results are a list in the same order as commands.
        """
        # TODO: Implement sliding window algorithm
        pass


# ============= TESTS =============
# Run with: pytest 023-rate-limiting/exercises/02_sliding_window.py -v


@pytest_asyncio.fixture
async def redis_client():
    """Create a fresh fakeredis async instance for each test."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield client
    await client.flushall()
    await client.aclose()


@pytest.mark.asyncio
async def test_first_request_allowed(redis_client):
    """First request should be allowed with correct remaining count."""
    limiter = SlidingWindowLimiter(redis_client, max_requests=5, window_seconds=60)

    allowed, remaining = await limiter.is_allowed("user:1")
    assert allowed is True, "First request should be allowed"
    assert remaining == 4, f"Should have 4 remaining, got {remaining}"


@pytest.mark.asyncio
async def test_requests_within_limit(redis_client):
    """All requests within the limit should be allowed with decreasing remaining."""
    limiter = SlidingWindowLimiter(redis_client, max_requests=5, window_seconds=60)

    base_time = 1000000.0
    for i in range(5):
        with patch("time.time", return_value=base_time + i * 0.001):
            allowed, remaining = await limiter.is_allowed("user:1")
            assert allowed is True, f"Request {i+1} should be allowed"
            assert remaining == 4 - i, f"Request {i+1}: expected {4-i} remaining, got {remaining}"


@pytest.mark.asyncio
async def test_request_denied_over_limit(redis_client):
    """Request exceeding the limit should be denied."""
    limiter = SlidingWindowLimiter(redis_client, max_requests=3, window_seconds=60)

    base_time = 1000000.0
    # Make 3 allowed requests
    for i in range(3):
        with patch("time.time", return_value=base_time + i * 0.001):
            allowed, _ = await limiter.is_allowed("user:1")
            assert allowed is True

    # 4th request should be denied
    with patch("time.time", return_value=base_time + 0.005):
        allowed, remaining = await limiter.is_allowed("user:1")
        assert allowed is False, "4th request should be denied"
        assert remaining == 0, f"Remaining should be 0, got {remaining}"


@pytest.mark.asyncio
async def test_old_requests_cleaned_up(redis_client):
    """Requests outside the window should be removed, allowing new requests."""
    limiter = SlidingWindowLimiter(redis_client, max_requests=3, window_seconds=60)

    # Make 3 requests at time 1000
    with patch("time.time", return_value=1000.0):
        for _ in range(3):
            await limiter.is_allowed("user:1")

    # At time 1000 + 0.001: should be denied (still within window)
    with patch("time.time", return_value=1000.001):
        allowed, _ = await limiter.is_allowed("user:1")
        assert allowed is False, "Should be denied while window is full"

    # At time 1061 (61 seconds later): all old requests are outside window
    with patch("time.time", return_value=1061.0):
        allowed, remaining = await limiter.is_allowed("user:1")
        assert allowed is True, "Should be allowed after window passes"
        assert remaining == 2, f"Should have 2 remaining, got {remaining}"


@pytest.mark.asyncio
async def test_independent_keys(redis_client):
    """Different keys should have independent rate limits."""
    limiter = SlidingWindowLimiter(redis_client, max_requests=2, window_seconds=60)

    fixed_time = 1000000.0
    with patch("time.time", return_value=fixed_time):
        # Use up user:1's limit
        await limiter.is_allowed("user:1")
        await limiter.is_allowed("user:1")

    with patch("time.time", return_value=fixed_time + 0.001):
        allowed_1, _ = await limiter.is_allowed("user:1")
        assert allowed_1 is False, "user:1 should be denied"

    with patch("time.time", return_value=fixed_time + 0.002):
        allowed_2, remaining_2 = await limiter.is_allowed("user:2")
        assert allowed_2 is True, "user:2 should not be affected"
        assert remaining_2 == 1, "user:2 should have 1 remaining"


@pytest.mark.asyncio
async def test_remaining_never_negative(redis_client):
    """Remaining count should never be negative."""
    limiter = SlidingWindowLimiter(redis_client, max_requests=2, window_seconds=60)

    base_time = 1000000.0
    with patch("time.time", return_value=base_time):
        await limiter.is_allowed("user:1")
        await limiter.is_allowed("user:1")

    # Try multiple denied requests
    for i in range(3):
        with patch("time.time", return_value=base_time + 0.001 + i * 0.001):
            _, remaining = await limiter.is_allowed("user:1")
            assert remaining >= 0, f"Remaining should never be negative, got {remaining}"


@pytest.mark.asyncio
async def test_denied_requests_not_counted(redis_client):
    """Denied requests should not be stored in the sorted set."""
    limiter = SlidingWindowLimiter(redis_client, max_requests=2, window_seconds=60)

    base_time = 1000000.0
    with patch("time.time", return_value=base_time):
        await limiter.is_allowed("user:1")
        await limiter.is_allowed("user:1")

    # Make several denied requests
    for i in range(5):
        with patch("time.time", return_value=base_time + 0.001 + i * 0.001):
            await limiter.is_allowed("user:1")

    # Check sorted set has only 2 entries (not 7)
    count = await redis_client.zcard("sw:user:1")
    assert count == 2, f"Sorted set should have 2 entries, got {count}"
