# Creating Your First Endpoint

## Why This Matters

This is like defining your first ViewController action that returns JSON. You've called these endpoints from mobile apps - now you'll create one from scratch.

## The Minimal FastAPI App

Every FastAPI app needs three things:

```python
from fastapi import FastAPI

# 1. Create the app instance
app = FastAPI()

# 2. Define a route with decorator
@app.get("/")
# 3. Define the handler function
async def read_root():
    return {"message": "Hello, World!"}
```

Let's break down each part.

## Creating the App Instance

```python
from fastapi import FastAPI

app = FastAPI()
```

The `app` object is your application. It:
- Registers routes (endpoints)
- Handles incoming requests
- Generates OpenAPI documentation
- Manages middleware and dependencies

**Mobile analogy**: Like your app's main router or navigation controller.

## Route Decorator

```python
@app.get("/")
```

The decorator tells FastAPI:
- **HTTP method**: `get`, `post`, `put`, `patch`, `delete`
- **Path**: The URL path (`/`, `/users`, `/posts/123`)

**Mobile analogy**: Like Retrofit's `@GET("/users")` or URLSession's request configuration.

## Handler Function

```python
async def read_root():
    return {"message": "Hello, World!"}
```

The function that runs when someone hits your endpoint. Notice:
- `async def` - Asynchronous by default (like Swift async functions)
- Returns a dict - FastAPI converts it to JSON automatically
- No manual serialization needed

## What Happens When a Request Comes In

```python
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
```

1. Client sends: `GET /` HTTP request
2. FastAPI matches the route `/` with method `GET`
3. Calls `read_root()` function
4. Converts dict to JSON
5. Sends response:
   ```
   HTTP/1.1 200 OK
   Content-Type: application/json

   {"message": "Hello, World!"}
   ```

**Mobile analogy**: Like your completion handler receiving `{"message": "Hello, World!"}`.

## Adding Path Parameters

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

The `{user_id}` in the path becomes a function parameter. FastAPI:
- Extracts it from the URL
- Converts it to `int` (type hint)
- Validates it (must be an integer)
- Passes it to your function

**Request**: `GET /users/123`
**Response**: `{"user_id": 123}`

**Request**: `GET /users/abc`
**Response**: `422 Validation Error` (not an integer)

**Mobile analogy**: Like extracting path components from a deep link URL.

## Adding Query Parameters

```python
@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

Function parameters not in the path become query parameters:

**Request**: `GET /items?skip=20&limit=50`
**Response**: `{"skip": 20, "limit": 50}`

**Request**: `GET /items` (uses defaults)
**Response**: `{"skip": 0, "limit": 10}`

**Mobile analogy**: Like URLComponents query items.

## Return Values

FastAPI automatically converts return values to JSON:

**Dict**:
```python
return {"name": "Alice"}
# → {"name": "Alice"}
```

**List**:
```python
return [1, 2, 3]
# → [1, 2, 3]
```

**Pydantic Model** (covered later):
```python
return User(name="Alice", email="alice@example.com")
# → {"name": "Alice", "email": "alice@example.com"}
```

**None**:
```python
return None
# → null
```

## Status Codes

By default, FastAPI returns:
- `200 OK` for GET
- `200 OK` for POST (should be 201, we'll fix this)

Customize with `status_code`:
```python
from fastapi import status

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user():
    return {"message": "User created"}
```

## Complete Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {"status": "healthy"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a user by ID."""
    # In real app, query database here
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    }

@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    """List items with pagination."""
    # In real app, query database here
    items = [{"id": i, "name": f"Item {i}"} for i in range(skip, skip + limit)]
    return {"items": items, "skip": skip, "limit": limit}
```

## Running Your App

Save as `main.py`, then run:
```bash
uvicorn main:app --reload
```

- `main` - Python file name (main.py)
- `app` - FastAPI instance variable name
- `--reload` - Auto-restart on file changes (like Xcode's hot reload)

Visit http://localhost:8000/docs to see interactive documentation!

## Key Takeaways

1. Every endpoint needs: decorator + async function + return value
2. `@app.get("/path")` maps HTTP method and path to function
3. Path parameters go in URL: `/users/{user_id}`
4. Query parameters come from function defaults: `skip: int = 0`
5. Return dicts/lists - FastAPI handles JSON serialization
6. `async def` for all handlers (async-first)
7. uvicorn runs your app with hot-reload for development
