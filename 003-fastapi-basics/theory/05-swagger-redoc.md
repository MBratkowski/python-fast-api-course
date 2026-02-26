# Auto-Generated API Documentation

## Why This Matters

This is like having Postman built into your API - automatically. FastAPI generates interactive documentation from your code, so testing endpoints is as easy as clicking buttons.

## What is OpenAPI?

OpenAPI (formerly Swagger) is a standard specification for describing REST APIs. It's a JSON/YAML file that describes:
- Available endpoints
- Request parameters
- Request/response formats
- Authentication methods
- Error responses

**Mobile analogy**: Like the API documentation you read when integrating a third-party SDK, but auto-generated from code.

## FastAPI's Auto-Documentation

FastAPI generates OpenAPI documentation automatically from:
- Route decorators (`@app.get`, `@app.post`)
- Type hints (`user_id: int`)
- Pydantic models
- Docstrings
- Response models

**You write code, FastAPI writes docs.**

## Swagger UI (/docs)

Visit `http://localhost:8000/docs` to see interactive documentation.

**What you get**:
- List of all endpoints organized by tags
- Try out any endpoint with a button click
- See request/response examples
- View schemas for request bodies
- Test authentication

**Mobile analogy**: Like Apple's SF Symbols app - interactive reference for what's available.

### Using Swagger UI

Given this endpoint:
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID."""
    return {"id": user_id, "name": "Alice"}
```

Swagger UI shows:
1. **Endpoint**: `GET /users/{user_id}`
2. **Description**: "Get user by ID" (from docstring)
3. **Parameters**: `user_id` (integer, required, in path)
4. **Try it out** button
5. **Example response**: `{"id": 1, "name": "Alice"}`

**To test**:
1. Click "Try it out"
2. Enter `user_id` value (e.g., 123)
3. Click "Execute"
4. See actual response from your API

## ReDoc (/redoc)

Visit `http://localhost:8000/redoc` for alternative documentation.

**Differences from Swagger UI**:
- Read-only (no "Try it out" button)
- Better for sharing with frontend devs
- Cleaner, more readable layout
- Better for printing/PDFs

**Use Swagger for testing, ReDoc for documentation.**

## OpenAPI Schema (/openapi.json)

Visit `http://localhost:8000/openapi.json` to see the raw OpenAPI spec.

This JSON file:
- Describes your entire API
- Can be imported into Postman, Insomnia, etc.
- Used to generate client SDKs
- Used by API gateways

**Mobile analogy**: Like an interface definition file (IDL) that code generators use.

## Customizing Documentation

### App Metadata

```python
app = FastAPI(
    title="My Awesome API",
    description="API for managing users and posts",
    version="1.0.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "API Support",
        "url": "https://example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
```

This appears at the top of your documentation.

### Endpoint Documentation

**Using docstrings**:
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """
    Get user by ID.

    This endpoint retrieves a single user's information.

    Parameters:
    - **user_id**: Unique user identifier

    Returns:
    - User object with id, name, email
    """
    return {"id": user_id}
```

**Using decorator parameters**:
```python
@app.get(
    "/users/{user_id}",
    summary="Get user by ID",
    description="Retrieve a single user's complete profile information",
    response_description="User profile data",
)
async def get_user(user_id: int):
    return {"id": user_id}
```

### Organizing with Tags

```python
@app.get("/users", tags=["users"])
async def list_users():
    return {"users": []}

@app.post("/users", tags=["users"])
async def create_user():
    return {"id": 1}

@app.get("/posts", tags=["posts"])
async def list_posts():
    return {"posts": []}
```

Tags group endpoints in documentation - all "users" endpoints appear together.

### Adding Examples

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(example="Alice Smith")
    email: str = Field(example="alice@example.com")
    age: int = Field(example=28)

@app.post("/users")
async def create_user(user: User):
    return user
```

The `example` values appear in documentation as sample inputs.

## What Gets Documented Automatically

**Path parameters**:
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    ...
# Docs show: user_id (integer, required, path parameter)
```

**Query parameters**:
```python
@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    ...
# Docs show: skip (integer, optional, default: 0)
#            limit (integer, optional, default: 10)
```

**Request body**:
```python
class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(user: UserCreate):
    ...
# Docs show: UserCreate schema with name and email fields
```

**Response models**:
```python
class User(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    ...
# Docs show: Response schema is User (id, name)
```

## Testing from Documentation

**1. Open Swagger UI**: `http://localhost:8000/docs`

**2. Find your endpoint**: Click to expand

**3. Click "Try it out"**

**4. Fill in parameters**:
- Path parameters (e.g., user_id)
- Query parameters (e.g., skip, limit)
- Request body (JSON editor appears)

**5. Click "Execute"**

**6. See results**:
- Request URL (what was called)
- Response body (actual JSON returned)
- Response headers
- Status code

**Mobile analogy**: Like testing your API integration without writing any mobile code first.

## Documentation Best Practices

**1. Add docstrings to all endpoints**:
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID."""  # ← Simple one-liner
    return {"id": user_id}
```

**2. Use tags for organization**:
```python
tags=["users"]  # Groups related endpoints
```

**3. Provide examples in models**:
```python
name: str = Field(example="Alice")
```

**4. Use response models**:
```python
response_model=User  # Documents exact response shape
```

**5. Set proper status codes**:
```python
status_code=status.HTTP_201_CREATED  # Documents correct status
```

## Disabling Documentation

For production or internal APIs:

```python
app = FastAPI(docs_url=None, redoc_url=None)
```

This disables `/docs` and `/redoc` endpoints.

## Key Takeaways

1. FastAPI generates OpenAPI docs automatically from your code
2. Visit `/docs` for interactive Swagger UI testing
3. Visit `/redoc` for clean, read-only documentation
4. Visit `/openapi.json` for raw OpenAPI schema
5. Add docstrings and tags to improve documentation
6. Test endpoints directly from Swagger UI (no Postman needed)
7. Use examples in Pydantic models for better docs
8. Documentation stays in sync with code automatically
