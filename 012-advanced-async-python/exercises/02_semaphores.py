"""
Exercise 2: Rate Limiting with Semaphores

Learn to control concurrency with asyncio.Semaphore to prevent overwhelming resources.
Practice limiting concurrent operations, tracking concurrency, and handling errors.

Run: pytest 012-advanced-async-python/exercises/02_semaphores.py -v
"""

import asyncio
import time
import pytest

# ============= HELPER FUNCTIONS (PROVIDED) =============

# Global counter to track concurrent execution
_concurrent_count = 0
_max_concurrent = 0

async def reset_counters():
    """Reset global counters."""
    global _concurrent_count, _max_concurrent
    _concurrent_count = 0
    _max_concurrent = 0

async def api_call(id: int, delay: float = 0.1) -> dict:
    """Simulate API call that tracks concurrency."""
    global _concurrent_count, _max_concurrent

    _concurrent_count += 1
    _max_concurrent = max(_max_concurrent, _concurrent_count)

    try:
        await asyncio.sleep(delay)
        return {"id": id, "data": f"Result {id}"}
    finally:
        _concurrent_count -= 1

# ============= TODO: Exercise 2.1 =============
# Limit concurrent API calls using a semaphore
# - Create asyncio.Semaphore(5) to limit to 5 concurrent calls
# - Use async with semaphore: inside api_call_limited()
# - Call api_call(id) inside the semaphore
# - Return the result from api_call

async def api_call_limited(id: int, semaphore: asyncio.Semaphore) -> dict:
    """Make API call with semaphore limit."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.2 =============
# Fetch all items with concurrency limit
# - Create a semaphore with limit of 10
# - Use asyncio.gather() to fetch IDs 1-50
# - Each fetch should use api_call_limited() with the semaphore
# - Return list of results
# - The max concurrent count should not exceed 10

async def fetch_with_limit(ids: list[int], limit: int = 10) -> list[dict]:
    """Fetch all items with concurrency limit."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.3 =============
# Batch processor with semaphore
# - Create semaphore with given limit
# - Process all items using gather() with api_call_limited()
# - Measure elapsed time
# - Return dict with:
#   - "results": list of results
#   - "max_concurrent": the max concurrent count reached
#   - "elapsed_time": total time in seconds

async def batch_process(ids: list[int], limit: int) -> dict:
    """Process batch with semaphore limit and track metrics."""
    # TODO: Implement
    # Reset counters first: await reset_counters()
    pass


# ============= TODO: Exercise 2.4 =============
# Semaphore with error handling
# - Create semaphore with limit
# - Some API calls will fail (id % 5 == 0 raises ValueError)
# - Use gather() with return_exceptions=True
# - Separate successes from failures
# - Return dict with:
#   - "successes": list of successful results
#   - "failures": list of exceptions

async def api_call_unreliable(id: int, semaphore: asyncio.Semaphore) -> dict:
    """API call that sometimes fails."""
    async with semaphore:
        if id % 5 == 0:
            raise ValueError(f"ID {id} failed")
        return await api_call(id)

async def fetch_with_errors(ids: list[int], limit: int = 10) -> dict:
    """Fetch with error handling."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 012-advanced-async-python/exercises/02_semaphores.py -v

@pytest.mark.asyncio
async def test_api_call_limited():
    """Test single API call with semaphore."""
    await reset_counters()
    semaphore = asyncio.Semaphore(5)

    result = await api_call_limited(1, semaphore)

    assert result["id"] == 1, "Should return correct result"
    assert _max_concurrent <= 5, "Should respect semaphore limit"

@pytest.mark.asyncio
async def test_fetch_with_limit():
    """Test fetching with concurrency limit."""
    await reset_counters()

    results = await fetch_with_limit(list(range(1, 51)), limit=10)

    assert len(results) == 50, "Should fetch 50 items"
    assert _max_concurrent <= 10, f"Max concurrent should be <= 10, was {_max_concurrent}"
    assert _max_concurrent >= 5, f"Max concurrent should be at least 5, was {_max_concurrent}"

@pytest.mark.asyncio
async def test_batch_process():
    """Test batch processing with metrics."""
    await reset_counters()

    result = await batch_process(list(range(1, 21)), limit=5)

    assert "results" in result, "Should have results key"
    assert "max_concurrent" in result, "Should have max_concurrent key"
    assert "elapsed_time" in result, "Should have elapsed_time key"

    assert len(result["results"]) == 20, "Should process 20 items"
    assert result["max_concurrent"] <= 5, f"Max concurrent should be <= 5, was {result['max_concurrent']}"
    assert result["elapsed_time"] > 0, "Should measure elapsed time"

@pytest.mark.asyncio
async def test_fetch_with_errors():
    """Test error handling with semaphore."""
    await reset_counters()

    result = await fetch_with_errors(list(range(1, 21)), limit=10)

    assert "successes" in result, "Should have successes key"
    assert "failures" in result, "Should have failures key"

    successes = result["successes"]
    failures = result["failures"]

    # IDs 5, 10, 15, 20 should fail
    assert len(successes) == 16, f"Should have 16 successes, got {len(successes)}"
    assert len(failures) == 4, f"Should have 4 failures, got {len(failures)}"
    assert all(isinstance(f, ValueError) for f in failures), "Failures should be ValueErrors"

@pytest.mark.asyncio
async def test_semaphore_releases_on_error():
    """Test that semaphore is released even when error occurs."""
    await reset_counters()
    semaphore = asyncio.Semaphore(3)

    # Make calls that will fail
    results = await asyncio.gather(
        api_call_unreliable(5, semaphore),
        api_call_unreliable(10, semaphore),
        api_call_unreliable(15, semaphore),
        return_exceptions=True
    )

    # All should fail
    assert all(isinstance(r, ValueError) for r in results), "All should fail"

    # Semaphore should be fully released (counter back to 0)
    # We can't directly check semaphore internals, but we can test it works
    result = await api_call_limited(1, semaphore)
    assert result["id"] == 1, "Semaphore should work after errors"
