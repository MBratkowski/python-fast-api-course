# Admin Routes and Panels

## Why This Matters

Admin routes are like the admin panel of your app — in mobile, you might have a separate admin app or a hidden settings screen accessible only to admins. In your API, admin routes are regular endpoints protected by role checks. You enforce "admin only" at the server level, not just in the UI.

## Admin-Specific Endpoints

Common admin operations:

```python
GET    /admin/users              # List all users
GET    /admin/users/{id}         # View any user
PATCH  /admin/users/{id}/role    # Change user role
PATCH  /admin/users/{id}/activate  # Activate/deactivate user
DELETE /admin/users/{id}         # Delete user
GET    /admin/stats              # System statistics
GET    /admin/logs               # View system logs
POST   /admin/maintenance/mode   # Toggle maintenance mode
```

## Protecting Entire Routers

Instead of adding `Depends(require_role(Role.ADMIN))` to every endpoint, apply it to the entire router:

```python
from fastapi import APIRouter, Depends

# Create router with admin dependency
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role(Role.ADMIN))]  # ALL routes require admin
)

# All endpoints in this router automatically require admin role
@admin_router.get("/users")
async def list_all_users(db: Session = Depends(get_db)):
    """List all users (admin only)."""
    users = db.query(User).all()
    return users

@admin_router.patch("/users/{user_id}/activate")
async def toggle_user_active(user_id: int, db: Session = Depends(get_db)):
    """Activate/deactivate user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    user.is_active = not user.is_active
    db.commit()
    return user

# Include router in main app
app.include_router(admin_router)
```

## User Management Endpoints

```python
from pydantic import BaseModel

class RoleUpdate(BaseModel):
    role: Role

@admin_router.get("/users", response_model=list[UserResponse])
async def list_all_users(db: Session = Depends(get_db)):
    """List all users with roles."""
    return db.query(User).all()

@admin_router.patch("/users/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    role_data: RoleUpdate,
    current_admin: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Change a user's role."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    # Prevent privilege escalation
    if role_data.role == Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cannot promote users to admin role"
        )

    # Prevent admins from demoting themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot change your own role"
        )

    user.role = role_data.role
    db.commit()
    return user
```

## Preventing Privilege Escalation

**Critical**: Prevent non-admins from becoming admins through API:

```python
# BAD - Allows privilege escalation
@router.patch("/users/me")
async def update_me(
    updates: UserUpdate,  # UserUpdate has "role" field
    current_user: Annotated[User, Depends(get_current_user)]
):
    current_user.role = updates.role  # User can set role=ADMIN!
    db.commit()

# GOOD - Prevent role changes via user endpoints
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    # No role field!

@router.patch("/users/me")
async def update_me(
    updates: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if updates.email:
        current_user.email = updates.email
    db.commit()
    return current_user

# GOOD - Only admins can change roles, and they can't promote to admin
@admin_router.patch("/users/{user_id}/role")
async def change_role(user_id: int, role_data: RoleUpdate, ...):
    if role_data.role == Role.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot promote to admin")
    # ... update role
```

## System Statistics

```python
@admin_router.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    users_by_role = {}
    for role in Role:
        count = db.query(User).filter(User.role == role).count()
        users_by_role[role.value] = count

    return {
        "total_users": total_users,
        "active_users": active_users,
        "users_by_role": users_by_role
    }
```

## Admin User Creation

Create admin users via seed script, never through public API:

```python
# scripts/create_admin.py
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app.models import User
from app.database import engine

def create_admin(username: str, email: str, password: str):
    """Create admin user via command line script."""
    db = Session(engine)
    password_hash = PasswordHash.recommended()

    # Check if admin exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"User '{username}' already exists")
        return

    admin = User(
        username=username,
        email=email,
        hashed_password=password_hash.hash(password),
        role=Role.ADMIN
    )
    db.add(admin)
    db.commit()
    print(f"Admin user '{username}' created successfully")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)

    create_admin(sys.argv[1], sys.argv[2], sys.argv[3])

# Run: python scripts/create_admin.py admin admin@example.com SecurePass123
```

## Audit Logging for Admin Actions

```python
from datetime import datetime

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(255))
    target_user_id: Mapped[int | None] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

def log_admin_action(db: Session, admin_id: int, action: str, target_user_id: int | None = None):
    """Log admin action for audit trail."""
    log = AdminLog(admin_id=admin_id, action=action, target_user_id=target_user_id)
    db.add(log)
    db.commit()

@admin_router.patch("/users/{user_id}/role")
async def change_role(
    user_id: int,
    role_data: RoleUpdate,
    current_admin: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    old_role = user.role
    user.role = role_data.role
    db.commit()

    # Log the action
    log_admin_action(
        db,
        current_admin.id,
        f"Changed role from {old_role.value} to {role_data.role.value}",
        user_id
    )

    return user
```

## Key Takeaways

1. **Admin routers**: Use `dependencies=[Depends(require_role(Role.ADMIN))]` on `APIRouter()` to protect all routes
2. **Prevent privilege escalation**: Never allow setting role to ADMIN via API
3. **Prevent self-demotion**: Admins cannot change their own role
4. **Create admins via scripts**, not public signup
5. **Audit logging**: Track admin actions for security and compliance
6. Admin endpoints: user management, system stats, activation/deactivation
