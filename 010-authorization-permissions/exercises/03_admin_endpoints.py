"""
Exercise 3: Admin-Only Endpoints

Build an admin panel with user management endpoints.

Run: pytest 010-authorization-permissions/exercises/03_admin_endpoints.py -v
"""

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy import String, Boolean, Enum as SQLEnum, create_engine
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
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: Role
    is_active: bool


class RoleUpdate(BaseModel):
    role: str  # "user" or "moderator" (NOT "admin")


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
    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401)
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401)


def require_role(required_role: Role):
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role != required_role:
            raise HTTPException(status_code=403)
        return current_user
    return role_checker


# Regular user endpoints (provided)
@app.get("/users/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


# ============= TODO: Exercise 3.1 =============
# Create admin router with admin dependency
# - prefix="/admin"
# - tags=["admin"]
# - dependencies=[Depends(require_role(Role.ADMIN))]
# This makes ALL routes in this router require admin role

# TODO: Create admin_router


# ============= TODO: Exercise 3.2 =============
# Implement GET /admin/users
# - Add to admin_router
# - Return list of all users as list[UserResponse]
# - Include is_active and role fields

# TODO: Implement (don't forget @admin_router decorator!)


# ============= TODO: Exercise 3.3 =============
# Implement PATCH /admin/users/{user_id}/role
# - Add to admin_router
# - Accept RoleUpdate schema
# - Prevent changing own role (if user_id == current_user.id, raise 403)
# - Prevent setting role to "admin" (privilege escalation guard)
# - Update user role to MODERATOR or USER
# - Return updated UserResponse

# TODO: Implement


# ============= TODO: Exercise 3.4 =============
# Implement PATCH /admin/users/{user_id}/activate
# - Add to admin_router
# - Toggle user's is_active status (True <-> False)
# - Return updated UserResponse

# TODO: Implement


# ============= TODO: Exercise 3.5 =============
# Implement GET /admin/stats
# - Add to admin_router
# - Return dict with:
#   - "total_users": count of all users
#   - "active_users": count where is_active=True
#   - "users_by_role": dict mapping role to count {"admin": 1, "user": 5, "moderator": 2}

# TODO: Implement


# Include admin router in app
# TODO: app.include_router(admin_router)


# ============= TESTS =============

client = TestClient(app)


def create_user(username: str, role: Role = Role.USER) -> tuple[int, str]:
    db = next(get_db())
    user = User(
        username=username,
        email=f"{username}@test.com",
        hashed_password=password_hash.hash("password123"),
        role=role
    )
    db.add(user)
    db.commit()
    user_id = user.id
    token = create_access_token(user)
    return user_id, token


def test_admin_can_list_all_users():
    create_user("user1")
    create_user("user2")
    _, admin_token = create_user("admin", Role.ADMIN)

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_non_admin_gets_403_on_admin_routes():
    _, user_token = create_user("user")

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 403


def test_admin_can_change_user_role():
    user_id, _ = create_user("user3")
    _, admin_token = create_user("admin2", Role.ADMIN)

    response = client.patch(
        f"/admin/users/{user_id}/role",
        json={"role": "moderator"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.json()["role"] == "moderator"


def test_admin_cannot_set_role_to_admin():
    user_id, _ = create_user("user4")
    _, admin_token = create_user("admin3", Role.ADMIN)

    response = client.patch(
        f"/admin/users/{user_id}/role",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 403


def test_admin_cannot_change_own_role():
    admin_id, admin_token = create_user("admin4", Role.ADMIN)

    response = client.patch(
        f"/admin/users/{admin_id}/role",
        json={"role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 403


def test_admin_can_deactivate_user():
    user_id, _ = create_user("user5")
    _, admin_token = create_user("admin5", Role.ADMIN)

    response = client.patch(
        f"/admin/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_admin_can_reactivate_user():
    user_id, _ = create_user("user6")
    _, admin_token = create_user("admin6", Role.ADMIN)

    # Deactivate
    client.patch(
        f"/admin/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Reactivate
    response = client.patch(
        f"/admin/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_admin_can_view_stats():
    create_user("user7")
    create_user("user8")
    create_user("mod", Role.MODERATOR)
    _, admin_token = create_user("admin7", Role.ADMIN)

    response = client.get(
        "/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "active_users" in data
    assert "users_by_role" in data
    assert data["total_users"] >= 4
    assert isinstance(data["users_by_role"], dict)
