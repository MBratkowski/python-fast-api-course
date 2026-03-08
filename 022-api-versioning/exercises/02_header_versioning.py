"""
Exercise 2: Header-Based Versioning

In this exercise, you'll implement API versioning using the X-API-Version
custom header instead of URL path prefixes.

Your tasks:
1. Create a single GET /users/{user_id} endpoint
2. Read the X-API-Version header (default: "1.0")
3. Return different response formats based on the version:
   - "1.0": {"id": user_id, "name": "Alice"}
   - "2.0": {"data": {"id": user_id, "name": "Alice", "email": "alice@example.com"}, "meta": {"version": "2.0"}}
4. Return 400 for unsupported versions

Mobile analogy: This is like using a custom HTTP header in your URLSession
or OkHttp requests to configure server behavior -- similar to feature flags.

Run: pytest 022-api-versioning/exercises/02_header_versioning.py -v
"""

from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient


# Simulated user data
USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}


app = FastAPI()


# ============= TODO: Implement header-versioned endpoint =============
# Create a GET /users/{user_id} endpoint that:
# 1. Accepts x_api_version as a Header parameter with default "1.0"
# 2. Looks up the user in USERS dict (404 if not found)
# 3. If version is "1.0": return {"id": ..., "name": "..."}
# 4. If version is "2.0": return {"data": {"id": ..., "name": "...", "email": "..."}, "meta": {"version": "2.0"}}
# 5. If version is anything else: raise HTTPException(status_code=400)
#
# Hints:
# - Use x_api_version: str = Header(default="1.0") as a parameter
# - FastAPI converts X-API-Version header to x_api_version parameter
# - Use HTTPException(status_code=400, detail="...") for unsupported versions
# - Use HTTPException(status_code=404, detail="...") for missing users


# TODO: Implement the endpoint


# ============= TESTS (do not modify below) =============


class TestDefaultVersion:
    """Tests for when no X-API-Version header is sent."""

    def test_no_header_returns_200(self):
        """Request without version header should return 200."""
        client = TestClient(app)
        response = client.get("/users/1")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            "Create a GET /users/{{user_id}} endpoint."
        )

    def test_no_header_returns_v1_format(self):
        """Without header, should return v1 format (flat response)."""
        client = TestClient(app)
        response = client.get("/users/1")
        data = response.json()
        assert data.get("id") == 1, (
            "Default (no header) should return v1 flat format with 'id'."
        )
        assert data.get("name") == "Alice", (
            "Default should return v1 format with 'name'."
        )
        assert "data" not in data, (
            "Default (v1) should NOT have a 'data' wrapper."
        )


class TestV1Header:
    """Tests for explicit X-API-Version: 1.0 header."""

    def test_v1_header_returns_flat(self):
        """X-API-Version: 1.0 should return flat response."""
        client = TestClient(app)
        response = client.get("/users/1", headers={"X-API-Version": "1.0"})
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == 1
        assert data.get("name") == "Alice"
        assert "data" not in data, (
            "V1 should return flat format, not wrapped in 'data'."
        )

    def test_v1_does_not_include_email(self):
        """V1 should NOT include email."""
        client = TestClient(app)
        response = client.get("/users/1", headers={"X-API-Version": "1.0"})
        data = response.json()
        assert "email" not in data, (
            "V1 format should not include email."
        )


class TestV2Header:
    """Tests for X-API-Version: 2.0 header."""

    def test_v2_header_returns_wrapped(self):
        """X-API-Version: 2.0 should return wrapped response."""
        client = TestClient(app)
        response = client.get("/users/1", headers={"X-API-Version": "2.0"})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data, (
            'V2 should wrap response in "data" key.'
        )
        assert "meta" in data, (
            'V2 should include "meta" key.'
        )

    def test_v2_data_has_email(self):
        """V2 data should include email."""
        client = TestClient(app)
        response = client.get("/users/1", headers={"X-API-Version": "2.0"})
        user_data = response.json()["data"]
        assert user_data.get("email") == "alice@example.com", (
            "V2 data should include email."
        )

    def test_v2_meta_has_version(self):
        """V2 meta should include version "2.0"."""
        client = TestClient(app)
        response = client.get("/users/1", headers={"X-API-Version": "2.0"})
        meta = response.json()["meta"]
        assert meta.get("version") == "2.0", (
            f'Expected meta.version "2.0", got {meta}'
        )


class TestUnsupportedVersion:
    """Tests for unsupported version values."""

    def test_unsupported_version_returns_400(self):
        """X-API-Version: 3.0 should return 400."""
        client = TestClient(app)
        response = client.get("/users/1", headers={"X-API-Version": "3.0"})
        assert response.status_code == 400, (
            f"Expected 400 for unsupported version '3.0', got {response.status_code}. "
            "Raise HTTPException(status_code=400) for unsupported versions."
        )

    def test_invalid_version_returns_400(self):
        """X-API-Version: invalid should return 400."""
        client = TestClient(app)
        response = client.get("/users/1", headers={"X-API-Version": "invalid"})
        assert response.status_code == 400, (
            f"Expected 400 for invalid version, got {response.status_code}"
        )


class TestUserNotFound:
    """Tests for missing users."""

    def test_not_found_v1(self):
        """Missing user should return 404 in v1."""
        client = TestClient(app)
        response = client.get("/users/999", headers={"X-API-Version": "1.0"})
        assert response.status_code == 404, (
            f"Expected 404 for missing user, got {response.status_code}"
        )

    def test_not_found_v2(self):
        """Missing user should return 404 in v2."""
        client = TestClient(app)
        response = client.get("/users/999", headers={"X-API-Version": "2.0"})
        assert response.status_code == 404, (
            f"Expected 404 for missing user, got {response.status_code}"
        )
