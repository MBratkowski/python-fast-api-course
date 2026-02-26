# Defining Roles and Permissions

## Why This Matters

This is like defining user types in your mobile app's backend — free users vs premium vs admin. In your mobile app, you show/hide UI based on the user type from the API response. Now you enforce those distinctions server-side, preventing unauthorized access even if users bypass your UI.

## Modeling Roles in Python

Use an `Enum` to define available roles:

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
```

**Why `str, Enum`?**
- Inherits from `str` for JSON serialization
- Inherits from `Enum` for type safety
- Can compare: `user.role == Role.ADMIN`
- Serializes to: `"admin"` (not `"Role.ADMIN"`)

## Adding Role to User Model

```python
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role),
        default=Role.USER,
        server_default=Role.USER.value
    )
    is_active: Mapped[bool] = mapped_column(default=True)
```

**Key points**:
- `SQLEnum(Role)` maps Python enum to database enum type
- `default=Role.USER` sets default in Python
- `server_default=Role.USER.value` sets default in database
- Every new user gets `USER` role by default

## Permissions as a Concept

Roles can map to permissions:

```python
# Simple approach: Check role directly
if current_user.role == Role.ADMIN:
    # Allow action

# Advanced approach: Role → Permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        "read", "write", "delete",
        "manage_users", "view_analytics", "change_roles"
    ],
    Role.MODERATOR: [
        "read", "write", "delete",
        "ban_users", "flag_content"
    ],
    Role.USER: [
        "read", "write_own", "delete_own"
    ]
}

def has_permission(user: User, permission: str) -> bool:
    """Check if user's role has specific permission."""
    return permission in ROLE_PERMISSIONS.get(user.role, [])
```

For most APIs, checking roles directly is sufficient. Use permission mapping if you need granular control.

## Default Roles on Signup

**Critical security rule**: New users ALWAYS get the least privileged role.

```python
@router.post("/auth/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create new user with default USER role."""
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=password_hash.hash(user_data.password),
        role=Role.USER  # Always USER, never ADMIN
    )
    db.add(user)
    db.commit()
    return user
```

**Never allow users to set their own role during signup**:

```python
# BAD - Security vulnerability!
@router.post("/auth/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=user_data.username,
        role=user_data.role  # User can set role=ADMIN!
    )
```

## Role in JWT Token

You can include role in the JWT payload for quick checks:

```python
def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value,  # Include role
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

**BUT**: Always verify role from database for critical operations.

```python
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = int(payload.get("sub"))

    # Load user from database (includes current role)
    user = db.query(User).filter(User.id == user_id).first()

    # Don't trust role from token alone - user role may have changed
    return user
```

**Why**: If you change a user's role, tokens issued before the change still have the old role. Loading from database ensures you get the current role.

## Creating Admin Users

**Option 1**: Seed script

```python
# seed_admin.py
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def create_admin(db: Session, username: str, email: str, password: str):
    """Create admin user via script."""
    admin = User(
        username=username,
        email=email,
        hashed_password=password_hash.hash(password),
        role=Role.ADMIN
    )
    db.add(admin)
    db.commit()
    print(f"Admin user '{username}' created")

# Run: python seed_admin.py
```

**Option 2**: Environment variable on first run

```python
import os

@app.on_event("startup")
async def create_initial_admin():
    """Create admin on startup if ADMIN_USERNAME env var is set."""
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if admin_username and admin_password:
        db = Session(engine)
        existing = db.query(User).filter(User.username == admin_username).first()
        if not existing:
            create_admin(db, admin_username, "admin@example.com", admin_password)
        db.close()
```

**Never**: Allow creating admin via public signup.

## Pydantic Schema with Role

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: Role  # Automatically serializes to "admin", "user", etc.
    is_active: bool
```

## Example: Complete Role Setup

```python
from enum import Enum
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, ConfigDict

# 1. Define roles
class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

# 2. User model with role
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER)

# 3. Response schema
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: Role

# 4. Signup with default role
@router.post("/auth/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=password_hash.hash(user_data.password),
        role=Role.USER  # Default for all signups
    )
    db.add(user)
    db.commit()
    return user

# Returns: {"id": 1, "username": "alice", "role": "user"}
```

## Key Takeaways

1. Define roles as `class Role(str, Enum)` for type safety and serialization
2. Add role field to User model with `SQLEnum(Role)`, default to `USER`
3. **Always** assign `USER` role on signup — never let users choose admin
4. Include role in Pydantic schemas for API responses
5. Load user from database (don't trust role in JWT alone) for critical checks
6. Create admin users via seed scripts or environment variables, not public signup
