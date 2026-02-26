# Service Layer Pattern

## Why This Matters

In mobile development, you separate UI from business logic: ViewModels in Android, Repositories in Flutter, or the MVVM pattern in iOS. The **service layer** is the backend equivalent - it sits between your API routes and your database, containing all business logic.

Without a service layer, your routes become bloated with database queries, validation, and business rules. With it, routes are thin controllers that delegate to services.

## The Problem: Fat Routes

**Bad pattern - everything in the route:**

```python
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username taken")

    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email taken")

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Send welcome email
    await send_email(user.email, "Welcome!")

    return user
```

**Problems:**
- ❌ Route is 30+ lines long
- ❌ Business logic mixed with HTTP concerns
- ❌ Hard to test (requires HTTP client)
- ❌ Can't reuse logic elsewhere
- ❌ Database queries scattered everywhere

## The Solution: Service Layer

**Good pattern - delegate to service:**

```python
# src/services/user_service.py
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create user with validation and side effects."""
        # Check username
        if await self._username_exists(user_data.username):
            raise ValueError("Username already exists")

        # Check email
        if await self._email_exists(user_data.email):
            raise ValueError("Email already exists")

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Send welcome email
        await send_email(user.email, "Welcome!")

        return user

    async def _username_exists(self, username: str) -> bool:
        """Check if username is taken."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None

    async def _email_exists(self, email: str) -> bool:
        """Check if email is taken."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None


# src/api/users.py (thin route)
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Create user - delegates to service."""
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Benefits:**
- ✅ Route is 8 lines - just handles HTTP concerns
- ✅ Business logic in service - can be tested without HTTP
- ✅ Reusable - can call `create_user` from anywhere
- ✅ Clear separation of concerns

## Service Layer Structure

### Typical Service Class

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

class UserService:
    """Business logic for user operations."""

    def __init__(self, db: AsyncSession):
        """Inject database session."""
        self.db = db

    # CREATE
    async def create(self, user_data: UserCreate) -> User:
        """Create new user with validation."""
        # Validation logic
        # Business rules
        # Database operations
        pass

    # READ
    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return await self.db.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # UPDATE
    async def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Update user fields."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Update logic
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    # DELETE
    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True

    # Private helper methods
    async def _username_exists(self, username: str) -> bool:
        """Check if username exists (private method)."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None
```

## Service Dependency Injection

Create a dependency function that provides the service:

```python
# src/api/dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.db.session import get_db
from src.services.user_service import UserService

async def get_user_service(
    db: AsyncSession = Depends(get_db)
) -> UserService:
    """Provide UserService with database session."""
    return UserService(db)


# src/api/users.py (use in routes)
from fastapi import APIRouter, Depends
from src.api.dependencies import get_user_service
from src.services.user_service import UserService

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """Get user - uses service."""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Routes → Service Flow

**Complete example showing the flow:**

```python
# 1. Models (src/models/user.py)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)


# 2. Schemas (src/schemas/user.py)
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str


# 3. Service (src/services/user_service.py)
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Business logic for creating user."""
        # Validation
        if await self._username_exists(user_data.username):
            raise ValueError("Username already taken")

        # Create
        user = User(**user_data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def _username_exists(self, username: str) -> bool:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None


# 4. Dependency (src/api/dependencies.py)
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


# 5. Routes (src/api/users.py)
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Thin route - just HTTP concerns."""
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Flow:**
1. Request arrives: `POST /users` with JSON body
2. FastAPI validates body against `UserCreate` schema
3. FastAPI calls `get_user_service()` → creates `UserService`
4. Route calls `service.create_user(user_data)`
5. Service performs business logic, database operations
6. Service returns `User` object
7. Route returns `User` (FastAPI converts to `UserResponse`)

## Error Handling in Services

Services raise exceptions, routes convert to HTTP errors:

```python
# Service raises domain exceptions
class UserService:
    async def create_user(self, user_data: UserCreate) -> User:
        if await self._username_exists(user_data.username):
            raise ValueError("Username already exists")  # Domain error

        if not self._is_valid_email(user_data.email):
            raise ValueError("Invalid email format")  # Domain error

        # ... create user


# Route converts to HTTP exceptions
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  # HTTP error
```

**Why separate?**
- Service doesn't know about HTTP (could be called from CLI, background job, etc.)
- Route translates domain errors to HTTP status codes

## Testing Services

Services are easy to test - no HTTP client needed:

```python
# tests/test_user_service.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test user creation."""
    service = UserService(db_session)

    user_data = UserCreate(username="alice", email="alice@example.com")
    user = await service.create_user(user_data)

    assert user.id is not None
    assert user.username == "alice"


@pytest.mark.asyncio
async def test_duplicate_username(db_session: AsyncSession):
    """Test duplicate username validation."""
    service = UserService(db_session)

    # Create first user
    user_data = UserCreate(username="alice", email="alice@example.com")
    await service.create_user(user_data)

    # Try to create with same username
    user_data2 = UserCreate(username="alice", email="bob@example.com")

    with pytest.raises(ValueError, match="Username already exists"):
        await service.create_user(user_data2)
```

No HTTP client, no route definitions - just test business logic directly.

## Mobile Development Analogy

The service layer is like your app's architecture:

| Mobile Pattern | Backend Equivalent |
|----------------|-------------------|
| **ViewModel** (MVVM) | Service Layer |
| **Repository** | Service Layer |
| **Use Case** (Clean Architecture) | Service Method |
| **View/Activity** | FastAPI Route |
| **Domain Model** | Pydantic Schema |
| **Data Model** | SQLAlchemy Model |

In mobile:
```kotlin
// ViewModel (business logic)
class UserViewModel(private val repository: UserRepository) {
    suspend fun createUser(username: String, email: String): User {
        if (repository.usernameExists(username)) {
            throw IllegalArgumentException("Username taken")
        }
        return repository.createUser(username, email)
    }
}

// Activity/Fragment (UI logic)
class UserActivity {
    fun onCreateClick() {
        viewModel.createUser(username, email)
            .onSuccess { user -> showSuccess() }
            .onFailure { error -> showError() }
    }
}
```

In backend:
```python
# Service (business logic)
class UserService:
    async def create_user(self, user_data: UserCreate) -> User:
        if await self._username_exists(user_data.username):
            raise ValueError("Username taken")
        return await self._create(user_data)

# Route (HTTP logic)
@router.post("/users")
async def create_user(user_data: UserCreate, service: UserService = Depends()):
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

Same separation of concerns!

## Key Takeaways

1. **Service layer = business logic** - sits between routes and database
2. **Thin routes, fat services** - routes handle HTTP, services handle domain logic
3. **Services are testable** - no HTTP client needed, just test Python functions
4. **Inject services via `Depends()`** - same pattern as database sessions
5. **Services raise domain exceptions** - routes convert to HTTP exceptions
6. **One service per resource** - UserService, PostService, etc.
7. **Services encapsulate database access** - routes don't write SQL
8. **Reusable** - services can be called from routes, CLI, background jobs
