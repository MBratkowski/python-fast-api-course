# FastAPI Introduction

## Why This Matters

FastAPI is to Python APIs what SwiftUI is to iOS — modern, declarative, type-safe. If you've used Swift types or Kotlin data classes, you'll feel right at home with FastAPI's type-hint-driven development.

## What is FastAPI?

FastAPI is a Python web framework designed specifically for building APIs. It's one of the fastest Python frameworks available and emphasizes developer experience through automatic validation and documentation.

Key features:
- **Type-hint driven**: Uses Python type hints for validation and docs
- **Automatic validation**: Catches errors before your code runs
- **Auto-generated docs**: Swagger UI and ReDoc built-in
- **Async-first**: Native async/await support
- **Fast**: Performance comparable to Node.js and Go

## Why FastAPI?

**Coming from mobile development, you'll appreciate:**

1. **Type safety** - Like Swift/Kotlin, catch errors at "compile time" (validation)
2. **Auto-documentation** - Like having Postman built into your API
3. **Fast iteration** - Hot-reload like Xcode/Android Studio
4. **Modern syntax** - Async/await patterns you already know

## FastAPI vs Other Frameworks

| Framework | Speed | Type Safety | Auto Docs | Learning Curve |
|-----------|-------|-------------|-----------|----------------|
| FastAPI | ⚡⚡⚡ | ✅ | ✅ | Easy |
| Flask | ⚡ | ❌ | ❌ | Easy |
| Django | ⚡⚡ | ❌ | ⚠️ | Steep |
| Express (Node) | ⚡⚡⚡ | ⚠️ | ❌ | Easy |

FastAPI gives you the best of all worlds: speed, safety, and developer experience.

## The FastAPI Philosophy

**1. Type hints everywhere**
```python
# Your mobile code
func getUser(id: Int) -> User? { ... }

# FastAPI equivalent
async def get_user(id: int) -> User | None: ...
```

**2. Automatic validation**
```python
# Instead of manual validation:
if not isinstance(user_id, int):
    raise ValueError("ID must be integer")

# FastAPI does this automatically:
async def get_user(user_id: int):  # ✅ Validated automatically
    ...
```

**3. Self-documenting**
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID."""
    ...
# Generates OpenAPI docs automatically
```

## Core Components

**1. Application Instance**
```python
from fastapi import FastAPI

app = FastAPI()
```

**2. Route Decorators**
```python
@app.get("/")      # Like @GetMapping in Spring
@app.post("/")     # Like @POST in JAX-RS
@app.put("/")
@app.delete("/")
```

**3. Type Hints**
```python
async def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age}
```

**4. Pydantic Models**
```python
from pydantic import BaseModel

class User(BaseModel):  # Like Swift structs or Kotlin data classes
    name: str
    email: str
```

## Your First FastAPI App

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
```

Run it:
```bash
uvicorn main:app --reload
```

Visit:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

**Mobile analogy**: Like creating a ViewController with an action method that returns JSON.

## What Makes It Fast?

1. **Async-first**: Non-blocking I/O like mobile async/await
2. **Starlette foundation**: Built on one of Python's fastest web frameworks
3. **Pydantic v2**: Rust-powered validation (5-50x faster than v1)
4. **No ORM overhead**: Use any database library you want

Performance is comparable to Node.js and Go for I/O-bound workloads.

## When to Use FastAPI

**Good fit:**
- REST APIs for mobile/web apps
- Microservices
- Data APIs (ML models, data processing)
- Real-time APIs (WebSockets)

**Not ideal for:**
- Full-stack web apps with templates (use Django or Flask)
- Simple scripts (overkill)

## Key Takeaways

1. FastAPI is designed for building modern APIs quickly
2. Type hints drive validation, documentation, and editor support
3. Async-first architecture like mobile async/await patterns
4. Automatic OpenAPI documentation (Swagger/ReDoc)
5. Fast development iteration with hot-reload
6. Performance comparable to Node.js and Go
7. If you know Swift/Kotlin types, you'll understand FastAPI types
