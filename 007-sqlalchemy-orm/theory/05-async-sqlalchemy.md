# Async SQLAlchemy for FastAPI

## Why This Matters

In mobile development, network calls don't block the UI thread - they run asynchronously using async/await (Swift), coroutines (Kotlin), or Futures (Dart). Backend APIs work the same way: database operations should NOT block the event loop while waiting for results.

FastAPI is built for async. Using sync database code with FastAPI would block the event loop and destroy performance under load. Async SQLAlchemy lets database operations run concurrently with other requests.

## The Async Stack

For async database access with FastAPI:

```
FastAPI (async framework)
    ↓
AsyncSession (async ORM session)
    ↓
create_async_engine (async connection pool)
    ↓
asyncpg (async PostgreSQL driver)
    ↓
PostgreSQL database
```

## Setting Up Async SQLAlchemy

### 1. Install Dependencies

```bash
pip install sqlalchemy[asyncio] asyncpg
```

- **`sqlalchemy[asyncio]`** - Async support for SQLAlchemy
- **`asyncpg`** - Fastest async PostgreSQL driver (5x faster than psycopg2)

### 2. Create Async Engine

```python
# src/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Async database URL - note the asyncpg driver
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_size=5,  # Number of connections to keep open
    max_overflow=10,  # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before use
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Critical for async - explained below
    autoflush=False,  # Manual flush control
)

# Base class for models
class Base(DeclarativeBase):
    pass
```

### 3. Create Database Dependency for FastAPI

```python
# src/db/session.py (continued)
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides database session to FastAPI routes.

    Usage in routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        yield session
        # Session automatically closes when context exits
```

**This is the dependency you'll use in all FastAPI routes.**

## The Database URL

Format: `postgresql+asyncpg://user:password@host:port/database`

```python
# Development (local PostgreSQL)
DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/myapp"

# Production (from environment variable)
import os
DATABASE_URL = os.getenv("DATABASE_URL")

# With special characters in password
from urllib.parse import quote_plus
password = quote_plus("p@ss!word#123")
DATABASE_URL = f"postgresql+asyncpg://user:{password}@localhost:5432/myapp"
```

**Key parts:**
- **`postgresql+asyncpg`** - Database type + async driver
- **`user:password`** - Database credentials
- **`localhost:5432`** - Host and port
- **`myapp`** - Database name

## Why `expire_on_commit=False` is Critical

By default, SQLAlchemy **expires** objects after commit - it clears their state to ensure you always read fresh data.

```python
# With expire_on_commit=True (default):
user = User(username="alice")
session.add(user)
await session.commit()

# Object is expired - accessing attributes triggers lazy load
print(user.username)  # 💥 Raises MissingGreenlet error in async!
```

**The problem:** After commit, accessing `user.username` tries to lazy-load from database. Lazy loading is synchronous and fails in async code.

**The solution:** Set `expire_on_commit=False`:

```python
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,  # Don't expire objects after commit
)

# Now this works:
user = User(username="alice")
session.add(user)
await session.commit()
print(user.username)  # ✅ Works - object not expired
```

**Trade-off:** You're working with potentially stale data after commit. If you need fresh data, manually refresh:

```python
await session.commit()
await session.refresh(user)  # Explicitly reload from database
```

For FastAPI, `expire_on_commit=False` is the standard choice.

## Using Async Session in FastAPI Routes

### Basic CRUD Operations

```python
# src/api/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.session import get_db
from src.models.user import User

router = APIRouter()

@router.post("/users")
async def create_user(
    username: str,
    email: str,
    db: AsyncSession = Depends(get_db)  # Inject database session
):
    """Create new user."""
    user = User(username=username, email=email)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"id": user.id, "username": user.username}

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user.id, "username": user.username, "email": user.email}

@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """List users with pagination."""
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return {"users": [{"id": u.id, "username": u.username} for u in users]}
```

**Key points:**
- Routes are `async def`
- Database operations use `await`
- Session injected via `Depends(get_db)`
- Session automatically closed after request

### With Eager Loading

```python
from sqlalchemy.orm import selectinload

@router.get("/users/{user_id}/posts")
async def get_user_with_posts(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user with all their posts."""
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.posts))  # Eager load posts
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "posts": [{"id": p.id, "title": p.title} for p in user.posts]
    }
```

## Connection Pool Configuration

The engine maintains a **connection pool** - a set of reusable database connections.

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,  # Keep 5 connections open at all times
    max_overflow=10,  # Allow up to 10 additional connections when busy
    pool_pre_ping=True,  # Test connections before using (detects stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour (3600 seconds)
)
```

**Why connection pooling matters:**
- Opening a database connection is slow (100ms+)
- Reusing connections is fast (<1ms)
- Pool prevents "too many connections" errors

**Recommended settings for FastAPI:**
- **`pool_size=5`** - Good default for most apps
- **`max_overflow=10`** - Handles traffic spikes
- **`pool_pre_ping=True`** - Prevents "connection closed" errors
- **`pool_recycle=3600`** - Prevents stale connections (PostgreSQL closes idle connections after a while)

**Calculating pool size:**
If you have 4 worker processes with `pool_size=5`, you have 4 × 5 = **20 total connections**.

Make sure your PostgreSQL `max_connections` is higher than this:

```sql
-- Check PostgreSQL max connections
SHOW max_connections;

-- Increase if needed (in postgresql.conf)
max_connections = 100
```

## Creating Tables (Development Only)

During development, you can create tables from models:

```python
# src/db/init_db.py
from sqlalchemy.ext.asyncio import create_async_engine
from src.db.session import Base, DATABASE_URL
from src.models import user, post  # Import all models

async def init_db():
    """Create all tables. Use only in development!"""
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        # Drop all tables (dangerous!)
        await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

# Run with: python -c "import asyncio; from src.db.init_db import init_db; asyncio.run(init_db())"
```

**Warning:** `create_all()` is for development and tests ONLY. For production, use Alembic migrations (next lesson).

## Complete Database Setup File

```python
# src/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/myapp"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG") == "true" else False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Base class for all models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session to routes."""
    async with async_session_maker() as session:
        yield session
```

## Async vs Sync: Key Differences

| Sync SQLAlchemy | Async SQLAlchemy |
|-----------------|------------------|
| `create_engine()` | `create_async_engine()` |
| `Session` | `AsyncSession` |
| `sessionmaker` | `async_sessionmaker` |
| `session.commit()` | `await session.commit()` |
| `session.get(User, 1)` | `await session.get(User, 1)` |
| `session.execute(query)` | `await session.execute(query)` |
| Import from `sqlalchemy.orm` | Import from `sqlalchemy.ext.asyncio` |

**Rule:** In async code, any database operation needs `await`.

## Testing with Async SQLAlchemy

```python
# tests/test_users.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.db.session import Base

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session():
    """Provide clean database session for each test."""
    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    # Cleanup
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test user creation."""
    user = User(username="alice", email="alice@example.com")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.username == "alice"
```

## Key Takeaways

1. **Use async SQLAlchemy with FastAPI** - sync code blocks the event loop
2. **Database URL format:** `postgresql+asyncpg://user:password@host:port/dbname`
3. **Three-part setup:** async engine → async_sessionmaker → get_db dependency
4. **Set `expire_on_commit=False`** - prevents lazy loading errors in async
5. **All database operations need `await`** - commit, execute, get, refresh
6. **Connection pooling** handles reusing database connections efficiently
7. **`get_db()` dependency** provides sessions to FastAPI routes
8. **Use Alembic for migrations** - `create_all()` is for development/tests only
9. **Configure pool size** based on number of workers and expected traffic
