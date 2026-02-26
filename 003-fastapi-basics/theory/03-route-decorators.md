# Route Decorators

## Why This Matters

Route decorators are like Retrofit annotations (@GET, @POST) or URLSession request methods. They define what HTTP method and path trigger your handler function.

## The Five Main Decorators

FastAPI provides one decorator for each HTTP method:

```python
@app.get("/resource")       # Read
@app.post("/resource")      # Create
@app.put("/resource/{id}")  # Replace
@app.patch("/resource/{id}")  # Update
@app.delete("/resource/{id}")  # Delete
```

## @app.get() - Reading Data

Use for retrieving data without modifications:

```python
@app.get("/users")
async def list_users():
    return {"users": [{"id": 1, "name": "Alice"}]}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": f"User {user_id}"}
```

**Mobile analogy**: Like your network call to fetch a user list or profile.

## @app.post() - Creating Resources

Use for creating new resources:

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(user: UserCreate):
    # In real app: save to database
    return {"id": 123, "name": user.name, "email": user.email}
```

Request body is passed as a parameter with type hint.

**Mobile analogy**: Like POSTing a form to create a new item.

## @app.put() - Replacing Entire Resource

Use for full resource replacement:

```python
class UserUpdate(BaseModel):
    name: str
    email: str
    bio: str

@app.put("/users/{user_id}")
async def replace_user(user_id: int, user: UserUpdate):
    # Replace all fields
    return {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "bio": user.bio
    }
```

All fields required - this replaces the entire resource.

## @app.patch() - Partial Updates

Use for updating specific fields:

```python
from pydantic import BaseModel

class UserPatch(BaseModel):
    name: str | None = None
    bio: str | None = None

@app.patch("/users/{user_id}")
async def update_user(user_id: int, user: UserPatch):
    # Update only provided fields
    updates = {}
    if user.name is not None:
        updates["name"] = user.name
    if user.bio is not None:
        updates["bio"] = user.bio

    return {"id": user_id, **updates}
```

Fields are optional - only provided fields get updated.

**Mobile analogy**: Like updating just the profile photo without resending the entire profile.

## @app.delete() - Removing Resources

Use for deleting resources:

```python
from fastapi import status

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    # In real app: delete from database
    return None  # 204 = no content in response
```

Often returns 204 No Content (empty response).

## Path Parameters

Capture dynamic parts of the URL:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

**Requests**:
- `GET /users/123` → `{"user_id": 123}`
- `GET /users/5/posts/42` → `{"user_id": 5, "post_id": 42}`

Path parameters are always required.

## Multiple Routes on Same Path

Different methods can use the same path:

```python
@app.get("/users")
async def list_users():
    return {"users": [...]}

@app.post("/users")
async def create_user(user: UserCreate):
    return {"id": 123, **user.model_dump()}
```

FastAPI routes based on method + path combination.

## Route Priority

Routes are matched in order of definition. More specific routes should come first:

```python
# Specific route first
@app.get("/users/me")
async def get_current_user():
    return {"user": "current user"}

# Generic route second
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id}
```

If reversed, `GET /users/me` would match `{user_id}` and pass "me" as the ID.

## Response Status Codes

Customize response status code:

```python
from fastapi import status

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    return {"id": 123, **user.model_dump()}

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    return None
```

Use `fastapi.status` constants for readability.

## Tags for Documentation

Group endpoints in docs with tags:

```python
@app.get("/users", tags=["users"])
async def list_users():
    return {"users": []}

@app.post("/users", tags=["users"])
async def create_user(user: UserCreate):
    return {"id": 123}

@app.get("/posts", tags=["posts"])
async def list_posts():
    return {"posts": []}
```

Tags organize endpoints in Swagger UI documentation.

## Summary and Description

Add documentation to your endpoints:

```python
@app.get(
    "/users/{user_id}",
    summary="Get user by ID",
    description="Retrieve a single user by their unique ID"
)
async def get_user(user_id: int):
    """
    Get user details.

    This endpoint returns user information including:
    - User ID
    - Name
    - Email
    """
    return {"id": user_id}
```

Use docstrings (triple quotes) or decorator parameters.

## Complete CRUD Example

```python
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

# In-memory storage (use database in real app)
items = {}
next_id = 1

@app.get("/items", tags=["items"])
async def list_items():
    """List all items."""
    return {"items": list(items.values())}

@app.get("/items/{item_id}", tags=["items"])
async def get_item(item_id: int):
    """Get single item by ID."""
    return items.get(item_id, {"error": "Not found"})

@app.post("/items", status_code=status.HTTP_201_CREATED, tags=["items"])
async def create_item(item: Item):
    """Create a new item."""
    global next_id
    items[next_id] = {"id": next_id, **item.model_dump()}
    item_id = next_id
    next_id += 1
    return items[item_id]

@app.patch("/items/{item_id}", tags=["items"])
async def update_item(item_id: int, item: Item):
    """Update an existing item."""
    if item_id in items:
        items[item_id].update(item.model_dump())
    return items.get(item_id, {"error": "Not found"})

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["items"])
async def delete_item(item_id: int):
    """Delete an item."""
    items.pop(item_id, None)
    return None
```

## Key Takeaways

1. Use `@app.get()`, `@app.post()`, `@app.put()`, `@app.patch()`, `@app.delete()` for different HTTP methods
2. Path parameters: `/users/{user_id}` → function parameter `user_id`
3. Same path can have different methods (GET /users and POST /users)
4. Order matters - specific routes before generic ones
5. Set `status_code` for proper HTTP responses (201 for create, 204 for delete)
6. Use `tags` to organize endpoints in documentation
7. Add docstrings for better API documentation
