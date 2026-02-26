# CRUD Endpoint Design

## Why This Matters

In mobile development, you design your API client interface: which endpoints to call, what data to send, what responses to expect. Now you're on the other side - **you're designing the API** that mobile apps will consume.

CRUD endpoints follow standard patterns that make APIs predictable and easy to use. Just like you expect `GET /users` to list users and `POST /users` to create one, your API should follow these conventions.

## The Five Standard CRUD Endpoints

For any resource (users, posts, products, etc.), you typically need five operations:

| Operation | HTTP Method | URL Pattern | Request Body | Response Status | Response Body |
|-----------|-------------|-------------|--------------|-----------------|---------------|
| **Create** | POST | `/users` | User data | 201 Created | Created user |
| **List** | GET | `/users` | None | 200 OK | Array of users |
| **Get by ID** | GET | `/users/{id}` | None | 200 OK | Single user |
| **Update** | PUT/PATCH | `/users/{id}` | Update data | 200 OK | Updated user |
| **Delete** | DELETE | `/users/{id}` | None | 204 No Content | None |

## URL Design Patterns

### Use Plural Nouns

```python
# ✅ Good
GET /users
POST /users
GET /users/123

# ❌ Bad
GET /user
POST /create-user
GET /getUserById?id=123
```

**Why plural?** The collection is plural (`/users`), and individual items are members of that collection (`/users/123`).

### Nest Related Resources

```python
# Get comments for a post
GET /posts/123/comments

# Create comment on a post
POST /posts/123/comments

# Get specific comment
GET /posts/123/comments/456
```

**Limit nesting to 2 levels.** Deeper nesting becomes hard to understand:

```python
# ⚠️ Too deep
GET /users/1/posts/2/comments/3/likes/4
```

### Use Query Parameters for Filtering

```python
# List with filters
GET /users?is_active=true&role=admin

# Pagination
GET /users?page=2&page_size=20

# Search
GET /users?search=alice

# Sorting
GET /users?sort_by=created_at&sort_order=desc
```

## HTTP Methods and Status Codes

### POST - Create Resource

```python
from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create new user - returns 201 Created."""
    # Create user in database
    user = User(**user_data.model_dump())
    # ... save to database
    return user
```

**Status Code:** **201 Created** (not 200 OK)

**Response:** The created resource with its ID

**Headers:** Optionally include `Location: /users/123` header

### GET - Retrieve Resource(s)

```python
@router.get("/users", response_model=list[UserResponse])
async def list_users():
    """List all users - returns 200 OK."""
    # Fetch users from database
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get single user - returns 200 OK or 404 Not Found."""
    user = # ... fetch from database
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Status Code:** **200 OK** (success) or **404 Not Found** (doesn't exist)

**Response:** Single object or array of objects

### PUT vs PATCH - Update Resource

**PUT** - Replace entire resource:

```python
class UserUpdate(BaseModel):
    username: str  # All fields required
    email: str
    is_active: bool

@router.put("/users/{user_id}", response_model=UserResponse)
async def replace_user(user_id: int, user_data: UserUpdate):
    """Replace user - all fields required."""
    # Replace all fields
    user.username = user_data.username
    user.email = user_data.email
    user.is_active = user_data.is_active
    return user
```

**PATCH** - Partial update:

```python
class UserPatch(BaseModel):
    username: str | None = None  # All fields optional
    email: str | None = None
    is_active: bool | None = None

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserPatch):
    """Update user - only provided fields changed."""
    update_dict = user_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)
    return user
```

**Use PATCH for most updates** - it's more flexible.

**Status Code:** **200 OK** (success) or **404 Not Found**

### DELETE - Remove Resource

```python
from fastapi import Response

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete user - returns 204 No Content."""
    user = # ... fetch from database
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user
    # ... delete from database

    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

**Status Code:** **204 No Content** (success, no response body) or **404 Not Found**

**Response:** Empty (204 means "success but no content to return")

## Request/Response Schema Design

### Separate Schemas for Different Operations

Don't reuse the same schema for create/update/response:

```python
# ✅ Good - separate schemas

class UserCreate(BaseModel):
    """Schema for creating user."""
    username: str
    email: str
    password: str  # Only for creation

class UserUpdate(BaseModel):
    """Schema for updating user."""
    username: str | None = None
    email: str | None = None
    # No password in updates (use separate endpoint)

class UserResponse(BaseModel):
    """Schema for API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    # No password in responses!
```

**Why separate?**
- **Security:** Don't expose password in responses
- **Clarity:** Create requires fields, update makes them optional
- **Flexibility:** Can add read-only fields (id, created_at) to response

### Response Schema with `from_attributes`

```python
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str

# Convert SQLAlchemy model to Pydantic
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)  # SQLAlchemy model
    return user  # FastAPI converts to UserResponse automatically
```

`from_attributes=True` lets Pydantic read from SQLAlchemy models.

## Complete CRUD Router Example

```python
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

# Schemas
class UserCreate(BaseModel):
    username: str
    email: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    is_active: bool | None = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

# Endpoints
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new user."""
    user = User(**user_data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List users with pagination."""
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user (partial update)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    update_dict = user_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

## Mobile Development Perspective

This is like designing your app's networking layer, but inverted:

| Mobile App Side | Backend API Side |
|-----------------|------------------|
| `apiClient.getUsers()` | `GET /users` endpoint |
| `apiClient.createUser(data)` | `POST /users` endpoint |
| `apiClient.updateUser(id, data)` | `PATCH /users/{id}` endpoint |
| Parse JSON response | Return Pydantic model |
| Handle 404, 400 errors | Raise HTTPException |

**Design APIs you'd want to consume.** If the endpoint feels awkward to use, redesign it.

## Key Takeaways

1. **Five standard CRUD operations:** Create (POST), List (GET), Get (GET /{id}), Update (PATCH), Delete (DELETE)
2. **Use plural nouns** for resource names: `/users`, not `/user`
3. **Correct status codes:** 201 for create, 200 for success, 204 for delete, 404 for not found
4. **Separate schemas** for create, update, and response (different fields)
5. **PATCH over PUT** for updates - partial updates are more flexible
6. **Query parameters** for filtering, pagination, sorting
7. **Nest related resources** up to 2 levels: `/posts/123/comments`
8. **`from_attributes=True`** lets Pydantic convert SQLAlchemy models automatically
