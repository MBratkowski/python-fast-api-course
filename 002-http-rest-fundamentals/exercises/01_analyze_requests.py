"""
Exercise 1: Analyzing HTTP Requests and Responses

Practice working with HTTP request/response data structures.
Run: pytest 002-http-rest-fundamentals/exercises/01_analyze_requests.py -v
"""


# Exercise 1.1: Extract request method
# TODO: Implement function
def get_request_method(request: dict) -> str:
    """Extract the HTTP method from a request dict.

    Args:
        request: Dict with keys 'method', 'url', 'headers', 'body'

    Returns:
        The HTTP method (e.g., 'GET', 'POST')
    """
    pass  # TODO: Implement


# Exercise 1.2: Check if status code indicates success
# TODO: Implement function
def is_successful(status_code: int) -> bool:
    """Check if an HTTP status code indicates success (2xx).

    Args:
        status_code: HTTP status code (e.g., 200, 404, 500)

    Returns:
        True if status code is 2xx, False otherwise
    """
    pass  # TODO: Implement


# Exercise 1.3: Get content type header (case-insensitive)
# TODO: Implement function
def get_content_type(headers: dict) -> str | None:
    """Find Content-Type header in a case-insensitive manner.

    Args:
        headers: Dict of HTTP headers (keys might be any case)

    Returns:
        The Content-Type value or None if not found
    """
    pass  # TODO: Implement


# Exercise 1.4: Classify status code by family
# TODO: Implement function
def classify_status_code(code: int) -> str:
    """Classify a status code into its family.

    Args:
        code: HTTP status code

    Returns:
        One of: "informational", "success", "redirect", "client_error", "server_error"
    """
    pass  # TODO: Implement


# Exercise 1.5: Extract query parameters from URL
# TODO: Implement function
def extract_query_params(url: str) -> dict:
    """Extract query parameters from a URL.

    Args:
        url: Full URL like "/users?page=1&limit=10"

    Returns:
        Dict of query parameters {"page": "1", "limit": "10"}
    """
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 002-http-rest-fundamentals/exercises/01_analyze_requests.py -v

def test_get_request_method():
    request = {"method": "POST", "url": "/users", "headers": {}, "body": "{}"}
    assert get_request_method(request) == "POST"

    request = {"method": "GET", "url": "/users", "headers": {}, "body": None}
    assert get_request_method(request) == "GET"


def test_is_successful():
    assert is_successful(200) is True
    assert is_successful(201) is True
    assert is_successful(204) is True
    assert is_successful(400) is False
    assert is_successful(404) is False
    assert is_successful(500) is False


def test_get_content_type():
    headers = {"Content-Type": "application/json"}
    assert get_content_type(headers) == "application/json"

    # Case-insensitive
    headers = {"content-type": "text/html"}
    assert get_content_type(headers) == "text/html"

    headers = {"CONTENT-TYPE": "application/xml"}
    assert get_content_type(headers) == "application/xml"

    # Not found
    headers = {"Authorization": "Bearer token"}
    assert get_content_type(headers) is None


def test_classify_status_code():
    assert classify_status_code(100) == "informational"
    assert classify_status_code(200) == "success"
    assert classify_status_code(201) == "success"
    assert classify_status_code(301) == "redirect"
    assert classify_status_code(404) == "client_error"
    assert classify_status_code(422) == "client_error"
    assert classify_status_code(500) == "server_error"
    assert classify_status_code(503) == "server_error"


def test_extract_query_params():
    url = "/users?page=1&limit=10"
    assert extract_query_params(url) == {"page": "1", "limit": "10"}

    url = "/search?q=python&sort=date"
    assert extract_query_params(url) == {"q": "python", "sort": "date"}

    # No query params
    url = "/users"
    assert extract_query_params(url) == {}

    # Single param
    url = "/users?id=123"
    assert extract_query_params(url) == {"id": "123"}
