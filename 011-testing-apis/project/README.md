# Project: Comprehensive CRUD API Test Suite

## Overview

Build a complete test suite for a mini CRUD API with User, Post, and Comment resources. This project tests everything you learned: fixtures, database testing, mocking external services, async tests, and achieving meaningful coverage.

**Goal**: Create a professional test suite with >80% coverage that can run in any order.

## Requirements

### 1. Test Infrastructure (conftest.py)

Create `conftest.py` with shared fixtures:

**Database fixtures:**
- `engine`: Session-scoped in-memory SQLite engine
- `db_session`: Function-scoped session with automatic rollback
- Tables: User, Post, Comment

**Client fixtures:**
- `client`: TestClient with database dependency override
- `auth_client`: Authenticated TestClient (logged-in user)
- `admin_client`: Authenticated TestClient (admin user)

**Data fixtures:**
- `sample_user`: Create and return a test user
- `sample_post`: Create and return a test post
- `sample_comment`: Create and return a test comment

### 2. User API Tests (test_users.py)

**POST /users (signup):**
- ✅ Valid data → 201 Created
- ✅ Duplicate email → 409 Conflict
- ✅ Invalid email → 422 Validation Error
- ✅ Missing required field → 422

**GET /users/{id}:**
- ✅ Existing user → 200 OK
- ✅ Non-existent user → 404 Not Found

**GET /users/me:**
- ✅ Authenticated → 200 OK with current user
- ✅ Unauthenticated → 401 Unauthorized

**PATCH /users/me:**
- ✅ Update email → 200 OK
- ✅ Invalid email → 422
- ✅ Unauthenticated → 401

**DELETE /users/me:**
- ✅ Deactivate account → 204 No Content
- ✅ Unauthenticated → 401

### 3. Post API Tests (test_posts.py)

**POST /posts:**
- ✅ Valid data → 201 Created
- ✅ Missing title → 422
- ✅ Unauthenticated → 401

**GET /posts:**
- ✅ List all posts → 200 OK
- ✅ Empty list → 200 OK with empty array
- ✅ Pagination works (skip/limit)

**GET /posts/{id}:**
- ✅ Existing post → 200 OK
- ✅ Non-existent post → 404

**PUT /posts/{id}:**
- ✅ Update own post → 200 OK
- ✅ Update someone else's post → 403 Forbidden
- ✅ Non-existent post → 404
- ✅ Unauthenticated → 401

**DELETE /posts/{id}:**
- ✅ Delete own post → 204
- ✅ Delete someone else's post → 403
- ✅ Admin can delete any post → 204
- ✅ Non-existent post → 404

### 4. Comment API Tests (test_comments.py)

**POST /posts/{post_id}/comments:**
- ✅ Valid comment → 201 Created
- ✅ Non-existent post → 404
- ✅ Empty content → 422

**GET /posts/{post_id}/comments:**
- ✅ List comments for post → 200 OK
- ✅ Empty list for post with no comments → 200 OK

**DELETE /comments/{id}:**
- ✅ Delete own comment → 204
- ✅ Delete someone else's comment → 403
- ✅ Post author can delete any comment on their post → 204

### 5. External Service Mocking (test_notifications.py)

The API sends email notifications via an external service. Mock these:

**Scenarios to test:**
- ✅ New post created → notification sent (mock successful send)
- ✅ New comment created → notification sent
- ✅ Email service fails (500 error) → handle gracefully
- ✅ Email service timeout → handle gracefully
- ✅ Verify notification was called with correct parameters

### 6. Async Tests (test_async.py)

Test async endpoints using AsyncClient:

- ✅ Concurrent requests to multiple endpoints
- ✅ Async dependency injection
- ✅ Background task execution (async)

## Starter Template

```python
"""
Comprehensive CRUD API Test Suite Project
TODO: Build complete test coverage for User, Post, Comment APIs
"""

import pytest
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.testclient import TestClient
from sqlalchemy import String, Text, ForeignKey, Boolean, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import List

# ============= Database Models =============

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    posts: Mapped[List["Post"]] = relationship(back_populates="author")
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")

# ============= Pydantic Schemas =============

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    is_admin: bool

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    author_id: int

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    post_id: int
    author_id: int

# ============= External Service (TO BE MOCKED) =============

async def send_notification(recipient: str, message: str):
    """Send email notification (to be mocked in tests)."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.emailservice.example.com/send",
            json={"to": recipient, "message": message},
            timeout=5.0
        )
        response.raise_for_status()

# ============= Database Dependency =============

def get_db():
    """Database dependency (override in tests)."""
    raise NotImplementedError("Override in tests")

# ============= Auth Dependency (Simplified) =============

def get_current_user(db: Session = Depends(get_db)) -> User:
    """Get current user (simplified for this project)."""
    # In real app: decode JWT, verify token, fetch user
    # For this project: return first user from database
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# ============= FastAPI App =============

app = FastAPI()

# ============= User Endpoints =============

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user."""
    # TODO: Implement (check duplicate email, create user)
    pass

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    # TODO: Implement
    pass

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    # TODO: Implement
    pass

# ============= Post Endpoints =============

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(
    post: PostCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new post."""
    # TODO: Implement (create post, send notification in background)
    pass

@app.get("/posts", response_model=List[PostResponse])
async def list_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List posts with pagination."""
    # TODO: Implement
    pass

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get post by ID."""
    # TODO: Implement
    pass

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update post (owner only)."""
    # TODO: Implement (check ownership)
    pass

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete post (owner or admin)."""
    # TODO: Implement (check ownership or admin)
    pass

# ============= Comment Endpoints =============

@app.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create comment on post."""
    # TODO: Implement
    pass

@app.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def list_comments(post_id: int, db: Session = Depends(get_db)):
    """List comments for post."""
    # TODO: Implement
    pass

@app.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete comment (author or post owner)."""
    # TODO: Implement
    pass

# ============= TODO: Create Tests =============

# tests/conftest.py - Shared fixtures
# tests/test_users.py - User API tests
# tests/test_posts.py - Post API tests
# tests/test_comments.py - Comment API tests
# tests/test_notifications.py - Mocked external service tests
# tests/test_async.py - Async tests with AsyncClient
```

## Success Criteria

- [ ] All endpoints have happy path tests
- [ ] All endpoints have error case tests (404, 422, 401, 403)
- [ ] Authorization is tested (own resources vs others' resources)
- [ ] Database isolation works (tests can run in any order)
- [ ] External email service is mocked (no real API calls)
- [ ] Test coverage >80%
- [ ] All tests pass with `pytest -v`
- [ ] conftest.py has reusable fixtures
- [ ] Tests use descriptive names

## Stretch Goals

1. **Pagination testing**: Test skip/limit edge cases (negative, zero, large numbers)
2. **Search functionality**: Add search endpoint for posts, test it
3. **Rate limiting**: Add rate limiting, test it with multiple rapid requests
4. **Soft delete**: Instead of deleting posts, mark as deleted, test visibility
5. **Comment threading**: Add parent_id to comments for replies, test nested structure
6. **Performance tests**: Test response time for list endpoints with large datasets
7. **Concurrent requests**: Use AsyncClient to test concurrent post creation
8. **Idempotency**: Test that duplicate requests don't create duplicate resources

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_users.py -v

# Run specific test
pytest tests/test_users.py::test_create_user_success -v

# Run with output (see print statements)
pytest tests/ -v -s
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing best practices](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#session-testing-strategies)
