# Module 001: Python for Backend Developers

## Why This Module?

You're already a developer. You don't need to learn what a variable or loop is. This module covers Python-specific concepts you'll need for backend development - the stuff that's different from Swift/Kotlin/Dart/JavaScript.

## What You'll Learn

- Python environment setup (virtual environments)
- Type hints (similar to Swift/Kotlin types)
- Async/await (you know this from mobile!)
- Python's data structures for API work
- Decorators (used everywhere in FastAPI)

## Time Estimate

- **Already know Python**: Skip to exercises (30 min)
- **New to Python**: Full module (2 hours)

## Quick Assessment

Can you read this code and understand what it does?

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None

async def get_user(user_id: int) -> User | None:
    users = {1: User(1, "Alice", "alice@example.com")}
    return users.get(user_id)
```

**If yes** → Jump to [exercises](exercises/) and [project](project/)
**If no** → Start with [theory](theory/)

## Module Contents

### Theory
1. [Environment Setup](theory/01-environment.md) - venv, pip, project structure
2. [Type Hints](theory/02-type-hints.md) - Python's optional typing system
3. [Data Classes](theory/03-dataclasses.md) - Like Swift structs or Kotlin data classes
4. [Async Python](theory/04-async-basics.md) - async/await fundamentals
5. [Decorators](theory/05-decorators.md) - Function wrappers (used by FastAPI)

### Exercises
- [Exercise 1](exercises/01_types.py) - Type hints practice
- [Exercise 2](exercises/02_dataclasses.py) - Model creation
- [Exercise 3](exercises/03_async.py) - Async functions

### Project
Build a simple data processing script using everything learned.

## Key Differences from Mobile Languages

| Concept | Swift/Kotlin | Python |
|---------|--------------|--------|
| Types | Required | Optional (but use them!) |
| Null safety | Optional/nullable | `Optional[T]` or `T \| None` |
| Data models | struct/data class | `@dataclass` or Pydantic |
| Async | async/await | async/await (very similar!) |
| Package manager | SPM/Gradle | pip + requirements.txt |
