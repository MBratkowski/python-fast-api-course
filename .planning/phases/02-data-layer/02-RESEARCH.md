# Phase 2: Data Layer - Research

**Researched:** 2026-02-26
**Domain:** SQL databases, PostgreSQL, SQLAlchemy 2.0 ORM, Alembic migrations, CRUD APIs with service layers, educational content for mobile developers
**Confidence:** HIGH

## Summary

Phase 2 focuses on teaching mobile developers how to work with relational databases: SQL fundamentals, PostgreSQL setup, SQLAlchemy 2.0 ORM with async patterns, and building production-ready CRUD APIs with service layers and dependency injection. The research reveals a mature, well-established ecosystem with clear best practices and strong async-first patterns that align with FastAPI's architecture.

**Key findings:**
- SQLAlchemy 2.0 (latest: 2.0.47) with async support is the definitive standard for Python database work in 2026, paired with asyncpg for PostgreSQL
- Educational progression should follow: SQL theory → database design → ORM basics → relationships → migrations → service layer → CRUD APIs
- Mobile developers benefit from relational analogies: SQL tables = entity models, foreign keys = object references, ORM models = data classes, async sessions = concurrent database operations
- The "repository pattern + service layer" architecture is now standard for FastAPI applications, with dependency injection via `Depends()` for database sessions

**Primary recommendation:** Teach SQL foundations first (without ORM) to build mental models, then introduce SQLAlchemy 2.0 with async patterns from the start (no sync code), emphasize the N+1 query problem and eager loading strategies, and establish the service layer pattern early as the standard architecture.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy | 2.0.47+ | ORM and database toolkit | Industry standard; SQLAlchemy 2.0 brings 20-40% performance improvements, native async support, improved type hints; supports Python 3.8-3.14 |
| asyncpg | 0.30.0+ | Async PostgreSQL driver | Fastest async PostgreSQL driver for Python (5x faster than psycopg2); pure async implementation; uses binary protocol |
| PostgreSQL | 14.0+ (ideally 15+) | Relational database | 55.6% developer adoption in 2026 (up from 48.7% in 2024); robust ACID compliance; excellent Python ecosystem |
| Alembic | 1.18.4+ | Database migrations | Official SQLAlchemy migration tool; production-standard for schema versioning; requires Python 3.10+ |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| psycopg3 | 3.2.0+ | Alternative async PostgreSQL driver | More Pythonic API, unified sync/async interface; good for mixed workloads; 28% slower than asyncpg but richer features |
| greenlet | 3.1.0+ | Async session dependency | Required by SQLAlchemy for async support; ensure Python 3.13 compatibility |
| python-dotenv | 1.0.0+ | Environment configuration | Managing DATABASE_URL and connection strings securely |
| fastapi-pagination | 0.12.0+ | Pagination library | Pre-built pagination patterns with SQLAlchemy integration |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SQLAlchemy | Django ORM | Django ORM is framework-locked, less flexible for standalone APIs, no native async in 2.0 |
| SQLAlchemy | Raw SQL queries | Loses type safety, manual query building, no migration tracking, more verbose |
| asyncpg | psycopg3 | psycopg3 is 28% slower but offers unified sync/async API; asyncpg is faster for pure async |
| PostgreSQL | MySQL | PostgreSQL has better JSON support, more advanced features, stronger ACID compliance |
| Alembic | Flask-Migrate | Flask-Migrate is Flask-specific wrapper around Alembic; use Alembic directly for FastAPI |

**Installation:**
```bash
# Add to requirements.txt
sqlalchemy>=2.0.47
asyncpg>=0.30.0
alembic>=1.18.4
psycopg2-binary>=2.9.9  # For Alembic connection during migrations
python-dotenv>=1.0.0
fastapi-pagination>=0.12.0  # Optional, for pagination
```

## Architecture Patterns

### Recommended Project Structure
For Modules 006-008:

```
src/
├── db/
│   ├── base.py              # Declarative base, metadata
│   ├── session.py           # Async engine, async_sessionmaker, get_db dependency
│   └── init_db.py           # Database initialization utilities
├── models/                  # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py              # User model with relationships
│   └── post.py              # Post model example
├── schemas/                 # Pydantic models (separate from ORM)
│   ├── user.py              # UserCreate, UserUpdate, UserResponse
│   └── post.py
├── services/                # Business logic layer
│   ├── user_service.py      # UserService with CRUD methods
│   └── post_service.py
├── api/
│   └── endpoints/
│       ├── users.py         # User routes using service layer
│       └── posts.py
└── core/
    └── config.py            # Database URL, settings

alembic/                     # Migration scripts
├── versions/                # Auto-generated migrations
├── env.py                   # Alembic environment configuration
└── alembic.ini             # Alembic configuration
```

### Pattern 1: Async Database Session Management
**What:** FastAPI dependency that provides request-scoped async database sessions
**When to use:** All database operations in FastAPI endpoints
**Example:**
```python
# src/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent lazy-loading after commit
    autoflush=False,  # Explicit flush control
)

# Dependency for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```
**Source:** [FastAPI SQL Databases Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/) + [SQLAlchemy AsyncIO Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Pattern 2: SQLAlchemy 2.0 Declarative Models
**What:** Type-hinted ORM models using SQLAlchemy 2.0's `Mapped` and `mapped_column`
**When to use:** All SQLAlchemy model definitions in Module 007
**Example:**
```python
# src/models/user.py
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationship (one-to-many)
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
```
**Source:** [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)

### Pattern 3: Service Layer with Repository Pattern
**What:** Business logic layer that sits between API routes and database, using dependency injection
**When to use:** All CRUD operations in Module 008
**Example:**
```python
# src/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user with validation."""
        user = User(**user_data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID with error handling."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List users with pagination."""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

# src/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserResponse

router = APIRouter()

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """Create user endpoint - clean separation of concerns."""
    return await service.create_user(user_data)
```
**Source:** [Service Layer Pattern](https://mpuig.github.io/Notes/fastapi_basics/04.service_layer_pattern/) + [Repository Pattern in Python](https://medium.com/@kmuhsinn/the-repository-pattern-in-python-write-flexible-testable-code-with-fastapi-examples-aa0105e40776)

### Pattern 4: Eager Loading to Prevent N+1 Queries
**What:** Using `selectinload()` or `joinedload()` to load relationships upfront
**When to use:** Any time you access related objects (Module 007 relationships)
**Example:**
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# BAD: N+1 query problem (lazy loading)
users = await session.execute(select(User))
for user in users.scalars():
    print(user.posts)  # ⚠️ Triggers separate query for EACH user!

# GOOD: Eager loading with selectinload
result = await session.execute(
    select(User).options(selectinload(User.posts))
)
users = result.scalars().all()
for user in users:
    print(user.posts)  # ✅ Already loaded, no additional queries
```
**Source:** [SQLAlchemy Relationship Loading](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)

### Pattern 5: Pagination Pattern
**What:** Standardized pagination with offset/limit and total count
**When to use:** All list endpoints in Module 008
**Example:**
```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

async def paginate(
    query,
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse:
    """Generic pagination helper."""
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Get paginated results
    offset = (page - 1) * page_size
    result = await session.execute(query.offset(offset).limit(page_size))
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )
```
**Source:** [FastAPI Pagination Implementation](https://oneuptime.com/blog/post/2026-02-02-fastapi-pagination/view)

### Pattern 6: Alembic Migration Workflow
**What:** Version-controlled database schema changes using Alembic
**When to use:** Module 007 for introducing migrations
**Example:**
```bash
# Initialize Alembic
alembic init alembic

# Configure alembic.ini with database URL
# Edit alembic/env.py to import models

# Auto-generate migration from model changes
alembic revision --autogenerate -m "create users table"

# Review and edit generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```
**Source:** [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/) + [FastAPI with Alembic Tutorial](https://testdriven.io/blog/fastapi-sqlmodel/)

### Anti-Patterns to Avoid
- **Don't use sync SQLAlchemy with FastAPI:** Blocks the async event loop; always use `create_async_engine` and `AsyncSession`
- **Don't access lazy-loaded relationships in async code:** Will raise errors; use `selectinload()` or `joinedload()` upfront
- **Don't reuse Pydantic models for ORM models:** Keep SQLAlchemy models and Pydantic schemas separate; ORM models have state, Pydantic models are for validation
- **Don't share AsyncSession across concurrent tasks:** Each concurrent operation needs its own session; sessions are NOT thread-safe
- **Don't use `SELECT *` in ORM queries:** Explicitly select columns or use `load_only()` for performance
- **Don't skip migration scripts:** Always use Alembic for schema changes, never `create_all()` in production
- **Don't put business logic in route handlers:** Use service layer for testability and separation of concerns
- **Don't forget `expire_on_commit=False`:** Without this, accessing attributes after commit triggers lazy loads (fails in async)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Database migrations | Manual ALTER TABLE scripts | Alembic | Tracks version history, handles rollbacks, auto-generates from model changes, prevents schema drift |
| Pagination | Manual OFFSET/LIMIT logic | fastapi-pagination library | Handles edge cases (page overflow, negative values), provides consistent response format, calculates total pages |
| Connection pooling | Custom connection manager | SQLAlchemy engine with pool settings | Handles connection lifecycle, prevents leaks, configurable pool size and overflow, battle-tested |
| N+1 query detection | Manual query counting | SQLAlchemy's eager loading + raiseload() | Built-in strategies (selectinload, joinedload), explicit control, prevents runtime lazy loads |
| Session lifecycle | Manual session.close() | FastAPI dependency with yield | Automatic cleanup, handles exceptions, prevents leaked connections, one session per request |
| SQL injection prevention | String concatenation with sanitization | SQLAlchemy parameterized queries | Automatic parameter binding, database-agnostic escaping, prevents all injection vectors |
| Database URL parsing | String splitting | SQLAlchemy URL.create() | Handles all database dialects, parses drivers and options, validates format |

**Key insight:** SQLAlchemy + Alembic eliminate most database management boilerplate. If you're writing raw SQL strings or manual connection management, you're fighting the ecosystem.

## Common Pitfalls

### Pitfall 1: Lazy Loading in Async Code
**What goes wrong:** Accessing relationship attributes triggers synchronous lazy loading, which raises errors in async context
**Why it happens:** Mobile developers expect object navigation to "just work" (like accessing properties on domain objects)
**How to avoid:**
- Always use eager loading: `selectinload()` for collections, `joinedload()` for single objects
- Set `lazy='raise'` on relationships during development to catch lazy loads immediately
- Use `expire_on_commit=False` to prevent post-commit attribute expiration
**Warning signs:** `MissingGreenlet` errors, unexpected database queries when accessing attributes
**Example:**
```python
# BAD
users = await session.execute(select(User))
for user in users.scalars():
    print(user.posts)  # 💥 Raises error in async!

# GOOD
users = await session.execute(
    select(User).options(selectinload(User.posts))
)
for user in users.scalars():
    print(user.posts)  # ✅ Already loaded
```

### Pitfall 2: Using Sync SQLAlchemy with FastAPI
**What goes wrong:** Using `create_engine` instead of `create_async_engine` blocks the event loop
**Why it happens:** Older tutorials use sync patterns, and sync code "seems to work" initially
**How to avoid:**
- Always use `create_async_engine` and `AsyncSession` from the start
- Import from `sqlalchemy.ext.asyncio`, not `sqlalchemy.orm`
- Use `async def` for all database operations
- Choose `asyncpg` (not `psycopg2`) as the PostgreSQL driver
**Warning signs:** Slow response times under load, event loop blocking warnings, using `psycopg2` driver

### Pitfall 3: Forgetting expire_on_commit
**What goes wrong:** After `session.commit()`, accessing model attributes triggers lazy loads which fail in async
**Why it happens:** SQLAlchemy expires objects after commit by default to ensure freshness
**How to avoid:**
- Set `expire_on_commit=False` in `async_sessionmaker`
- Use `session.refresh(obj)` explicitly if you need updated state
- Load all needed attributes before commit if `expire_on_commit=True`
**Warning signs:** Errors when accessing attributes immediately after commit
**Example:**
```python
# BAD: Will fail after commit
async_session_maker = async_sessionmaker(engine)  # expire_on_commit=True by default
user = User(username="alice")
session.add(user)
await session.commit()
print(user.username)  # 💥 Triggers lazy load, raises error

# GOOD: Disable expiration
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
user = User(username="alice")
session.add(user)
await session.commit()
print(user.username)  # ✅ Works fine
```

### Pitfall 4: Mixing Pydantic and SQLAlchemy Models
**What goes wrong:** Using SQLAlchemy models directly as Pydantic response models or vice versa
**Why it happens:** Both use similar class-based syntax, and returning ORM objects "works" initially
**How to avoid:**
- Keep SQLAlchemy models in `models/` and Pydantic schemas in `schemas/`
- Never inherit from both `Base` (SQLAlchemy) and `BaseModel` (Pydantic)
- Convert ORM objects to Pydantic with explicit mapping or `model_validate()`
- Use Pydantic's `from_attributes=True` (ConfigDict) to read from ORM objects
**Warning signs:** Unexpected fields exposed in API, serialization errors, mixing validation with ORM state
**Example:**
```python
# BAD: Reusing models
class User(Base, BaseModel):  # 💥 Don't inherit from both!
    __tablename__ = "users"
    id: int
    username: str

# GOOD: Separate models
# models/user.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]

# schemas/user.py
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str

# api/users.py
user = await service.get_user(user_id)
return UserResponse.model_validate(user)  # ✅ Convert ORM to Pydantic
```

### Pitfall 5: N+1 Query Problem
**What goes wrong:** Loading a collection of objects triggers one query per object for related data
**Why it happens:** Default lazy loading is convenient but inefficient; mobile devs used to in-memory object graphs don't think about database queries
**How to avoid:**
- Always profile queries during development (set `echo=True` on engine)
- Use `selectinload()` for one-to-many/many-to-many relationships
- Use `joinedload()` for many-to-one/one-to-one relationships
- Set `lazy='raise'` during development to catch lazy loads
**Warning signs:** Seeing dozens/hundreds of SELECT queries for one endpoint, slow list endpoints
**Example:**
```python
# BAD: N+1 problem
# Query 1: Load all users
users = await session.execute(select(User))
for user in users.scalars():  # 100 users
    # Query 2-101: Load posts for each user!
    print(len(user.posts))  # 💥 N+1 queries (101 total)

# GOOD: Eager loading
users = await session.execute(
    select(User).options(selectinload(User.posts))
)
for user in users.scalars():
    print(len(user.posts))  # ✅ 2 queries total (users + posts)
```

### Pitfall 6: Not Using Alembic for Migrations
**What goes wrong:** Using `Base.metadata.create_all()` in production, making manual schema changes
**Why it happens:** `create_all()` is shown in tutorials for getting started, manual SQL seems faster
**How to avoid:**
- Set up Alembic from the start (Module 007)
- Never use `create_all()` outside of tests
- Always generate migrations: `alembic revision --autogenerate`
- Review auto-generated migrations before applying
- Keep migrations in version control
**Warning signs:** Schema drift between environments, no rollback capability, merge conflicts on schema changes

### Pitfall 7: Service Layer Bypass
**What goes wrong:** Putting database logic directly in route handlers
**Why it happens:** Seems simpler initially, fewer files to manage
**How to avoid:**
- Introduce service layer pattern early (Module 008)
- Keep routes thin: validate → call service → return response
- Put all business logic, transactions, and complex queries in services
- Makes testing easier (can test services without HTTP)
**Warning signs:** Route handlers with complex database queries, difficulty testing business logic

### Pitfall 8: Ignoring Transaction Management
**What goes wrong:** Not using transactions for multi-step operations, partial data corruption on failures
**Why it happens:** Mobile developers used to local data persistence don't think about ACID properties
**How to avoid:**
- Use `async with session.begin()` for explicit transactions
- Understand that `session.commit()` is the transaction boundary
- Group related operations in same transaction
- Test rollback scenarios
**Warning signs:** Partial data after errors, inconsistent state between related tables

## Code Examples

Verified patterns from official sources:

### Database Connection Setup (Module 007)
```python
# src/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

# Database URL format: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/mydb"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Additional connections allowed
    pool_pre_ping=True,  # Verify connections before use
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Critical for async
    autoflush=False,  # Explicit flush control
)

# Declarative base for models
class Base(DeclarativeBase):
    pass

# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```
**Source:** [SQLAlchemy AsyncIO Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) + [FastAPI SQL Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)

### SQLAlchemy 2.0 Model with Relationships (Module 007)
```python
# src/models/user.py
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime
from src.db.session import Base

class User(Base):
    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Basic fields with constraints
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Optional field (nullable)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Field with default
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # One-to-many relationship (user has many posts)
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",  # Delete posts when user deleted
    )

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)

    # Foreign key (many-to-one)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Many-to-one relationship (post belongs to user)
    author: Mapped["User"] = relationship(back_populates="posts")
```
**Source:** [SQLAlchemy 2.0 ORM Documentation](https://docs.sqlalchemy.org/en/20/)

### CRUD Operations with Service Layer (Module 008)
```python
# src/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from typing import List

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        """Create new user."""
        user = User(**user_data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID with posts loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.posts))  # Eager load posts
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()

    async def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Update user fields."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Update only provided fields
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True

# src/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """Create new user."""
    # Check if username exists
    existing = await service.get_by_username(user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    return await service.create(user_data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    """Get user by ID."""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
):
    """List users with pagination."""
    return await service.list(skip=skip, limit=limit)
```
**Source:** [Service Layer Pattern](https://mpuig.github.io/Notes/fastapi_basics/04.service_layer_pattern/) + [FastAPI Best Practices](https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy)

### SQL Query Examples (Module 006)
```sql
-- Basic SELECT with WHERE
SELECT id, username, email
FROM users
WHERE is_active = true
ORDER BY created_at DESC
LIMIT 10;

-- JOIN to get user posts
SELECT u.username, p.title, p.created_at
FROM users u
INNER JOIN posts p ON u.id = p.author_id
WHERE u.is_active = true
ORDER BY p.created_at DESC;

-- LEFT JOIN to include users without posts
SELECT u.username, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.author_id
GROUP BY u.id, u.username
ORDER BY post_count DESC;

-- Aggregate functions
SELECT
    DATE(created_at) as date,
    COUNT(*) as user_count,
    COUNT(CASE WHEN is_active THEN 1 END) as active_count
FROM users
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Index creation for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC);
```
**Source:** Standard SQL patterns for PostgreSQL

### Alembic Migration Setup (Module 007)
```bash
# Initialize Alembic
alembic init alembic

# Configure alembic/env.py to import models
# Add to alembic/env.py:
from src.db.session import Base
from src.models import user, post  # Import all models
target_metadata = Base.metadata

# Create migration from model changes
alembic revision --autogenerate -m "create users and posts tables"

# Review generated migration in alembic/versions/xxxx_create_users_and_posts_tables.py

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history --verbose
```

Example generated migration:
```python
# alembic/versions/xxxx_create_users_and_posts_tables.py
"""create users and posts tables

Revision ID: xxxx
Revises:
Create Date: 2026-02-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxx'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create posts table
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_posts_author_id', 'posts', ['author_id'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_posts_author_id', table_name='posts')
    op.drop_table('posts')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
```
**Source:** [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SQLAlchemy 1.4 sync | SQLAlchemy 2.0 async | January 2023 | Native async/await support; 20-40% performance improvement; better type hints with `Mapped[]`; breaking changes require migration |
| psycopg2 (sync) | asyncpg for async | 2016-2018 | asyncpg is 5x faster; pure async implementation; binary protocol; now standard for FastAPI+PostgreSQL |
| `relationship()` without type hints | `Mapped[List["Model"]]` syntax | SQLAlchemy 2.0 | Better IDE support; type checking with mypy; explicit relationship types |
| Manual SQL queries | SQLAlchemy Core/ORM | Ongoing | Type safety; SQL injection prevention; database-agnostic; migration support |
| `create_all()` for schema | Alembic migrations | 2011+ | Version control for schema; rollback capability; team collaboration; production-standard |
| Flask-Migrate | Alembic directly | 2020+ | Framework-agnostic; works with FastAPI; more control; official SQLAlchemy tool |
| Lazy loading default | Eager loading with `selectinload()` | Emphasized in 2.0 | Prevents N+1 queries; async-compatible; explicit control; better performance |
| String-based column definitions | `mapped_column()` with type hints | SQLAlchemy 2.0 | Type safety; better IDE support; clearer intent; required for `Mapped[]` |

**Deprecated/outdated:**
- **SQLAlchemy 1.4 patterns:** Using `declarative_base()` instead of `DeclarativeBase`, using `Column()` instead of `mapped_column()`
- **Sync SQLAlchemy with FastAPI:** Blocks event loop; use `create_async_engine` and `AsyncSession`
- **psycopg2 for async workloads:** Use asyncpg for FastAPI; psycopg3 is acceptable but slower
- **`create_all()` in production:** Always use Alembic migrations for schema management
- **Direct ORM model exposure in APIs:** Return Pydantic schemas, not ORM objects

## Open Questions

1. **How deep should SQL theory go in Module 006?**
   - What we know: Mobile developers may have used SQLite locally but not relational design
   - What's unclear: Should we cover normalization forms (1NF, 2NF, 3NF) in depth or just principles?
   - Recommendation: Cover practical normalization (avoid duplication, use foreign keys) without formal normal form theory. Focus on "why" not "what" (1NF/2NF labels). Save advanced topics (triggers, stored procedures, CTEs) for "what's next" references.

2. **Should exercises use Docker PostgreSQL from the start?**
   - What we know: Project README shows Docker Compose setup; learners need PostgreSQL running
   - What's unclear: Module 006 is SQL-focused, might not need ORM/FastAPI yet
   - Recommendation: Introduce Docker Compose in Module 006 theory but allow learners to use local PostgreSQL if preferred. Module 007 should require Docker for consistency (Alembic migrations need database).

3. **How to balance raw SQL vs SQLAlchemy in Module 006?**
   - What we know: Module 006 is "SQL & Database Fundamentals", Module 007 introduces SQLAlchemy ORM
   - What's unclear: Should Module 006 exercises use pure SQL or include Python drivers (psycopg3)?
   - Recommendation: Module 006 exercises should use raw SQL with psycopg3 for execution (not ORM). This builds SQL fundamentals before ORM abstracts them. Use `psql` command-line tool for direct SQL practice, Python+psycopg3 for scripting exercises.

4. **Should service layer be introduced gradually or all at once?**
   - What we know: Module 008 covers service layer pattern; earlier modules might show direct database access
   - What's unclear: Should Module 007 exercises use service layer or direct session access?
   - Recommendation: Module 007 exercises use direct `session` access to focus on ORM concepts. Module 008 refactors to service layer pattern, showing "why" (separation of concerns, testability). This mirrors the Phase 1 pattern of introducing concepts incrementally.

## Sources

### Primary (HIGH confidence)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/) - ORM patterns, async support, relationship loading
- [SQLAlchemy AsyncIO Extension](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - Async session patterns, best practices
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/) - Migration workflows, commands
- [FastAPI SQL Databases Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/) - Session management, dependencies
- [FastAPI Dependencies Tutorial](https://fastapi.tiangolo.com/tutorial/dependencies/) - Dependency injection, `Depends()`
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - SQL syntax, database design
- [SQLAlchemy PyPI](https://pypi.org/project/SQLAlchemy/) - Version 2.0.47, Python 3.8-3.14 support
- [Alembic PyPI](https://pypi.org/project/alembic/) - Version 1.18.4, Python 3.10+ required
- [asyncpg GitHub](https://github.com/MagicStack/asyncpg) - Fastest async PostgreSQL driver

### Secondary (MEDIUM confidence)
- [Patterns and Practices for SQLAlchemy 2.0 with FastAPI](https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy) - Session management, expire_on_commit
- [Setting up FastAPI with Async SQLAlchemy 2.0 & Pydantic V2](https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308) - Complete setup guide
- [Building High-Performance Async APIs with FastAPI, SQLAlchemy 2.0, and Asyncpg](https://leapcell.io/blog/building-high-performance-async-apis-with-fastapi-sqlalchemy-2-0-and-asyncpg) - Performance patterns
- [The Service Layer Pattern](https://mpuig.github.io/Notes/fastapi_basics/04.service_layer_pattern/) - Service layer architecture
- [Repository Pattern in Python with FastAPI Examples](https://medium.com/@kmuhsinn/the-repository-pattern-in-python-write-flexible-testable-code-with-fastapi-examples-aa0105e40776) - Repository pattern
- [FastAPI Pagination Implementation](https://oneuptime.com/blog/post/2026-02-02-fastapi-pagination/view) - Pagination patterns
- [How to Use Alembic with FastAPI](https://www.nashruddinamin.com/blog/how-to-use-alembic-for-database-migrations-in-your-fastapi-application) - Alembic setup
- [TestDriven.io: FastAPI with SQLModel and Alembic](https://testdriven.io/blog/fastapi-sqlmodel/) - Complete tutorial
- [Psycopg3 vs Asyncpg Performance](https://fernandoarteaga.dev/blog/psycopg-vs-asyncpg/) - Driver comparison
- [Understanding N+1 Query Problem](https://planetscale.com/blog/what-is-n-1-query-problem-and-how-to-solve-it) - N+1 explanation
- [SQL Join Types Explained 2026](https://www.sqlnoir.com/blog/sql-join-types-explained) - JOIN patterns
- [ACID Properties in DBMS](https://www.geeksforgeeks.org/dbms/acid-properties-in-dbms/) - ACID principles
- [Database Indexing Best Practices](https://oneuptime.com/blog/post/2026-01-30-index-optimization/view) - Index optimization
- [PostgreSQL 2026 Usage Statistics](https://www.programming-helper.com/tech/postgresql-2026-most-popular-database-developers-python) - 55.6% adoption

### Tertiary (LOW confidence)
- [FastAPI Best Practices Production 2026](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026) - General best practices
- [SQL for Backend Developers](https://blog.boot.dev/backend/do-backend-devs-need-sql/) - Learning SQL importance

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - SQLAlchemy 2.0 + asyncpg + Alembic are clearly dominant; official documentation is authoritative; version numbers verified from PyPI
- Architecture patterns: HIGH - Service layer + repository pattern are well-documented across multiple sources; FastAPI dependency injection is official; async session patterns from SQLAlchemy docs
- Common pitfalls: HIGH - Lazy loading in async, N+1 queries, expire_on_commit issues are extensively documented in official SQLAlchemy docs and community sources
- Educational progression: MEDIUM - SQL-first approach is inferred from general pedagogical practices; mobile-dev-specific framing is adapted from Phase 1 patterns

**Research date:** 2026-02-26
**Valid until:** 2026-04-26 (60 days - stable ecosystem, SQLAlchemy 2.0 mature, incremental updates expected)

**Key uncertainties resolved:**
- SQLAlchemy 2.0 is standard (1.4 deprecated): Confirmed via official docs and PyPI (2.0.47 latest)
- asyncpg is fastest async driver: Confirmed via benchmarks and community consensus (5x faster than psycopg2)
- Python 3.10+ required for Alembic: Confirmed via PyPI package requirements
- Service layer + repository pattern is standard: Confirmed across multiple 2026 FastAPI tutorials
- expire_on_commit=False critical for async: Confirmed via SQLAlchemy async documentation
- Separate Pydantic and SQLAlchemy models: Confirmed as best practice across all sources
