# Project: Complete Authentication System

## Overview

Build a production-ready authentication system for a FastAPI application with signup, login, token refresh, and logout functionality. This project combines everything you learned about password hashing, JWT tokens, and OAuth2.

**Goal**: Implement secure user authentication with access and refresh tokens.

## Requirements

### 1. User Model

Create a SQLAlchemy User model with:
- `id`: Primary key
- `username`: Unique, indexed
- `email`: Unique, indexed
- `hashed_password`: Store hashed passwords (never plain text!)
- `is_active`: Boolean, default True
- `created_at`: Timestamp

### 2. RefreshToken Model

Create a SQLAlchemy RefreshToken model for token storage:
- `id`: Primary key
- `user_id`: Foreign key to users table
- `token`: Unique refresh token string
- `expires_at`: Expiration timestamp
- `is_revoked`: Boolean, default False

### 3. Authentication Endpoints

**POST /auth/signup**
- Accept: `UserCreate` schema (username, email, password)
- Hash password with pwdlib/Argon2
- Create user in database
- Return: `UserResponse` (no password in response!)
- Status: 201 Created

**POST /auth/login**
- Accept: `OAuth2PasswordRequestForm` (form data)
- Verify username and password
- Implement timing attack prevention
- Create access token (30 min expiration)
- Create refresh token (7 days expiration)
- Store refresh token in database
- Return: `{"access_token": str, "refresh_token": str, "token_type": "bearer"}`
- Status: 200 OK or 401 Unauthorized

**POST /auth/refresh**
- Accept: `{"refresh_token": str}`
- Verify refresh token (signature, expiration, not revoked)
- Issue new access token
- Optionally: Rotate refresh token (issue new one, revoke old one)
- Return: `{"access_token": str, "token_type": "bearer"}`
- Status: 200 OK or 401 Unauthorized

**POST /auth/logout**
- Accept: Refresh token
- Require authentication (current user from access token)
- Revoke refresh token in database
- Return: `{"message": "Logged out successfully"}`
- Status: 200 OK

### 4. Protected User Endpoints

**GET /users/me**
- Require authentication (Depends on get_current_user)
- Return: Current user profile as `UserResponse`

**PATCH /users/me**
- Require authentication
- Accept: `UserUpdate` schema (email, optional)
- Update user profile
- Return: Updated `UserResponse`

**DELETE /users/me**
- Require authentication
- Deactivate user account (set `is_active = False`)
- Don't actually delete from database
- Return: 204 No Content

### 5. Security Requirements

- **Password hashing**: Use pwdlib with Argon2
- **Access tokens**: Expire in 30 minutes
- **Refresh tokens**: Expire in 7 days
- **Timing attack prevention**: Always hash password even for invalid usernames
- **Token storage**: Store refresh tokens in database with expiration
- **Logout**: Revoke refresh tokens on logout

## Success Criteria

- [ ] Users can signup with username, email, and password
- [ ] Passwords are hashed with Argon2 (never stored plain text)
- [ ] Users can login and receive access + refresh tokens
- [ ] Protected routes require valid access token
- [ ] Access token expires after 30 minutes
- [ ] Users can refresh access token with refresh token
- [ ] Users can logout (refresh token revoked)
- [ ] Deactivated users cannot login
- [ ] All endpoints return appropriate status codes
- [ ] No timing attacks (constant-time authentication)

## Starter Template

```python
"""
Complete Authentication System
TODO: Implement all endpoints and authentication logic
"""

from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy import String, Boolean, DateTime, create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

# ============= Configuration =============

SECRET_KEY = "your-secret-key-here"  # TODO: Generate with openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ============= Database Models =============

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


# ============= Pydantic Schemas =============

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


# ============= Database Setup =============

engine = create_engine("sqlite:///./auth.db")
Base.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


# ============= Security Setup =============

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")

# ============= Auth Utilities =============

def create_access_token(username: str) -> str:
    """Create JWT access token."""
    # TODO: Implement
    pass


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token."""
    # TODO: Implement
    pass


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    # TODO: Implement
    pass


# ============= FastAPI App =============

app = FastAPI(title="Authentication System")

# ============= Auth Endpoints =============

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create new user account."""
    # TODO: Implement
    pass


@app.post("/auth/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """Login and get tokens."""
    # TODO: Implement
    pass


@app.post("/auth/refresh")
async def refresh(refresh_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token."""
    # TODO: Implement
    pass


@app.post("/auth/logout")
async def logout(
    refresh_data: TokenRefresh,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Logout and revoke refresh token."""
    # TODO: Implement
    pass


# ============= User Endpoints =============

@app.get("/users/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user profile."""
    # TODO: Implement
    pass


@app.patch("/users/me", response_model=UserResponse)
async def update_me(
    updates: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    # TODO: Implement
    pass


@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Deactivate current user account."""
    # TODO: Implement
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Testing Your Implementation

```python
from fastapi.testclient import TestClient

client = TestClient(app)

# Test signup
response = client.post("/auth/signup", json={
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePass123"
})
assert response.status_code == 201

# Test login
response = client.post("/auth/login", data={
    "username": "alice",
    "password": "SecurePass123"
})
assert response.status_code == 200
tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

# Test protected route
response = client.get(
    "/users/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
assert response.status_code == 200

# Test refresh
response = client.post("/auth/refresh", json={
    "refresh_token": refresh_token
})
assert response.status_code == 200
new_access_token = response.json()["access_token"]

# Test logout
response = client.post(
    "/auth/logout",
    json={"refresh_token": refresh_token},
    headers={"Authorization": f"Bearer {access_token}"}
)
assert response.status_code == 200
```

## Stretch Goals

1. **Email verification**: Send verification email on signup, require email verification before login
2. **Password reset**: Add forgot password endpoint with email-based reset link
3. **Remember me**: Support longer refresh token expiration for "remember me" option
4. **Rate limiting**: Add login rate limiting to prevent brute force attacks
5. **Password requirements**: Enforce password complexity (length, special chars, etc.)
6. **2FA**: Add two-factor authentication with TOTP (Google Authenticator)
7. **OAuth2 scopes**: Implement scope-based permissions in tokens
8. **Session management**: Show user's active sessions and allow revoking specific sessions

## Resources

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [pwdlib Documentation](https://github.com/frankie567/pwdlib)
- [OAuth2 Password Flow](https://oauth.net/2/grant-types/password/)
