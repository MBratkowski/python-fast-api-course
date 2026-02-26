# FastAPI Depends() for Database Sessions

## Why This Matters

In mobile development, you use **dependency injection** to provide dependencies where needed: Dagger/Hilt in Android, SwiftUI's `@EnvironmentObject`, or Flutter's Provider. FastAPI's `Depends()` is the same concept - it automatically provides database sessions (and other dependencies) to your route handlers.

Without `Depends()`, you'd manually create and close database sessions in every route. With it, FastAPI handles session lifecycle automatically.

## What is Dependency Injection?

**Dependency Injection (DI)** = Passing dependencies to functions instead of creating them inside.

```python
# ❌ Without DI - create dependency inside
async def get_user(user_id: int):
    db = create_session()  # Create manually
    try:
        user = await db.get(User, user_id)
        return user
    finally:
        await db.close()  # Remember to close!

# ✅ With DI - dependency provided
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    return user  # FastAPI closes session automatically
```

**Benefits:**
- **Automatic cleanup** - no forgotten `close()` calls
- **Testability** - inject mock database for tests
- **Reusability** - same session pattern across all routes
- **Composability** - dependencies can depend on other dependencies

## The `get_db()` Pattern

This is the standard pattern for providing database sessions:

```python
# src/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.

    Provides an async database session to routes.
    Session is automatically closed when request completes.
    """
    async with async_session_maker() as session:
        yield session
        # Session closes automatically when context exits
```

**Key parts:**
1. **`async def`** - It's async (database operations are async)
2. **`AsyncGenerator[AsyncSession, None]`** - Type hint for generator
3. **`async with`** - Context manager creates session
4. **`yield session`** - Provide session to caller
5. **Automatic cleanup** - Session closes when function exits

## Using `Depends()` in Routes

### Basic Usage

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)  # Inject database session
):
    """FastAPI calls get_db() and provides the session."""
    user = await db.get(User, user_id)
    return user
```

**What happens:**
1. Request arrives: `GET /users/123`
2. FastAPI sees `db: AsyncSession = Depends(get_db)`
3. FastAPI calls `get_db()`, gets session
4. FastAPI passes session to `get_user()`
5. Route handler uses session
6. Request completes
7. FastAPI cleans up: `get_db()` context exits, session closes

### Multiple Dependencies

```python
@router.post("/posts")
async def create_post(
    title: str,
    content: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Another dependency
):
    """Use multiple dependencies."""
    post = Post(title=title, content=content, author_id=current_user.id)
    db.add(post)
    await db.commit()
    return post
```

FastAPI calls both `get_db()` and `get_current_user()`.

## Dependency Scope

Each **request** gets its own session:

```python
# Request 1: GET /users/1
# FastAPI creates session A
# Routes uses session A
# Session A closes

# Request 2: GET /users/2
# FastAPI creates session B
# Route uses session B
# Session B closes
```

**Sessions are NOT shared across requests.** This prevents race conditions and ensures isolation.

## Composing Dependencies

Dependencies can depend on other dependencies:

```python
# Lower-level dependency: database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Higher-level dependency: user service (depends on db)
async def get_user_service(
    db: AsyncSession = Depends(get_db)
) -> UserService:
    """Provide UserService with database session."""
    return UserService(db)

# Route: depends on service (which depends on db)
@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """FastAPI resolves the dependency chain automatically."""
    user = await service.get_by_id(user_id)
    return user
```

**Dependency chain:**
1. Route needs `UserService`
2. `get_user_service` needs `AsyncSession`
3. `get_db` provides `AsyncSession`

FastAPI resolves this automatically: `get_db()` → `get_user_service()` → route handler

## Overriding Dependencies for Testing

In tests, override `get_db` to use a test database:

```python
# tests/test_users.py
from fastapi.testclient import TestClient
from src.main import app
from src.db.session import get_db

# Test database session
async def override_get_db():
    async with test_session_maker() as session:
        yield session

# Override dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_get_user():
    """Test uses test database, not production database."""
    response = client.get("/users/1")
    assert response.status_code == 200
```

This is why DI is powerful for testing - swap real database for test database without changing route code.

## Class-Based Dependencies

You can use classes as dependencies:

```python
class Pagination:
    """Dependency for pagination parameters."""

    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit

@router.get("/users")
async def list_users(
    pagination: Pagination = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Query params become class attributes."""
    result = await db.execute(
        select(User).offset(pagination.skip).limit(pagination.limit)
    )
    return result.scalars().all()
```

Request: `GET /users?skip=10&limit=20`

FastAPI creates: `Pagination(skip=10, limit=20)`

## The Full Flow

Here's what happens when a request arrives:

```python
@router.get("/users/{user_id}")
async def get_user(
    user_id: int,  # Path parameter
    db: AsyncSession = Depends(get_db)  # Dependency
):
    user = await db.get(User, user_id)
    return user
```

**Request:** `GET /users/123`

**FastAPI's steps:**
1. **Parse path:** Extract `user_id = 123`
2. **Resolve dependencies:**
   - Call `get_db()`
   - Create async session
   - Yield session
3. **Call route handler:** `await get_user(user_id=123, db=<session>)`
4. **Route executes:** Fetch user, return response
5. **Cleanup dependencies:**
   - `get_db()` context exits
   - Session closes
6. **Return response:** User data as JSON

All automatic. You just write business logic.

## Common Dependency Patterns

### Current User

```python
from fastapi import Header, HTTPException

async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get user from authorization header."""
    token = authorization.replace("Bearer ", "")
    user_id = decode_token(token)

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user
```

### Permission Check

```python
async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin role."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return current_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),  # Must be admin
    db: AsyncSession = Depends(get_db)
):
    """Only admins can delete users."""
    user = await db.get(User, user_id)
    await db.delete(user)
    await db.commit()
    return {"status": "deleted"}
```

### Configuration

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str

@lru_cache()
def get_settings():
    """Singleton settings (cached)."""
    return Settings()

@router.get("/info")
async def get_info(settings: Settings = Depends(get_settings)):
    """Use configuration in routes."""
    return {"database": settings.database_url}
```

## Dependency Injection Analogy

If you've used DI in mobile development:

| Mobile Framework | FastAPI Equivalent |
|------------------|-------------------|
| **Dagger/Hilt (Android)** | |
| `@Inject lateinit var db: Database` | `db: AsyncSession = Depends(get_db)` |
| `@Module` | Dependency function |
| `@Provides` | Function that returns dependency |
| Component graph | FastAPI's dependency resolver |
| **SwiftUI** | |
| `@EnvironmentObject var settings: Settings` | `settings: Settings = Depends(get_settings)` |
| `.environmentObject(settings)` | `app.dependency_overrides` |
| **Flutter Provider** | |
| `Provider.of<Database>(context)` | `db: AsyncSession = Depends(get_db)` |
| `ChangeNotifierProvider` | Dependency function |

FastAPI's DI is simpler - just functions that return values.

## Key Takeaways

1. **`Depends()` injects dependencies into routes** - database sessions, services, current user
2. **`get_db()` pattern** - async generator that yields session and auto-closes
3. **One session per request** - sessions are NOT shared across requests
4. **Dependencies can depend on dependencies** - FastAPI resolves the chain
5. **Use `yield` for cleanup** - code after `yield` runs when request completes
6. **Override for testing** - `app.dependency_overrides[get_db] = test_db`
7. **Classes can be dependencies** - useful for grouping related parameters
8. **Same pattern for auth, permissions, config** - not just database sessions
