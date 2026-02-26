# Middleware for Auth

## Why This Matters

Middleware is like a global OkHttp Interceptor that runs on every network call. Dependencies are like per-request checks. Use middleware for cross-cutting concerns (logging every request), use dependencies for endpoint-specific rules (only admins can delete).

## Middleware vs Dependencies

| Aspect | Middleware | Dependencies |
|--------|------------|--------------|
| **Runs** | On EVERY request | On specific endpoints |
| **When to use** | Logging, CORS, rate limiting | Authentication, authorization |
| **Knows endpoint context** | No | Yes (can access path parameters) |
| **Best for** | Global cross-cutting concerns | Endpoint-specific rules |

## When to Use Middleware

**Good use cases**:
- Request/response logging with user context
- CORS headers
- Request ID tracking
- Global rate limiting
- Adding security headers to all responses
- Performance monitoring

**Bad use cases**:
- Authentication (use `OAuth2PasswordBearer` + dependencies)
- Authorization (use `require_role` dependencies)
- Endpoint-specific validation (use Pydantic + dependencies)

## Auth Middleware Pattern

Middleware can **attach user** to request state, but **dependencies still check permissions**:

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

class AuthMiddleware(BaseHTTPMiddleware):
    """Attach authenticated user to request state."""

    async def dispatch(self, request: Request, call_next):
        # Extract token
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            try:
                # Decode token
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = int(payload.get("sub"))

                # Attach user info to request state
                request.state.user_id = user_id
                request.state.username = payload.get("username")
                request.state.role = payload.get("role")

            except jwt.InvalidTokenError:
                # Don't fail here - let dependencies handle it
                request.state.user_id = None

        else:
            request.state.user_id = None

        # Continue processing
        response = await call_next(request)
        return response

# Add middleware
app.add_middleware(AuthMiddleware)
```

**Dependencies still enforce authorization**:

```python
@app.get("/admin/dashboard")
async def admin_dashboard(
    request: Request,
    admin: Annotated[User, Depends(require_role(Role.ADMIN))]
):
    # Middleware populated request.state.user_id
    # Dependency verified admin role
    return {"message": f"Welcome {request.state.username}"}
```

## Request Logging with User Context

```python
import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with user context."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Get user from state (if AuthMiddleware ran first)
        user_id = getattr(request.state, "user_id", None)
        username = getattr(request.state, "username", "anonymous")

        # Process request
        response = await call_next(request)

        # Log request
        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration:.3f}s "
            f"user={username} (id={user_id})"
        )

        return response

app.add_middleware(RequestLoggingMiddleware)
```

## Global Auth (All Routes Require Login)

If ALL routes require authentication except a whitelist:

```python
class GlobalAuthMiddleware(BaseHTTPMiddleware):
    """Require authentication on all routes except whitelist."""

    WHITELIST = [
        "/auth/login",
        "/auth/signup",
        "/docs",
        "/openapi.json",
        "/health"
    ]

    async def dispatch(self, request: Request, call_next):
        # Skip auth for whitelisted paths
        if request.url.path in self.WHITELIST:
            return await call_next(request)

        # Require token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                content='{"detail": "Not authenticated"}',
                status_code=401,
                media_type="application/json"
            )

        # Validate token
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = int(payload.get("sub"))
        except jwt.InvalidTokenError:
            return Response(
                content='{"detail": "Invalid token"}',
                status_code=401,
                media_type="application/json"
            )

        return await call_next(request)
```

**However**: Dependencies are usually cleaner for this:

```python
# Instead of middleware, use dependency on app
from fastapi import FastAPI

# Require auth globally
app = FastAPI(dependencies=[Depends(get_current_user)])

# Opt-out specific routes
router_public = APIRouter()

@router_public.post("/auth/login")
async def login():  # No dependency = no auth required
    pass

app.include_router(router_public)
```

## Why Not Do Authorization in Middleware?

**Problem**: Middleware doesn't know the endpoint context.

```python
# BAD - Middleware can't know which endpoints need which roles
class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # How do we know this endpoint needs admin?
        # Middleware has no access to endpoint metadata!
        if request.url.path.startswith("/admin"):  # Brittle!
            if request.state.role != "admin":
                return Response(status_code=403)
        return await call_next(request)

# GOOD - Dependencies have full context
@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Annotated[User, Depends(require_role(Role.ADMIN))]
):
    # Dependency knows this specific endpoint needs admin
    pass
```

## Adding User Info to Response Headers

```python
class UserHeaderMiddleware(BaseHTTPMiddleware):
    """Add user info to response headers."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add user context to response headers
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            response.headers["X-User-ID"] = str(user_id)
            response.headers["X-Username"] = request.state.username

        return response
```

## Middleware Order Matters

```python
# Middleware runs in the order added
app.add_middleware(CORSMiddleware, ...)  # 1. CORS first (handles preflight)
app.add_middleware(AuthMiddleware)       # 2. Auth (populates request.state)
app.add_middleware(RequestLoggingMiddleware)  # 3. Logging (uses request.state.user)
```

Execution order:
```
Request →
  CORSMiddleware →
    AuthMiddleware →
      RequestLoggingMiddleware →
        Route Handler →
      RequestLoggingMiddleware ←
    AuthMiddleware ←
  CORSMiddleware ←
← Response
```

## Key Takeaways

1. **Middleware** runs on every request — use for logging, CORS, rate limiting
2. **Dependencies** run on specific endpoints — use for authentication and authorization
3. Middleware can populate `request.state` with user context
4. **Don't do authorization in middleware** — it doesn't know endpoint requirements
5. Use dependencies for auth — they're cleaner and have full endpoint context
6. Middleware order matters — auth before logging, CORS before everything
7. Prefer **dependencies over middleware** for auth — better testability and clarity
