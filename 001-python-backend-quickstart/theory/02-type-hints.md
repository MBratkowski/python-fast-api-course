# Type Hints in Python

## Why This Matters

Coming from Swift/Kotlin, you expect type safety. Python is dynamically typed, but **type hints** give you:
- IDE autocomplete
- Error detection with mypy
- Self-documenting code
- Better FastAPI integration (it uses types for validation!)

## Basic Type Hints

```python
# Variables
name: str = "Alice"
age: int = 30
price: float = 19.99
is_active: bool = True

# Functions
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b
```

## Common Types

```python
from typing import Optional, List, Dict, Any

# Optional (like Swift Optional or Kotlin nullable)
def find_user(id: int) -> Optional[str]:
    users = {1: "Alice"}
    return users.get(id)  # Returns None if not found

# Python 3.10+ syntax (cleaner)
def find_user(id: int) -> str | None:
    ...

# Collections
def get_names() -> list[str]:
    return ["Alice", "Bob"]

def get_ages() -> dict[str, int]:
    return {"Alice": 30, "Bob": 25}
```

## Complex Types

```python
from typing import Union, Callable, TypeVar

# Union types
def process(value: int | str) -> str:
    return str(value)

# Callable (function types)
def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Generic types
T = TypeVar('T')

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

## Type Hints with Classes

```python
class User:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email

    def get_display_name(self) -> str:
        return self.name.title()

def create_user(name: str, email: str) -> User:
    return User(name, email)
```

## FastAPI Uses Types!

This is why types matter for backend:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:  # FastAPI validates user_id is int!
    return {"user_id": user_id}
```

FastAPI automatically:
- Validates `user_id` is an integer
- Returns 422 error if validation fails
- Generates OpenAPI documentation

## Type Checking with mypy

```bash
# Install
pip install mypy

# Run type checker
mypy src/

# Example error:
# error: Argument 1 to "greet" has incompatible type "int"; expected "str"
```

## Key Takeaways

1. **Use type hints everywhere** - they're optional but invaluable
2. **`Optional[T]`** or **`T | None`** for nullable values
3. **FastAPI uses types for validation** - this is powerful!
4. **Run mypy** to catch type errors before runtime
