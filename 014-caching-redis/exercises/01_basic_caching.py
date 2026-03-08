"""
Exercise 1: Basic Caching with Redis

Learn the cache-aside pattern using fakeredis (no Docker required).
Practice cache reads, writes, and tracking hit/miss statistics.

Run: pytest 014-caching-redis/exercises/01_basic_caching.py -v

Requirements: pip install fakeredis
"""

import json
import time
import fakeredis
import pytest

# ============= SIMULATED SLOW DATABASE (PROVIDED) =============

# Simulates a database with artificial delay
_database = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
}

# Track database calls to verify caching works
db_call_count = 0


def reset_db_calls():
    """Reset the database call counter."""
    global db_call_count
    db_call_count = 0


def fetch_from_database(user_id: int) -> dict | None:
    """
    Simulate a slow database query.
    Returns user dict or None if not found.
    """
    global db_call_count
    db_call_count += 1
    time.sleep(0.01)  # Simulate 10ms database latency
    return _database.get(user_id)


# ============= TODO: Exercise 1.1 =============
# Implement the cache-aside pattern.
# - Check the cache (Redis) first using the key pattern "user:{user_id}"
# - If cache hit: return the cached data (parse JSON)
# - If cache miss: fetch from database using fetch_from_database()
# - Store the result in cache as JSON with a 3600-second TTL
# - Return the user dict or None if not found
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   user_id: int

def get_user_cached(cache, user_id: int) -> dict | None:
    """Get user with cache-aside pattern."""
    # TODO: Implement cache-aside
    # 1. Build cache key: f"user:{user_id}"
    # 2. Check cache with cache.get(key)
    # 3. If cached: return json.loads(cached)
    # 4. If not cached: call fetch_from_database(user_id)
    # 5. If found: store in cache with cache.setex(key, 3600, json.dumps(data))
    # 6. Return the user dict (or None)
    pass


# ============= TODO: Exercise 1.2 =============
# Implement a cache write function.
# - Store the user data in Redis with consistent key pattern "user:{user_id}"
# - Serialize as JSON
# - Set TTL to the provided value (default 3600)
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   user_id: int
#   user_data: dict
#   ttl: int (default 3600)

def cache_user(cache, user_id: int, user_data: dict, ttl: int = 3600) -> None:
    """Store user data in cache with TTL."""
    # TODO: Implement
    # 1. Build cache key: f"user:{user_id}"
    # 2. Serialize user_data to JSON
    # 3. Store with cache.setex(key, ttl, json_string)
    pass


# ============= TODO: Exercise 1.3 =============
# Implement a function that returns cache statistics.
# Track hits and misses using a simple class.
#
# The CacheStats class should:
# - Initialize with hits=0, misses=0
# - record_hit() increments hits
# - record_miss() increments misses
# - hit_rate() returns float (hits / total), or 0.0 if no requests
# - to_dict() returns {"hits": N, "misses": N, "total": N, "hit_rate": float}

class CacheStats:
    """Track cache hit/miss statistics."""

    def __init__(self):
        # TODO: Initialize hits and misses counters
        pass

    def record_hit(self):
        """Record a cache hit."""
        # TODO: Implement
        pass

    def record_miss(self):
        """Record a cache miss."""
        # TODO: Implement
        pass

    def hit_rate(self) -> float:
        """Calculate hit rate as a percentage (0.0 to 1.0)."""
        # TODO: Implement
        # Return hits / (hits + misses), or 0.0 if no requests
        pass

    def to_dict(self) -> dict:
        """Return stats as a dictionary."""
        # TODO: Implement
        # Return {"hits": N, "misses": N, "total": N, "hit_rate": float}
        pass


# ============= TODO: Exercise 1.4 =============
# Combine cache-aside with statistics tracking.
# - Use get_user_cached logic but also track hits and misses
# - Return the user dict or None
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   user_id: int
#   stats: CacheStats instance

def get_user_with_stats(cache, user_id: int, stats: CacheStats) -> dict | None:
    """Get user with cache-aside pattern and track stats."""
    # TODO: Implement
    # 1. Check cache for "user:{user_id}"
    # 2. If hit: stats.record_hit(), return cached data
    # 3. If miss: stats.record_miss(), fetch from DB, cache result, return
    pass


# ============= TESTS =============
# Run with: pytest 014-caching-redis/exercises/01_basic_caching.py -v


@pytest.fixture
def cache():
    """Create a fresh fakeredis instance for each test."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def reset_state():
    """Reset database call counter before each test."""
    reset_db_calls()
    yield


def test_cache_aside_miss_then_hit(cache):
    """First call should miss cache, second should hit."""
    # First call: cache miss, should query database
    user = get_user_cached(cache, 1)
    assert user is not None, "Should return user data"
    assert user["name"] == "Alice", "Should return correct user"
    assert db_call_count == 1, "Should have queried database once"

    # Second call: cache hit, should NOT query database
    user2 = get_user_cached(cache, 1)
    assert user2 is not None, "Should return cached user data"
    assert user2["name"] == "Alice", "Should return same user"
    assert db_call_count == 1, "Should NOT query database again (cache hit)"


def test_cache_aside_nonexistent_user(cache):
    """Cache miss for non-existent user should return None."""
    user = get_user_cached(cache, 999)
    assert user is None, "Should return None for non-existent user"
    assert db_call_count == 1, "Should have queried database"


def test_cache_aside_stores_with_ttl(cache):
    """Cached data should have a TTL set."""
    get_user_cached(cache, 1)
    ttl = cache.ttl("user:1")
    assert ttl > 0, "Cached key should have a TTL"
    assert ttl <= 3600, "TTL should be at most 3600 seconds"


def test_cache_user_function(cache):
    """cache_user should store data retrievable by key."""
    user_data = {"id": 10, "name": "Test", "email": "test@example.com"}
    cache_user(cache, 10, user_data, ttl=1800)

    cached = cache.get("user:10")
    assert cached is not None, "Should store data in cache"
    parsed = json.loads(cached)
    assert parsed["name"] == "Test", "Should store correct data"

    ttl = cache.ttl("user:10")
    assert 0 < ttl <= 1800, "Should set correct TTL"


def test_cache_stats_tracking():
    """CacheStats should correctly track hits and misses."""
    stats = CacheStats()
    stats.record_hit()
    stats.record_hit()
    stats.record_miss()

    result = stats.to_dict()
    assert result["hits"] == 2, "Should have 2 hits"
    assert result["misses"] == 1, "Should have 1 miss"
    assert result["total"] == 3, "Should have 3 total"
    assert abs(result["hit_rate"] - 2 / 3) < 0.01, "Hit rate should be ~0.67"


def test_cache_stats_empty():
    """CacheStats with no requests should return 0.0 hit rate."""
    stats = CacheStats()
    assert stats.hit_rate() == 0.0, "Empty stats should have 0.0 hit rate"


def test_get_user_with_stats(cache):
    """get_user_with_stats should track hits and misses correctly."""
    stats = CacheStats()

    # First call: miss
    user = get_user_with_stats(cache, 1, stats)
    assert user is not None, "Should return user"
    assert stats.to_dict()["misses"] == 1, "Should record 1 miss"

    # Second call: hit
    user = get_user_with_stats(cache, 1, stats)
    assert user is not None, "Should return cached user"
    assert stats.to_dict()["hits"] == 1, "Should record 1 hit"

    # Third call different user: miss
    user = get_user_with_stats(cache, 2, stats)
    assert user is not None, "Should return user 2"
    assert stats.to_dict()["misses"] == 2, "Should record 2 misses total"
    assert stats.to_dict()["total"] == 3, "Should have 3 total requests"
