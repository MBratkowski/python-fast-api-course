# Path Parameters

## Why This Matters

In your mobile app, when you tap on a user's profile, the app navigates to `/user/123` where `123` is the user's ID. On the backend, you need to extract that ID from the URL path. That's what path parameters do - they capture dynamic parts of the URL, just like route parameters in your mobile navigation.

## What are Path Parameters?

Path parameters are variable parts of your URL path. They're defined with curly braces `{}` in the route decorator.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """user_id is extracted from the URL path."""
    return {"user_id": user_id, "name": "Alice"}
```

When a client requests `GET /users/123`, FastAPI:
1. Matches the route pattern
2. Extracts `123` from the path
3. Converts it to `int` (because of the type hint)
4. Passes it to your function as `user_id`

## Automatic Type Conversion

FastAPI automatically converts path parameters based on type hints:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # user_id is an integer
    return {"user_id": user_id, "type": type(user_id).__name__}

@app.get("/posts/{slug}")
async def get_post(slug: str):
    # slug is a string
    return {"slug": slug, "type": type(slug).__name__}

@app.get("/settings/{is_enabled}")
async def toggle_setting(is_enabled: bool):
    # is_enabled is a boolean (true/false, 1/0)
    return {"enabled": is_enabled, "type": type(is_enabled).__name__}
```

**What happens on type mismatch?**
- Request: `GET /users/abc`
- Response: `422 Unprocessable Entity` with a clear error message
- FastAPI tells the client: "Expected integer, got string"

## Path Parameter Validation

Use the `Path()` function from `fastapi` to add constraints:

```python
from fastapi import FastAPI, Path
from typing import Annotated

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(
    user_id: Annotated[int, Path(ge=1, description="User ID must be positive")]
):
    """ge=1 means 'greater than or equal to 1'."""
    return {"user_id": user_id}
```

**Validation constraints:**
- `ge` = greater than or equal
- `le` = less than or equal
- `gt` = greater than
- `lt` = less than
- `min_length`, `max_length` (for strings)
- `pattern` (regex for strings)

```python
@app.get("/products/{product_id}")
async def get_product(
    product_id: Annotated[int, Path(ge=1, le=999999)]
):
    """Product ID must be between 1 and 999999."""
    return {"product_id": product_id}

@app.get("/files/{file_path:path}")
async def get_file(
    file_path: Annotated[str, Path(min_length=1)]
):
    """The :path allows capturing slashes in the path."""
    return {"file_path": file_path}
```

## Multiple Path Parameters

You can have multiple path parameters in one route:

```python
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(
    user_id: Annotated[int, Path(ge=1)],
    post_id: Annotated[int, Path(ge=1)]
):
    return {
        "user_id": user_id,
        "post_id": post_id,
        "message": f"Post {post_id} by user {user_id}"
    }
```

## The :path Converter

For capturing full paths including slashes:

```python
@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    """Matches /files/docs/api/intro.md"""
    return {"file_path": file_path}
```

Without `:path`, FastAPI stops at the first `/` and wouldn't match nested paths.

## Mobile Developer Context

| Mobile Navigation | FastAPI Path Params |
|-------------------|---------------------|
| `router.push('/user/123')` | `@app.get("/users/{user_id}")` |
| Extract `userId` from route | FastAPI extracts automatically |
| Type-safe route params (Swift/Kotlin) | Type hints + validation |
| Invalid ID shows error screen | Returns 422 with error details |

## Key Takeaways

1. **Path parameters capture dynamic URL parts** - use `{param_name}` in route
2. **Type hints enable automatic conversion** - `user_id: int` converts string to int
3. **Validation happens before your function runs** - invalid data returns 422
4. **`Path()` adds constraints** - `ge`, `le`, `min_length`, etc.
5. **`:path` converter captures full paths** - for nested file paths
6. **Order matters** - specific routes before general: `/users/me` before `/users/{user_id}`
