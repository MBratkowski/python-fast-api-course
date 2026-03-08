"""
Exercise 1: Identify and Fix Security Vulnerabilities

This FastAPI app has multiple OWASP API Security vulnerabilities:
- Broken Object Level Authorization (BOLA)
- Mass Assignment
- Excessive Data Exposure

Your job: Fix the vulnerable endpoints by implementing proper security.

Run: pytest 019-security-best-practices/exercises/01_identify_vulnerabilities.py -v
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

# ============= SIMULATED DATABASE =============

# In-memory "database" for this exercise
users_db: dict[int, dict] = {
    1: {
        "id": 1,
        "username": "alice",
        "email": "alice@example.com",
        "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$hash_alice",
        "is_admin": False,
        "bio": "I love coding",
    },
    2: {
        "id": 2,
        "username": "bob",
        "email": "bob@example.com",
        "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$hash_bob",
        "is_admin": False,
        "bio": "Backend developer",
    },
    3: {
        "id": 3,
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$hash_admin",
        "is_admin": True,
        "bio": "System administrator",
    },
}

orders_db: dict[int, dict] = {
    1: {"id": 1, "user_id": 1, "item": "Laptop", "amount": 999.99},
    2: {"id": 2, "user_id": 1, "item": "Mouse", "amount": 29.99},
    3: {"id": 3, "user_id": 2, "item": "Keyboard", "amount": 79.99},
}


# Simulated "current user" dependency (pretend JWT auth happened)
def get_current_user() -> dict:
    """Simulate an authenticated user (user_id=1, alice)."""
    return users_db[1]


# ============= SCHEMAS =============

# These schemas are used by the VULNERABLE endpoints.
# You will create SECURE schemas for your fixed endpoints.


class UserUpdateVulnerable(BaseModel):
    """VULNERABLE: Accepts any field including is_admin."""

    username: str | None = None
    email: str | None = None
    bio: str | None = None
    is_admin: bool | None = None  # This should NOT be here!


# ============= APP SETUP =============

app = FastAPI()


# ============= VULNERABLE ENDPOINTS (for reference) =============
# These show the vulnerabilities. DO NOT modify them.


@app.get("/vulnerable/users/{user_id}")
async def get_user_vulnerable(user_id: int):
    """VULNERABLE: Returns ALL fields including password_hash."""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user  # Exposes password_hash!


@app.get("/vulnerable/orders/{order_id}")
async def get_order_vulnerable(order_id: int):
    """VULNERABLE: No ownership check -- any user can see any order (BOLA)."""
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@app.put("/vulnerable/users/me")
async def update_user_vulnerable(
    data: UserUpdateVulnerable,
    current_user: dict = Depends(get_current_user),
):
    """VULNERABLE: Accepts is_admin field -- mass assignment!"""
    update_data = data.model_dump(exclude_unset=True)
    users_db[current_user["id"]].update(update_data)
    return users_db[current_user["id"]]


# ============= TODO: Exercise 1.1 -- Fix Excessive Data Exposure =============
# Create a GET endpoint at /secure/users/{user_id} that:
# - Returns user data WITHOUT exposing password_hash or is_admin
# - Uses a Pydantic response model (UserResponse) that only includes:
#   id, username, email, bio
# - Returns 404 if user not found
#
# Hints:
# - Create a UserResponse schema with only safe fields
# - Use model_config = ConfigDict(from_attributes=True) is not needed here
#   since we're working with dicts, just return a dict with only safe fields
# - Or construct UserResponse manually from the database dict


class UserResponse(BaseModel):
    """TODO: Define a response model with only safe fields."""

    # TODO: Add fields: id, username, email, bio
    pass


@app.get("/secure/users/{user_id}")
async def get_user_secure(user_id: int):
    """Return user data without exposing sensitive fields."""
    # TODO: Implement -- look up user, return only safe fields
    pass


# ============= TODO: Exercise 1.2 -- Fix BOLA (Broken Object Level Auth) =============
# Create a GET endpoint at /secure/orders/{order_id} that:
# - Only returns the order if it belongs to the current user
# - Uses Depends(get_current_user) to get the authenticated user
# - Returns 404 if order not found OR if it belongs to another user
#   (returning 404 instead of 403 prevents information leakage)
#
# Hints:
# - Compare order["user_id"] with current_user["id"]
# - Use the same 404 message for "not found" and "not yours"


@app.get("/secure/orders/{order_id}")
async def get_order_secure(
    order_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Return order only if it belongs to the current user."""
    # TODO: Implement -- check ownership before returning
    pass


# ============= TODO: Exercise 1.3 -- Fix Mass Assignment =============
# Create a PUT endpoint at /secure/users/me that:
# - Only allows updating username, email, and bio
# - Does NOT allow setting is_admin (not in schema at all)
# - Uses a strict Pydantic model (UserUpdateSecure) for input
# - Returns the updated user using UserResponse (no sensitive fields)
#
# Hints:
# - Create UserUpdateSecure with only: username, email, bio (all optional)
# - Use model_dump(exclude_unset=True) to only update provided fields
# - Return UserResponse to avoid exposing sensitive data


class UserUpdateSecure(BaseModel):
    """TODO: Define an update model WITHOUT is_admin."""

    # TODO: Add fields: username, email, bio (all optional)
    pass


@app.put("/secure/users/me")
async def update_user_secure(
    data: UserUpdateSecure,
    current_user: dict = Depends(get_current_user),
):
    """Update user profile without allowing mass assignment."""
    # TODO: Implement -- update only allowed fields, return safe response
    pass


# ============= TESTS =============

client = TestClient(app)


# --- Tests for Exercise 1.1: Excessive Data Exposure ---


def test_vulnerable_endpoint_exposes_password():
    """The vulnerable endpoint leaks password_hash (this is the bug)."""
    response = client.get("/vulnerable/users/1")
    assert response.status_code == 200
    assert "password_hash" in response.json()  # BAD!


def test_secure_endpoint_hides_password():
    """The secure endpoint should NOT expose password_hash."""
    response = client.get("/secure/users/1")
    assert response.status_code == 200
    data = response.json()
    assert "password_hash" not in data
    assert "is_admin" not in data
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["bio"] == "I love coding"
    assert data["id"] == 1


def test_secure_endpoint_returns_404_for_missing_user():
    """The secure endpoint returns 404 for non-existent users."""
    response = client.get("/secure/users/999")
    assert response.status_code == 404


# --- Tests for Exercise 1.2: BOLA ---


def test_vulnerable_endpoint_allows_bola():
    """The vulnerable endpoint lets alice see bob's order (this is the bug)."""
    response = client.get("/vulnerable/orders/3")  # Bob's order
    assert response.status_code == 200  # BAD! Alice can see it


def test_secure_endpoint_blocks_bola():
    """Alice should NOT be able to see Bob's order."""
    response = client.get("/secure/orders/3")  # Bob's order
    assert response.status_code == 404  # Returns 404 (not 403) to prevent info leakage


def test_secure_endpoint_allows_own_orders():
    """Alice CAN see her own orders."""
    response = client.get("/secure/orders/1")  # Alice's order
    assert response.status_code == 200
    data = response.json()
    assert data["item"] == "Laptop"
    assert data["user_id"] == 1


def test_secure_endpoint_returns_404_for_missing_order():
    """Non-existent orders return 404."""
    response = client.get("/secure/orders/999")
    assert response.status_code == 404


# --- Tests for Exercise 1.3: Mass Assignment ---


def test_vulnerable_endpoint_allows_admin_escalation():
    """The vulnerable endpoint lets users set is_admin (this is the bug)."""
    response = client.put(
        "/vulnerable/users/me",
        json={"is_admin": True},
    )
    assert response.status_code == 200
    assert response.json()["is_admin"] is True  # BAD!

    # Reset for other tests
    users_db[1]["is_admin"] = False


def test_secure_endpoint_blocks_admin_escalation():
    """The secure endpoint should ignore is_admin field entirely."""
    response = client.put(
        "/secure/users/me",
        json={"username": "alice_updated", "is_admin": True},
    )
    assert response.status_code == 200
    data = response.json()
    # is_admin should not be in the response (using UserResponse)
    assert "is_admin" not in data
    # The username should be updated
    assert data["username"] == "alice_updated"
    # Verify in "database" that is_admin was NOT changed
    assert users_db[1]["is_admin"] is False

    # Reset for other tests
    users_db[1]["username"] = "alice"


def test_secure_endpoint_updates_allowed_fields():
    """The secure endpoint allows updating bio."""
    response = client.put(
        "/secure/users/me",
        json={"bio": "Updated bio"},
    )
    assert response.status_code == 200
    assert response.json()["bio"] == "Updated bio"

    # Reset
    users_db[1]["bio"] = "I love coding"


def test_secure_endpoint_response_hides_sensitive_fields():
    """The update response should use UserResponse (no password_hash)."""
    response = client.put(
        "/secure/users/me",
        json={"bio": "test"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "password_hash" not in data
    assert "is_admin" not in data

    # Reset
    users_db[1]["bio"] = "I love coding"
