# Field Validation

## Why This Matters

In mobile development, you validate form inputs manually: "password must be 8+ characters", "email must be valid", "age must be 0-120". In Pydantic, you declare these rules once in your model using `Field()`, and validation happens automatically. It's like having form validation built into your data classes.

## The Field() Function

`Field()` adds validation constraints and metadata to model fields:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    bio: str | None = Field(default=None, max_length=500)
```

## String Validation

**Length constraints:**
```python
from pydantic import BaseModel, Field

class Post(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=10)
    slug: str = Field(min_length=3, max_length=50, pattern=r'^[a-z0-9-]+$')

# Valid
post = Post(
    title="My Post",
    content="This is the content of my post.",
    slug="my-post"
)

# Invalid - title too long
try:
    post = Post(
        title="x" * 101,  # ❌ Exceeds max_length
        content="Content",
        slug="slug"
    )
except ValidationError as e:
    print(e)
```

**Pattern matching (regex):**
```python
class Account(BaseModel):
    username: str = Field(pattern=r'^[a-zA-Z0-9_]{3,20}$')
    phone: str = Field(pattern=r'^\d{3}-\d{3}-\d{4}$')

# Valid
account = Account(
    username="john_doe123",
    phone="555-123-4567"
)
```

## Numeric Validation

**Greater than / Less than:**
```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    price: float = Field(gt=0)  # Greater than 0
    quantity: int = Field(ge=0)  # Greater than or equal to 0
    discount: float = Field(ge=0, le=1)  # Between 0 and 1
    rating: int = Field(ge=1, le=5)  # Between 1 and 5

# Valid
product = Product(
    price=99.99,
    quantity=10,
    discount=0.15,
    rating=4
)
```

**Constraints:**
- `gt` = greater than
- `ge` = greater than or equal
- `lt` = less than
- `le` = less than or equal
- `multiple_of` = must be multiple of value

```python
class Pagination(BaseModel):
    page_size: int = Field(ge=1, le=100, multiple_of=10)

# Valid: 10, 20, 30, ..., 100
# Invalid: 15, 105, 0
```

## Documentation with Field

Add descriptions for API documentation:

```python
class User(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username for login (alphanumeric)"
    )
    age: int = Field(
        ge=0,
        le=150,
        description="User's age in years"
    )
```

These descriptions appear in FastAPI's auto-generated docs.

## Default Values

```python
class Settings(BaseModel):
    debug: bool = Field(default=False, description="Enable debug mode")
    port: int = Field(default=8000, ge=1024, le=65535)
    host: str = Field(default="localhost")

# Use defaults
settings = Settings()
print(settings.debug)  # False
print(settings.port)  # 8000
```

## Field Aliases

Use different names in JSON vs Python:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(alias="userName")
    email_address: str = Field(alias="emailAddress")

# JSON uses camelCase
user_data = {
    "userName": "alice",
    "emailAddress": "alice@example.com"
}

user = User(**user_data)
print(user.username)  # "alice"
print(user.email_address)  # "alice@example.com"

# Serialize back to JSON with aliases
print(user.model_dump(by_alias=True))
# {"userName": "alice", "emailAddress": "alice@example.com"}
```

## Common Field Types

**UUID:**
```python
from pydantic import BaseModel, Field
from uuid import UUID

class Entity(BaseModel):
    id: UUID
    name: str

entity = Entity(
    id="550e8400-e29b-41d4-a716-446655440000",
    name="Test"
)
```

**Datetime:**
```python
from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    name: str
    created_at: datetime

event = Event(
    name="Meeting",
    created_at="2026-02-26T10:00:00Z"  # Auto-converted to datetime
)
```

**Email:**
```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr  # Requires: pip install email-validator

user = User(email="alice@example.com")
```

## Annotated Pattern (Modern)

Modern Pydantic v2 uses `Annotated`:

```python
from pydantic import BaseModel, Field
from typing import Annotated

class User(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    age: Annotated[int, Field(ge=0, le=150)]
    bio: Annotated[str | None, Field(max_length=500)] = None
```

This is especially useful in FastAPI for consistency with Path/Query/Header.

## Key Takeaways

1. **Field() adds validation constraints** - min_length, max_length, ge, le, pattern
2. **Constraints are declarative** - define once, validate everywhere
3. **String constraints:** min_length, max_length, pattern (regex)
4. **Number constraints:** gt, ge, lt, le, multiple_of
5. **Descriptions appear in docs** - FastAPI uses them for OpenAPI
6. **Aliases map JSON to Python** - camelCase ↔ snake_case
7. **Use Annotated for modern style** - `Annotated[str, Field(...)]`
