"""
Exercise 3: Retry Logic Patterns

Learn to implement retry patterns for Celery tasks: autoretry, manual retry,
and error callbacks. Uses a mock external service that fails N times before succeeding.

Run: pytest 013-background-tasks/exercises/03_retry_logic.py -v

Note: Uses task_always_eager=True so tasks run synchronously without a broker.
"""

from celery import Celery
from celery.exceptions import MaxRetriesExceededError
import pytest

# ============= CELERY APP SETUP (PROVIDED) =============

celery_app = Celery("retry_worker")
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=False,   # Don't propagate -- we test failure handling
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)


# ============= MOCK EXTERNAL SERVICE (PROVIDED) =============

class MockExternalService:
    """Simulates an external service that fails N times before succeeding.

    Usage:
        service = MockExternalService(fail_times=2)
        service.call()  # Raises ConnectionError (attempt 1)
        service.call()  # Raises ConnectionError (attempt 2)
        service.call()  # Returns {"status": "success"} (attempt 3)
    """

    def __init__(self, fail_times: int = 2):
        self.fail_times = fail_times
        self.attempt_count = 0

    def call(self) -> dict:
        self.attempt_count += 1
        if self.attempt_count <= self.fail_times:
            raise ConnectionError(
                f"Service unavailable (attempt {self.attempt_count})"
            )
        return {"status": "success", "attempts": self.attempt_count}

    def reset(self):
        self.attempt_count = 0


# Global services for tasks to use
# (Celery tasks can't easily receive complex objects as args)
reliable_service = MockExternalService(fail_times=2)    # Fails 2 times, succeeds on 3rd
flaky_service = MockExternalService(fail_times=5)       # Fails 5 times
always_fails = MockExternalService(fail_times=999)      # Always fails

# Track retry attempts for verification
retry_tracker: list[str] = []


def clear_tracker():
    retry_tracker.clear()


# ============= TODO: Exercise 3.1 =============
# Create a task with autoretry_for configuration.
# - Task name: fetch_with_autoretry
# - Use autoretry_for to retry on ConnectionError
# - Set max_retries to 5
# - Set retry_backoff to False (for faster tests)
# - Set default_retry_delay to 0 (for faster tests)
# - Call reliable_service.call() and return the result
# - Before calling, append f"attempt:{self.request.retries}" to retry_tracker
#
# Hint: Use bind=True to access self.request.retries

@celery_app.task(
    bind=True,
    # TODO: Add autoretry_for, max_retries, retry_backoff, default_retry_delay
)
def fetch_with_autoretry(self):
    """Fetch data with automatic retry on connection errors."""
    # TODO: Implement
    # - Track attempt in retry_tracker
    # - Call reliable_service.call()
    # - Return the result
    pass


# ============= TODO: Exercise 3.2 =============
# Create a task with manual retry and custom countdown.
# - Task name: fetch_with_manual_retry
# - Use bind=True for self access
# - Set max_retries to 3
# - Try calling reliable_service.call()
# - On ConnectionError: append "retry:{retry_count}" to retry_tracker,
#   then raise self.retry(exc=exc, countdown=0)
# - On success: return the result

@celery_app.task(bind=True, max_retries=3)
def fetch_with_manual_retry(self):
    """Fetch data with manual retry logic."""
    # TODO: Implement
    # - Try calling reliable_service.call()
    # - On ConnectionError, track and retry
    # - On success, return result
    pass


# ============= TODO: Exercise 3.3 =============
# Create a task with max_retries and an error callback.
# - Task name: fetch_with_error_handling
# - Use bind=True, max_retries=2
# - Try calling always_fails.call()
# - On ConnectionError: raise self.retry(exc=exc, countdown=0)
# - The task WILL exceed max_retries (service always fails)
#
# Also create an error handler function (not a task):
# - Function name: handle_task_failure
# - Parameters: task_id (str), exception_message (str)
# - Append f"failed:{task_id}:{exception_message}" to retry_tracker
#
# In fetch_with_error_handling, catch MaxRetriesExceededError
# and call handle_task_failure with the task ID and error message.

def handle_task_failure(task_id: str, exception_message: str):
    """Handle permanent task failure."""
    # TODO: Implement - append failure info to retry_tracker
    pass


@celery_app.task(bind=True, max_retries=2)
def fetch_with_error_handling(self):
    """Fetch data with error handling when retries exhausted."""
    # TODO: Implement
    # - Try calling always_fails.call()
    # - On ConnectionError: try self.retry(exc=exc, countdown=0)
    # - Catch MaxRetriesExceededError: call handle_task_failure
    #   and return {"status": "permanently_failed", "task_id": self.request.id}
    pass


# ============= TODO: Exercise 3.4 =============
# Create a task that retries differently based on the exception type.
# - Task name: smart_retry
# - Use bind=True, max_retries=5
# - Parameters: operation (str)
# - If operation == "timeout": raise TimeoutError("Timeout!")
#     -> retry with countdown=0 (quick retry for timeouts)
# - If operation == "rate_limit": raise RuntimeError("Rate limited!")
#     -> retry with countdown=0 (would be longer in production)
# - If operation == "success": return {"status": "ok"}
# - If operation == "invalid": raise ValueError("Invalid input!")
#     -> DON'T retry (bad input won't fix itself)
#     -> return {"status": "invalid", "error": "Invalid input!"}
# - Track each attempt in retry_tracker: f"smart:{operation}:{self.request.retries}"

@celery_app.task(bind=True, max_retries=5)
def smart_retry(self, operation: str):
    """Handle different error types with different retry strategies."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 013-background-tasks/exercises/03_retry_logic.py -v


@pytest.fixture(autouse=True)
def reset_services():
    """Reset all mock services and tracker before each test."""
    reliable_service.reset()
    flaky_service.reset()
    always_fails.reset()
    clear_tracker()
    yield


def test_autoretry_succeeds_after_failures():
    """Test that autoretry retries on ConnectionError and eventually succeeds."""
    result = fetch_with_autoretry.apply()

    assert result.successful(), f"Task should succeed after retries, state: {result.state}"
    data = result.result
    assert data["status"] == "success"
    assert data["attempts"] == 3  # Failed 2 times, succeeded on 3rd
    assert len(retry_tracker) >= 1, "Should have tracked at least one attempt"


def test_manual_retry_succeeds():
    """Test manual retry with self.retry()."""
    result = fetch_with_manual_retry.apply()

    assert result.successful(), "Task should succeed after manual retries"
    data = result.result
    assert data["status"] == "success"
    assert len(retry_tracker) >= 1, "Should have tracked retry attempts"


def test_error_handling_on_permanent_failure():
    """Test that error callback is called when retries are exhausted."""
    result = fetch_with_error_handling.apply()

    # Task should handle the failure gracefully
    data = result.result
    assert data is not None, "Task should return a result even on failure"
    assert data["status"] == "permanently_failed"

    # Error handler should have been called
    assert any("failed:" in entry for entry in retry_tracker), \
        f"Error handler should have been called, tracker: {retry_tracker}"


def test_smart_retry_success():
    """Test smart retry with successful operation."""
    result = smart_retry.apply(args=["success"])

    assert result.successful()
    assert result.result["status"] == "ok"


def test_smart_retry_invalid_no_retry():
    """Test that invalid operations don't retry."""
    result = smart_retry.apply(args=["invalid"])

    assert result.successful(), "Should handle invalid gracefully without retrying"
    data = result.result
    assert data["status"] == "invalid"
    # Should only have one attempt (no retries for validation errors)
    smart_entries = [e for e in retry_tracker if e.startswith("smart:invalid")]
    assert len(smart_entries) == 1, \
        f"Should have exactly 1 attempt (no retries), got {len(smart_entries)}"
