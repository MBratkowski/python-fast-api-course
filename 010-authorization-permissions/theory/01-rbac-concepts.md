# RBAC Concepts

## Why This Matters

In mobile development, you check permissions before accessing the camera or location — `AVCaptureDevice.authorizationStatus()` on iOS, `ContextCompat.checkSelfPermission()` on Android. RBAC (Role-Based Access Control) is the same concept for your API: can this user access this endpoint?

You've built the client-side checks. Now you build the server-side enforcement.

## What is RBAC?

**Role-Based Access Control** is a permission model where:
1. Users are assigned **roles** (admin, user, moderator)
2. Roles have **permissions** (can delete posts, can ban users, can edit own profile)
3. Endpoints check the user's role before granting access

Instead of managing permissions per-user, you manage permissions per-role. Users inherit permissions from their role.

## Common Role Models

### Flat Roles

Simple role assignment — each user has one role:

```
Admin  → Full system access
Moderator → Can moderate content, ban users
User → Can manage own content only
```

**Example**:
```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
```

### Hierarchical Roles

Roles inherit permissions from lower roles:

```
Admin → All moderator permissions + system management
  ↓
Moderator → All user permissions + content moderation
  ↓
User → Basic permissions (edit own profile, create posts)
```

### Permission-Based

Roles map to specific permissions:

```python
ROLE_PERMISSIONS = {
    "admin": ["read", "write", "delete", "manage_users", "view_analytics"],
    "moderator": ["read", "write", "delete", "ban_users"],
    "user": ["read", "write_own", "delete_own"]
}
```

## RBAC vs ABAC

**RBAC (Role-Based)**: Access based on user's role
- Simple to understand and implement
- Sufficient for most APIs
- Example: "Only admins can delete users"

**ABAC (Attribute-Based)**: Access based on attributes (user, resource, environment)
- More flexible but complex
- Needed for fine-grained rules
- Example: "Users can delete posts if they are the author AND post is less than 24 hours old AND user is not banned"

For most backend APIs, **RBAC is enough**. Start with RBAC, add ABAC if you need complex rules.

## Where Authorization Fits

```
1. HTTP Request arrives
2. Authentication: Who is this user? (validate JWT token)
3. Authorization: Can this user perform this action? (check role/permissions)
4. Business Logic: Execute the action
5. HTTP Response
```

**Key distinction**:
- **Authentication** happens first (establish identity)
- **Authorization** happens second (check permissions)
- You can be authenticated but not authorized (logged in but lack permissions)

## The Principle of Least Privilege

**Rule**: Users should have the minimum permissions needed to do their job.

- New users → `USER` role by default (not `ADMIN`)
- Admin role → Only for trusted administrators
- Moderator role → Only for content moderators
- Guest/Anonymous → Read-only access (or no access)

**Anti-pattern**: Giving everyone admin role for convenience.

## Request Flow with RBAC

```
User makes request: DELETE /users/123
    ↓
1. Extract and validate JWT token
   → Authenticated user: id=42, username=alice, role=admin
    ↓
2. Check role requirement
   → Endpoint requires: admin role
   → User has: admin role
   → AUTHORIZED ✓
    ↓
3. Execute delete operation
    ↓
4. Return 200 OK

---

Unauthorized example:

User makes request: DELETE /users/123
    ↓
1. Extract and validate JWT token
   → Authenticated user: id=99, username=bob, role=user
    ↓
2. Check role requirement
   → Endpoint requires: admin role
   → User has: user role
   → NOT AUTHORIZED ✗
    ↓
3. Return 403 Forbidden (not 401 — user IS authenticated, just lacks permissions)
```

## HTTP Status Codes for Auth

| Code | Meaning | When to Use |
|------|---------|-------------|
| **401 Unauthorized** | Authentication failed | No token, invalid token, expired token |
| **403 Forbidden** | Authorization failed | Valid token, but user lacks required role/permission |
| **404 Not Found** | Resource doesn't exist | Use instead of 403 to prevent info leakage |

**Critical**: Use 401 for authentication errors, 403 for authorization errors.

## Example: Mobile App Analogy

Think of your mobile app's backend:

```swift
// iOS - Mobile app checks user type from API
struct User {
    let id: Int
    let username: String
    let role: String  // "admin", "user", "moderator"
}

func showUI(for user: User) {
    if user.role == "admin" {
        // Show admin panel button
        showAdminPanel()
    } else {
        // Hide admin features
        hideAdminPanel()
    }
}
```

**Problem**: Malicious users can call admin APIs directly (bypass UI checks).

**Solution**: Server-side RBAC — enforce roles on the API endpoints themselves.

```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(Role.ADMIN))
):
    # Only reaches here if current_user.role == ADMIN
    await user_service.delete(user_id)
```

## Key Takeaways

1. **RBAC** assigns permissions via roles (admin, moderator, user)
2. **Authentication** establishes WHO you are, **authorization** determines WHAT you can do
3. Flat roles (admin/user) are simplest and sufficient for most APIs
4. Use **401** for authentication failures, **403** for authorization failures
5. Enforce RBAC server-side — never trust client-side UI checks
6. **Principle of least privilege**: Default to minimal permissions, escalate as needed
