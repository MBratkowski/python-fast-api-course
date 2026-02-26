# FastAPI OAuth2PasswordBearer

## Why This Matters

`OAuth2PasswordBearer` is like your mobile app's auth interceptor (OkHttp Interceptor in Android, Alamofire RequestAdapter in iOS) — it automatically extracts and validates the token from every request. But here it's server-side, using FastAPI's dependency injection system.

## What is OAuth2PasswordBearer?

`OAuth2PasswordBearer` is a FastAPI utility that:
1. Declares where tokens come from (the `/auth/login` endpoint)
2. Extracts the `Authorization: Bearer <token>` header automatically
3. Provides the token to your dependencies
4. Integrates with OpenAPI/Swagger (adds a login button to docs)

It's part of FastAPI's **security module** — built-in tools for authentication.

## Basic Setup

```python
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# Declare the token URL (where clients get tokens)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    """This route requires a Bearer token."""
    # oauth2_scheme extracts the token from:
    # Authorization: Bearer <token>
    return {"token": token}
```

**What happens**:
- Client sends: `Authorization: Bearer eyJhbGci...`
- FastAPI extracts: `token = "eyJhbGci..."`
- If header is missing: Returns 401 Unauthorized

## OAuth2PasswordRequestForm

For login, FastAPI provides `OAuth2PasswordRequestForm` — a dependency that parses **form data** (not JSON).

**Why form data?** The OAuth2 spec requires `application/x-www-form-urlencoded`, not JSON.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username and password (form data)."""
    # form_data.username
    # form_data.password

    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(user.id, user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

**Client request** (form data):
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=alice&password=SecurePass123
```

**NOT** JSON:
```http
POST /auth/login
Content-Type: application/json

{"username": "alice", "password": "SecurePass123"}
```

## Building the get_current_user Dependency

This is the core authentication dependency — used on every protected route.

```python
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user.

    Dependency chain:
    1. oauth2_scheme extracts token from Authorization header
    2. Decode and validate JWT
    3. Load user from database
    4. Return user or raise 401
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise credentials_exception

    # Load user from database
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception

    return user
```

## Using Dependencies on Protected Routes

```python
from typing import Annotated
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user profile."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

@router.put("/me")
async def update_me(
    updates: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    current_user.email = updates.email
    db.commit()
    return current_user
```

## The Dependency Chain

FastAPI's dependency injection creates a chain:

```
HTTP Request
    ↓
oauth2_scheme
    ↓ (extracts token from header)
get_current_user(token, db)
    ↓ (validates token, loads user)
Route Handler(current_user)
    ↓
HTTP Response
```

Each dependency can depend on other dependencies. FastAPI resolves them automatically.

## OpenAPI Integration

One of the best features: **automatic Swagger UI authentication**.

When you use `OAuth2PasswordBearer`, the Swagger docs at `/docs` get a **login button**:

1. Click "Authorize"
2. Enter username and password
3. Swagger calls your `/auth/login` endpoint
4. Stores the token
5. Automatically includes it in all subsequent requests

No extra code needed — it's automatic!

## Complete Authentication Example

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

app = FastAPI()

# Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hash = PasswordHash.recommended()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Token creation
def create_access_token(user_id: int, username: str) -> str:
    payload = {
        "sub": username,
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Authentication dependency
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception

        return user

    except jwt.InvalidTokenError:
        raise credentials_exception

# Login endpoint
@app.post("/auth/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    # Get user
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        # Timing attack prevention
        password_hash.verify(form_data.password, DUMMY_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not password_hash.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token
    access_token = create_access_token(user.id, user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# Protected endpoints
@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@app.get("/protected")
async def protected_route(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {
        "message": "This is a protected route",
        "user": current_user.username
    }
```

## Testing with TestClient

```python
from fastapi.testclient import TestClient

client = TestClient(app)

# Signup
client.post("/auth/signup", json={
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePass123"
})

# Login (form data, not JSON!)
response = client.post("/auth/login", data={
    "username": "alice",
    "password": "SecurePass123"
})
token = response.json()["access_token"]

# Access protected route
response = client.get(
    "/users/me",
    headers={"Authorization": f"Bearer {token}"}
)
assert response.status_code == 200
```

## Key Takeaways

1. **OAuth2PasswordBearer** extracts tokens from `Authorization: Bearer <token>` headers
2. **OAuth2PasswordRequestForm** parses login form data (username + password)
3. **get_current_user** is the standard authentication dependency
4. **Dependency chain**: oauth2_scheme → get_current_user → route handler
5. **OpenAPI integration**: Swagger UI automatically gets a login button
6. Login uses **form data**, not JSON (OAuth2 spec requirement)
7. Protected routes use `Depends(get_current_user)` to enforce authentication
