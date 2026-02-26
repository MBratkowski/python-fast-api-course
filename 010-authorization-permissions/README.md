# Module 010: Authorization & Permissions

## Why This Module?

Authentication tells you WHO the user is. Authorization tells you WHAT they can do. Learn roles, permissions, and access control.

## What You'll Learn

- Role-based access control (RBAC)
- Permission systems
- Resource ownership
- Admin vs user routes
- Middleware for auth

## Topics

### Theory
1. RBAC Concepts
2. Defining Roles & Permissions
3. Permission Decorators
4. Resource-Level Authorization
5. Admin Routes
6. Middleware Approach

### Project
Add roles (admin, user) and permissions to your API.

## Example

```python
from enum import Enum
from fastapi import Depends, HTTPException

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

def require_role(required_role: Role):
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_role(Role.ADMIN))
):
    # Only admins can delete users
    await user_service.delete(user_id)
```
