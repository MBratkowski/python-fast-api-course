# Authentication vs Authorization

## Why This Matters

Authentication is like unlocking your phone with Face ID — proving you are you. Authorization is like app permissions — you're logged in, but can you access the camera?

In mobile development, you handle the client side: storing tokens in Keychain (iOS) or Keystore (Android), sending `Authorization: Bearer <token>` headers with every request. Now you're building the server side — the system that issues those tokens and validates them.

## The Core Concepts

**Authentication** answers: "Who are you?"
- User proves identity with credentials (username + password, biometrics, OAuth)
- Server verifies credentials
- Server issues a token as proof

**Authorization** answers: "What can you do?"
- User sends token with each request
- Server validates token
- Server checks permissions for the requested operation

These are separate concerns. A user might be authenticated (logged in) but not authorized (can't access admin panel).

## HTTP is Stateless

Every HTTP request is independent. The server doesn't remember previous requests. Unlike a mobile app where the user is "logged in" during the session, the API needs proof of identity on every single request.

That's where tokens come in: compact, verifiable proof that the user authenticated earlier.

## The Authentication Flow

```
1. User -> Server: POST /auth/login with username + password
2. Server: Verify credentials against database
3. Server -> User: Return access token (JWT)
4. User stores token (Keychain/Keystore/localStorage)
5. User -> Server: GET /api/posts with Authorization: Bearer <token>
6. Server: Validate token, extract user identity
7. Server: Check if user can access /api/posts (authorization)
8. Server -> User: Return posts
```

## Where Auth Fits in the Request Lifecycle

```
HTTP Request arrives
    ↓
Middleware (CORS, logging)
    ↓
Authentication: Validate token → Identify user
    ↓
Authorization: Check permissions → Allow/Deny
    ↓
Route Handler: Execute business logic
    ↓
HTTP Response
```

In FastAPI, authentication and authorization happen via **dependencies** — functions that run before your route handler.

## Example: Token-Based Flow

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# This extracts the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Authentication: Validate token and get user."""
    user = validate_token_and_get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user

@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    """This route requires authentication."""
    return {"message": f"Hello, {current_user.username}"}
```

## Authentication Methods

| Method | How It Works | When to Use |
|--------|--------------|-------------|
| **JWT (Token-based)** | Server issues signed token, client sends it with each request | APIs, mobile/web apps (stateless) |
| **Session cookies** | Server stores session, sends cookie ID to client | Traditional web apps (stateful) |
| **OAuth 2.0** | User authorizes app via third-party (Google, GitHub) | "Login with Google" flows |
| **API keys** | Static key assigned to client | Machine-to-machine, third-party integrations |

For modern APIs, **JWT is the standard**. It's stateless (no server-side session storage) and works seamlessly with mobile apps.

## Key Takeaways

1. **Authentication = identity**, **Authorization = permissions**
2. HTTP is stateless — tokens make each request independently verifiable
3. JWT is the standard for API authentication (what you'll learn in this module)
4. In FastAPI, use dependencies to enforce authentication and authorization
5. Mobile apps handle token storage (Keychain/Keystore); your API handles token generation and validation
