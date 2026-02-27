"""
Exercise 2: Fixtures and Database Testing

Learn to use pytest fixtures for setup/teardown, create database test fixtures,
and test CRUD operations with proper test isolation.

A FastAPI app with SQLite database is provided. Your job: write fixtures and tests.

Run: pytest 011-testing-apis/exercises/02_fixtures_and_db.py -v
"""

import pytest
from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from pydantic import BaseModel

# ============= PROVIDED API (DO NOT MODIFY) =============

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    email: str

# Database dependency
def get_db():
    """Real database dependency (will be overridden in tests)."""
    raise NotImplementedError("Override this in tests")

app = FastAPI()

@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """List all users."""
    return db.query(User).all()

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

# ============= TODO: Exercise 2.1 =============
# Create a database engine fixture
# - Use in-memory SQLite: "sqlite:///:memory:"
# - Create all tables: Base.metadata.create_all(engine)
# - Use scope="module" (one engine for all tests in this file)
# - Return the engine

@pytest.fixture(scope="module")
def engine():
    """Create test database engine."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.2 =============
# Create a database session fixture
# - Use the engine fixture
# - Create a connection and transaction
# - Create a Session bound to the connection
# - Yield the session
# - After yield: close session, rollback transaction, close connection
# - Use scope="function" (new session per test for isolation)

@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session with automatic rollback."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.3 =============
# Create a test client fixture
# - Use the db_session fixture
# - Override app's get_db dependency to return db_session
# - Create and return TestClient(app)
# - After yield: clear dependency overrides

@pytest.fixture
def client(db_session):
    """Create test client with database dependency override."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.4 =============
# Test creating a user
# - Use the client fixture
# - POST to /users with user data
# - Assert status code 201
# - Assert response contains user data with id

def test_create_user(client):
    """Test creating a user."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.5 =============
# Test listing users
# - Use the client fixture
# - Create 2-3 users first
# - GET /users
# - Assert response is a list with created users

def test_list_users(client):
    """Test listing users."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.6 =============
# Test getting a specific user
# - Use the client fixture
# - Create a user first
# - GET /users/{user_id}
# - Assert correct user data

def test_get_user(client):
    """Test getting a user."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.7 =============
# Test deleting a user
# - Use the client fixture
# - Create a user first
# - DELETE /users/{user_id}
# - Assert status 204
# - Verify user is gone (GET returns 404)

def test_delete_user(client):
    """Test deleting a user."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.8 =============
# Test database isolation
# - Use the client fixture
# - Create a user
# - Assert exactly 1 user exists
# - This test should pass even after previous tests create users
# - (Proves each test gets a clean database via rollback)

def test_database_isolation(client):
    """Test that each test has isolated database."""
    # TODO: Implement
    pass


# ============= TESTS =============
# These tests verify YOUR implementations

def test_engine_fixture_exists():
    """Verify engine fixture is implemented."""
    assert engine is not None, "Implement engine fixture"
    # Try to get the fixture
    eng = pytest.fixture(lambda: None)

def test_db_session_fixture_exists():
    """Verify db_session fixture is implemented."""
    assert db_session is not None, "Implement db_session fixture"

def test_client_fixture_exists():
    """Verify client fixture is implemented."""
    assert client is not None, "Implement client fixture"

def test_create_user_implementation(client):
    """Verify test_create_user is implemented."""
    if client is None:
        pytest.skip("client fixture not implemented yet")

    test_create_user(client)

def test_list_users_implementation(client):
    """Verify test_list_users is implemented."""
    if client is None:
        pytest.skip("client fixture not implemented yet")

    test_list_users(client)

def test_get_user_implementation(client):
    """Verify test_get_user is implemented."""
    if client is None:
        pytest.skip("client fixture not implemented yet")

    test_get_user(client)

def test_delete_user_implementation(client):
    """Verify test_delete_user is implemented."""
    if client is None:
        pytest.skip("client fixture not implemented yet")

    test_delete_user(client)

def test_database_isolation_implementation(client):
    """Verify test_database_isolation is implemented."""
    if client is None:
        pytest.skip("client fixture not implemented yet")

    test_database_isolation(client)
