"""
Exercise 1: Concurrent Execution with gather() and TaskGroup

Learn to run multiple async operations concurrently and collect results.
Practice using asyncio.gather(), asyncio.as_completed(), and asyncio.TaskGroup().

Run: pytest 012-advanced-async-python/exercises/01_concurrent_gather.py -v
"""

import asyncio
import time
import pytest

# ============= HELPER FUNCTIONS (PROVIDED) =============

async def fetch_data(id: int, delay: float = 0.1) -> dict:
    """Simulate fetching data from an API."""
    await asyncio.sleep(delay)
    return {"id": id, "data": f"Data for ID {id}"}

async def compute(value: int, delay: float = 0.1) -> int:
    """Simulate computation."""
    await asyncio.sleep(delay)
    return value * 2

# ============= TODO: Exercise 1.1 =============
# Fetch multiple items concurrently using gather()
# - Use asyncio.gather() to fetch IDs 1-5 concurrently
# - Each fetch takes 0.1s, so total should be ~0.1s (not 0.5s)
# - Return list of results from gather

async def fetch_all_concurrent(ids: list[int]) -> list[dict]:
    """Fetch all IDs concurrently using gather()."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.2 =============
# Fetch and compute concurrently
# - Use asyncio.gather() to run both operations at the same time:
#   1. fetch_data(10)
#   2. compute(42)
# - Total time should be ~0.1s (not 0.2s)
# - Return tuple (fetch_result, compute_result)

async def fetch_and_compute() -> tuple[dict, int]:
    """Run fetch and compute concurrently."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.3 =============
# Process results as they complete using as_completed()
# - Create coroutines for fetching IDs [1, 2, 3] with delays [0.3, 0.1, 0.2]
# - Use asyncio.as_completed() to process results as they arrive
# - Collect results in order of completion (should be: 2, 3, 1)
# - Return list of IDs in completion order

async def fetch_as_completed() -> list[int]:
    """Process fetch results as they complete."""
    # TODO: Implement
    # Hint: Create coroutines like:
    # coros = [
    #     fetch_data(1, 0.3),
    #     fetch_data(2, 0.1),
    #     fetch_data(3, 0.2)
    # ]
    pass


# ============= TODO: Exercise 1.4 =============
# Use TaskGroup for structured concurrency (Python 3.11+)
# - Create async with asyncio.TaskGroup() as tg:
# - Use tg.create_task() to create 3 tasks:
#   - fetch_data(1)
#   - fetch_data(2)
#   - fetch_data(3)
# - After exiting context, collect results from tasks
# - Return list of results

async def fetch_with_task_group() -> list[dict]:
    """Use TaskGroup to run tasks concurrently."""
    # TODO: Implement
    # Note: Requires Python 3.11+
    # If you're on Python < 3.11, return empty list to skip
    pass


# ============= TODO: Exercise 1.5 =============
# Measure concurrent vs sequential timing
# - Sequential: await each of 5 fetches one by one (total ~0.5s)
# - Concurrent: use gather() to run all 5 at once (total ~0.1s)
# - Return dict with "sequential_time" and "concurrent_time" in seconds
# - concurrent_time should be much less than sequential_time

async def measure_performance() -> dict[str, float]:
    """Compare sequential vs concurrent execution time."""
    # TODO: Implement
    # Hint: use time.time() to measure elapsed time
    pass


# ============= TESTS =============
# Run with: pytest 012-advanced-async-python/exercises/01_concurrent_gather.py -v

@pytest.mark.asyncio
async def test_fetch_all_concurrent():
    """Test concurrent fetching with gather()."""
    start = time.time()
    results = await fetch_all_concurrent([1, 2, 3, 4, 5])
    elapsed = time.time() - start

    assert len(results) == 5, "Should fetch 5 items"
    assert all(isinstance(r, dict) for r in results), "All results should be dicts"
    assert results[0]["id"] == 1, "First result should have ID 1"
    assert elapsed < 0.2, f"Should be concurrent (~0.1s), was {elapsed:.2f}s"

@pytest.mark.asyncio
async def test_fetch_and_compute():
    """Test running fetch and compute concurrently."""
    start = time.time()
    fetch_result, compute_result = await fetch_and_compute()
    elapsed = time.time() - start

    assert fetch_result["id"] == 10, "Fetch result should have ID 10"
    assert compute_result == 84, "Compute result should be 42 * 2 = 84"
    assert elapsed < 0.2, f"Should be concurrent (~0.1s), was {elapsed:.2f}s"

@pytest.mark.asyncio
async def test_fetch_as_completed():
    """Test processing results as they complete."""
    ids = await fetch_as_completed()

    assert len(ids) == 3, "Should process 3 items"
    assert ids == [2, 3, 1], f"Order should be [2, 3, 1] based on delays, got {ids}"

@pytest.mark.asyncio
async def test_fetch_with_task_group():
    """Test TaskGroup usage."""
    import sys
    if sys.version_info < (3, 11):
        pytest.skip("TaskGroup requires Python 3.11+")

    results = await fetch_with_task_group()

    assert len(results) == 3, "Should fetch 3 items"
    assert all(isinstance(r, dict) for r in results), "All results should be dicts"

@pytest.mark.asyncio
async def test_measure_performance():
    """Test sequential vs concurrent timing."""
    timings = await measure_performance()

    assert "sequential_time" in timings, "Should have sequential_time"
    assert "concurrent_time" in timings, "Should have concurrent_time"

    seq_time = timings["sequential_time"]
    con_time = timings["concurrent_time"]

    assert seq_time > 0.4, f"Sequential should take ~0.5s, got {seq_time:.2f}s"
    assert con_time < 0.2, f"Concurrent should take ~0.1s, got {con_time:.2f}s"
    assert con_time < seq_time / 2, "Concurrent should be much faster than sequential"
