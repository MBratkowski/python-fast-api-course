# Module 009: Authentication with JWT

## Why This Module?

Secure your API. Learn JWT (JSON Web Tokens) - the standard for API authentication that you've likely used from mobile apps.

## What You'll Learn

- Password hashing (bcrypt)
- JWT tokens (access + refresh)
- Login/signup endpoints
- Token validation
- Protected routes
- FastAPI security utilities

## Mobile Developer Context

You know how to store and send tokens from the client. Now learn how to generate, validate, and manage them on the server.

## Topics

### Theory
1. Authentication vs Authorization
2. Password Hashing with bcrypt
3. JWT Structure & Claims
4. Access vs Refresh Tokens
5. Token Expiration & Rotation
6. FastAPI OAuth2PasswordBearer

### Project
Implement complete auth system: signup, login, refresh, logout.

## Example

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await user_service.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```
