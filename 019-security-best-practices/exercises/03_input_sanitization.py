"""
Exercise 3: Input Sanitization

Add Pydantic validators, Field constraints, and bleach sanitization to
protect against malicious input.

Run: pytest 019-security-best-practices/exercises/03_input_sanitization.py -v
"""

import re

import bleach
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, field_validator

# ============= APP SETUP =============

app = FastAPI()


# ============= TODO: Exercise 3.1 -- Username Validation =============
# Create a Pydantic model UserCreate with:
# - username: str, min 3 chars, max 50 chars
#   Add a field_validator that only allows alphanumeric characters and underscores
#   (regex: ^[a-zA-Z0-9_]+$)
# - email: str, max 254 chars
#   Add a field_validator that checks basic email format
#   (regex: ^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)
#   Also normalize to lowercase
# - bio: str, default "", max 500 chars
#   Add a field_validator that strips ALL HTML tags using bleach.clean(v, tags=[], strip=True)
#
# Hints:
# - Use Field(..., min_length=3, max_length=50) for constraints
# - Use @field_validator("field_name") with @classmethod
# - Raise ValueError for validation failures


class UserCreate(BaseModel):
    """TODO: Add fields with proper validation and sanitization."""

    # TODO: Add username field with constraints and validator
    # TODO: Add email field with constraints and validator
    # TODO: Add bio field with constraints and sanitizer
    pass


@app.post("/users")
async def create_user(user: UserCreate):
    return {
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
    }


# ============= TODO: Exercise 3.2 -- Comment Sanitization =============
# Create a Pydantic model CommentCreate with:
# - content: str, min 1 char, max 1000 chars
#   Add a field_validator that uses bleach.clean() to allow only safe tags:
#   allowed tags: ["p", "br", "strong", "em"]
#   strip=True to remove disallowed tags entirely
# - author_name: str, min 1 char, max 100 chars
#   Add a field_validator that strips ALL HTML (tags=[], strip=True)
#
# Hints:
# - bleach.clean(v, tags=["p", "br", "strong", "em"], strip=True)


class CommentCreate(BaseModel):
    """TODO: Add fields with HTML sanitization."""

    # TODO: Add content field with selective HTML sanitization
    # TODO: Add author_name field with full HTML stripping
    pass


@app.post("/comments")
async def create_comment(comment: CommentCreate):
    return {
        "content": comment.content,
        "author_name": comment.author_name,
    }


# ============= TODO: Exercise 3.3 -- Search Query Validation =============
# Create a Pydantic model SearchQuery with:
# - q: str, min 1 char, max 200 chars
#   Add a field_validator that rejects common SQL injection patterns:
#   Reject if the query contains (case-insensitive): "';", "--", "/*", "*/"
#   "UNION SELECT", "DROP TABLE", "DELETE FROM", "INSERT INTO"
#   Raise ValueError("Invalid characters in search query")
# - limit: int, default 20, must be between 1 and 100 (use Field ge/le)
# - offset: int, default 0, must be >= 0 (use Field ge)
#
# Hints:
# - Check v.upper() against uppercase patterns
# - Use Field(default=20, ge=1, le=100) for limit


class SearchQuery(BaseModel):
    """TODO: Add fields with SQL injection pattern rejection."""

    # TODO: Add q field with SQL injection pattern validator
    # TODO: Add limit field with bounds
    # TODO: Add offset field with lower bound
    pass


@app.get("/search")
async def search(params: SearchQuery):
    return {
        "query": params.q,
        "limit": params.limit,
        "offset": params.offset,
    }


# ============= TESTS =============

client = TestClient(app)


# --- Tests for Exercise 3.1: Username Validation ---


def test_valid_user_creation():
    """Valid input should succeed."""
    response = client.post("/users", json={
        "username": "alice_123",
        "email": "Alice@Example.COM",
        "bio": "Hello world",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice_123"
    assert data["email"] == "alice@example.com"  # Normalized to lowercase
    assert data["bio"] == "Hello world"


def test_username_rejects_special_characters():
    """Username with special characters should be rejected."""
    response = client.post("/users", json={
        "username": "alice<script>",
        "email": "alice@example.com",
    })
    assert response.status_code == 422


def test_username_rejects_spaces():
    """Username with spaces should be rejected."""
    response = client.post("/users", json={
        "username": "alice smith",
        "email": "alice@example.com",
    })
    assert response.status_code == 422


def test_username_too_short():
    """Username shorter than 3 chars should be rejected."""
    response = client.post("/users", json={
        "username": "ab",
        "email": "alice@example.com",
    })
    assert response.status_code == 422


def test_email_invalid_format():
    """Invalid email format should be rejected."""
    response = client.post("/users", json={
        "username": "alice",
        "email": "not-an-email",
    })
    assert response.status_code == 422


def test_bio_html_stripped():
    """HTML in bio should be completely stripped."""
    response = client.post("/users", json={
        "username": "alice",
        "email": "alice@example.com",
        "bio": "<script>alert('xss')</script>Hello <b>world</b>",
    })
    assert response.status_code == 200
    data = response.json()
    assert "<script>" not in data["bio"]
    assert "<b>" not in data["bio"]
    assert "Hello" in data["bio"]
    assert "world" in data["bio"]


# --- Tests for Exercise 3.2: Comment Sanitization ---


def test_comment_allows_safe_html():
    """Safe HTML tags should be preserved in content."""
    response = client.post("/comments", json={
        "content": "<p>Hello <strong>world</strong></p>",
        "author_name": "Alice",
    })
    assert response.status_code == 200
    data = response.json()
    assert "<p>" in data["content"]
    assert "<strong>" in data["content"]


def test_comment_strips_script_tags():
    """Script tags should be stripped from content."""
    response = client.post("/comments", json={
        "content": "<p>Hello</p><script>alert('xss')</script>",
        "author_name": "Alice",
    })
    assert response.status_code == 200
    data = response.json()
    assert "<script>" not in data["content"]
    assert "<p>Hello</p>" in data["content"]


def test_comment_strips_html_from_author():
    """ALL HTML should be stripped from author_name."""
    response = client.post("/comments", json={
        "content": "<p>Hello</p>",
        "author_name": "<b>Alice</b>",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["author_name"] == "Alice"
    assert "<b>" not in data["author_name"]


def test_comment_content_max_length():
    """Content exceeding max length should be rejected."""
    response = client.post("/comments", json={
        "content": "x" * 1001,
        "author_name": "Alice",
    })
    assert response.status_code == 422


# --- Tests for Exercise 3.3: Search Query Validation ---


def test_valid_search():
    """Valid search query should succeed."""
    response = client.get("/search", params={
        "q": "python fastapi",
        "limit": 10,
        "offset": 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "python fastapi"
    assert data["limit"] == 10


def test_search_rejects_sql_injection_union():
    """UNION SELECT pattern should be rejected."""
    response = client.get("/search", params={
        "q": "test' UNION SELECT * FROM users --",
    })
    assert response.status_code == 422


def test_search_rejects_sql_injection_drop():
    """DROP TABLE pattern should be rejected."""
    response = client.get("/search", params={
        "q": "test'; DROP TABLE users; --",
    })
    assert response.status_code == 422


def test_search_rejects_sql_comment():
    """SQL comment patterns should be rejected."""
    response = client.get("/search", params={
        "q": "test /* comment */",
    })
    assert response.status_code == 422


def test_search_limit_max():
    """Limit exceeding 100 should be rejected."""
    response = client.get("/search", params={
        "q": "test",
        "limit": 200,
    })
    assert response.status_code == 422


def test_search_limit_default():
    """Default limit should be 20."""
    response = client.get("/search", params={"q": "test"})
    assert response.status_code == 200
    assert response.json()["limit"] == 20


def test_search_offset_negative():
    """Negative offset should be rejected."""
    response = client.get("/search", params={
        "q": "test",
        "offset": -1,
    })
    assert response.status_code == 422
