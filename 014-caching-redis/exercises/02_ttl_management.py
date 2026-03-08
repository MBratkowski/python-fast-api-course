"""
Exercise 2: TTL Management

Practice setting, checking, and refreshing TTL (Time-To-Live) values.
Learn sliding expiration and per-type TTL configuration.

Run: pytest 014-caching-redis/exercises/02_ttl_management.py -v

Requirements: pip install fakeredis
"""

import json
import fakeredis
import pytest

# ============= TTL CONFIGURATION (PROVIDED) =============

# Different data types deserve different TTL values
TTL_CONFIG = {
    "user": 3600,       # 1 hour -- profiles change infrequently
    "session": 1800,    # 30 minutes -- security consideration
    "product": 900,     # 15 minutes -- inventory changes often
    "config": 86400,    # 24 hours -- rarely changes
}


# ============= TODO: Exercise 2.1 =============
# Implement a cache setter that uses a configurable TTL.
# - Store the value as JSON string in Redis
# - Use the TTL from TTL_CONFIG based on data_type
# - If data_type is not in TTL_CONFIG, use default_ttl (3600)
# - Cache key format: "{data_type}:{entity_id}"
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   data_type: str (e.g., "user", "session", "product")
#   entity_id: int or str
#   data: dict
#   default_ttl: int (fallback TTL, default 3600)

def cache_set(
    cache,
    data_type: str,
    entity_id: int | str,
    data: dict,
    default_ttl: int = 3600
) -> None:
    """Store data in cache with type-specific TTL."""
    # TODO: Implement
    # 1. Look up TTL from TTL_CONFIG, fall back to default_ttl
    # 2. Build cache key: f"{data_type}:{entity_id}"
    # 3. Store with cache.setex(key, ttl, json.dumps(data))
    pass


# ============= TODO: Exercise 2.2 =============
# Implement a getter that refreshes TTL on access (sliding expiration).
# - Get the value from cache
# - If found: refresh the TTL using cache.expire() and return parsed data
# - If not found: return None
# - The TTL to refresh with comes from TTL_CONFIG (or default_ttl)
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   data_type: str
#   entity_id: int or str
#   default_ttl: int (fallback TTL, default 3600)

def cache_get_sliding(
    cache,
    data_type: str,
    entity_id: int | str,
    default_ttl: int = 3600
) -> dict | None:
    """Get data from cache and refresh TTL (sliding expiration)."""
    # TODO: Implement
    # 1. Build cache key: f"{data_type}:{entity_id}"
    # 2. Get value from cache
    # 3. If found: refresh TTL with cache.expire(key, ttl), return json.loads(value)
    # 4. If not found: return None
    pass


# ============= TODO: Exercise 2.3 =============
# Implement a function that returns the remaining TTL for a cached key.
# - Return the TTL in seconds (positive int)
# - Return 0 if the key doesn't exist or has no TTL
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   data_type: str
#   entity_id: int or str

def get_remaining_ttl(cache, data_type: str, entity_id: int | str) -> int:
    """Get remaining TTL for a cached key."""
    # TODO: Implement
    # 1. Build cache key: f"{data_type}:{entity_id}"
    # 2. Get TTL with cache.ttl(key)
    # 3. Return TTL if positive, otherwise 0
    #    (Redis returns -1 for no TTL, -2 for non-existent key)
    pass


# ============= TODO: Exercise 2.4 =============
# Implement a function that stores data with different TTLs based on data type.
# This combines Exercise 2.1 with bulk operations.
# - Accept a list of items, each with (data_type, entity_id, data)
# - Store each item using the correct TTL from TTL_CONFIG
# - Use a Redis pipeline for efficiency
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   items: list of tuples (data_type: str, entity_id: int|str, data: dict)

def cache_set_bulk(
    cache,
    items: list[tuple[str, int | str, dict]]
) -> int:
    """Store multiple items with type-specific TTLs using a pipeline."""
    # TODO: Implement
    # 1. Create a pipeline: pipe = cache.pipeline()
    # 2. For each (data_type, entity_id, data) in items:
    #    - Look up TTL from TTL_CONFIG (default 3600)
    #    - Build key: f"{data_type}:{entity_id}"
    #    - Add to pipeline: pipe.setex(key, ttl, json.dumps(data))
    # 3. Execute pipeline: pipe.execute()
    # 4. Return the number of items stored
    pass


# ============= TESTS =============
# Run with: pytest 014-caching-redis/exercises/02_ttl_management.py -v


@pytest.fixture
def cache():
    """Create a fresh fakeredis instance for each test."""
    return fakeredis.FakeRedis(decode_responses=True)


def test_cache_set_user_ttl(cache):
    """User data should be cached with 1-hour TTL."""
    data = {"id": 1, "name": "Alice"}
    cache_set(cache, "user", 1, data)

    cached = cache.get("user:1")
    assert cached is not None, "Should store data"
    assert json.loads(cached)["name"] == "Alice"

    ttl = cache.ttl("user:1")
    assert 3590 < ttl <= 3600, f"User TTL should be ~3600, got {ttl}"


def test_cache_set_session_ttl(cache):
    """Session data should be cached with 30-minute TTL."""
    data = {"user_id": 1, "token": "abc123"}
    cache_set(cache, "session", "abc123", data)

    ttl = cache.ttl("session:abc123")
    assert 1790 < ttl <= 1800, f"Session TTL should be ~1800, got {ttl}"


def test_cache_set_product_ttl(cache):
    """Product data should be cached with 15-minute TTL."""
    data = {"id": 100, "name": "Widget", "price": 9.99}
    cache_set(cache, "product", 100, data)

    ttl = cache.ttl("product:100")
    assert 890 < ttl <= 900, f"Product TTL should be ~900, got {ttl}"


def test_cache_set_unknown_type_uses_default(cache):
    """Unknown data types should use the default TTL."""
    data = {"id": 1, "content": "hello"}
    cache_set(cache, "comment", 1, data)

    ttl = cache.ttl("comment:1")
    assert 3590 < ttl <= 3600, f"Default TTL should be ~3600, got {ttl}"


def test_sliding_expiration_refreshes_ttl(cache):
    """Getting a key with sliding expiration should refresh its TTL."""
    # Store with short TTL to test refresh
    cache.setex("user:1", 100, json.dumps({"id": 1, "name": "Alice"}))

    # Access with sliding expiration (should reset to full user TTL: 3600)
    result = cache_get_sliding(cache, "user", 1)
    assert result is not None, "Should return cached data"
    assert result["name"] == "Alice"

    ttl = cache.ttl("user:1")
    assert ttl > 100, f"TTL should be refreshed above 100, got {ttl}"
    assert ttl <= 3600, f"TTL should be at most 3600, got {ttl}"


def test_sliding_expiration_returns_none_for_missing(cache):
    """Sliding get on missing key should return None."""
    result = cache_get_sliding(cache, "user", 999)
    assert result is None, "Should return None for missing key"


def test_get_remaining_ttl_existing_key(cache):
    """Should return positive TTL for existing key."""
    cache.setex("user:1", 3600, "data")
    ttl = get_remaining_ttl(cache, "user", 1)
    assert 0 < ttl <= 3600, f"TTL should be positive, got {ttl}"


def test_get_remaining_ttl_missing_key(cache):
    """Should return 0 for non-existent key."""
    ttl = get_remaining_ttl(cache, "user", 999)
    assert ttl == 0, f"Should return 0 for missing key, got {ttl}"


def test_cache_set_bulk(cache):
    """Bulk set should store all items with correct TTLs."""
    items = [
        ("user", 1, {"id": 1, "name": "Alice"}),
        ("product", 100, {"id": 100, "name": "Widget"}),
        ("session", "xyz", {"user_id": 1}),
        ("config", "app", {"debug": False}),
    ]

    count = cache_set_bulk(cache, items)
    assert count == 4, f"Should return 4 items stored, got {count}"

    # Verify each item is stored with correct TTL
    assert cache.get("user:1") is not None, "User should be cached"
    assert cache.get("product:100") is not None, "Product should be cached"
    assert cache.get("session:xyz") is not None, "Session should be cached"
    assert cache.get("config:app") is not None, "Config should be cached"

    # Verify TTLs match configuration
    assert cache.ttl("user:1") <= 3600, "User TTL should be ~3600"
    assert cache.ttl("product:100") <= 900, "Product TTL should be ~900"
    assert cache.ttl("session:xyz") <= 1800, "Session TTL should be ~1800"
    assert cache.ttl("config:app") <= 86400, "Config TTL should be ~86400"
