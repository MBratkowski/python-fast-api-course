"""
Exercise 1: URL Path Versioning

In this exercise, you'll create URL path versioning using FastAPI's APIRouter
with separate routers for v1 and v2.

Your tasks:
1. Create a v1_router with prefix "/v1"
2. Create a v2_router with prefix "/v2"
3. Add GET /users/{user_id} to v1_router that returns a flat response:
   {"id": user_id, "name": "Alice"}
4. Add GET /users/{user_id} to v2_router that returns a wrapped response:
   {"data": {"id": user_id, "name": "Alice", "email": "alice@example.com"}, "meta": {"version": "2.0"}}
5. Include both routers in the app

Mobile analogy: This is like supporting iOS 16 and iOS 17 with different
UI implementations but the same underlying data model.

Run: pytest 022-api-versioning/exercises/01_url_versioning.py -v
"""

from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient


# Simulated user data (shared between versions)
USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}


# ============= TODO 1: Create v1 router =============
# Create an APIRouter with prefix="/v1" and tags=["v1"]
# Add a GET /users/{user_id} endpoint that returns:
#   {"id": <user_id>, "name": "<name>"}
# Return 404 if user not found
#
# Hints:
# - v1_router = APIRouter(prefix="/v1", tags=["v1"])
# - Use @v1_router.get("/users/{user_id}") decorator
# - Look up user in USERS dict
# - Use HTTPException(status_code=404) for missing users


# TODO: Create v1_router and its endpoint


# ============= TODO 2: Create v2 router =============
# Create an APIRouter with prefix="/v2" and tags=["v2"]
# Add a GET /users/{user_id} endpoint that returns:
#   {
#     "data": {"id": <user_id>, "name": "<name>", "email": "<email>"},
#     "meta": {"version": "2.0"}
#   }
# Return 404 if user not found


# TODO: Create v2_router and its endpoint


# ============= TODO 3: Create app and include routers =============
# Create a FastAPI app and include both routers
#
# Hints:
# - app = FastAPI()
# - app.include_router(v1_router)
# - app.include_router(v2_router)

app = FastAPI()

# TODO: Include v1_router and v2_router in the app


# ============= TESTS (do not modify below) =============


class TestV1Router:
    """Tests for v1 API endpoints."""

    def test_v1_get_user_returns_200(self):
        """GET /v1/users/1 should return 200."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            "Create a v1_router with prefix='/v1' and a GET /users/{{user_id}} endpoint."
        )

    def test_v1_returns_flat_response(self):
        """V1 should return a flat response with id and name."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        data = response.json()
        assert data.get("id") == 1, (
            f'Expected "id": 1, got {data}. V1 should return a flat dict with id and name.'
        )
        assert data.get("name") == "Alice", (
            f'Expected "name": "Alice", got {data}'
        )

    def test_v1_does_not_include_email(self):
        """V1 should NOT include email in the response."""
        client = TestClient(app)
        response = client.get("/v1/users/1")
        data = response.json()
        assert "email" not in data, (
            "V1 should NOT include email. Return only id and name."
        )

    def test_v1_user_not_found(self):
        """GET /v1/users/999 should return 404."""
        client = TestClient(app)
        response = client.get("/v1/users/999")
        assert response.status_code == 404, (
            f"Expected 404 for non-existent user, got {response.status_code}"
        )

    def test_v1_second_user(self):
        """V1 should work for different users."""
        client = TestClient(app)
        response = client.get("/v1/users/2")
        data = response.json()
        assert data.get("id") == 2
        assert data.get("name") == "Bob"


class TestV2Router:
    """Tests for v2 API endpoints."""

    def test_v2_get_user_returns_200(self):
        """GET /v2/users/1 should return 200."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            "Create a v2_router with prefix='/v2' and a GET /users/{{user_id}} endpoint."
        )

    def test_v2_returns_wrapped_response(self):
        """V2 should return a wrapped response with data and meta."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        data = response.json()
        assert "data" in data, (
            'V2 response should have a "data" key wrapping the user object.'
        )
        assert "meta" in data, (
            'V2 response should have a "meta" key with version info.'
        )

    def test_v2_data_includes_email(self):
        """V2 data should include id, name, and email."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        user_data = response.json()["data"]
        assert user_data.get("id") == 1
        assert user_data.get("name") == "Alice"
        assert user_data.get("email") == "alice@example.com", (
            "V2 data should include email. "
            'Expected "alice@example.com".'
        )

    def test_v2_meta_has_version(self):
        """V2 meta should include version "2.0"."""
        client = TestClient(app)
        response = client.get("/v2/users/1")
        meta = response.json()["meta"]
        assert meta.get("version") == "2.0", (
            f'Expected meta.version "2.0", got {meta}'
        )

    def test_v2_user_not_found(self):
        """GET /v2/users/999 should return 404."""
        client = TestClient(app)
        response = client.get("/v2/users/999")
        assert response.status_code == 404, (
            f"Expected 404 for non-existent user, got {response.status_code}"
        )


class TestBothVersions:
    """Tests that verify both versions coexist correctly."""

    def test_same_user_different_format(self):
        """Both versions should return the same user but in different formats."""
        client = TestClient(app)
        v1 = client.get("/v1/users/1").json()
        v2 = client.get("/v2/users/1").json()

        # Same underlying data
        assert v1["id"] == v2["data"]["id"], (
            "Both versions should return the same user ID."
        )
        assert v1["name"] == v2["data"]["name"], (
            "Both versions should return the same user name."
        )
