# Data Classes

## Why This Matters

You're used to Swift `struct` or Kotlin `data class` - simple containers for data with automatic equality, copying, etc. Python's `@dataclass` gives you the same thing.

## The Problem

Without dataclasses, you write boilerplate:

```python
# Boring, repetitive code
class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.id == other.id and self.name == other.name and self.email == other.email
```

## The Solution: @dataclass

```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

# That's it! You get __init__, __repr__, __eq__ automatically

user = User(id=1, name="Alice", email="alice@example.com")
print(user)  # User(id=1, name='Alice', email='alice@example.com')
```

## Default Values

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None  # Optional with default
    is_active: bool = True       # Default value

user = User(id=1, name="Alice")
# User(id=1, name='Alice', email=None, is_active=True)
```

## Immutable Dataclasses

Like Swift structs, you can make them immutable:

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

point = Point(1.0, 2.0)
point.x = 3.0  # Error! FrozenInstanceError
```

## Dataclass Methods

```python
from dataclasses import dataclass, field

@dataclass
class User:
    id: int
    name: str
    email: str
    tags: list[str] = field(default_factory=list)  # Mutable default

    def get_display_name(self) -> str:
        return self.name.title()

    @property
    def is_valid_email(self) -> bool:
        return "@" in self.email
```

## Pydantic: Dataclasses on Steroids

FastAPI uses **Pydantic** models which are like dataclasses with validation:

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    name: str
    email: EmailStr  # Validates email format!

# Automatic validation
user = User(id=1, name="Alice", email="not-an-email")
# ValidationError: value is not a valid email address
```

We'll cover Pydantic in depth in Module 005.

## When to Use What

| Use Case | Solution |
|----------|----------|
| Internal data structures | `@dataclass` |
| API request/response | Pydantic `BaseModel` |
| Database models | SQLAlchemy models |
| Config/settings | Pydantic `BaseSettings` |

## Key Takeaways

1. **`@dataclass`** eliminates boilerplate for data containers
2. **`frozen=True`** for immutable data
3. **Pydantic** is used in FastAPI for validation
4. Use the right tool: dataclass for internal, Pydantic for APIs
