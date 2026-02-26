# Schema Patterns: Create vs Update vs Response

## Why This Matters

In mobile apps, you send different data shapes for different operations: creating a user (send username, password), updating (send only changed fields), receiving user data (includes id, excludes password). Backend needs separate schemas for each. The "Create/Update/Response" pattern is the RESTful way to model these differences.

## The Problem

Don't use one model for everything:

```python
# BAD - Don't do this
class User(BaseModel):
    id: int | None = None  # Only for responses
    username: str
    password: str  # Exposed in responses!
    created_at: str | None = None  # Only for responses

# Creates confusion:
# - Client must send id=None when creating?
# - Password sent in all responses?
# - Update requires all fields?
```

## The Solution: Separate Schemas

Use different schemas for different operations:

```python
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    """Shared fields across all schemas."""
    username: str = Field(min_length=3, max_length=50)
    email: str

class UserCreate(UserBase):
    """Schema for POST /users (creating user)."""
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    """Schema for PATCH /users/{id} (partial update)."""
    username: str | None = None
    email: str | None = None
    password: str | None = None
    # All fields optional - only provided fields updated

class UserResponse(UserBase):
    """Schema for GET /users (response to client)."""
    id: int
    is_active: bool
    created_at: str
    # No password field

class UserInDB(UserBase):
    """Schema for database model."""
    id: int
    hashed_password: str  # Not raw password
    is_active: bool
    created_at: str
```

## Usage with FastAPI

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """
    Client sends: UserCreate (username, email, password)
    Server returns: UserResponse (id, username, email, is_active, created_at)
    """
    # Hash password
    hashed_pwd = hash_password(user.password)

    # Save to database
    db_user = {
        "id": 123,
        "username": user.username,
        "email": user.email,
        "is_active": True,
        "created_at": "2026-02-26T10:00:00Z"
    }

    return db_user  # response_model filters to UserResponse fields

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Returns UserResponse (no password)."""
    user = database.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    """
    Client sends: UserUpdate (only fields to change)
    Server returns: UserResponse (full updated user)
    """
    db_user = database.get_user(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    database.save(db_user)
    return db_user
```

## Base Model Pattern

Share common fields with inheritance:

```python
class ProductBase(BaseModel):
    """Shared product fields."""
    name: str
    description: str
    price: float
    category: str

class ProductCreate(ProductBase):
    """Creating product - inherits all base fields."""
    pass

class ProductUpdate(BaseModel):
    """Updating product - all fields optional."""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None

class ProductResponse(ProductBase):
    """Product response - base fields + server-generated."""
    id: int
    created_at: str
    updated_at: str
```

## Partial Updates (PATCH)

```python
@app.patch("/products/{product_id}", response_model=ProductResponse)
async def partial_update(product_id: int, update: ProductUpdate):
    """Update only provided fields."""
    product = database.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404)

    # Only update fields that were provided
    update_data = update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    database.save(product)
    return product

# Client can send:
# {"name": "New Name"}  # Only update name
# {"price": 99.99, "category": "sale"}  # Update price and category
```

## Full Updates (PUT)

```python
class ProductPut(ProductBase):
    """Full update - all fields required."""
    pass

@app.put("/products/{product_id}", response_model=ProductResponse)
async def full_update(product_id: int, update: ProductPut):
    """Replace entire product (all fields required)."""
    product = database.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404)

    # Replace all fields
    for field, value in update.model_dump().items():
        setattr(product, field, value)

    database.save(product)
    return product
```

## ORM Integration

Use `from_attributes` for ORM models:

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # db_user is SQLAlchemy model
    db_user = database.query(User).filter(User.id == user_id).first()

    # Pydantic reads from db_user.id, db_user.username, etc.
    return db_user
```

## Complete Pattern Example

```python
# Base
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str

# Create
class PostCreate(PostBase):
    pass

# Update (partial)
class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None

# Response
class PostResponse(PostBase):
    id: int
    author_id: int
    published: bool
    created_at: str
    updated_at: str

# Database
class PostInDB(PostBase):
    id: int
    author_id: int
    published: bool
    created_at: str
    updated_at: str
```

## Mobile Developer Context

| Mobile | Backend Schema |
|--------|----------------|
| Create user form | `UserCreate` schema |
| Update profile form | `UserUpdate` schema |
| Display user info | `UserResponse` schema |
| Optional fields in form | All optional in `Update` schema |
| Required fields in form | Required in `Create` schema |

## Key Takeaways

1. **Separate schemas for different operations** - Create/Update/Response
2. **Create schema: input for POST** - what client sends
3. **Update schema: all fields optional** - for PATCH operations
4. **Response schema: output for GET** - what client receives
5. **Base schema shares common fields** - use inheritance
6. **Never expose passwords in responses** - omit from Response schema
7. **`from_attributes=True` for ORMs** - reads from object attributes
8. **`exclude_unset=True` for partial updates** - only include provided fields
