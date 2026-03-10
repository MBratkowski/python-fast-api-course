"""
Exercise 1: Profile Python Code to Find Bottlenecks

In this exercise, you'll use Python's cProfile module to identify performance
bottlenecks, optimize slow code, and measure the improvement.

Your task:
1. Implement find_bottleneck() that profiles slow_function() and returns the
   name of the function consuming the most cumulative time.
2. Implement optimize_function() that produces the same result as slow_function()
   but runs significantly faster.
3. Implement compare_performance() that benchmarks both functions and returns
   timing data.

Mobile analogy: This is like using Instruments Time Profiler on iOS to find which
method is eating CPU time, then optimizing it and verifying the improvement. On
Android, it's like using the CPU Profiler to identify the hot method, then
comparing before/after execution times.

Run: pytest 020-performance-optimization/exercises/01_profile_code.py -v
"""

import cProfile
import io
import pstats
import time


# ============= Pre-built slow function (do NOT modify) =============

def _compute_partial_sum(n: int) -> int:
    """Compute sum of range(n). Deliberately uses sum() for profiling."""
    return sum(range(n))


def slow_function(size: int = 5000) -> list[int]:
    """Build a list of cumulative sums using an O(n^2) approach.

    For each index i, computes sum(range(i)) from scratch.
    This is intentionally slow -- sum(range(i)) is called N times,
    each computing up to i additions.

    Returns:
        A list where result[i] = 0 + 1 + 2 + ... + (i-1)
    """
    result = []
    for i in range(size):
        result.append(_compute_partial_sum(i))
    return result


# ============= TODO 1: Implement find_bottleneck =============
# Use cProfile to profile slow_function() and find which function
# takes the most cumulative time (excluding the wrapper).
#
# Steps:
# 1. Create a cProfile.Profile() instance
# 2. Profile slow_function() with profiler.enable() / profiler.disable()
# 3. Create pstats.Stats from the profiler
# 4. Sort by "cumulative" time
# 5. Use stats.get_stats_profile() or capture print_stats output
#    to find the function name with the highest cumtime
#
# Hints:
# - pstats.Stats(profiler) creates stats from a profiler
# - stats.sort_stats("cumulative") sorts by cumulative time
# - The top function by cumtime (after the main call) is the bottleneck
# - stats.get_stats_profile().func_profiles is a dict of function stats

def find_bottleneck() -> str:
    """Profile slow_function() and return the name of the bottleneck function.

    Returns:
        The function name (e.g., "_compute_partial_sum") that has the highest
        cumulative time after slow_function itself.
    """
    # TODO: Implement this function
    pass


# ============= TODO 2: Implement optimize_function =============
# Create a faster version that produces the same result as slow_function().
# Instead of calling sum(range(i)) for each i, use a running total.
#
# Hints:
# - Keep a running_sum variable, add i each iteration
# - Or use itertools.accumulate(range(size))
# - The result must be identical to slow_function(size)

def optimize_function(size: int = 5000) -> list[int]:
    """Produce the same result as slow_function() but in O(n) time.

    Returns:
        A list where result[i] = 0 + 1 + 2 + ... + (i-1)
        Identical output to slow_function(size).
    """
    # TODO: Implement this function
    pass


# ============= TODO 3: Implement compare_performance =============
# Time both slow_function and optimize_function, return a dict with
# the elapsed times.
#
# Hints:
# - Use time.perf_counter() for high-resolution timing
# - Use a smaller size (e.g., 2000) to keep test runtime reasonable
# - Return {"slow": float_seconds, "fast": float_seconds}

def compare_performance(size: int = 2000) -> dict:
    """Benchmark slow_function vs optimize_function.

    Args:
        size: The input size to use for both functions.

    Returns:
        {"slow": elapsed_seconds, "fast": elapsed_seconds}
    """
    # TODO: Implement this function
    pass


# ============= TESTS (do not modify below) =============


class TestFindBottleneck:
    """Tests for the profiling exercise."""

    def test_find_bottleneck_returns_string(self):
        """find_bottleneck should return a string (function name)."""
        result = find_bottleneck()
        assert isinstance(result, str), (
            f"find_bottleneck should return a string, got {type(result).__name__}"
        )

    def test_find_bottleneck_identifies_compute_partial_sum(self):
        """The bottleneck in slow_function is _compute_partial_sum."""
        result = find_bottleneck()
        assert result == "_compute_partial_sum", (
            f"Expected '_compute_partial_sum' as the bottleneck, got '{result}'. "
            "Profile slow_function() and look for the function with the highest "
            "cumulative time (after slow_function itself)."
        )


class TestOptimizeFunction:
    """Tests for the optimization exercise."""

    def test_optimize_returns_list(self):
        """optimize_function should return a list."""
        result = optimize_function(10)
        assert isinstance(result, list), (
            f"optimize_function should return a list, got {type(result).__name__}"
        )

    def test_optimize_matches_slow_small(self):
        """optimize_function should produce identical output to slow_function."""
        expected = slow_function(100)
        actual = optimize_function(100)
        assert actual == expected, (
            "optimize_function(100) should produce the same result as "
            "slow_function(100). Check your cumulative sum logic."
        )

    def test_optimize_matches_slow_medium(self):
        """optimize_function should match slow_function for larger inputs."""
        expected = slow_function(500)
        actual = optimize_function(500)
        assert actual == expected, (
            "optimize_function(500) should match slow_function(500)."
        )

    def test_optimize_handles_zero(self):
        """optimize_function(0) should return an empty list."""
        assert optimize_function(0) == [], (
            "optimize_function(0) should return []"
        )

    def test_optimize_handles_one(self):
        """optimize_function(1) should return [0]."""
        assert optimize_function(1) == [0], (
            "optimize_function(1) should return [0] (sum of range(0) is 0)"
        )


class TestComparePerformance:
    """Tests for the benchmarking exercise."""

    def test_compare_returns_dict(self):
        """compare_performance should return a dict."""
        result = compare_performance(100)
        assert isinstance(result, dict), (
            f"compare_performance should return a dict, got {type(result).__name__}"
        )

    def test_compare_has_required_keys(self):
        """compare_performance should return dict with 'slow' and 'fast' keys."""
        result = compare_performance(100)
        assert "slow" in result, "Result dict must have a 'slow' key"
        assert "fast" in result, "Result dict must have a 'fast' key"

    def test_compare_values_are_floats(self):
        """Timing values should be floats (seconds)."""
        result = compare_performance(100)
        assert isinstance(result["slow"], float), "result['slow'] should be a float"
        assert isinstance(result["fast"], float), "result['fast'] should be a float"

    def test_compare_values_are_positive(self):
        """Timing values should be positive."""
        result = compare_performance(100)
        assert result["slow"] > 0, "result['slow'] should be positive"
        assert result["fast"] > 0, "result['fast'] should be positive"

    def test_fast_is_faster_than_slow(self):
        """The optimized function should be faster than the slow one."""
        result = compare_performance(2000)
        assert result["fast"] < result["slow"], (
            f"optimize_function should be faster than slow_function. "
            f"Got slow={result['slow']:.4f}s, fast={result['fast']:.4f}s. "
            f"Make sure optimize_function uses O(n) approach, not O(n^2)."
        )
