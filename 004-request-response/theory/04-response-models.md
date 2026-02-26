# Response Models

## Why This Matters

In your mobile app, you decode JSON responses into typed models (Codable in Swift, data classes in Kotlin). On the backend, you define what shape that JSON takes. Response models ensure you send consistent, validated data to clients - and they automatically generate API documentation showing clients exactly what to expect.

## What are Response Models?

Response models are Pydantic classes that define the structure of your API responses. They serve three purposes:

1. **Type safety** - ensures you return the right data structure
2. **Field filtering** - controls which fields get sent to clients
3. **Documentation** - auto-generates OpenAPI schema for your API docs

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    """Defines the shape of user response data."""
    id: int
    name: str
    email: str
    is_active: bool = True

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    response_model=UserResponse ensures:
    - Return value matches UserResponse structure
    - Only id, name, email, is_active are included
    - OpenAPI docs show this schema
    """
    user_data = {
        "id": user_id,
        "name": "Alice",
        "email": "alice@example.com",
        "is_active": True,
        "password_hash": "secret123",  # This won't be in response!
    }
    return user_data
```

FastAPI will:
1. Validate the return value matches `UserResponse`
2. Remove any extra fields (like `password_hash`)
3. Return only: `{"id": 1, "name": "Alice", "email": "alice@example.com", "is_active": true}`

## Why Separate Response Models?

**The danger of reusing models:**

```python
# BAD - Don't do this
class User(BaseModel):
    id: int
    name: str
    email: str
    password_hash: str  # ⚠️ Will be exposed to clients!

@app.post("/users", response_model=User)
async def create_user(user: User):
    return user  # ❌ Sends password_hash to client
```

**The safe approach:**

```python
# GOOD - Separate request and response models
class UserCreate(BaseModel):
    """What clients send when creating a user."""
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    """What clients receive back."""
    id: int
    name: str
    email: str
    created_at: str

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    # Hash password, save to database, generate ID
    user_data = {
        "id": 123,
        "name": user.name,
        "email": user.email,
        "created_at": "2026-02-26T10:00:00Z"
    }
    return user_data  # ✅ No password in response
```

## Response Model in Action

```python
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """
    Return value MUST match Product shape.
    Extra fields are filtered out.
    """
    # Simulate database response with extra fields
    product_data = {
        "id": product_id,
        "name": "Laptop",
        "price": 999.99,
        "in_stock": True,
        "internal_cost": 500.00,  # Won't be in response
        "supplier_id": 42,  # Won't be in response
    }

    return product_data

# Client receives only:
# {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": true}
```

## List Responses

For endpoints that return multiple items:

```python
@app.get("/products", response_model=list[Product])
async def list_products():
    """
    response_model=list[Product] means:
    - Return value is a list
    - Each item matches Product schema
    """
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": True},
        {"id": 2, "name": "Mouse", "price": 29.99, "in_stock": True},
    ]
    return products
```

**Better approach with envelope:**

```python
class ProductListResponse(BaseModel):
    """Envelope pattern - allows adding metadata."""
    products: list[Product]
    total: int
    page: int

@app.get("/products", response_model=ProductListResponse)
async def list_products(skip: int = 0, limit: int = 10):
    """
    Envelope allows adding pagination metadata.
    Future-proof: can add fields without breaking clients.
    """
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": True},
        {"id": 2, "name": "Mouse", "price": 29.99, "in_stock": True},
    ]

    return {
        "products": products,
        "total": 100,
        "page": skip // limit + 1
    }
```

## Computed Fields

Add fields that don't exist in your database:

```python
from pydantic import BaseModel, computed_field

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed field - calculated from other fields."""
        return f"{self.first_name} {self.last_name}"

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {
        "id": user_id,
        "first_name": "Alice",
        "last_name": "Smith"
    }

# Client receives:
# {"id": 1, "first_name": "Alice", "last_name": "Smith", "full_name": "Alice Smith"}
```

## Excluding Fields

Control which fields are sent to clients:

```python
class UserFull(BaseModel):
    id: int
    name: str
    email: str
    password_hash: str
    internal_notes: str

# Exclude sensitive fields
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = UserFull(
        id=user_id,
        name="Alice",
        email="alice@example.com",
        password_hash="secret",
        internal_notes="VIP customer"
    )

    # Exclude specific fields from response
    return user.model_dump(exclude={"password_hash", "internal_notes"})

# Client receives only: id, name, email
```

**Better approach:** Define separate response model without sensitive fields (as shown earlier).

## Response Model Inheritance

Share common fields across models:

```python
class BaseResponse(BaseModel):
    """Common fields for all responses."""
    id: int
    created_at: str
    updated_at: str

class UserResponse(BaseResponse):
    """User response inherits base fields."""
    name: str
    email: str
    # Automatically includes: id, created_at, updated_at

class PostResponse(BaseResponse):
    """Post response also inherits base fields."""
    title: str
    content: str
    author_id: int
    # Automatically includes: id, created_at, updated_at

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {
        "id": user_id,
        "name": "Alice",
        "email": "alice@example.com",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-02-26T10:00:00Z"
    }
```

## Response Model Config

Configure how models behave:

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    """Response model with ORM mode enabled."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str

# Now you can return ORM objects directly
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # user_obj is an SQLAlchemy model or similar ORM object
    user_obj = database.get_user(user_id)

    # from_attributes=True allows reading from object attributes
    return user_obj  # FastAPI reads user_obj.id, user_obj.name, user_obj.email
```

## Optional Fields in Responses

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    bio: str | None = None  # Optional field
    avatar_url: str | None = None  # Optional field

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {
        "id": user_id,
        "name": "Alice",
        "email": "alice@example.com",
        # bio and avatar_url not provided - will be null in response
    }

# Client receives:
# {"id": 1, "name": "Alice", "email": "alice@example.com", "bio": null, "avatar_url": null}
```

## Mobile Developer Context

| Mobile Code | FastAPI Response Model |
|-------------|----------------------|
| `struct User: Codable { let id: Int; let name: String }` | `class UserResponse(BaseModel): id: int; name: str` |
| Decode JSON to typed model | FastAPI encodes model to JSON |
| Hidden fields stay on server | `response_model` filters fields |
| API contract in Swagger/OpenAPI | Auto-generated from response model |

## Response Validation

FastAPI validates your response before sending it:

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # This will fail validation (id is string, not int)
    return {
        "id": "not_a_number",  # ❌ ValidationError
        "name": "Alice",
        "email": "alice@example.com"
    }
```

FastAPI will return 500 Internal Server Error with error details (in development mode). This catches bugs before they reach production.

## Key Takeaways

1. **Use `response_model` parameter to define response shape** - type safety and documentation
2. **Separate request and response models** - never expose sensitive fields
3. **Response models filter extra fields** - only defined fields are sent
4. **Envelope pattern for lists** - `{"items": [...], "total": 100}` instead of bare list
5. **Computed fields add derived data** - full_name from first_name + last_name
6. **Inheritance shares common fields** - id, created_at, updated_at across all models
7. **`from_attributes=True` enables ORM support** - return database objects directly
