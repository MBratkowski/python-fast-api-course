"""
Exercise 3: Cache Invalidation

Practice invalidating cached data on create, update, and delete operations.
Learn tag-based invalidation for grouping related cache keys.

Run: pytest 014-caching-redis/exercises/03_cache_invalidation.py -v

Requirements: pip install fakeredis
"""

import json
import fakeredis
import pytest

# ============= PRE-BUILT CRUD SERVICE (PROVIDED) =============

# Simulated database
_products_db: dict[int, dict] = {}
_next_id = 1


def reset_db():
    """Reset the simulated database."""
    global _products_db, _next_id
    _products_db = {
        1: {"id": 1, "name": "Widget", "price": 9.99, "category": "tools"},
        2: {"id": 2, "name": "Gadget", "price": 19.99, "category": "electronics"},
        3: {"id": 3, "name": "Gizmo", "price": 14.99, "category": "electronics"},
    }
    _next_id = 4


def db_get_product(product_id: int) -> dict | None:
    """Fetch product from simulated database."""
    return _products_db.get(product_id)


def db_create_product(data: dict) -> dict:
    """Create product in simulated database."""
    global _next_id
    product = {"id": _next_id, **data}
    _products_db[_next_id] = product
    _next_id += 1
    return product


def db_update_product(product_id: int, data: dict) -> dict | None:
    """Update product in simulated database."""
    if product_id not in _products_db:
        return None
    _products_db[product_id].update(data)
    return _products_db[product_id]


def db_delete_product(product_id: int) -> bool:
    """Delete product from simulated database."""
    if product_id in _products_db:
        del _products_db[product_id]
        return True
    return False


# ============= CACHING LAYER (PROVIDED) =============

def get_product_cached(cache, product_id: int) -> dict | None:
    """Get product with cache-aside pattern (provided)."""
    cache_key = f"product:{product_id}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    product = db_get_product(product_id)
    if product:
        cache.setex(cache_key, 1800, json.dumps(product))
    return product


# ============= TODO: Exercise 3.1 =============
# Implement cache invalidation on UPDATE.
# - Update the product in the database using db_update_product()
# - Invalidate (delete) the cached product entry
# - Return the updated product dict or None if not found
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   product_id: int
#   update_data: dict

def update_product(cache, product_id: int, update_data: dict) -> dict | None:
    """Update product and invalidate cache."""
    # TODO: Implement
    # 1. Update in database: db_update_product(product_id, update_data)
    # 2. Delete cache key: cache.delete(f"product:{product_id}")
    # 3. Return the updated product
    pass


# ============= TODO: Exercise 3.2 =============
# Implement cache invalidation on DELETE.
# - Delete the product from the database using db_delete_product()
# - Invalidate (delete) the cached product entry
# - Return True if deleted, False if not found
#
# Parameters:
#   cache: fakeredis.FakeRedis instance
#   product_id: int

def delete_product(cache, product_id: int) -> bool:
    """Delete product and invalidate cache."""
    # TODO: Implement
    # 1. Delete from database: db_delete_product(product_id)
    # 2. Delete cache key: cache.delete(f"product:{product_id}")
    # 3. Return True/False based on db_delete_product result
    pass


# ============= TODO: Exercise 3.3 =============
# Implement tag-based cache invalidation.
# When caching a product, also register it under category and "all_products" tags.
# When invalidating a tag, delete all keys associated with that tag.
#
# You need to implement two functions:
#
# 1. cache_product_with_tags(cache, product):
#    - Cache the product at "product:{id}" with 1800s TTL
#    - Add the cache key to a Redis set "tag:category:{category}"
#    - Add the cache key to a Redis set "tag:all_products"
#
# 2. invalidate_by_tag(cache, tag):
#    - Get all keys from the Redis set "tag:{tag}"
#    - Delete all those keys from cache
#    - Delete the tag set itself
#    - Return the number of keys invalidated

def cache_product_with_tags(cache, product: dict) -> None:
    """Cache a product and register it under category and all_products tags."""
    # TODO: Implement
    # 1. Build cache key: f"product:{product['id']}"
    # 2. Store product: cache.setex(key, 1800, json.dumps(product))
    # 3. Register under category tag: cache.sadd(f"tag:category:{product['category']}", key)
    # 4. Register under all_products tag: cache.sadd("tag:all_products", key)
    pass


def invalidate_by_tag(cache, tag: str) -> int:
    """Invalidate all cache keys associated with a tag."""
    # TODO: Implement
    # 1. Get all keys from the tag set: cache.smembers(f"tag:{tag}")
    # 2. If keys exist: delete them all with cache.delete(*keys)
    # 3. Delete the tag set itself: cache.delete(f"tag:{tag}")
    # 4. Return the number of keys that were invalidated
    pass


# ============= TESTS =============
# Run with: pytest 014-caching-redis/exercises/03_cache_invalidation.py -v


@pytest.fixture
def cache():
    """Create a fresh fakeredis instance for each test."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def reset_state():
    """Reset database before each test."""
    reset_db()
    yield


def test_update_invalidates_cache(cache):
    """After update, cache should NOT return stale data."""
    # Populate cache
    product = get_product_cached(cache, 1)
    assert product["name"] == "Widget"

    # Verify it's cached
    assert cache.get("product:1") is not None, "Should be cached"

    # Update the product
    updated = update_product(cache, 1, {"name": "Super Widget"})
    assert updated is not None
    assert updated["name"] == "Super Widget"

    # Cache should be invalidated
    assert cache.get("product:1") is None, "Cache should be cleared after update"

    # Next read should get fresh data from DB
    fresh = get_product_cached(cache, 1)
    assert fresh["name"] == "Super Widget", "Should get updated data"


def test_update_nonexistent_product(cache):
    """Updating a non-existent product should return None."""
    result = update_product(cache, 999, {"name": "Phantom"})
    assert result is None, "Should return None for non-existent product"


def test_delete_invalidates_cache(cache):
    """After delete, cache should NOT return deleted data."""
    # Populate cache
    product = get_product_cached(cache, 2)
    assert product["name"] == "Gadget"

    # Verify it's cached
    assert cache.get("product:2") is not None, "Should be cached"

    # Delete the product
    deleted = delete_product(cache, 2)
    assert deleted is True, "Should return True for successful delete"

    # Cache should be invalidated
    assert cache.get("product:2") is None, "Cache should be cleared after delete"

    # Next read should return None (product doesn't exist)
    result = get_product_cached(cache, 2)
    assert result is None, "Should return None for deleted product"


def test_delete_nonexistent_product(cache):
    """Deleting a non-existent product should return False."""
    result = delete_product(cache, 999)
    assert result is False, "Should return False for non-existent product"


def test_cache_product_with_tags(cache):
    """Products should be cached and registered under tags."""
    product = {"id": 1, "name": "Widget", "price": 9.99, "category": "tools"}
    cache_product_with_tags(cache, product)

    # Verify product is cached
    cached = cache.get("product:1")
    assert cached is not None, "Product should be cached"
    assert json.loads(cached)["name"] == "Widget"

    # Verify registered under category tag
    tools_keys = cache.smembers("tag:category:tools")
    assert "product:1" in tools_keys, "Should be registered under category tag"

    # Verify registered under all_products tag
    all_keys = cache.smembers("tag:all_products")
    assert "product:1" in all_keys, "Should be registered under all_products tag"


def test_invalidate_by_category_tag(cache):
    """Invalidating a category tag should clear all products in that category."""
    # Cache products in different categories
    cache_product_with_tags(cache, {"id": 2, "name": "Gadget", "price": 19.99, "category": "electronics"})
    cache_product_with_tags(cache, {"id": 3, "name": "Gizmo", "price": 14.99, "category": "electronics"})
    cache_product_with_tags(cache, {"id": 1, "name": "Widget", "price": 9.99, "category": "tools"})

    # Verify all are cached
    assert cache.get("product:2") is not None
    assert cache.get("product:3") is not None
    assert cache.get("product:1") is not None

    # Invalidate electronics category
    count = invalidate_by_tag(cache, "category:electronics")
    assert count == 2, f"Should invalidate 2 electronics products, got {count}"

    # Electronics products should be gone
    assert cache.get("product:2") is None, "Gadget should be invalidated"
    assert cache.get("product:3") is None, "Gizmo should be invalidated"

    # Tools product should still be cached
    assert cache.get("product:1") is not None, "Widget (tools) should still be cached"


def test_invalidate_all_products_tag(cache):
    """Invalidating all_products tag should clear everything."""
    cache_product_with_tags(cache, {"id": 1, "name": "Widget", "price": 9.99, "category": "tools"})
    cache_product_with_tags(cache, {"id": 2, "name": "Gadget", "price": 19.99, "category": "electronics"})

    count = invalidate_by_tag(cache, "all_products")
    assert count == 2, f"Should invalidate 2 products, got {count}"

    assert cache.get("product:1") is None, "All products should be invalidated"
    assert cache.get("product:2") is None, "All products should be invalidated"


def test_invalidate_empty_tag(cache):
    """Invalidating a tag with no keys should return 0."""
    count = invalidate_by_tag(cache, "nonexistent_tag")
    assert count == 0, "Should return 0 for empty tag"
