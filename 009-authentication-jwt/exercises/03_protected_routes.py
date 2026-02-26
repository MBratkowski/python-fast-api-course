"""
Exercise 3: Protecting FastAPI Routes

Build authentication endpoints and protect routes with JWT tokens.

Run: pytest 009-authentication-jwt/exercises/03_protected_routes.py -v
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Boolean, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from typing import Annotated
import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash


# ============= Setup (provided) =============

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# Pydantic schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


# Database setup
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)


def get_db():
    """Database session dependency."""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


# FastAPI app
app = FastAPI()

# Security setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hash = PasswordHash.recommended()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")


def create_access_token(username: str) -> str:
    """Create JWT access token."""
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ============= TODO: Exercise 3.1 =============
# Implement signup endpoint
# - POST /auth/signup
# - Accept UserCreate schema
# - Hash the password with password_hash.hash()
# - Create User in database
# - Return 201 Created with UserResponse (no password in response!)

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create new user account."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.2 =============
# Implement login endpoint
# - POST /auth/login
# - Accept OAuth2PasswordRequestForm (form data, not JSON!)
# - Find user by username
# - Verify password with password_hash.verify()
# - Use DUMMY_HASH for timing attack prevention if user not found
# - Return Token (access_token, token_type="bearer") if valid
# - Return 401 if invalid credentials

@app.post("/auth/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.3 =============
# Implement get_current_user dependency
# - Extract token with Depends(oauth2_scheme)
# - Decode JWT with jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# - Extract username from "sub" claim
# - Load user from database
# - Return user or raise HTTPException 401
# - Handle jwt.InvalidTokenError

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.4 =============
# Implement protected endpoint: GET /users/me
# - Use Depends(get_current_user) to require authentication
# - Return current user as UserResponse

@app.get("/users/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user profile."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.5 =============
# Implement protected endpoint: GET /users/me/items
# - Use Depends(get_current_user) to require authentication
# - Return dict with "items" (empty list) and "owner" (current_user.username)

@app.get("/users/me/items")
async def get_my_items(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user's items."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 009-authentication-jwt/exercises/03_protected_routes.py -v

client = TestClient(app)


def test_signup():
    """Test creating a new user."""
    response = client.post("/auth/signup", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["is_active"] is True
    assert "id" in data


def test_signup_no_password_in_response():
    """Test that signup doesn't return password."""
    response = client.post("/auth/signup", json={
        "username": "bob",
        "email": "bob@example.com",
        "password": "SecurePass456"
    })

    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
    assert "hashed_password" not in data


def test_login_valid_credentials():
    """Test login with valid credentials."""
    # Create user
    client.post("/auth/signup", json={
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "MyPassword123"
    })

    # Login (form data!)
    response = client.post("/auth/login", data={
        "username": "charlie",
        "password": "MyPassword123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 50


def test_login_invalid_password():
    """Test login with wrong password."""
    # Create user
    client.post("/auth/signup", json={
        "username": "dave",
        "email": "dave@example.com",
        "password": "CorrectPassword"
    })

    # Login with wrong password
    response = client.post("/auth/login", data={
        "username": "dave",
        "password": "WrongPassword"
    })

    assert response.status_code == 401


def test_login_unknown_user():
    """Test login with non-existent user."""
    response = client.post("/auth/login", data={
        "username": "unknown",
        "password": "anypassword"
    })

    assert response.status_code == 401


def test_protected_route_without_token():
    """Test accessing protected route without token."""
    response = client.get("/users/me")

    assert response.status_code == 401


def test_protected_route_with_token():
    """Test accessing protected route with valid token."""
    # Create and login
    client.post("/auth/signup", json={
        "username": "eve",
        "email": "eve@example.com",
        "password": "EvePassword123"
    })

    login_response = client.post("/auth/login", data={
        "username": "eve",
        "password": "EvePassword123"
    })
    token = login_response.json()["access_token"]

    # Access protected route
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "eve"
    assert data["email"] == "eve@example.com"


def test_get_my_items():
    """Test getting user's items."""
    # Create and login
    client.post("/auth/signup", json={
        "username": "frank",
        "email": "frank@example.com",
        "password": "FrankPass456"
    })

    login_response = client.post("/auth/login", data={
        "username": "frank",
        "password": "FrankPass456"
    })
    token = login_response.json()["access_token"]

    # Get items
    response = client.get(
        "/users/me/items",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["owner"] == "frank"


def test_invalid_token():
    """Test accessing protected route with invalid token."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token_12345"}
    )

    assert response.status_code == 401
