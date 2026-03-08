"""
Exercise 3: Deprecation Headers

In this exercise, you'll add deprecation headers to v1 API endpoints
to communicate that they will be sunset.

Your tasks:
1. Create v1_router and v2_router with URL path versioning
2. On v1 GET /users/{user_id}:
   - Return the user data (flat format)
   - Add Deprecation: true header
   - Add Sunset header with a date string (e.g., "Sat, 01 Jun 2026 00:00:00 GMT")
   - Add Link header pointing to v2: '</v2/users/{user_id}>; rel="successor-version"'
3. On v2 GET /users/{user_id}:
   - Return wrapped response (data + meta)
   - Do NOT add deprecation headers (v2 is current)

Mobile analogy: This is like adding @available(*, deprecated, message: "Use v2 instead")
to your Swift API, or @Deprecated annotation in Kotlin.

Run: pytest 022-api-versioning/exercises/03_deprecation.py -v
"""

from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.testclient import TestClient


# Simulated user data
USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}


# ============= TODO 1: Create v1 router with deprecation headers =============
# Create an APIRouter with prefix="/v1" and tags=["v1 (deprecated)"]
# Add GET /users/{user_id} that:
# 1. Looks up user in USERS (404 if not found)
# 2. Returns flat response: {"id": ..., "name": "..."}
# 3. Sets response.headers["Deprecation"] = "true"
# 4. Sets response.headers["Sunset"] = "Sat, 01 Jun 2026 00:00:00 GMT"
# 5. Sets response.headers["Link"] = '</v2/users/{user_id}>; rel="successor-version"'
#
# Hints:
# - Add 'response: Response' as a parameter to access response headers
# - Use response.headers["Header-Name"] = "value" to set headers
# - The Link header format is: </path>; rel="relation-type"


# TODO: Create v1_router with deprecated endpoint


# ============= TODO 2: Create v2 router (no deprecation headers) =============
# Create an APIRouter with prefix="/v2" and tags=["v2"]
# Add GET /users/{user_id} that:
# 1. Looks up user in USERS (404 if not found)
# 2. Returns wrapped response:
#    {"data": {"id": ..., "name": "...", "email": "..."}, "meta": {"version": "2.0"}}
# 3. Does NOT set any deprecation headers


# TODO: Create v2_router with current endpoint


# ============= TODO 3: Create app and include routers =============

app = FastAPI()

# TODO: Include both routers in the app


# ============= TESTS (do not modify below) =============


class TestV1DeprecationHeaders:
    """Tests that v1 endpoints include deprecation headers."""

    def test_v1_returns_200(self):
        """V1 endpoint should still return 200 (deprecated, not removed)."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            "Create v1_router with prefix='/v1' and GET /users/{{user_id}}."
        )

    def test_v1_has_deprecation_header(self):
        """V1 should include Deprecation: true header."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        assert "deprecation" in response.headers, (
            "V1 response should include a 'Deprecation' header. "
            'Set response.headers["Deprecation"] = "true".'
        )
        assert response.headers["deprecation"] == "true", (
            f'Expected Deprecation: true, got: {response.headers["deprecation"]}'
        )

    def test_v1_has_sunset_header(self):
        """V1 should include a Sunset header with a date."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        assert "sunset" in response.headers, (
            "V1 response should include a 'Sunset' header with the removal date. "
            'Set response.headers["Sunset"] = "Sat, 01 Jun 2026 00:00:00 GMT".'
        )
        sunset = response.headers["sunset"]
        assert "GMT" in sunset, (
            f"Sunset header should contain a date in GMT format. Got: {sunset}"
        )

    def test_v1_has_link_header(self):
        """V1 should include a Link header pointing to v2."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        assert "link" in response.headers, (
            "V1 response should include a 'Link' header pointing to the v2 endpoint. "
            'Set response.headers["Link"] = \'</v2/users/1>; rel="successor-version"\'.'
        )
        link = response.headers["link"]
        assert "successor-version" in link, (
            f'Link header should contain rel="successor-version". Got: {link}'
        )
        assert "/v2/" in link, (
            f"Link header should point to /v2/ endpoint. Got: {link}"
        )

    def test_v1_link_contains_correct_user_id(self):
        """Link header should reference the correct user ID in v2 URL."""
        client = TestClient(app)
        response = client.get("/v1/users/2")
        link = response.headers.get("link", "")
        assert "/v2/users/2" in link, (
            f"Link header should contain /v2/users/2 for user 2. Got: {link}"
        )

    def test_v1_returns_flat_response(self):
        """V1 should still return the flat response format."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        data = response.json()
        assert data.get("id") == 1
        assert data.get("name") == "Alice"

    def test_v1_not_found(self):
        """V1 should return 404 for missing users."""
        client = TestClient(app)
        response = client.get("/v1/users/999")
        assert response.status_code == 404


class TestV2NoDeprecation:
    """Tests that v2 endpoints do NOT include deprecation headers."""

    def test_v2_returns_200(self):
        """V2 endpoint should return 200."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            "Create v2_router with prefix='/v2' and GET /users/{{user_id}}."
        )

    def test_v2_no_deprecation_header(self):
        """V2 should NOT include a Deprecation header."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        assert "deprecation" not in response.headers, (
            "V2 (current version) should NOT have a Deprecation header."
        )

    def test_v2_no_sunset_header(self):
        """V2 should NOT include a Sunset header."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        assert "sunset" not in response.headers, (
            "V2 (current version) should NOT have a Sunset header."
        )

    def test_v2_returns_wrapped_response(self):
        """V2 should return the wrapped response format."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        data = response.json()
        assert "data" in data, 'V2 should have "data" wrapper.'
        assert "meta" in data, 'V2 should have "meta" key.'
        assert data["data"].get("email") == "alice@example.com"
        assert data["meta"].get("version") == "2.0"

    def test_v2_not_found(self):
        """V2 should return 404 for missing users."""
        client = TestClient(app)
        response = client.get("/v2/users/999")
        assert response.status_code == 404
