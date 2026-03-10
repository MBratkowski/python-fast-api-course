"""
Exercise 3: Benchmarking and Load Test Configuration

In this exercise, you'll build micro-benchmarking utilities and learn to
structure load test configurations -- skills needed for measuring and
validating API performance.

Your task:
1. Implement benchmark_function() that runs a function N times and returns
   timing statistics (min, max, avg, p95).
2. Implement compare_implementations() that benchmarks two functions and
   returns which one is faster.
3. Implement create_locust_config() that builds a load test configuration
   as a structured dict (no Locust import required).

Mobile analogy: This is like using XCTest measure blocks on iOS or the
Jetpack Benchmark library on Android to time function execution, plus
configuring a test plan for performance testing.

Run: pytest 020-performance-optimization/exercises/03_load_test.py -v
"""

import statistics
import time


# ============= TODO 1: Implement benchmark_function =============
# Run a function N times and collect timing statistics.
#
# Steps:
# 1. Create an empty list to store elapsed times
# 2. For each iteration:
#    a. Record start time with time.perf_counter()
#    b. Call the function
#    c. Record end time
#    d. Append elapsed time (end - start) to the list
# 3. Calculate and return min, max, avg, and p95
#
# Hints:
# - statistics.mean(times) gives the average
# - For p95: sort the times, take the value at index int(len(times) * 0.95)
# - All values should be in seconds (float)

def benchmark_function(func, iterations: int = 100) -> dict:
    """Run func() N times and return timing statistics.

    Args:
        func: A callable to benchmark (no arguments).
        iterations: Number of times to run the function.

    Returns:
        {
            "min": float,   # Fastest run (seconds)
            "max": float,   # Slowest run (seconds)
            "avg": float,   # Average time (seconds)
            "p95": float,   # 95th percentile (seconds)
        }
    """
    # TODO: Implement this function
    pass


# ============= TODO 2: Implement compare_implementations =============
# Benchmark two functions and return which is faster by average time.
#
# Steps:
# 1. Benchmark func_a using benchmark_function
# 2. Benchmark func_b using benchmark_function
# 3. Compare avg times and return "a" or "b"
#
# Hints:
# - Use your benchmark_function from TODO 1
# - Return the string "a" if func_a is faster, "b" if func_b is faster

def compare_implementations(func_a, func_b, iterations: int = 100) -> str:
    """Benchmark two functions and return which is faster.

    Args:
        func_a: First function to benchmark.
        func_b: Second function to benchmark.
        iterations: Number of iterations for each benchmark.

    Returns:
        "a" if func_a is faster by average time, "b" otherwise.
    """
    # TODO: Implement this function
    pass


# ============= TODO 3: Implement create_locust_config =============
# Build a load test configuration as a structured dict.
# This exercises your understanding of load test parameters without
# requiring a Locust installation.
#
# Steps:
# 1. Build a dict with the specified structure
# 2. Include the provided parameters
# 3. Include a "tasks" list built from the task_weights dict
#
# Hints:
# - Each task should be a dict with "name", "method", "path", "weight"
# - The total weight across tasks is used for proportional distribution

def create_locust_config(
    host: str,
    users: int,
    spawn_rate: int,
    run_time_seconds: int,
    task_weights: dict[str, dict],
) -> dict:
    """Build a load test configuration dict.

    Args:
        host: Target host URL (e.g., "http://localhost:8000")
        users: Number of simulated concurrent users
        spawn_rate: Users spawned per second
        run_time_seconds: Total test duration in seconds
        task_weights: Dict mapping task name to {"method": str, "path": str, "weight": int}
            Example: {"list_users": {"method": "GET", "path": "/users", "weight": 5}}

    Returns:
        {
            "host": str,
            "users": int,
            "spawn_rate": int,
            "run_time_seconds": int,
            "tasks": [
                {"name": str, "method": str, "path": str, "weight": int},
                ...
            ],
            "total_weight": int,
        }
    """
    # TODO: Implement this function
    pass


# ============= TESTS (do not modify below) =============


# Helper functions for testing
def _fast_function():
    """O(n) operation -- fast."""
    return sum(range(1000))


def _slow_function():
    """O(n^2) operation -- slow."""
    result = []
    for i in range(1000):
        result.append(sum(range(i)))
    return result


class TestBenchmarkFunction:
    """Tests for the benchmarking utility."""

    def test_returns_dict(self):
        """benchmark_function should return a dict."""
        result = benchmark_function(lambda: None, iterations=10)
        assert isinstance(result, dict), (
            f"Expected a dict, got {type(result).__name__}"
        )

    def test_has_required_keys(self):
        """Result should have min, max, avg, and p95 keys."""
        result = benchmark_function(lambda: None, iterations=10)
        for key in ["min", "max", "avg", "p95"]:
            assert key in result, f"Result dict must have a '{key}' key"

    def test_values_are_floats(self):
        """All timing values should be floats."""
        result = benchmark_function(lambda: None, iterations=10)
        for key in ["min", "max", "avg", "p95"]:
            assert isinstance(result[key], float), (
                f"result['{key}'] should be a float, got {type(result[key]).__name__}"
            )

    def test_values_are_non_negative(self):
        """All timing values should be non-negative."""
        result = benchmark_function(lambda: None, iterations=10)
        for key in ["min", "max", "avg", "p95"]:
            assert result[key] >= 0, f"result['{key}'] should be >= 0"

    def test_min_less_equal_avg(self):
        """min should be <= avg."""
        result = benchmark_function(_fast_function, iterations=50)
        assert result["min"] <= result["avg"], (
            f"min ({result['min']}) should be <= avg ({result['avg']})"
        )

    def test_avg_less_equal_max(self):
        """avg should be <= max."""
        result = benchmark_function(_fast_function, iterations=50)
        assert result["avg"] <= result["max"], (
            f"avg ({result['avg']}) should be <= max ({result['max']})"
        )

    def test_p95_greater_equal_avg(self):
        """p95 should be >= avg (95th percentile is at least as large as mean)."""
        result = benchmark_function(_fast_function, iterations=100)
        # p95 >= avg is not strictly guaranteed for all distributions,
        # but for timing data (right-skewed) it virtually always holds.
        # We use a small tolerance for edge cases.
        assert result["p95"] >= result["avg"] * 0.9, (
            f"p95 ({result['p95']}) should be >= avg ({result['avg']}) "
            f"for timing data (right-skewed distribution)"
        )

    def test_slow_function_has_measurable_time(self):
        """Benchmarking a slow function should show measurable times."""
        result = benchmark_function(_slow_function, iterations=5)
        assert result["avg"] > 0, (
            "avg time for a slow function should be measurably > 0"
        )


class TestCompareImplementations:
    """Tests for the comparison utility."""

    def test_returns_string(self):
        """compare_implementations should return a string."""
        result = compare_implementations(lambda: None, lambda: None, iterations=10)
        assert isinstance(result, str), (
            f"Expected a string, got {type(result).__name__}"
        )

    def test_returns_a_or_b(self):
        """Result should be either 'a' or 'b'."""
        result = compare_implementations(lambda: None, lambda: None, iterations=10)
        assert result in ("a", "b"), (
            f"Expected 'a' or 'b', got '{result}'"
        )

    def test_identifies_faster_function(self):
        """Should correctly identify the faster function."""
        # _fast_function is O(n), _slow_function is O(n^2)
        result = compare_implementations(
            _fast_function, _slow_function, iterations=20
        )
        assert result == "a", (
            "func_a (O(n)) should be identified as faster than func_b (O(n^2)). "
            "Make sure you compare average times correctly."
        )

    def test_identifies_faster_when_reversed(self):
        """Should still identify the faster function when order is swapped."""
        result = compare_implementations(
            _slow_function, _fast_function, iterations=20
        )
        assert result == "b", (
            "func_b (O(n)) should be identified as faster than func_a (O(n^2))."
        )


class TestCreateLocustConfig:
    """Tests for the load test configuration builder."""

    def _sample_config(self):
        return create_locust_config(
            host="http://localhost:8000",
            users=100,
            spawn_rate=10,
            run_time_seconds=60,
            task_weights={
                "list_users": {"method": "GET", "path": "/users", "weight": 5},
                "get_user": {"method": "GET", "path": "/users/1", "weight": 3},
                "create_user": {"method": "POST", "path": "/users", "weight": 1},
            },
        )

    def test_returns_dict(self):
        """create_locust_config should return a dict."""
        result = self._sample_config()
        assert isinstance(result, dict), (
            f"Expected a dict, got {type(result).__name__}"
        )

    def test_has_host(self):
        """Config should include the host."""
        result = self._sample_config()
        assert result["host"] == "http://localhost:8000"

    def test_has_users(self):
        """Config should include users count."""
        result = self._sample_config()
        assert result["users"] == 100

    def test_has_spawn_rate(self):
        """Config should include spawn rate."""
        result = self._sample_config()
        assert result["spawn_rate"] == 10

    def test_has_run_time(self):
        """Config should include run time."""
        result = self._sample_config()
        assert result["run_time_seconds"] == 60

    def test_has_tasks_list(self):
        """Config should include a tasks list."""
        result = self._sample_config()
        assert "tasks" in result, "Config must have a 'tasks' key"
        assert isinstance(result["tasks"], list), "tasks should be a list"

    def test_tasks_count(self):
        """Tasks list should have one entry per task_weight."""
        result = self._sample_config()
        assert len(result["tasks"]) == 3, (
            f"Expected 3 tasks, got {len(result['tasks'])}"
        )

    def test_task_structure(self):
        """Each task should have name, method, path, and weight."""
        result = self._sample_config()
        for task in result["tasks"]:
            assert "name" in task, "Each task must have a 'name'"
            assert "method" in task, "Each task must have a 'method'"
            assert "path" in task, "Each task must have a 'path'"
            assert "weight" in task, "Each task must have a 'weight'"

    def test_total_weight(self):
        """Config should include total_weight summing all task weights."""
        result = self._sample_config()
        assert "total_weight" in result, "Config must have a 'total_weight' key"
        assert result["total_weight"] == 9, (
            f"Expected total_weight 9 (5+3+1), got {result['total_weight']}"
        )

    def test_task_names_match(self):
        """Task names should match the keys from task_weights."""
        result = self._sample_config()
        names = {task["name"] for task in result["tasks"]}
        assert names == {"list_users", "get_user", "create_user"}, (
            f"Task names should be the keys from task_weights, got {names}"
        )
