"""
Exercise 3: Error Handling in Async Code

Learn to handle errors in async operations: gather with return_exceptions,
timeout handling with wait_for(), and exception groups with TaskGroup.

Run: pytest 012-advanced-async-python/exercises/03_error_handling.py -v
"""

import asyncio
import time
import pytest

# ============= HELPER FUNCTIONS (PROVIDED) =============

async def task_ok(name: str, delay: float = 0.1) -> str:
    """Task that succeeds."""
    await asyncio.sleep(delay)
    return f"{name} OK"

async def task_error(name: str, error_msg: str, delay: float = 0.1):
    """Task that fails."""
    await asyncio.sleep(delay)
    raise ValueError(error_msg)

async def slow_task(delay: float = 5.0) -> str:
    """Task that takes a long time."""
    await asyncio.sleep(delay)
    return "Slow task done"

# ============= TODO: Exercise 3.1 =============
# Handle errors with gather and return_exceptions
# - Use asyncio.gather() with return_exceptions=True
# - Run 4 tasks: task_ok("A"), task_error("B", "B failed"), task_ok("C"), task_error("D", "D failed")
# - Separate successes from failures
# - Return dict with:
#   - "successes": list of successful results (strings)
#   - "failures": list of error messages (strings from exceptions)

async def gather_with_errors() -> dict:
    """Run tasks and separate successes from failures."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.2 =============
# Handle timeout with wait_for()
# - Use asyncio.wait_for(slow_task(5.0), timeout=1.0)
# - Catch asyncio.TimeoutError
# - Return "timeout" if timeout occurs
# - Return result if task completes in time

async def task_with_timeout() -> str:
    """Run task with timeout."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.3 =============
# Run multiple tasks with individual timeouts
# - Create 3 tasks with different delays: 0.5s, 2.0s, 0.3s
# - Wrap each in wait_for() with 1.0s timeout
# - Use gather() with return_exceptions=True
# - Count how many succeeded vs timed out
# - Return dict with:
#   - "completed": count of completed tasks
#   - "timed_out": count of timed out tasks

async def multiple_with_timeouts() -> dict:
    """Run multiple tasks with individual timeouts."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.4 =============
# Retry failed task with exponential backoff
# - Try to run task_error("Retry", "Transient failure") up to 3 times
# - Wait between retries: 0.1s, 0.2s, 0.4s (exponential backoff)
# - Return dict with:
#   - "success": False (since task always fails)
#   - "attempts": 3 (number of attempts made)
#   - Note: Don't actually fix the error, just demonstrate retry logic

async def retry_with_backoff() -> dict:
    """Retry failed task with exponential backoff."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.5 =============
# Use TaskGroup with exception handling (Python 3.11+)
# - Create async with asyncio.TaskGroup() as tg:
# - Create 4 tasks: 2 successes and 2 failures
# - Catch exception group with except* ValueError as eg:
# - Return dict with:
#   - "error_count": number of exceptions in the group
#   - "error_messages": list of error messages
# - If Python < 3.11, return {"skipped": True}

async def task_group_with_errors() -> dict:
    """Use TaskGroup and handle exception groups."""
    # TODO: Implement
    # Note: Requires Python 3.11+
    pass


# ============= TODO: Exercise 3.6 =============
# Fallback pattern: try task, return fallback on error
# - Try to run task_error("Main", "Main task failed")
# - If it fails, return fallback value: "fallback_value"
# - Should return "fallback_value" since task always fails

async def task_with_fallback() -> str:
    """Run task with fallback on error."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 012-advanced-async-python/exercises/03_error_handling.py -v

@pytest.mark.asyncio
async def test_gather_with_errors():
    """Test gathering results with error handling."""
    result = await gather_with_errors()

    assert "successes" in result, "Should have successes key"
    assert "failures" in result, "Should have failures key"

    successes = result["successes"]
    failures = result["failures"]

    assert len(successes) == 2, f"Should have 2 successes, got {len(successes)}"
    assert len(failures) == 2, f"Should have 2 failures, got {len(failures)}"
    assert "A OK" in successes, "Should include task A"
    assert "C OK" in successes, "Should include task C"
    assert any("B failed" in f for f in failures), "Should include B error"
    assert any("D failed" in f for f in failures), "Should include D error"

@pytest.mark.asyncio
async def test_task_with_timeout():
    """Test timeout handling."""
    start = time.time()
    result = await task_with_timeout()
    elapsed = time.time() - start

    assert result == "timeout", f"Should return 'timeout', got '{result}'"
    assert elapsed < 2.0, f"Should timeout quickly (~1s), took {elapsed:.2f}s"

@pytest.mark.asyncio
async def test_multiple_with_timeouts():
    """Test multiple tasks with timeouts."""
    result = await multiple_with_timeouts()

    assert "completed" in result, "Should have completed key"
    assert "timed_out" in result, "Should have timed_out key"

    # Tasks with delays: 0.5s (OK), 2.0s (timeout), 0.3s (OK)
    # Timeout: 1.0s
    assert result["completed"] == 2, f"Should have 2 completed, got {result['completed']}"
    assert result["timed_out"] == 1, f"Should have 1 timed out, got {result['timed_out']}"

@pytest.mark.asyncio
async def test_retry_with_backoff():
    """Test retry with exponential backoff."""
    start = time.time()
    result = await retry_with_backoff()
    elapsed = time.time() - start

    assert "success" in result, "Should have success key"
    assert "attempts" in result, "Should have attempts key"

    assert result["success"] is False, "Should not succeed"
    assert result["attempts"] == 3, f"Should have 3 attempts, got {result['attempts']}"

    # Should take at least 0.1 + 0.2 + 0.4 = 0.7s
    assert elapsed >= 0.7, f"Should take at least 0.7s for backoff, took {elapsed:.2f}s"

@pytest.mark.asyncio
async def test_task_group_with_errors():
    """Test TaskGroup exception handling."""
    import sys
    if sys.version_info < (3, 11):
        result = await task_group_with_errors()
        assert result.get("skipped") is True, "Should skip on Python < 3.11"
        pytest.skip("TaskGroup requires Python 3.11+")
        return

    result = await task_group_with_errors()

    assert "error_count" in result, "Should have error_count key"
    assert "error_messages" in result, "Should have error_messages key"

    assert result["error_count"] == 2, f"Should catch 2 errors, got {result['error_count']}"
    assert len(result["error_messages"]) == 2, "Should have 2 error messages"

@pytest.mark.asyncio
async def test_task_with_fallback():
    """Test fallback pattern."""
    result = await task_with_fallback()

    assert result == "fallback_value", f"Should return fallback, got '{result}'"
