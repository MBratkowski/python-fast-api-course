"""
Exercise 1: Token Bucket Rate Limiter

Implement a token bucket rate limiter using fakeredis.
The token bucket allows bursts up to capacity, then refills tokens at a steady rate.

Run: pytest 023-rate-limiting/exercises/01_token_bucket.py -v

Requirements: pip install fakeredis pytest pytest-asyncio
"""

import time
from unittest.mock import patch

import fakeredis.aioredis
import pytest
import pytest_asyncio


# ============= TOKEN BUCKET LIMITER (IMPLEMENT THIS) =============

class TokenBucketLimiter:
    """
    Token bucket rate limiter backed by Redis.

    How it works:
    - Bucket starts full with `capacity` tokens
    - Each request consumes one token
    - Tokens refill at `refill_rate` tokens per second
    - Request denied if no tokens available

    Uses a Redis hash to store:
    - "tokens": current token count (float, stored as string)
    - "last_refill": timestamp of last refill calculation (float, stored as string)
    """

    def __init__(self, redis_client, capacity: int = 10, refill_rate: float = 1.0):
        """
        Args:
            redis_client: Redis (or fakeredis) async client
            capacity: Maximum tokens in the bucket
            refill_rate: Tokens added per second
        """
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate

    async def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed under the rate limit.
        If allowed, consumes one token and returns True.
        If denied, returns False.

        Steps:
        1. Build bucket key: f"bucket:{key}"
        2. Get current bucket state with HGETALL
        3. If no bucket exists (first request):
           - Set tokens = capacity - 1, last_refill = current time
           - Set key expiry to 3600 seconds
           - Return True
        4. If bucket exists:
           - Parse tokens and last_refill from hash (values are bytes)
           - Calculate elapsed time since last_refill
           - Refill tokens: tokens + elapsed * refill_rate (cap at capacity)
           - If tokens < 1: return False (no tokens available)
           - Otherwise: consume one token (tokens - 1), update hash, return True

        Hint: Use time.time() for timestamps. Hash values from Redis
        are bytes -- decode with float(bucket[b"tokens"]).
        """
        # TODO: Implement token bucket algorithm
        pass


# ============= TESTS =============
# Run with: pytest 023-rate-limiting/exercises/01_token_bucket.py -v


@pytest_asyncio.fixture
async def redis_client():
    """Create a fresh fakeredis async instance for each test."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield client
    await client.flushall()
    await client.aclose()


@pytest.mark.asyncio
async def test_first_request_allowed(redis_client):
    """First request should always be allowed (bucket starts full)."""
    limiter = TokenBucketLimiter(redis_client, capacity=5, refill_rate=1.0)

    result = await limiter.is_allowed("user:1")
    assert result is True, "First request should be allowed"


@pytest.mark.asyncio
async def test_requests_up_to_capacity_allowed(redis_client):
    """All requests up to bucket capacity should be allowed."""
    limiter = TokenBucketLimiter(redis_client, capacity=5, refill_rate=1.0)

    # Mock time to stay constant (no refill between requests)
    fixed_time = 1000000.0
    with patch("time.time", return_value=fixed_time):
        results = []
        for _ in range(5):
            results.append(await limiter.is_allowed("user:1"))

    assert all(results), f"All 5 requests should be allowed, got {results}"


@pytest.mark.asyncio
async def test_request_denied_when_bucket_empty(redis_client):
    """Request should be denied when bucket has no tokens."""
    limiter = TokenBucketLimiter(redis_client, capacity=3, refill_rate=1.0)

    # Use up all tokens with fixed time
    fixed_time = 1000000.0
    with patch("time.time", return_value=fixed_time):
        for _ in range(3):
            await limiter.is_allowed("user:1")

        # 4th request should be denied
        result = await limiter.is_allowed("user:1")
        assert result is False, "Request should be denied when bucket is empty"


@pytest.mark.asyncio
async def test_tokens_refill_over_time(redis_client):
    """After time passes, tokens should refill and requests should be allowed again."""
    limiter = TokenBucketLimiter(redis_client, capacity=3, refill_rate=1.0)

    # Use up all tokens at time 1000
    with patch("time.time", return_value=1000.0):
        for _ in range(3):
            await limiter.is_allowed("user:1")

        # Verify bucket is empty
        result = await limiter.is_allowed("user:1")
        assert result is False, "Bucket should be empty"

    # Advance time by 2 seconds (2 tokens refill at rate 1.0/sec)
    with patch("time.time", return_value=1002.0):
        result = await limiter.is_allowed("user:1")
        assert result is True, "Should be allowed after tokens refill"

        result2 = await limiter.is_allowed("user:1")
        assert result2 is True, "Should have another refilled token"


@pytest.mark.asyncio
async def test_tokens_cap_at_capacity(redis_client):
    """Tokens should never exceed capacity even after long idle periods."""
    limiter = TokenBucketLimiter(redis_client, capacity=5, refill_rate=1.0)

    # Use one token at time 1000
    with patch("time.time", return_value=1000.0):
        await limiter.is_allowed("user:1")

    # Wait a very long time (1000 seconds) -- should cap at capacity
    with patch("time.time", return_value=2000.0):
        results = []
        for _ in range(5):
            results.append(await limiter.is_allowed("user:1"))

        assert all(results), "Should allow up to capacity requests"

        # 6th request should be denied (only 5 capacity)
        result = await limiter.is_allowed("user:1")
        assert result is False, "Should not exceed capacity"


@pytest.mark.asyncio
async def test_independent_keys(redis_client):
    """Different keys should have independent buckets."""
    limiter = TokenBucketLimiter(redis_client, capacity=2, refill_rate=1.0)

    fixed_time = 1000000.0
    with patch("time.time", return_value=fixed_time):
        # Use up user:1's tokens
        await limiter.is_allowed("user:1")
        await limiter.is_allowed("user:1")
        result_1 = await limiter.is_allowed("user:1")
        assert result_1 is False, "user:1 should be rate limited"

        # user:2 should still have tokens
        result_2 = await limiter.is_allowed("user:2")
        assert result_2 is True, "user:2 should not be affected by user:1"


@pytest.mark.asyncio
async def test_fractional_refill_rate(redis_client):
    """Refill rate of 0.5 should add one token every 2 seconds."""
    limiter = TokenBucketLimiter(redis_client, capacity=3, refill_rate=0.5)

    # Use all tokens at time 1000
    with patch("time.time", return_value=1000.0):
        for _ in range(3):
            await limiter.is_allowed("user:1")

        result = await limiter.is_allowed("user:1")
        assert result is False, "Bucket should be empty"

    # After 1 second at rate 0.5, only 0.5 tokens -- not enough
    with patch("time.time", return_value=1001.0):
        result = await limiter.is_allowed("user:1")
        assert result is False, "0.5 tokens is not enough for a request"

    # After 2 seconds at rate 0.5, 1.0 token -- enough for one request
    with patch("time.time", return_value=1002.0):
        result = await limiter.is_allowed("user:1")
        assert result is True, "1.0 token should allow one request"
