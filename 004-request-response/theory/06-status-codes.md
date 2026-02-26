# Status Codes

## Why This Matters

When your mobile app makes an API request, you check `response.statusCode` to determine success or failure: 200 means success, 404 means not found, 401 means unauthorized. As a backend developer, YOU set those status codes. Choosing the right code helps clients handle responses correctly and makes your API predictable and RESTful.

## Common Status Codes

### Success (2xx)

**200 OK** - Request succeeded
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Default status code is 200 OK."""
    return {"id": user_id, "name": "Alice"}
```

**201 Created** - Resource was created
```python
from fastapi import status

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Use 201 for POST that creates a resource."""
    return {"id": 123, "name": user.name}
```

**204 No Content** - Success, but no response body
```python
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Use 204 for DELETE or when no content to return."""
    # Delete user from database
    return None  # or Response(status_code=204)
```

### Client Errors (4xx)

**400 Bad Request** - Invalid request data
```python
from fastapi import HTTPException, status

@app.post("/calculate")
async def calculate(a: int, b: int):
    """Raise 400 for invalid business logic."""
    if b == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot divide by zero"
        )
    return {"result": a / b}
```

**401 Unauthorized** - Authentication required
```python
@app.get("/me")
async def get_current_user(authorization: str | None = Header(None)):
    """Raise 401 when authentication is missing or invalid."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {"user": "alice"}
```

**403 Forbidden** - Authenticated but not authorized
```python
@app.delete("/admin/users/{user_id}")
async def delete_user_admin(user_id: int, current_user: User):
    """Raise 403 when user lacks permission."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    # Delete user
    return {"message": "User deleted"}
```

**404 Not Found** - Resource doesn't exist
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Raise 404 when resource not found."""
    user = database.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    return user
```

**409 Conflict** - Resource already exists or state conflict
```python
@app.post("/users")
async def create_user(user: UserCreate):
    """Raise 409 when email already exists."""
    if database.email_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user.email} already exists"
        )

    # Create user
    return {"id": 123}
```

**422 Unprocessable Entity** - Validation failed
```python
# FastAPI automatically returns 422 for validation errors
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=150)

@app.post("/users")
async def create_user(user: User):
    """FastAPI returns 422 if validation fails."""
    return {"user": user}

# POST /users with {"name": "", "age": -5}
# Returns: 422 with validation error details
```

### Server Errors (5xx)

**500 Internal Server Error** - Unhandled exception
```python
@app.get("/broken")
async def broken_endpoint():
    """Unhandled exceptions return 500."""
    raise Exception("Something went wrong")
    # FastAPI catches this and returns 500
```

**503 Service Unavailable** - Service temporarily down
```python
@app.get("/data")
async def get_data():
    """Raise 503 when dependency is down."""
    if not database.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is temporarily unavailable"
        )
    return {"data": []}
```

## Using Status Code Constants

FastAPI provides constants from the `status` module:

```python
from fastapi import status

# Success
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_202_ACCEPTED
status.HTTP_204_NO_CONTENT

# Client errors
status.HTTP_400_BAD_REQUEST
status.HTTP_401_UNAUTHORIZED
status.HTTP_403_FORBIDDEN
status.HTTP_404_NOT_FOUND
status.HTTP_409_CONFLICT
status.HTTP_422_UNPROCESSABLE_ENTITY
status.HTTP_429_TOO_MANY_REQUESTS

# Server errors
status.HTTP_500_INTERNAL_SERVER_ERROR
status.HTTP_502_BAD_GATEWAY
status.HTTP_503_SERVICE_UNAVAILABLE
```

**Why use constants?**
- More readable than numbers
- Auto-complete in IDE
- Self-documenting code

```python
# Less clear
@app.post("/users", status_code=201)
async def create_user():
    pass

# More clear
@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user():
    pass
```

## Setting Status Codes

### In Decorator

```python
@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Status code set in decorator."""
    return {"id": 123, "name": user.name}
```

### With HTTPException

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Raise HTTPException to return error status."""
    if user_id < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be positive"
        )

    return {"id": user_id, "name": "Alice"}
```

### With Response Object

```python
from fastapi import Response

@app.get("/conditional")
async def conditional_response(response: Response):
    """Set status code dynamically."""
    data_exists = check_data()

    if not data_exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "No data found"}

    response.status_code = status.HTTP_200_OK
    return {"data": "found"}
```

## Status Code Ranges

| Range | Meaning | When to Use |
|-------|---------|-------------|
| 1xx | Informational | Rarely used in REST APIs |
| 2xx | Success | Request succeeded |
| 3xx | Redirection | Resource moved |
| 4xx | Client Error | Client sent bad request |
| 5xx | Server Error | Server failed to process valid request |

## RESTful Status Code Patterns

| HTTP Method | Success Status | Error Status |
|-------------|---------------|--------------|
| GET | 200 OK | 404 Not Found |
| POST (create) | 201 Created | 400 Bad Request, 409 Conflict |
| PUT (replace) | 200 OK | 404 Not Found |
| PATCH (update) | 200 OK | 404 Not Found |
| DELETE | 204 No Content | 404 Not Found |

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """GET: 200 on success, 404 if not found."""
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", status_code=201)
async def create_item(item: ItemCreate):
    """POST: 201 when created, 409 if duplicate."""
    if item_exists(item.name):
        raise HTTPException(status_code=409, detail="Item already exists")
    return create_new_item(item)

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """DELETE: 204 on success, 404 if not found."""
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    delete_from_db(item_id)
    return None
```

## Error Response Format

Consistent error format helps clients handle errors:

```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Raise HTTPException with structured detail."""
    if user_id < 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "InvalidUserID",
                "detail": "User ID must be positive",
                "timestamp": "2026-02-26T10:00:00Z"
            }
        )
    return {"id": user_id}
```

## Custom Exception Handlers

Handle specific exceptions globally:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class ItemNotFoundError(Exception):
    """Custom exception for missing items."""
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    """Convert custom exception to 404 response."""
    return JSONResponse(
        status_code=404,
        content={"detail": f"Item {exc.item_id} not found"}
    )

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """Raise custom exception - handler converts to 404."""
    item = find_item(item_id)
    if not item:
        raise ItemNotFoundError(item_id)
    return item
```

## Mobile Developer Context

| Mobile Code | FastAPI |
|-------------|---------|
| `if response.statusCode == 200` | Default for successful GET |
| `if response.statusCode == 201` | Set `status_code=201` for POST |
| `if response.statusCode == 401` | `raise HTTPException(status_code=401)` |
| `if response.statusCode == 404` | `raise HTTPException(status_code=404)` |
| Handle network errors | Return 503 when service down |

## Key Takeaways

1. **Use status code constants** - `status.HTTP_200_OK` not `200`
2. **201 for resource creation** - POST endpoints should return 201
3. **204 for no content** - DELETE endpoints typically return 204
4. **404 for missing resources** - clear signal to client
5. **401 vs 403** - 401 = not authenticated, 403 = not authorized
6. **422 is automatic** - FastAPI returns it for validation errors
7. **4xx = client's fault, 5xx = server's fault** - helps debugging
8. **HTTPException for errors** - raises exception and returns status + detail
