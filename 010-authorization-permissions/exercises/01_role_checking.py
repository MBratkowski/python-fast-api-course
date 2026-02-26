"""
Exercise 1: Role-Based Access Control

Implement role checking dependencies and admin-only endpoints.

Run: pytest 010-authorization-permissions/exercises/01_role_checking.py -v
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Enum as SQLEnum, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from typing import Annotated
from enum import Enum
import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash


# ============= Setup (provided) =============

class Base(DeclarativeBase):
    pass


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER)


# Pydantic schemas
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: Role


# Database
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

# Auth setup
password_hash = PasswordHash.recommended()
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"


def create_access_token(user: User) -> str:
    """Create JWT token."""
    payload = {
        "sub": user.username,
        "role": user.role.value,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    """Get current user from token (provided)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401)
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401)


@app.post("/auth/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """Login endpoint (provided)."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not password_hash.verify(password, user.hashed_password):
        raise HTTPException(status_code=401)
    return {"access_token": create_access_token(user), "token_type": "bearer"}


# ============= TODO: Exercise 1.1 =============
# Implement require_role dependency factory
# - Accept required_role parameter
# - Return a dependency function
# - Dependency should get current_user via Depends(get_current_user)
# - Check if current_user.role == required_role
# - Raise 403 if not matching
# - Return current_user if authorized

def require_role(required_role: Role):
    """Dependency factory for role checking."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.2 =============
# Implement require_any_role dependency factory
# - Accept list of allowed_roles
# - Return a dependency function
# - Check if current_user.role in allowed_roles
# - Raise 403 if not in list
# - Return current_user if authorized

def require_any_role(allowed_roles: list[Role]):
    """Dependency factory for multiple roles."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.3 =============
# Implement GET /admin/dashboard
# - Use Depends(require_role(Role.ADMIN))
# - Return dict with "message": "Welcome to admin dashboard", "admin": current_user.username

@app.get("/admin/dashboard")
async def admin_dashboard():
    """Admin-only endpoint."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.4 =============
# Implement GET /moderator/reports
# - Use Depends(require_any_role([Role.ADMIN, Role.MODERATOR]))
# - Return dict with "message": "Moderation reports", "moderator": current_user.username

@app.get("/moderator/reports")
async def moderator_reports():
    """Moderator or admin endpoint."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.5 =============
# Implement GET /users
# - Admin-only: Use Depends(require_role(Role.ADMIN))
# - Return list of all users as list[UserResponse]

@app.get("/users")
async def list_users():
    """List all users (admin only)."""
    # TODO: Implement
    pass


# ============= TESTS =============

client = TestClient(app)


def create_user_with_role(username: str, role: Role, db: Session) -> str:
    """Helper: Create user and return token."""
    user = User(
        username=username,
        email=f"{username}@test.com",
        hashed_password=password_hash.hash("password123"),
        role=role
    )
    db.add(user)
    db.commit()
    return create_access_token(user)


def test_admin_can_access_admin_dashboard():
    """Test admin can access admin endpoint."""
    db = next(get_db())
    token = create_user_with_role("admin", Role.ADMIN, db)

    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "admin dashboard" in data["message"].lower()
    assert data["admin"] == "admin"


def test_user_cannot_access_admin_dashboard():
    """Test regular user gets 403 on admin endpoint."""
    db = next(get_db())
    token = create_user_with_role("user", Role.USER, db)

    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_moderator_cannot_access_admin_dashboard():
    """Test moderator gets 403 on admin-only endpoint."""
    db = next(get_db())
    token = create_user_with_role("moderator", Role.MODERATOR, db)

    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_access_moderator_reports():
    """Test admin can access moderator endpoint."""
    db = next(get_db())
    token = create_user_with_role("admin2", Role.ADMIN, db)

    response = client.get(
        "/moderator/reports",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "moderation" in data["message"].lower() or "reports" in data["message"].lower()


def test_moderator_can_access_moderator_reports():
    """Test moderator can access moderator endpoint."""
    db = next(get_db())
    token = create_user_with_role("mod", Role.MODERATOR, db)

    response = client.get(
        "/moderator/reports",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["moderator"] == "mod"


def test_user_cannot_access_moderator_reports():
    """Test regular user gets 403 on moderator endpoint."""
    db = next(get_db())
    token = create_user_with_role("user2", Role.USER, db)

    response = client.get(
        "/moderator/reports",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_list_users():
    """Test admin can list all users."""
    db = next(get_db())
    create_user_with_role("user3", Role.USER, db)
    create_user_with_role("user4", Role.USER, db)
    admin_token = create_user_with_role("admin3", Role.ADMIN, db)

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_user_cannot_list_users():
    """Test regular user gets 403 on list users."""
    db = next(get_db())
    token = create_user_with_role("user5", Role.USER, db)

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
