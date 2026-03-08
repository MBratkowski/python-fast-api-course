"""
Exercise 3: Per-User Rate Limiting

Combine rate limiting with user identification. Each authenticated user
gets independent rate limit counters. Unauthenticated requests fall back
to IP-based rate limiting.

Run: pytest 023-rate-limiting/exercises/03_per_user_limits.py -v

Requirements: pip install fakeredis fastapi httpx pytest pytest-asyncio
"""

import time
from unittest.mock import patch

import fakeredis.aioredis
import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.testclient import TestClient


# ============= RATE LIMITER (PROVIDED) =============
# A simple sliding window rate limiter for use in this exercise.

class SimpleLimiter:
    """Provided sliding window limiter. Use this in your endpoint."""

    def __init__(self, redis_client, max_requests: int, window_seconds: int):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, key: str) -> tuple[bool, int]:
        """Check if request is allowed. Returns (allowed, remaining)."""
        now = time.time()
        window_start = now - self.window_seconds
        sorted_set_key = f"sw:{key}"

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(sorted_set_key, 0, window_start)
        pipe.zadd(sorted_set_key, {str(now): now})
        pipe.zcard(sorted_set_key)
        pipe.expire(sorted_set_key, self.window_seconds)
        results = await pipe.execute()

        request_count = results[2]
        if request_count > self.max_requests:
            await self.redis.zrem(sorted_set_key, str(now))
            return False, 0

        remaining = max(0, self.max_requests - request_count)
        return True, remaining


# ============= APP SETUP (PROVIDED) =============

# Global redis client and limiter -- will be replaced in tests
_redis_client = None
_limiter = None


def get_redis():
    """Get Redis client (replaced in tests)."""
    return _redis_client


def get_limiter():
    """Get rate limiter (replaced in tests)."""
    return _limiter


app = FastAPI()


# ============= TODO: Exercise 3.1 =============
# Implement a function that extracts the user ID from a simple auth header.
#
# The header format is: "Authorization: Bearer user_{user_id}"
# For example: "Authorization: Bearer user_42" -> returns "user_42"
#
# If no Authorization header is present, return None.
# If the header does not start with "Bearer ", return None.
#
# This is a simplified auth -- real apps use JWT tokens (Module 009).

def extract_user_id(authorization: str | None = Header(default=None)) -> str | None:
    """
    Extract user identifier from Authorization header.

    Args:
        authorization: The Authorization header value, or None if not present.

    Returns:
        User identifier string (e.g., "user_42") or None if unauthenticated.
    """
    # TODO: Implement
    # 1. If authorization is None, return None
    # 2. If authorization doesn't start with "Bearer ", return None
    # 3. Extract and return the token part (after "Bearer ")
    pass


# ============= TODO: Exercise 3.2 =============
# Implement a function that builds the rate limit key.
#
# If a user_id is provided: return f"rl:user:{user_id}"
# If no user_id (unauthenticated): return f"rl:ip:{client_ip}"
#
# This determines whether rate limiting is per-user or per-IP.

def build_rate_limit_key(
    request: Request,
    user_id: str | None,
) -> str:
    """
    Build rate limit key based on user identity.

    Args:
        request: The FastAPI Request object (use request.client.host for IP).
        user_id: User identifier or None if unauthenticated.

    Returns:
        Rate limit key string.
    """
    # TODO: Implement
    # 1. If user_id is not None, return f"rl:user:{user_id}"
    # 2. Otherwise, return f"rl:ip:{request.client.host}"
    pass


# ============= TODO: Exercise 3.3 =============
# Implement the rate-limited endpoint.
#
# This endpoint should:
# 1. Extract user_id using extract_user_id
# 2. Build the rate limit key using build_rate_limit_key
# 3. Check the rate limit using the limiter's is_allowed method
# 4. If denied: raise HTTPException(status_code=429, detail="Rate limit exceeded")
# 5. If allowed: return {"message": "OK", "user": user_id, "remaining": remaining}

@app.get("/api/data")
async def get_data(
    request: Request,
    user_id: str | None = Depends(extract_user_id),
):
    """
    Rate-limited endpoint.

    Uses per-user rate limiting for authenticated requests
    and per-IP rate limiting for unauthenticated requests.
    """
    # TODO: Implement
    # 1. Get limiter via get_limiter()
    # 2. Build rate limit key using build_rate_limit_key(request, user_id)
    # 3. Call await limiter.is_allowed(key)
    # 4. If not allowed: raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # 5. If allowed: return {"message": "OK", "user": user_id, "remaining": remaining}
    pass


# ============= TESTS =============
# Run with: pytest 023-rate-limiting/exercises/03_per_user_limits.py -v


@pytest_asyncio.fixture
async def redis_for_test():
    """Create a fresh fakeredis instance."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=False)
    yield client
    await client.flushall()
    await client.aclose()


@pytest.fixture
def test_client(redis_for_test):
    """Create a test client with fakeredis-backed rate limiter."""
    global _redis_client, _limiter
    _redis_client = redis_for_test
    _limiter = SimpleLimiter(redis_for_test, max_requests=3, window_seconds=60)
    return TestClient(app)


def test_extract_user_id_with_bearer():
    """Should extract user ID from valid Bearer token."""
    result = extract_user_id("Bearer user_42")
    assert result == "user_42", f"Expected 'user_42', got {result}"


def test_extract_user_id_without_header():
    """Should return None when no header provided."""
    result = extract_user_id(None)
    assert result is None, "Should return None for missing header"


def test_extract_user_id_invalid_format():
    """Should return None for non-Bearer auth."""
    result = extract_user_id("Basic abc123")
    assert result is None, "Should return None for non-Bearer auth"


def test_authenticated_requests_allowed(test_client):
    """Authenticated user should get requests allowed up to limit."""
    with patch("time.time", return_value=1000000.0):
        for i in range(3):
            response = test_client.get(
                "/api/data",
                headers={"Authorization": "Bearer user_1"},
            )
            assert response.status_code == 200, f"Request {i+1} should be allowed"
            data = response.json()
            assert data["user"] == "user_1"


def test_authenticated_user_rate_limited(test_client):
    """Authenticated user should be denied after exceeding limit."""
    with patch("time.time", return_value=1000000.0):
        # Use up the limit
        for _ in range(3):
            test_client.get(
                "/api/data",
                headers={"Authorization": "Bearer user_1"},
            )

        # Next request should be denied
        response = test_client.get(
            "/api/data",
            headers={"Authorization": "Bearer user_1"},
        )
        assert response.status_code == 429, "Should return 429 when rate limited"


def test_different_users_independent_limits(test_client):
    """Different users should have independent rate limit counters."""
    with patch("time.time", return_value=1000000.0):
        # User A uses all their requests
        for _ in range(3):
            test_client.get(
                "/api/data",
                headers={"Authorization": "Bearer user_A"},
            )

        # User A is now rate limited
        response_a = test_client.get(
            "/api/data",
            headers={"Authorization": "Bearer user_A"},
        )
        assert response_a.status_code == 429, "User A should be rate limited"

        # User B should still be allowed
        response_b = test_client.get(
            "/api/data",
            headers={"Authorization": "Bearer user_B"},
        )
        assert response_b.status_code == 200, "User B should not be affected by User A"
        assert response_b.json()["user"] == "user_B"


def test_unauthenticated_uses_ip(test_client):
    """Unauthenticated requests should use IP-based rate limiting."""
    with patch("time.time", return_value=1000000.0):
        for i in range(3):
            response = test_client.get("/api/data")
            assert response.status_code == 200, f"Request {i+1} should be allowed"
            data = response.json()
            assert data["user"] is None, "User should be None for unauthenticated"

        # Next unauthenticated request should be denied
        response = test_client.get("/api/data")
        assert response.status_code == 429, "Should be rate limited by IP"


def test_authenticated_and_unauthenticated_independent(test_client):
    """Authenticated user limits should be independent from IP-based limits."""
    with patch("time.time", return_value=1000000.0):
        # Use up IP-based limit (unauthenticated)
        for _ in range(3):
            test_client.get("/api/data")

        # IP is now rate limited
        response_anon = test_client.get("/api/data")
        assert response_anon.status_code == 429, "Anonymous should be rate limited"

        # But authenticated user should still be allowed (different key)
        response_auth = test_client.get(
            "/api/data",
            headers={"Authorization": "Bearer user_99"},
        )
        assert response_auth.status_code == 200, "Authenticated user should not be affected by IP limit"


def test_response_includes_remaining(test_client):
    """Successful response should include remaining request count."""
    with patch("time.time", return_value=1000000.0):
        response = test_client.get(
            "/api/data",
            headers={"Authorization": "Bearer user_1"},
        )
        data = response.json()
        assert "remaining" in data, "Response should include 'remaining' count"
        assert isinstance(data["remaining"], int), "remaining should be an integer"
