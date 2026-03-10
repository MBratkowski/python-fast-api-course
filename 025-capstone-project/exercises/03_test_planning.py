"""
Exercise 3: Test Plan Creation

Create a comprehensive test plan for your capstone project.
Define test cases that cover authentication, CRUD operations,
error handling, and edge cases from Module 011.

You will create a TestPlan with individual test cases categorized
by type (unit, integration, e2e) and priority (critical, high,
medium, low). The tests verify your plan is thorough and covers
the essential paths.

Run: pytest 025-capstone-project/exercises/03_test_planning.py -v
"""

from pydantic import BaseModel


# ============= TEST PLAN MODELS (PROVIDED) =============


class TestCase(BaseModel):
    """Specification for a single test case."""

    name: str  # Test function name (e.g., "test_user_registration_success")
    category: str  # "unit", "integration", or "e2e"
    endpoint: str  # API endpoint being tested (e.g., "POST /auth/register")
    description: str  # What this test verifies
    setup_required: str  # What fixtures/setup are needed (e.g., "auth_headers, db_session")
    expected_status: int  # Expected HTTP status code
    priority: str  # "critical", "high", "medium", or "low"


class TestPlan(BaseModel):
    """Complete test plan for the capstone project."""

    project_name: str  # Which capstone project (e.g., "Social Media API")
    test_cases: list[TestCase]


# ============= TODO (IMPLEMENT) =============
# Create a test plan for your capstone project.
#
# Requirements:
# - At least 15 test cases covering your API's critical paths
# - At least 5 test cases with "critical" priority
# - At least 3 test cases covering auth endpoints
# - Both "unit" and "integration" categories represented
# - At least 3 test cases with expected_status >= 400 (error cases)
# - All test names follow the "test_" naming convention


def create_test_plan() -> TestPlan:
    """
    Create a comprehensive test plan for your capstone project.

    Design test cases that cover authentication, CRUD operations,
    authorization, validation, and error handling. Prioritize tests
    that protect critical user flows.

    Returns:
        TestPlan with at least 15 well-designed test cases.
    """
    pass  # TODO: Implement


# ============= TESTS =============


def test_minimum_test_cases():
    """Test plan should have at least 15 test cases."""
    plan = create_test_plan()
    assert len(plan.test_cases) >= 15, (
        f"Need at least 15 test cases, got {len(plan.test_cases)}"
    )


def test_has_critical_tests():
    """Test plan should have at least 5 critical-priority test cases."""
    plan = create_test_plan()
    critical = [t for t in plan.test_cases if t.priority == "critical"]
    assert len(critical) >= 5, (
        f"Need at least 5 critical tests, got {len(critical)}"
    )


def test_covers_auth():
    """Test plan should have at least 3 test cases covering auth endpoints."""
    plan = create_test_plan()
    auth_tests = [t for t in plan.test_cases if "auth" in t.endpoint.lower()]
    assert len(auth_tests) >= 3, (
        f"Need at least 3 auth-related tests, got {len(auth_tests)}"
    )


def test_has_all_categories():
    """Test plan should include both unit and integration test categories."""
    plan = create_test_plan()
    categories = {t.category for t in plan.test_cases}
    assert "unit" in categories, (
        f"Missing 'unit' category. Found: {categories}"
    )
    assert "integration" in categories, (
        f"Missing 'integration' category. Found: {categories}"
    )


def test_has_error_cases():
    """Test plan should have at least 3 test cases for error responses (status >= 400)."""
    plan = create_test_plan()
    error_tests = [t for t in plan.test_cases if t.expected_status >= 400]
    assert len(error_tests) >= 3, (
        f"Need at least 3 error case tests, got {len(error_tests)}"
    )


def test_naming_convention():
    """All test case names should start with 'test_'."""
    plan = create_test_plan()
    for tc in plan.test_cases:
        assert tc.name.startswith("test_"), (
            f"Test case name '{tc.name}' should start with 'test_'"
        )
