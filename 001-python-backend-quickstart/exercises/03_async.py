"""
Exercise 3: Async Python Practice

Practice async/await patterns used in backend development.
Run: pytest 001-python-backend-quickstart/exercises/03_async.py -v
"""

import asyncio
from typing import Any


# Simulated async database/API calls (don't modify these)
async def _fetch_user_from_db(user_id: int) -> dict | None:
    await asyncio.sleep(0.1)  # Simulate DB latency
    users = {1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}}
    return users.get(user_id)


async def _fetch_posts_from_db(user_id: int) -> list[dict]:
    await asyncio.sleep(0.1)
    posts = {
        1: [{"id": 1, "title": "Hello"}, {"id": 2, "title": "World"}],
        2: [{"id": 3, "title": "Python"}],
    }
    return posts.get(user_id, [])


async def _fetch_followers_count(user_id: int) -> int:
    await asyncio.sleep(0.1)
    return user_id * 100


# Exercise 3.1: Basic Async Function
# Create an async function that fetches a user and returns their name
# Return None if user not found
async def get_user_name(user_id: int) -> str | None:
    """Fetch user and return their name."""
    # TODO: Use _fetch_user_from_db and return the name
    pass


# Exercise 3.2: Sequential Async Calls
# Fetch user, then fetch their posts, return both
async def get_user_with_posts(user_id: int) -> dict | None:
    """
    Fetch user and their posts.
    Return: {"user": {...}, "posts": [...]} or None if user not found
    """
    # TODO: Fetch user first, then posts
    pass


# Exercise 3.3: Concurrent Async Calls
# Fetch user, posts, and followers count CONCURRENTLY
# This should be faster than sequential!
async def get_user_profile(user_id: int) -> dict | None:
    """
    Fetch user profile with posts and followers count concurrently.
    Return: {"user": {...}, "posts": [...], "followers": int} or None
    """
    # TODO: Use asyncio.gather to fetch all data concurrently
    pass


# Exercise 3.4: Async with Error Handling
# Fetch user with a timeout - return None if it takes too long
async def get_user_with_timeout(user_id: int, timeout: float = 0.05) -> dict | None:
    """Fetch user with timeout, return None on timeout."""
    # TODO: Use asyncio.wait_for with timeout
    pass


# Exercise 3.5: Batch Async Operations
# Fetch multiple users concurrently
async def get_users_batch(user_ids: list[int]) -> list[dict]:
    """
    Fetch multiple users concurrently.
    Return list of users (skip None results).
    """
    # TODO: Fetch all users concurrently and filter out None
    pass


# ============= TESTS =============

import pytest


@pytest.mark.asyncio
async def test_get_user_name():
    assert await get_user_name(1) == "Alice"
    assert await get_user_name(2) == "Bob"
    assert await get_user_name(99) is None


@pytest.mark.asyncio
async def test_get_user_with_posts():
    result = await get_user_with_posts(1)
    assert result is not None
    assert result["user"]["name"] == "Alice"
    assert len(result["posts"]) == 2

    assert await get_user_with_posts(99) is None


@pytest.mark.asyncio
async def test_get_user_profile():
    import time

    start = time.time()
    result = await get_user_profile(1)
    elapsed = time.time() - start

    assert result is not None
    assert result["user"]["name"] == "Alice"
    assert len(result["posts"]) == 2
    assert result["followers"] == 100

    # Should be concurrent, so ~0.1s not ~0.3s
    assert elapsed < 0.2, "Should run concurrently!"


@pytest.mark.asyncio
async def test_get_user_with_timeout():
    # Normal fetch should work
    result = await get_user_with_timeout(1, timeout=1.0)
    assert result is not None

    # Very short timeout should return None
    result = await get_user_with_timeout(1, timeout=0.01)
    assert result is None


@pytest.mark.asyncio
async def test_get_users_batch():
    users = await get_users_batch([1, 2, 99])
    assert len(users) == 2  # user 99 doesn't exist
    names = [u["name"] for u in users]
    assert "Alice" in names
    assert "Bob" in names
