# Fixtures and conftest.py

## Why This Matters

Fixtures are pytest's version of setUp/tearDown from XCTest, @BeforeEach/@AfterEach from JUnit, or setUp/tearDown in flutter_test. But they're more powerful: reusable, composable, and injected via dependency injection.

Think of fixtures as test dependencies. Need a database connection? Write a fixture. Need a test user? Write a fixture. Need an authenticated client? Write a fixture that depends on the user fixture.

## Basic Fixtures

```python
import pytest

@pytest.fixture
def sample_user():
    """Provide a sample user dict."""
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

def test_user_has_id(sample_user):
    """Test that user has an ID."""
    assert "id" in sample_user
    assert sample_user["id"] == 1

def test_user_has_name(sample_user):
    """Test that user has a name."""
    assert sample_user["name"] == "Alice"
```

**How it works:**
1. Define fixture with `@pytest.fixture` decorator
2. pytest sees test function parameter matches fixture name
3. pytest calls fixture function
4. pytest passes return value to test

**No manual setUp/tearDown needed!**

**Mobile Parallel:**

| Platform | Setup/Teardown Pattern |
|----------|------------------------|
| **Swift (XCTest)** | `setUp()` runs before each test, `tearDown()` after |
| **Kotlin (JUnit)** | `@BeforeEach` / `@AfterEach` methods |
| **Flutter (flutter_test)** | `setUp()` / `tearDown()` callbacks |
| **Python (pytest)** | `@pytest.fixture` with dependency injection |

**Key difference:** pytest fixtures are injected by name, not run automatically.

## Fixture Scope

Control how often fixtures are created:

```python
import pytest

@pytest.fixture(scope="function")  # Default: new instance per test
def user():
    print("Creating user")
    return {"id": 1, "name": "Alice"}

@pytest.fixture(scope="module")  # Once per test file
def database():
    print("Connecting to database")
    db = connect_to_db()
    yield db
    print("Disconnecting from database")
    db.close()

@pytest.fixture(scope="session")  # Once for entire test run
def config():
    print("Loading config")
    return load_config()
```

**Scope levels:**
- `function`: New instance for each test (default)
- `module`: One instance per test file
- `session`: One instance for entire test run

**When to use:**
- **function**: Test data that should be isolated (users, posts)
- **module**: Expensive setup that's safe to share (database connection)
- **session**: Global config, API clients

## Setup and Teardown with yield

Use `yield` to run code before and after the test:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

@pytest.fixture
def db_session():
    """Provide a database session with automatic rollback."""
    # SETUP: runs before test
    engine = create_engine("sqlite:///:memory:")
    session = Session(engine)

    yield session  # Test runs here

    # TEARDOWN: runs after test
    session.rollback()
    session.close()

def test_create_user(db_session):
    """Test creating a user."""
    user = User(name="Alice")
    db_session.add(user)
    db_session.commit()

    assert db_session.query(User).count() == 1
    # After this test, session is rolled back automatically
```

**Pattern:**
1. Code before `yield`: setup (runs before test)
2. `yield`: pass value to test
3. Code after `yield`: teardown (runs after test, even if test fails)

## Fixture Chaining

Fixtures can depend on other fixtures:

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def app():
    """Create FastAPI app."""
    from main import app
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    # Login to get token
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass"
    })
    token = response.json()["access_token"]

    # Add auth header
    client.headers["Authorization"] = f"Bearer {token}"
    return client

def test_public_endpoint(client):
    """Test endpoint without auth."""
    response = client.get("/public")
    assert response.status_code == 200

def test_protected_endpoint(authenticated_client):
    """Test endpoint with auth."""
    response = authenticated_client.get("/protected")
    assert response.status_code == 200
```

## conftest.py: Shared Fixtures

Put fixtures in `conftest.py` to share them across multiple test files:

```
tests/
├── conftest.py           # Shared fixtures
├── test_api/
│   ├── conftest.py       # API-specific fixtures
│   ├── test_users.py
│   └── test_posts.py
└── test_services/
    └── test_user_service.py
```

**tests/conftest.py** (shared by all tests):

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

@pytest.fixture(scope="session")
def engine():
    """Create database engine (once per test session)."""
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session with rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create test client with test database."""
    from main import app

    # Override database dependency
    def get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db

    yield TestClient(app)

    # Clean up
    app.dependency_overrides.clear()
```

Now all tests can use these fixtures:

```python
# tests/test_api/test_users.py
def test_create_user(client):
    """Test creating a user."""
    response = client.post("/users", json={"name": "Alice"})
    assert response.status_code == 201

# tests/test_api/test_posts.py
def test_create_post(client):
    """Test creating a post."""
    response = client.post("/posts", json={"title": "Test"})
    assert response.status_code == 201
```

## Database Fixture Pattern

The standard pattern for testing with databases:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base

@pytest.fixture(scope="session")
def engine():
    """Create in-memory database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def db_session(engine):
    """Create session with automatic rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_user_creation(db_session):
    """Test creating a user."""
    user = User(name="Alice", email="alice@example.com")
    db_session.add(user)
    db_session.commit()

    result = db_session.query(User).filter_by(email="alice@example.com").first()
    assert result.name == "Alice"
```

**Why this works:**
- `engine` is created once (fast)
- Each test gets its own `db_session`
- Changes are rolled back after each test (isolation)
- No need to clean up test data manually

## Fixture Factory Pattern

When you need multiple instances in one test:

```python
import pytest

@pytest.fixture
def make_user(db_session):
    """Factory for creating users."""
    def _make_user(name: str, email: str):
        user = User(name=name, email=email)
        db_session.add(user)
        db_session.commit()
        return user
    return _make_user

def test_multiple_users(make_user):
    """Test creating multiple users."""
    alice = make_user("Alice", "alice@example.com")
    bob = make_user("Bob", "bob@example.com")

    assert alice.id != bob.id
    assert alice.name == "Alice"
    assert bob.name == "Bob"
```

## Auto-use Fixtures

Run fixtures automatically without explicit injection:

```python
import pytest

@pytest.fixture(autouse=True)
def reset_database(db_session):
    """Reset database before each test."""
    db_session.query(User).delete()
    db_session.commit()

def test_user_count(db_session):
    """Test starts with empty database."""
    count = db_session.query(User).count()
    assert count == 0  # Database was reset automatically
```

Use sparingly — explicit is better than implicit.

## Key Takeaways

1. **Fixtures replace setUp/tearDown** with dependency injection
2. **@pytest.fixture** decorator defines fixtures
3. **Fixture scope** controls lifetime (function, module, session)
4. **yield** separates setup (before) from teardown (after)
5. **Fixtures can depend on other fixtures** (chaining)
6. **conftest.py** shares fixtures across test files
7. **Database pattern**: session-scoped engine, function-scoped session with rollback
8. **Factory pattern**: return function from fixture to create multiple instances
9. **autouse=True**: run fixture automatically (use sparingly)
