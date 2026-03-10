"""
Exercise 1: API Design Review

Design a complete REST API specification for your chosen capstone project
(Social Media, E-Commerce, or Task Management). Your design will be
validated against REST best practices from Modules 002-005.

You will create an APIDesign object containing endpoint specifications.
The tests verify your design follows REST conventions: proper HTTP methods,
authentication requirements, response models, and status codes.

Run: pytest 025-capstone-project/exercises/01_design_review.py -v
"""

from pydantic import BaseModel


# ============= API SPECIFICATION MODELS (PROVIDED) =============


class EndpointSpec(BaseModel):
    """Specification for a single API endpoint."""

    method: str  # GET, POST, PUT, PATCH, DELETE
    path: str  # /users/{id}, /posts, /auth/login
    description: str  # What this endpoint does
    auth_required: bool  # Whether Bearer token is required
    request_body: str | None = None  # Pydantic schema name (e.g., "UserCreate")
    response_model: str  # Pydantic schema name (e.g., "UserResponse")
    status_codes: list[int]  # Expected status codes (e.g., [200, 404, 422])


class APIDesign(BaseModel):
    """Complete API design specification."""

    title: str  # Project name (e.g., "Social Media API")
    version: str  # API version (e.g., "1.0.0")
    base_url: str  # Base URL (e.g., "/api/v1")
    endpoints: list[EndpointSpec]


# ============= TODO (IMPLEMENT) =============
# Design your capstone API specification.
#
# Requirements:
# - At least 10 endpoints covering CRUD for 2+ resources
# - Auth endpoints (register, login, refresh)
# - Proper HTTP methods for each operation (GET reads, POST creates, etc.)
# - All endpoints have descriptive response_model names
# - Protected endpoints marked with auth_required=True
# - Correct status codes (POST -> 201, DELETE -> 204 or 200, etc.)


def create_api_design() -> APIDesign:
    """
    Design your capstone API specification.

    Choose one of the three capstone projects and create a complete
    API design with endpoints covering authentication, CRUD operations,
    and any additional features your project requires.

    Returns:
        APIDesign with at least 10 well-designed endpoints.
    """
    pass  # TODO: Implement


# ============= TESTS =============


def test_minimum_endpoints():
    """API design should have at least 10 endpoints."""
    design = create_api_design()
    assert len(design.endpoints) >= 10, (
        f"Need at least 10 endpoints, got {len(design.endpoints)}"
    )


def test_has_auth_endpoints():
    """API design should include register and login endpoints."""
    design = create_api_design()
    paths = [e.path.lower() for e in design.endpoints]
    assert any("register" in p or "signup" in p for p in paths), (
        "Missing registration endpoint (path should contain 'register' or 'signup')"
    )
    assert any("login" in p or "token" in p for p in paths), (
        "Missing login endpoint (path should contain 'login' or 'token')"
    )


def test_crud_coverage():
    """API design should use all four main HTTP methods."""
    design = create_api_design()
    methods = {e.method.upper() for e in design.endpoints}
    assert methods >= {"GET", "POST", "PUT", "DELETE"}, (
        f"Need GET, POST, PUT, DELETE methods. Got: {methods}"
    )


def test_protected_endpoints():
    """API design should have at least 5 protected (auth required) endpoints."""
    design = create_api_design()
    protected = [e for e in design.endpoints if e.auth_required]
    assert len(protected) >= 5, (
        f"Need at least 5 protected endpoints, got {len(protected)}"
    )


def test_has_response_models():
    """Every endpoint should have a response_model defined."""
    design = create_api_design()
    for endpoint in design.endpoints:
        assert endpoint.response_model, (
            f"{endpoint.method} {endpoint.path} is missing response_model"
        )


def test_proper_status_codes():
    """POST endpoints should include 201, DELETE endpoints should include 204 or 200."""
    design = create_api_design()
    post_endpoints = [e for e in design.endpoints if e.method.upper() == "POST"]
    delete_endpoints = [e for e in design.endpoints if e.method.upper() == "DELETE"]

    for endpoint in post_endpoints:
        assert 201 in endpoint.status_codes or 200 in endpoint.status_codes, (
            f"POST {endpoint.path} should include 201 (Created) or 200 in status_codes"
        )

    for endpoint in delete_endpoints:
        assert 204 in endpoint.status_codes or 200 in endpoint.status_codes, (
            f"DELETE {endpoint.path} should include 204 (No Content) or 200 in status_codes"
        )
