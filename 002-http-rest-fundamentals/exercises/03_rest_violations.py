"""
Exercise 3: Identifying REST Violations

Practice identifying and fixing REST API design issues.
Run: pytest 002-http-rest-fundamentals/exercises/03_rest_violations.py -v
"""


# Exercise 3.1: Find REST violations in endpoint list
# TODO: Implement function
def find_violations(endpoints: list[dict]) -> list[str]:
    """Identify REST violations in a list of endpoints.

    Args:
        endpoints: List of dicts with keys: method, path
        Example: [
            {"method": "GET", "path": "/getUsers"},
            {"method": "POST", "path": "/users/delete"}
        ]

    Returns:
        List of violation descriptions
        Example: [
            "Verb in URL: /getUsers should be /users",
            "Wrong method: DELETE /users/delete should use DELETE method"
        ]
    """
    pass  # TODO: Implement


# Exercise 3.2: Fix a non-RESTful endpoint
# TODO: Implement function
def fix_endpoint(method: str, path: str) -> dict:
    """Fix a non-RESTful endpoint to follow REST conventions.

    Args:
        method: HTTP method
        path: URL path (might have violations)

    Returns:
        Dict with corrected method and path
        Example: fix_endpoint("GET", "/deleteUser/123")
                 -> {"method": "DELETE", "path": "/users/123"}
    """
    pass  # TODO: Implement


# Exercise 3.3: Check if URL follows REST naming conventions
# TODO: Implement function
def is_restful_url(url: str) -> bool:
    """Check if a URL follows REST naming conventions.

    Args:
        url: URL path to validate

    Returns:
        True if follows REST conventions, False otherwise

    REST conventions:
    - Uses plural nouns for resources
    - No verbs in URL
    - Uses /resource or /resource/{id} pattern
    """
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 002-http-rest-fundamentals/exercises/03_rest_violations.py -v

def test_find_violations():
    # Good endpoints - no violations
    good_endpoints = [
        {"method": "GET", "path": "/users"},
        {"method": "POST", "path": "/users"},
        {"method": "GET", "path": "/users/123"}
    ]
    assert find_violations(good_endpoints) == []

    # Endpoints with violations
    bad_endpoints = [
        {"method": "GET", "path": "/getUsers"},
        {"method": "POST", "path": "/createUser"},
        {"method": "GET", "path": "/users/delete/123"}
    ]
    violations = find_violations(bad_endpoints)
    assert len(violations) > 0
    assert any("verb" in v.lower() or "getUsers" in v for v in violations)


def test_fix_endpoint():
    # Fix verb in URL
    fixed = fix_endpoint("GET", "/getUser/123")
    assert fixed["method"] == "GET"
    assert fixed["path"] in ["/users/123", "/user/123"]

    # Fix wrong method
    fixed = fix_endpoint("POST", "/users/delete/123")
    assert fixed["method"] == "DELETE"
    assert "/delete" not in fixed["path"]

    # Fix create verb
    fixed = fix_endpoint("POST", "/createUser")
    assert fixed["method"] == "POST"
    assert fixed["path"] in ["/users", "/user"]


def test_is_restful_url():
    # Good URLs
    assert is_restful_url("/users") is True
    assert is_restful_url("/users/123") is True
    assert is_restful_url("/posts") is True
    assert is_restful_url("/users/123/posts") is True

    # Bad URLs - verbs
    assert is_restful_url("/getUsers") is False
    assert is_restful_url("/createUser") is False
    assert is_restful_url("/deletePost") is False
    assert is_restful_url("/users/delete") is False

    # Bad URLs - singular
    assert is_restful_url("/user") is False
    assert is_restful_url("/post/123") is False
