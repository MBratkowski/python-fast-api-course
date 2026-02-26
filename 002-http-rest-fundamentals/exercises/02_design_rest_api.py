"""
Exercise 2: Designing REST APIs

Practice designing RESTful API endpoints.
Run: pytest 002-http-rest-fundamentals/exercises/02_design_rest_api.py -v
"""


# Exercise 2.1: Design CRUD endpoints for a resource
# TODO: Implement function
def design_user_endpoints() -> list[dict]:
    """Design REST endpoints for user CRUD operations.

    Returns:
        List of endpoint dicts with keys: method, path, description
        Example: [
            {"method": "GET", "path": "/users", "description": "List all users"},
            ...
        ]
    """
    pass  # TODO: Implement


# Exercise 2.2: Design nested resource endpoints
# TODO: Implement function
def design_nested_resource(parent: str, child: str) -> list[dict]:
    """Design endpoints for a nested resource.

    Args:
        parent: Parent resource name (e.g., "users")
        child: Child resource name (e.g., "posts")

    Returns:
        List of endpoint dicts for nested resource
        Example for users/posts:
        [
            {"method": "GET", "path": "/users/{id}/posts", "description": "List user's posts"},
            {"method": "POST", "path": "/users/{id}/posts", "description": "Create post for user"},
            ...
        ]
    """
    pass  # TODO: Implement


# Exercise 2.3: Choose correct HTTP method for action
# TODO: Implement function
def choose_method(action_description: str) -> str:
    """Given an action description, return the correct HTTP method.

    Args:
        action_description: Description like "create a new user" or "delete a post"

    Returns:
        HTTP method: "GET", "POST", "PUT", "PATCH", or "DELETE"
    """
    pass  # TODO: Implement


# Exercise 2.4: Choose correct status code for scenario
# TODO: Implement function
def choose_status_code(scenario: str) -> int:
    """Given a scenario, return the correct HTTP status code.

    Args:
        scenario: Description like "resource created" or "not found"

    Returns:
        HTTP status code as integer
    """
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 002-http-rest-fundamentals/exercises/02_design_rest_api.py -v

def test_design_user_endpoints():
    endpoints = design_user_endpoints()

    # Should have 5 CRUD endpoints
    assert len(endpoints) == 5

    # Check list endpoint
    list_ep = next(e for e in endpoints if e["method"] == "GET" and "/users/{" not in e["path"])
    assert list_ep["path"] == "/users"

    # Check create endpoint
    create_ep = next(e for e in endpoints if e["method"] == "POST")
    assert create_ep["path"] == "/users"

    # Check get single endpoint
    get_ep = next(e for e in endpoints if e["method"] == "GET" and "/users/{" in e["path"])
    assert "{id}" in get_ep["path"] or "{user_id}" in get_ep["path"]

    # Check update endpoint
    update_ep = next(e for e in endpoints if e["method"] in ["PUT", "PATCH"])
    assert "{id}" in update_ep["path"] or "{user_id}" in update_ep["path"]

    # Check delete endpoint
    delete_ep = next(e for e in endpoints if e["method"] == "DELETE")
    assert "{id}" in delete_ep["path"] or "{user_id}" in delete_ep["path"]


def test_design_nested_resource():
    endpoints = design_nested_resource("users", "posts")

    # Should have at least list and create for nested resource
    assert len(endpoints) >= 2

    # Check list nested endpoint
    list_ep = next((e for e in endpoints if e["method"] == "GET"), None)
    assert list_ep is not None
    assert "users" in list_ep["path"]
    assert "posts" in list_ep["path"]
    assert "{id}" in list_ep["path"] or "{user_id}" in list_ep["path"]

    # Check create nested endpoint
    create_ep = next((e for e in endpoints if e["method"] == "POST"), None)
    assert create_ep is not None
    assert "users" in create_ep["path"]
    assert "posts" in create_ep["path"]


def test_choose_method():
    assert choose_method("create a new user") == "POST"
    assert choose_method("list all users") == "GET"
    assert choose_method("get user details") == "GET"
    assert choose_method("update user profile") in ["PUT", "PATCH"]
    assert choose_method("delete a user") == "DELETE"
    assert choose_method("fetch posts") == "GET"


def test_choose_status_code():
    assert choose_status_code("resource created") == 201
    assert choose_status_code("success") == 200
    assert choose_status_code("not found") == 404
    assert choose_status_code("unauthorized") == 401
    assert choose_status_code("validation error") == 422
    assert choose_status_code("server error") == 500
    assert choose_status_code("deleted") in [200, 204]
