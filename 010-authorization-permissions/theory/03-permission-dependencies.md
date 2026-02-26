# Permission Dependencies in FastAPI

## Why This Matters

Dependencies in FastAPI are like middleware interceptors in your mobile networking stack — each one checks a condition and either passes through or blocks. `require_role` is like a route guard in Angular or a NavigationGuard in Vue, but for API endpoints instead of page routes.

## The require_role() Dependency Factory

A **dependency factory** is a function that returns a dependency function:

```python
from fastapi import Depends, HTTPException, status
from typing import Annotated

def require_role(required_role: Role):
    """Dependency factory that checks user role."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role"
            )
        return current_user
    return role_checker
```

**Usage**:

```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Annotated[User, Depends(require_role(Role.ADMIN))]
):
    """Only admins can delete users."""
    await user_service.delete(user_id)
    return {"message": "User deleted"}
```

**What happens**:
1. Request arrives
2. `get_current_user` dependency runs (validates token, loads user)
3. `role_checker` runs (checks if `user.role == Role.ADMIN`)
4. If role matches → continues to endpoint
5. If role doesn't match → raises 403 Forbidden

## require_any_role() for Multiple Roles

Some endpoints should be accessible by multiple roles:

```python
def require_any_role(allowed_roles: list[Role]):
    """Dependency factory that accepts any role from the list."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker
```

**Usage**:

```python
# Admin or moderator can access
@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: Annotated[User, Depends(require_any_role([Role.ADMIN, Role.MODERATOR]))]
):
    await post_service.delete(post_id)
```

## Composing Dependencies

FastAPI dependencies form a **dependency chain** — each can depend on others:

```
HTTP Request
    ↓
oauth2_scheme (extracts token from header)
    ↓
get_current_user(token, db)
    ↓
require_role(Role.ADMIN)(current_user)
    ↓
Endpoint Handler(admin_user)
```

Each layer adds a check. FastAPI resolves them automatically.

## The Full Dependency Chain

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

# Layer 1: Extract token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Layer 2: Validate token and get user
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401)
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401)

# Layer 3: Check role
def require_role(required_role: Role):
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(status_code=403)
        return current_user
    return role_checker

# Layer 4: Endpoint
@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Annotated[User, Depends(require_role(Role.ADMIN))]
):
    # Reaches here only if:
    # - Valid token was provided
    # - User exists in database
    # - User has ADMIN role
    return {"message": "User deleted"}
```

## Error Handling: 401 vs 403

**401 Unauthorized**: Authentication problem
- No token provided
- Invalid token
- Expired token
- User doesn't exist

**403 Forbidden**: Authorization problem
- Valid token
- User exists and is authenticated
- User lacks required role/permission

```python
# 401 - Can't verify who you are
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# 403 - Know who you are, but you can't do this
if current_user.role != Role.ADMIN:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions"
    )
```

## Using Dependencies on Multiple Endpoints

Don't repeat yourself — reuse dependencies:

```python
# Instead of this:
@router.get("/admin/users")
async def list_users(admin: Annotated[User, Depends(require_role(Role.ADMIN))]):
    pass

@router.delete("/admin/users/{id}")
async def delete_user(id: int, admin: Annotated[User, Depends(require_role(Role.ADMIN))]):
    pass

# Do this:
AdminDep = Annotated[User, Depends(require_role(Role.ADMIN))]

@router.get("/admin/users")
async def list_users(admin: AdminDep):
    pass

@router.delete("/admin/users/{id}")
async def delete_user(id: int, admin: AdminDep):
    pass
```

## Testing with Roles

```python
from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def admin_client(client: TestClient, db: Session) -> TestClient:
    """Client authenticated as admin."""
    # Create admin user
    admin = User(
        username="admin",
        email="admin@test.com",
        hashed_password=password_hash.hash("admin123"),
        role=Role.ADMIN
    )
    db.add(admin)
    db.commit()

    # Login
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["access_token"]

    # Set auth header
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

def test_admin_can_delete_users(admin_client: TestClient):
    """Test admin can access admin endpoint."""
    response = admin_client.delete("/users/123")
    assert response.status_code == 200

def test_regular_user_cannot_delete_users(client: TestClient):
    """Test regular user gets 403."""
    # Create and login as regular user
    # ... login as user role ...

    response = client.delete("/users/123")
    assert response.status_code == 403
```

## Key Takeaways

1. **`require_role()`** is a dependency factory pattern for role checks
2. **`require_any_role()`** accepts multiple roles (admin OR moderator)
3. Dependencies compose: `oauth2_scheme → get_current_user → require_role → endpoint`
4. Use **403** for authorization failures (user authenticated but lacks permissions)
5. Use **401** for authentication failures (invalid/missing token)
6. Create type aliases (`AdminDep`) to avoid repeating dependency definitions
7. FastAPI resolves the dependency chain automatically — you just declare what you need
