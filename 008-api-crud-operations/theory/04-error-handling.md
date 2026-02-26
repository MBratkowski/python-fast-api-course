# Error Handling in CRUD APIs

## Why This Matters

In mobile development, you handle different error states: network errors, validation errors, not found, unauthorized. Your backend API needs to communicate these errors clearly using HTTP status codes and error messages.

Good error handling makes APIs predictable and easier to debug. Bad error handling leaves clients guessing what went wrong.

## HTTP Status Codes for Errors

| Status Code | Meaning | When to Use |
|-------------|---------|-------------|
| **400 Bad Request** | Client sent invalid data | Validation errors, malformed JSON |
| **401 Unauthorized** | Authentication required | Missing or invalid auth token |
| **403 Forbidden** | Authenticated but no permission | User can't access resource |
| **404 Not Found** | Resource doesn't exist | User/post/item not found |
| **409 Conflict** | Request conflicts with current state | Duplicate username/email |
| **422 Unprocessable Entity** | Validation failed | Pydantic validation errors (auto) |
| **500 Internal Server Error** | Server error | Unexpected exceptions |

## Using HTTPException

FastAPI's standard way to return errors:

```python
from fastapi import HTTPException, status

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user by ID."""
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
```

**Response when user not found:**

```json
HTTP/1.1 404 Not Found
{
    "detail": "User not found"
}
```

### With More Details

```python
raise HTTPException(
    status_code=400,
    detail={
        "error": "Invalid input",
        "field": "email",
        "message": "Email format is invalid"
    }
)
```

**Response:**

```json
HTTP/1.1 400 Bad Request
{
    "detail": {
        "error": "Invalid input",
        "field": "email",
        "message": "Email format is invalid"
    }
}
```

## Common Error Patterns

### 404 Not Found

```python
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )

    return user
```

### 400 Bad Request (Validation)

```python
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 409 Conflict (Duplicate)

```python
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if username exists
    existing = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    # Create user...
```

### 403 Forbidden (No Permission)

```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only admins or the user themselves can delete
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this user"
        )

    await db.delete(user)
    await db.commit()
    return {"status": "deleted"}
```

## Handling Database Errors

### Integrity Errors (Unique Constraints)

```python
from sqlalchemy.exc import IntegrityError

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = User(**user_data.model_dump())
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as e:
        await db.rollback()

        # Check what constraint was violated
        if "username" in str(e.orig):
            raise HTTPException(status_code=409, detail="Username already exists")
        elif "email" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already exists")
        else:
            raise HTTPException(status_code=400, detail="Database constraint violated")
```

**Better approach:** Check before inserting (prevents database error):

```python
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    # Service checks for duplicates BEFORE inserting
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
```

## Custom Exception Handlers

Define global exception handlers for common errors:

```python
# src/api/exceptions.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": errors}
    )


# src/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from src.api.exceptions import validation_exception_handler

app = FastAPI()

app.add_exception_handler(RequestValidationError, validation_exception_handler)
```

**Now validation errors return:**

```json
HTTP/1.1 422 Unprocessable Entity
{
    "detail": "Validation failed",
    "errors": [
        {
            "field": "body -> email",
            "message": "value is not a valid email address",
            "type": "value_error.email"
        }
    ]
}
```

## Consistent Error Response Format

Define a standard error schema:

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    message: str
    field: str | None = None

@router.post("/users", response_model=UserResponse, responses={
    409: {"model": ErrorResponse, "description": "Duplicate username or email"}
})
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                error="conflict",
                message=str(e),
                field="username"
            ).model_dump()
        )
```

## Logging Errors

Log errors for debugging:

```python
import logging

logger = logging.getLogger(__name__)

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        logger.warning(f"User creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Error Handling in Services

Services raise domain exceptions, routes translate to HTTP:

```python
# Service raises domain exceptions
class UserService:
    async def create_user(self, user_data: UserCreate) -> User:
        if await self._username_exists(user_data.username):
            raise ValueError("Username already exists")

        if not self._is_valid_email(user_data.email):
            raise ValueError("Invalid email format")

        # Create user...


# Route translates to HTTP exceptions
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        # Business rule violations → 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors → 500 Internal Server Error
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Mobile Development Perspective

Error handling mirrors mobile error states:

| Mobile App Error Handling | Backend API Error Handling |
|---------------------------|----------------------------|
| Check network connectivity | Return appropriate status code |
| Show "Item not found" | 404 Not Found |
| Show "Invalid input" | 400 Bad Request |
| Show "Login required" | 401 Unauthorized |
| Show "No permission" | 403 Forbidden |
| Log error to Crashlytics | Log error to logging system |

**Design errors for the consuming client.**

## Key Takeaways

1. **Use appropriate HTTP status codes** - 404 for not found, 400 for validation, 409 for conflicts
2. **`HTTPException` is the standard** way to return errors in FastAPI
3. **Include helpful error messages** - client needs to know what went wrong
4. **Handle database errors** - catch `IntegrityError`, rollback transaction
5. **Custom exception handlers** for consistent error format
6. **Log errors** - especially 500 errors for debugging
7. **Services raise domain exceptions** - routes translate to HTTP status codes
8. **Document error responses** in OpenAPI spec with `responses=` parameter
