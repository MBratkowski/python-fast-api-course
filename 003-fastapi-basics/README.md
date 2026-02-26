# Module 003: FastAPI Basics

## Why This Module?

FastAPI is the framework you'll use to build APIs. It's modern, fast, and developer-friendly - with automatic documentation and type validation.

## What You'll Learn

- Creating a FastAPI application
- Defining route handlers
- Running with Uvicorn
- Automatic OpenAPI documentation
- Interactive API testing with Swagger UI

## Topics

### Theory
1. FastAPI Introduction & Philosophy
2. Creating Your First Endpoint
3. Route Decorators (@app.get, @app.post, etc.)
4. Running the Development Server
5. Swagger UI & ReDoc Documentation
6. Project Structure Patterns

### Exercises
- Create a "Hello World" API
- Build multiple endpoints for a resource
- Explore the auto-generated documentation

### Project
Create a simple quotes API with endpoints to list, get, and add quotes.

## Quick Start

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

Run it:
```bash
uvicorn main:app --reload
```

Visit:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
