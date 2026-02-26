# FastAPI Project Structure

## Why This Matters

Just like you wouldn't put all your mobile code in one ViewController, you shouldn't put all API code in one file. Good structure makes your code maintainable and testable.

## Single-File Structure (Starter Projects)

For learning or tiny APIs:

```
project/
├── main.py           # All code here
├── requirements.txt
└── .env
```

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.get("/")
async def root():
    return {"message": "Hello"}

@app.get("/users")
async def list_users():
    return {"users": []}
```

**Good for**: Learning, prototypes, APIs with <5 endpoints

**Problems**: Grows messy fast, hard to test, can't share code

## Multi-File Structure (Production)

For real applications:

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py          # App entry point
│   ├── api/             # Route handlers
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   └── auth.py
│   ├── models/          # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── post_service.py
│   └── db/              # Database
│       ├── __init__.py
│       └── database.py
├── tests/
│   ├── __init__.py
│   ├── test_users.py
│   └── test_posts.py
├── requirements.txt
├── .env
└── .gitignore
```

**Mobile analogy**: Like MVVM or Clean Architecture - separation of concerns.

## Main Application File

```python
# src/main.py
from fastapi import FastAPI
from src.api import users, posts

app = FastAPI(
    title="My API",
    description="API for users and posts",
    version="1.0.0"
)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])

@app.get("/")
async def root():
    return {"message": "API is running"}
```

The main file:
- Creates the FastAPI app
- Includes routers from other files
- Configures global settings
- Minimal business logic

## Using APIRouter

Break endpoints into separate files using `APIRouter`:

```python
# src/api/users.py
from fastapi import APIRouter
from src.models.user import User, UserCreate

router = APIRouter()

@router.get("/")
async def list_users():
    """List all users."""
    return {"users": []}

@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get single user."""
    return {"id": user_id}

@router.post("/", status_code=201)
async def create_user(user: UserCreate):
    """Create new user."""
    return {"id": 123, **user.model_dump()}
```

Then include in main:
```python
# src/main.py
from src.api import users

app.include_router(users.router, prefix="/users", tags=["users"])
```

**Mobile analogy**: Like splitting your app into feature modules or coordinators.

## Pydantic Models

Keep data models in separate files:

```python
# src/models/user.py
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """Shared user properties."""
    name: str
    email: EmailStr

class UserCreate(UserBase):
    """For creating users - includes password."""
    password: str

class UserUpdate(UserBase):
    """For updating users - all optional."""
    name: str | None = None
    email: EmailStr | None = None

class User(UserBase):
    """User response - includes generated fields."""
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # For ORM compatibility
```

**Separate models for**:
- **Create**: Input when creating (includes password)
- **Update**: Input when updating (fields optional)
- **Response**: Output to clients (excludes password)

**Mobile analogy**: Like having separate DTOs or data classes for requests and responses.

## Service Layer

Business logic goes in services:

```python
# src/services/user_service.py
from src.models.user import UserCreate, User

class UserService:
    def __init__(self):
        self.users = {}  # In real app: database
        self.next_id = 1

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user_dict = user_data.model_dump()
        user_dict["id"] = self.next_id
        user_dict["is_active"] = True
        user = User(**user_dict)
        self.users[self.next_id] = user
        self.next_id += 1
        return user

    async def get_user(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.users.get(user_id)

    async def list_users(self) -> list[User]:
        """List all users."""
        return list(self.users.values())

# Global instance (use dependency injection in real apps)
user_service = UserService()
```

Then use in routes:

```python
# src/api/users.py
from fastapi import APIRouter, HTTPException
from src.services.user_service import user_service
from src.models.user import UserCreate, User

router = APIRouter()

@router.post("/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    return await user_service.create_user(user)

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Benefits**:
- Routes stay thin (just HTTP concerns)
- Logic is testable independently
- Reusable across endpoints

**Mobile analogy**: Like ViewModels or Use Cases - business logic separate from UI/API layer.

## Directory Naming Conventions

**api/** - Route handlers (HTTP layer)
- Handles requests/responses
- Validates input
- Returns status codes
- Thin layer

**models/** - Data structures (Pydantic models)
- Request/response schemas
- Validation rules
- Serialization

**services/** - Business logic
- Core application logic
- Database operations
- External API calls

**db/** - Database configuration
- Connection setup
- Session management
- Base models (SQLAlchemy)

**tests/** - Test files
- Mirror source structure
- Use `test_` prefix

## Starting a New Project

**1. Create structure**:
```bash
mkdir -p src/{api,models,services,db} tests
touch src/__init__.py src/main.py
touch src/api/__init__.py src/models/__init__.py
touch src/services/__init__.py src/db/__init__.py
touch tests/__init__.py
```

**2. Set up virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install fastapi uvicorn pydantic
```

**3. Create main.py**:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello"}
```

**4. Run**:
```bash
uvicorn src.main:app --reload
```

## Configuration Management

Keep config in separate file:

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    debug: bool = False
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
```

Load from `.env`:
```
# .env
DATABASE_URL=postgresql://localhost/mydb
DEBUG=true
```

Use in app:
```python
from src.config import settings

@app.get("/info")
async def info():
    return {"app_name": settings.app_name}
```

## When to Split Files

**Keep in one file if**:
- <10 endpoints
- Learning/prototyping
- Quick scripts

**Split into multiple files if**:
- 10+ endpoints
- Multiple resources
- Team collaboration
- Long-term maintenance

## Key Takeaways

1. Start simple (one file), refactor as you grow
2. Use `APIRouter` to organize routes by resource
3. Separate models by purpose: Create, Update, Response
4. Keep business logic in services, not routes
5. Structure mirrors concerns: api/ = HTTP, services/ = logic, models/ = data
6. Use `prefix` and `tags` when including routers
7. Mirror structure in tests/
8. Configuration in separate file, loaded from .env
