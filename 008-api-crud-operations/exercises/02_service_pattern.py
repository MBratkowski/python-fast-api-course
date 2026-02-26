"""
Exercise 2: Implement Service Layer Pattern

Refactor database logic into a service layer, keeping routes thin.

Run: pytest 008-api-crud-operations/exercises/02_service_pattern.py -v
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# ============= Models and Schemas (provided) =============

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)


class UserCreate(BaseModel):
    username: str
    email: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


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


# ============= TODO: Exercise 2.1 =============
# Create UserService class with these methods:
#
# - create(user_data: UserCreate) -> User
#   - Check if username exists, raise ValueError if taken
#   - Check if email exists, raise ValueError if taken
#   - Create and return user
#
# - get_by_id(user_id: int) -> User | None
#   - Get user by ID, return None if not found
#
# - get_by_username(username: str) -> User | None
#   - Get user by username, return None if not found
#
# - list(skip: int = 0, limit: int = 100) -> list[User]
#   - List users with pagination
#
# - update(user_id: int, user_data: UserUpdate) -> User | None
#   - Update user fields (only provided fields)
#   - Return None if user not found
#
# - delete(user_id: int) -> bool
#   - Delete user
#   - Return True if deleted, False if not found

class UserService:
    """Service layer for user operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db

    # TODO: Implement all methods
    pass


# ============= TODO: Exercise 2.2 =============
# Create get_user_service dependency function
# - Accept db: Session = Depends(get_db)
# - Return UserService(db)

def get_user_service(db: Session = Depends(get_db)):
    """Provide UserService dependency."""
    # TODO: Implement
    pass


# ============= Routes (provided - use service) =============

app = FastAPI()


# ============= TODO: Exercise 2.3 =============
# Implement route handlers that use the service
# Routes should be thin - just handle HTTP concerns
# Delegate all business logic to the service

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Create user via service."""
    # TODO: Implement
    # - Call service.create(user_data)
    # - Catch ValueError, raise HTTPException 400
    pass


@app.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service)
):
    """List users via service."""
    # TODO: Implement
    pass


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """Get user via service."""
    # TODO: Implement
    # - Call service.get_by_id(user_id)
    # - Raise HTTPException 404 if None
    pass


@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    """Update user via service."""
    # TODO: Implement
    # - Call service.update(user_id, user_data)
    # - Raise HTTPException 404 if None
    pass


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """Delete user via service."""
    # TODO: Implement
    # - Call service.delete(user_id)
    # - Raise HTTPException 404 if False
    # - Return Response(status_code=204)
    pass


# ============= TESTS =============
# Run with: pytest 008-api-crud-operations/exercises/02_service_pattern.py -v

client = TestClient(app)


def test_create_user():
    """Test user creation through service."""
    response = client.post("/users", json={
        "username": "alice",
        "email": "alice@example.com"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_create_duplicate_username():
    """Test duplicate username validation in service."""
    client.post("/users", json={
        "username": "bob",
        "email": "bob@example.com"
    })

    # Try to create with same username
    response = client.post("/users", json={
        "username": "bob",
        "email": "different@example.com"
    })

    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()


def test_create_duplicate_email():
    """Test duplicate email validation in service."""
    client.post("/users", json={
        "username": "charlie",
        "email": "charlie@example.com"
    })

    # Try to create with same email
    response = client.post("/users", json={
        "username": "different",
        "email": "charlie@example.com"
    })

    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_list_users():
    """Test listing users through service."""
    client.post("/users", json={"username": "user1", "email": "user1@example.com"})
    client.post("/users", json={"username": "user2", "email": "user2@example.com"})

    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_user():
    """Test getting user by ID through service."""
    create_response = client.post("/users", json={
        "username": "dave",
        "email": "dave@example.com"
    })
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "dave"


def test_get_user_not_found():
    """Test 404 when user doesn't exist."""
    response = client.get("/users/99999")
    assert response.status_code == 404


def test_update_user():
    """Test updating user through service."""
    create_response = client.post("/users", json={
        "username": "eve",
        "email": "eve@example.com"
    })
    user_id = create_response.json()["id"]

    response = client.patch(f"/users/{user_id}", json={
        "email": "newemail@example.com"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"
    assert data["username"] == "eve"  # Unchanged


def test_delete_user():
    """Test deleting user through service."""
    create_response = client.post("/users", json={
        "username": "frank",
        "email": "frank@example.com"
    })
    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404
