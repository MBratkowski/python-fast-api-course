"""
Exercise 3: Health Check Endpoints

In this exercise, you'll build health check endpoints for a FastAPI application
with liveness and readiness probes.

Your tasks:
1. Create a FastAPI app with two health endpoints:
   - GET /health/live  -- returns {"status": "alive"} with 200
   - GET /health/ready -- checks dependencies and returns 200 or 503

2. Implement check functions that the readiness endpoint uses:
   - check_database() returns {"status": "healthy"} or {"status": "unhealthy", "error": "..."}
   - check_cache() returns {"status": "healthy"} or {"status": "unhealthy", "error": "..."}

3. The readiness endpoint should:
   - Call all check functions
   - Return 200 with {"status": "ready", "checks": {...}} if all healthy
   - Return 503 with {"status": "not_ready", "checks": {...}} if any unhealthy

4. Use dependency injection to make check functions replaceable for testing.

Mobile analogy: This is like the App Store pre-launch checks that verify your
app starts correctly, but running continuously in production.

Run: pytest 021-logging-monitoring/exercises/03_health_endpoint.py -v
"""

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from typing import Callable


# ============= TODO 1: Implement dependency check functions =============
# These simulate checking external dependencies (database, cache).
# In a real app, you'd actually connect to the database/cache.
#
# Each function should return a dict with:
#   - {"status": "healthy"} if the dependency is available
#   - {"status": "unhealthy", "error": "description"} if not
#
# For this exercise, default implementations should return healthy.
# The tests will override them to simulate failures.


def check_database() -> dict:
    """Check database connectivity.

    Returns:
        Dict with "status" key ("healthy" or "unhealthy")
    """
    # TODO: Return a healthy status dict
    pass


def check_cache() -> dict:
    """Check cache (Redis) connectivity.

    Returns:
        Dict with "status" key ("healthy" or "unhealthy")
    """
    # TODO: Return a healthy status dict
    pass


# ============= TODO 2: Create the FastAPI app with health endpoints =============
# Create a FastAPI app with:
# 1. GET /health/live  -- simple liveness probe
#    Returns: {"status": "alive"} with HTTP 200
#
# 2. GET /health/ready -- readiness probe with dependency checks
#    Uses Depends() to inject check_database and check_cache functions
#    Returns:
#      - HTTP 200 with {"status": "ready", "checks": {...}} if all healthy
#      - HTTP 503 with {"status": "not_ready", "checks": {...}} if any unhealthy
#
# Hints:
# - Use app.dependency_overrides to make checks replaceable in tests
# - Use JSONResponse(status_code=503, content={...}) for unhealthy response
# - The "checks" dict should contain results from each check function
#   e.g., {"database": {"status": "healthy"}, "cache": {"status": "healthy"}}

app = FastAPI()


# TODO: Implement GET /health/live endpoint


# TODO: Implement GET /health/ready endpoint
# Use Depends(check_database) and Depends(check_cache) to inject check functions
# so tests can override them with app.dependency_overrides


# ============= TESTS (do not modify below) =============


class TestLivenessProbe:
    """Tests for the /health/live endpoint."""

    def test_liveness_returns_200(self):
        """Liveness endpoint should return HTTP 200."""
        client = TestClient(app)
        response = client.get("/health/live")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            "Create a GET /health/live endpoint that returns 200."
        )

    def test_liveness_returns_alive_status(self):
        """Liveness endpoint should return {"status": "alive"}."""
        client = TestClient(app)
        response = client.get("/health/live")
        data = response.json()
        assert data.get("status") == "alive", (
            f'Expected {{"status": "alive"}}, got {data}. '
            "The liveness endpoint should return a simple alive status."
        )


class TestReadinessProbe:
    """Tests for the /health/ready endpoint."""

    def test_ready_when_all_healthy(self):
        """Readiness should return 200 when all dependencies are healthy."""
        # Override with healthy checks
        app.dependency_overrides[check_database] = lambda: {"status": "healthy"}
        app.dependency_overrides[check_cache] = lambda: {"status": "healthy"}

        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            assert response.status_code == 200, (
                f"Expected 200 when all healthy, got {response.status_code}"
            )
            data = response.json()
            assert data.get("status") == "ready", (
                f'Expected {{"status": "ready"}}, got {data}'
            )
        finally:
            app.dependency_overrides.clear()

    def test_ready_includes_checks(self):
        """Readiness response should include individual check results."""
        app.dependency_overrides[check_database] = lambda: {"status": "healthy"}
        app.dependency_overrides[check_cache] = lambda: {"status": "healthy"}

        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            data = response.json()
            assert "checks" in data, (
                "Readiness response should include a 'checks' key with "
                "individual dependency results."
            )
            checks = data["checks"]
            assert "database" in checks, (
                "Checks should include 'database' status."
            )
            assert "cache" in checks, (
                "Checks should include 'cache' status."
            )
        finally:
            app.dependency_overrides.clear()

    def test_not_ready_when_database_unhealthy(self):
        """Readiness should return 503 when database is unhealthy."""
        app.dependency_overrides[check_database] = lambda: {
            "status": "unhealthy",
            "error": "Connection refused",
        }
        app.dependency_overrides[check_cache] = lambda: {"status": "healthy"}

        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            assert response.status_code == 503, (
                f"Expected 503 when database unhealthy, got {response.status_code}. "
                "Use JSONResponse(status_code=503, ...) when any dependency is unhealthy."
            )
            data = response.json()
            assert data.get("status") == "not_ready", (
                f'Expected {{"status": "not_ready"}}, got {data}'
            )
        finally:
            app.dependency_overrides.clear()

    def test_not_ready_when_cache_unhealthy(self):
        """Readiness should return 503 when cache is unhealthy."""
        app.dependency_overrides[check_database] = lambda: {"status": "healthy"}
        app.dependency_overrides[check_cache] = lambda: {
            "status": "unhealthy",
            "error": "Redis connection timeout",
        }

        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            assert response.status_code == 503, (
                f"Expected 503 when cache unhealthy, got {response.status_code}"
            )
        finally:
            app.dependency_overrides.clear()

    def test_not_ready_when_all_unhealthy(self):
        """Readiness should return 503 when all dependencies are unhealthy."""
        app.dependency_overrides[check_database] = lambda: {
            "status": "unhealthy",
            "error": "Connection refused",
        }
        app.dependency_overrides[check_cache] = lambda: {
            "status": "unhealthy",
            "error": "Redis down",
        }

        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            assert response.status_code == 503, (
                f"Expected 503 when all unhealthy, got {response.status_code}"
            )
            data = response.json()
            assert data.get("status") == "not_ready"
            checks = data.get("checks", {})
            assert checks.get("database", {}).get("status") == "unhealthy"
            assert checks.get("cache", {}).get("status") == "unhealthy"
        finally:
            app.dependency_overrides.clear()

    def test_unhealthy_check_includes_error(self):
        """Unhealthy check results should include the error message."""
        error_msg = "Connection refused on port 5432"
        app.dependency_overrides[check_database] = lambda: {
            "status": "unhealthy",
            "error": error_msg,
        }
        app.dependency_overrides[check_cache] = lambda: {"status": "healthy"}

        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            data = response.json()
            db_check = data.get("checks", {}).get("database", {})
            assert db_check.get("error") == error_msg, (
                f"Unhealthy check should include the error message. "
                f"Expected '{error_msg}', got {db_check}"
            )
        finally:
            app.dependency_overrides.clear()
