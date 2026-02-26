# Phase 03: Auth and Security - Research

**Researched:** 2026-02-26
**Domain:** JWT authentication and role-based authorization in FastAPI
**Confidence:** HIGH

## Summary

This research covers implementing secure JWT-based authentication and role-based access control (RBAC) in FastAPI applications. The standard approach uses FastAPI's built-in OAuth2 security utilities with PyJWT for token operations and pwdlib for password hashing. Authentication establishes user identity through JWT tokens, while authorization controls access through roles, permissions, and resource ownership checks.

The ecosystem has matured significantly with FastAPI's official documentation moving away from deprecated libraries (python-jose, passlib) toward actively maintained alternatives (PyJWT, pwdlib). The dependency injection system makes it straightforward to implement layered security: basic authentication → role checking → resource ownership verification.

**Primary recommendation:** Use PyJWT + pwdlib + FastAPI's OAuth2PasswordBearer with dependency injection for authentication. Implement RBAC through custom dependencies that check user roles/permissions. Keep access tokens short-lived (15-30 min) and implement refresh token rotation for production systems.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyJWT | 2.x+ | JWT encoding/decoding | Actively maintained, recommended by FastAPI team, simple API, industry standard |
| pwdlib | latest | Password hashing (Argon2/Bcrypt) | Modern replacement for abandoned passlib, supports Argon2 (most secure), Python 3.13+ compatible |
| FastAPI OAuth2PasswordBearer | built-in | OAuth2 token scheme | Native FastAPI integration, automatic OpenAPI docs, follows OAuth2 standards |
| FastAPI Security | built-in | Dependency injection for auth | Enables scope-based permissions, integrates with OAuth2, supports SecurityScopes |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Redis | 5.0+ | Refresh token storage | Production refresh token whitelist/blacklist, token rotation tracking |
| python-multipart | latest | Form data parsing | Required for OAuth2PasswordRequestForm (username/password login) |
| Pydantic | 2.x | Token/user schemas | Validation of JWT claims, user data models |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyJWT | python-jose | python-jose is abandoned (3+ years no updates), PyJWT is actively maintained and sufficient |
| pwdlib | passlib | passlib deprecated in Python 3.13+, no active maintenance; use only for legacy hash migration |
| Argon2 | Bcrypt | Argon2 more resistant to GPU cracking; Bcrypt acceptable but Argon2 preferred for new projects |
| Custom RBAC | External services (Auth0 FGA, Permit.io) | External services add latency but provide fine-grained authorization, audit logs, multi-tenancy |

**Installation:**
```bash
pip install pyjwt "pwdlib[argon2]" python-multipart redis
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── core/
│   ├── security.py          # JWT creation, password hashing utilities
│   ├── config.py             # SECRET_KEY, ALGORITHM, TOKEN_EXPIRE settings
│   └── dependencies.py       # get_current_user, require_role, etc.
├── models/
│   ├── user.py               # User SQLAlchemy model with role field
│   └── refresh_token.py      # Optional: RefreshToken model for DB storage
├── schemas/
│   ├── auth.py               # Token, TokenData, UserLogin, UserCreate
│   └── user.py               # UserResponse, UserInDB
├── api/
│   ├── auth.py               # POST /auth/login, /auth/refresh, /auth/signup
│   └── users.py              # Protected user endpoints
└── services/
    ├── auth_service.py       # authenticate_user, create_tokens, verify_token
    └── user_service.py       # User CRUD operations
```

### Pattern 1: Basic JWT Authentication Flow

**What:** Standard OAuth2 password flow with JWT tokens

**When to use:** All authenticated APIs requiring user login

**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

SECRET_KEY = "your-secret-key-here"  # openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hash = PasswordHash.recommended()  # Uses Argon2

# Token creation
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token validation
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Fetch user from database
    user = await user_service.get_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

# Login endpoint
@router.post("/auth/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@router.get("/users/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
```

### Pattern 2: Password Hashing with Timing Attack Prevention

**What:** Secure password verification with constant-time comparison

**When to use:** All authentication systems to prevent timing attacks

**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# Dummy hash for timing attack prevention
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user_from_db(username)
    if not user:
        # Still hash to prevent timing attacks revealing valid usernames
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
```

### Pattern 3: Role-Based Access Control (RBAC)

**What:** Dependency that checks user role before granting access

**When to use:** Endpoints that require specific roles (admin, moderator, etc.)

**Example:**
```python
# Source: Multiple RBAC tutorials
from enum import Enum
from fastapi import Depends, HTTPException, status

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

def require_role(required_role: Role):
    """Dependency factory that checks user role."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker

# Usage
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Annotated[User, Depends(require_role(Role.ADMIN))]
):
    await user_service.delete(user_id)
    return {"message": "User deleted"}
```

### Pattern 4: Resource Ownership Authorization

**What:** Verify user owns or has permission for specific resource

**When to use:** User-owned resources (posts, profiles, comments)

**Example:**
```python
# Source: FastAPI authorization patterns
async def get_post_or_403(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> Post:
    """Get post if user owns it or is admin."""
    post = await post_service.get_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Allow if owner or admin
    if post.user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return post

@router.put("/posts/{post_id}")
async def update_post(
    post_data: PostUpdate,
    post: Annotated[Post, Depends(get_post_or_403)]
):
    return await post_service.update(post.id, post_data)
```

### Pattern 5: OAuth2 Scopes for Fine-Grained Permissions

**What:** Use OAuth2 scopes for permission-based access control

**When to use:** APIs with multiple permission levels beyond simple roles

**Example:**
```python
# Source: https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
from fastapi.security import SecurityScopes, Security

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "users:read": "Read user information",
        "users:write": "Create or update users",
        "posts:read": "Read posts",
        "posts:write": "Create or update posts",
    }
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    # Build WWW-Authenticate header with required scopes
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_scopes = payload.get("scope", "").split()
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Verify user has all required scopes
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    user = get_user(username)
    return user

# Usage with Security() instead of Depends()
@router.get("/users/")
async def read_users(
    current_user: Annotated[User, Security(get_current_user, scopes=["users:read"])]
):
    return await user_service.get_all()

@router.post("/users/")
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Security(get_current_user, scopes=["users:write"])]
):
    return await user_service.create(user_data)
```

### Pattern 6: Refresh Token with Redis Storage

**What:** Long-lived refresh tokens stored in Redis with rotation

**When to use:** Production systems requiring token refresh without re-login

**Example:**
```python
# Source: Redis token storage patterns
import redis.asyncio as redis
from datetime import timedelta

REFRESH_TOKEN_EXPIRE_DAYS = 7

async def create_refresh_token(user_id: int, redis_client: redis.Redis) -> str:
    """Create refresh token and store in Redis."""
    token_data = {"sub": str(user_id), "type": "refresh"}
    refresh_token = create_access_token(
        token_data,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    # Store in Redis with expiration
    await redis_client.setex(
        f"refresh_token:{user_id}:{refresh_token}",
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "valid"
    )
    return refresh_token

async def refresh_access_token(
    refresh_token: str,
    redis_client: redis.Redis
) -> dict:
    """Validate refresh token and issue new access token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        # Check token exists in Redis (not revoked)
        exists = await redis_client.exists(f"refresh_token:{user_id}:{refresh_token}")
        if not exists:
            raise HTTPException(status_code=401, detail="Token revoked or expired")

        # Issue new access token
        access_token = create_access_token({"sub": user_id})
        return {"access_token": access_token, "token_type": "bearer"}

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/auth/refresh")
async def refresh(
    refresh_token: str,
    redis_client: Annotated[redis.Redis, Depends(get_redis)]
):
    return await refresh_access_token(refresh_token, redis_client)

@router.post("/auth/logout")
async def logout(
    refresh_token: str,
    current_user: Annotated[User, Depends(get_current_user)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)]
):
    """Revoke refresh token by removing from Redis."""
    await redis_client.delete(f"refresh_token:{current_user.id}:{refresh_token}")
    return {"message": "Logged out successfully"}
```

### Anti-Patterns to Avoid

- **Storing JWT in localStorage**: Vulnerable to XSS attacks. Use HTTP-only cookies instead or accept the risk for simplicity in learning contexts
- **Long-lived access tokens**: Keep access tokens short (15-30 min). Use refresh tokens for persistence
- **No token expiration**: Always set `exp` claim. Tokens without expiration are permanent security risks
- **Checking passwords before username**: Timing attacks can reveal valid usernames. Always hash even for invalid users
- **Role in JWT payload only**: Store role in database and verify on each request. JWT can be decoded by anyone
- **Using python-jose or passlib**: Both are abandoned. Use PyJWT and pwdlib
- **Algorithm confusion**: Explicitly specify `algorithms=["HS256"]` in decode to prevent algorithm substitution attacks
- **Weak secrets**: Generate strong keys with `openssl rand -hex 32`, never commit to git

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom hash function | pwdlib with Argon2 | Timing attacks, salt generation, algorithm updates require expertise |
| JWT validation | String parsing | PyJWT library | Signature verification, timing attacks, algorithm confusion vulnerabilities |
| Token expiration | Manual timestamp checks | PyJWT's `exp` claim | Timezone handling, clock skew, automatic validation |
| RBAC permission system | Custom decorators from scratch | FastAPI Security + SecurityScopes | Standardized, OpenAPI integration, scope inheritance |
| Token blacklisting | Custom in-memory storage | Redis with TTL | Distributed systems, memory leaks, expiration cleanup |
| Session management | Rolling your own | Redis + refresh tokens | Concurrency, atomic operations, distributed systems |

**Key insight:** Authentication security is full of subtle timing attacks, cryptographic pitfalls, and edge cases. The FastAPI + PyJWT ecosystem has battle-tested solutions that handle these correctly.

## Common Pitfalls

### Pitfall 1: Signature Verification Disabled or Accepting "none" Algorithm

**What goes wrong:** JWT validation accepts tokens without signatures, allowing attackers to forge arbitrary tokens

**Why it happens:** Using jwt.decode without specifying algorithms, or accepting user-controlled algorithm header

**How to avoid:**
- Always specify `algorithms=["HS256"]` explicitly in `jwt.decode()`
- Never allow "none" algorithm
- Don't let token headers dictate which algorithm to use

**Warning signs:**
- `jwt.decode(token)` without algorithms parameter
- Dynamic algorithm selection based on token header
- Disabled signature verification in testing that leaked to production

### Pitfall 2: Weak or Exposed Secret Keys

**What goes wrong:** Attackers can sign valid tokens if they obtain the SECRET_KEY

**Why it happens:** Hardcoded secrets in code, committed to git, short/predictable keys

**How to avoid:**
- Generate strong keys: `openssl rand -hex 32`
- Store in environment variables, never commit to git
- Use different secrets for dev/staging/production
- Rotate keys periodically

**Warning signs:**
- SECRET_KEY in source code or committed files
- Generic secrets like "secret" or "your-secret-key-here"
- Same secret across environments

### Pitfall 3: JWT Payload Confusion (Storing Sensitive Data or Trusting Without Verification)

**What goes wrong:** Developers treat JWT payload as trusted data or store sensitive information

**Why it happens:** Misunderstanding that JWT is signed but not encrypted—anyone can decode it

**How to avoid:**
- Never store passwords, API keys, or PII in JWT
- Always verify claims (exp, sub) even though JWT is valid
- Re-fetch user data from database for authorization checks
- Treat JWT as opaque token identifier, not complete user session

**Warning signs:**
- Putting `password`, `credit_card`, or similar in JWT
- Using `payload["role"]` directly without DB verification
- Assuming JWT validity means user still exists/has permissions

### Pitfall 4: Missing or Improper Token Expiration

**What goes wrong:** Tokens never expire or have extremely long lifetimes (days/months)

**Why it happens:** Developer convenience or misunderstanding security implications

**How to avoid:**
- Access tokens: 15-30 minutes maximum
- Refresh tokens: 7-14 days with rotation
- Always include `exp` claim
- Validate expiration on every request

**Warning signs:**
- No `exp` claim in token
- `ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30` (30 days)
- No refresh token implementation

### Pitfall 5: Timing Attacks Revealing Valid Usernames

**What goes wrong:** Authentication response times differ for valid vs invalid usernames

**Why it happens:** Checking if user exists before hashing password

**How to avoid:**
- Always hash the password even if user doesn't exist
- Use dummy hash for consistent timing
- Return same error message for invalid username and password

**Warning signs:**
```python
# BAD - reveals valid usernames via timing
user = get_user(username)
if not user:
    return False  # Fast return, no hashing
if not verify_password(password, user.hash):
    return False  # Slow return after hashing
```

**Good pattern:**
```python
DUMMY_HASH = password_hash.hash("dummy")

user = get_user(username)
if not user:
    verify_password(password, DUMMY_HASH)  # Hash anyway
    return False
if not verify_password(password, user.hash):
    return False
return user
```

### Pitfall 6: Inadequate Authorization Checks (Confused Deputy)

**What goes wrong:** Authenticated user can access other users' resources

**Why it happens:** Only checking authentication (who you are) without authorization (what you can access)

**How to avoid:**
- Always verify resource ownership or permissions
- Don't trust user_id from request path/body
- Use current_user.id from validated token
- Implement ownership checks in dependencies

**Warning signs:**
```python
# BAD - any authenticated user can delete any post
@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)]
):
    await post_service.delete(post_id)  # No ownership check!
```

### Pitfall 7: Algorithm Confusion (RS256 → HS256 Attack)

**What goes wrong:** Server accepts tokens signed with wrong algorithm, using public key as HMAC secret

**Why it happens:** Not validating algorithm, trusting algorithm from token header

**How to avoid:**
- Specify exact algorithms in `jwt.decode(..., algorithms=["HS256"])`
- Don't use RS256 unless you need asymmetric encryption
- Reject tokens with unexpected algorithms

**Warning signs:**
- `jwt.decode(token, key)` without algorithms parameter
- Accepting multiple algorithms when only one is needed
- Algorithm verification logic based on token content

### Pitfall 8: Token Revocation Impossible

**What goes wrong:** Compromised tokens remain valid until expiration, can't logout users immediately

**Why it happens:** JWT is stateless by design—no built-in revocation mechanism

**How to avoid:**
- Implement token blacklist in Redis with TTL
- Store refresh tokens in Redis/DB for instant revocation
- Keep access token lifetime short
- On logout, blacklist refresh token and optionally access token

**Warning signs:**
- No logout endpoint
- No mechanism to revoke user's tokens
- Users can't be force-logged-out

## Code Examples

Verified patterns from official sources:

### Complete Login Flow with TestClient

```python
# Source: FastAPI testing patterns + OAuth2 docs
from fastapi.testclient import TestClient

# Test signup
response = client.post(
    "/auth/signup",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
)
assert response.status_code == 201
user_data = response.json()

# Test login
response = client.post(
    "/auth/login",
    data={  # OAuth2PasswordRequestForm expects form data, not JSON
        "username": "testuser",
        "password": "SecurePass123!"
    }
)
assert response.status_code == 200
token = response.json()["access_token"]

# Test protected endpoint
response = client.get(
    "/users/me",
    headers={"Authorization": f"Bearer {token}"}
)
assert response.status_code == 200
assert response.json()["username"] == "testuser"
```

### Role Enum and Database Model

```python
# Source: FastAPI RBAC patterns + SQLAlchemy 2.0
from enum import Enum
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role),
        default=Role.USER,
        server_default=Role.USER.value
    )
    is_active: Mapped[bool] = mapped_column(default=True)
```

### Permission Decorator with Multiple Roles

```python
# Source: FastAPI authorization patterns
from typing import List

def require_any_role(allowed_roles: List[Role]):
    """Dependency that accepts multiple roles."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

# Admin or moderator can delete posts
@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: Annotated[User, Depends(require_any_role([Role.ADMIN, Role.MODERATOR]))]
):
    await post_service.delete(post_id)
```

### Testing with Authentication Fixtures

```python
# Source: pytest + FastAPI testing patterns
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """Fixture that returns client with authentication token."""
    # Create test user
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )

    # Login to get token
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]

    # Set default authorization header
    client.headers = {
        "Authorization": f"Bearer {token}"
    }
    return client

def test_protected_endpoint(auth_client: TestClient):
    """Test with authenticated client."""
    response = auth_client.get("/users/me")
    assert response.status_code == 200

@pytest.fixture
def admin_client(client: TestClient, db: Session) -> TestClient:
    """Fixture for admin-authenticated client."""
    # Create admin user
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=password_hash.hash("adminpass"),
        role=Role.ADMIN
    )
    db.add(admin)
    db.commit()

    # Login as admin
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpass"}
    )
    token = response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

def test_admin_endpoint(admin_client: TestClient):
    """Test admin-only endpoint."""
    response = admin_client.delete("/users/123")
    assert response.status_code == 200
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| python-jose | PyJWT | 2024-2025 | FastAPI docs updated, python-jose abandoned 3+ years |
| passlib | pwdlib | 2024-2025 | passlib deprecated in Python 3.13+, pwdlib actively maintained |
| Bcrypt only | Argon2 preferred | 2023+ | Argon2 more resistant to GPU cracking attacks |
| Middleware auth | Dependency injection | Always preferred | Better testability, OpenAPI integration, scope-based permissions |
| Sessions | JWT tokens | 2020+ | Stateless, scalable, works across services |
| OAuth2PasswordRequestForm JSON | OAuth2PasswordRequestForm form data | FastAPI standard | OAuth2 spec requires form data (application/x-www-form-urlencoded) |

**Deprecated/outdated:**

- **python-jose**: Abandoned library, last update 3+ years ago, FastAPI docs migrated to PyJWT
- **passlib**: Deprecated in Python 3.13+ (crypt module removed), replaced by pwdlib
- **CryptContext**: Part of passlib, use pwdlib's PasswordHash.recommended() instead
- **"none" algorithm**: Security vulnerability, modern libraries reject it by default
- **localStorage for tokens**: XSS vulnerability, use HTTP-only cookies or accept risk for simpler implementations

## Open Questions

Things that couldn't be fully resolved:

1. **Refresh Token Storage: Redis vs Database**
   - What we know: Redis provides fast TTL and atomic operations, databases provide durability
   - What's unclear: Performance tradeoffs at scale, best practices for hybrid approaches
   - Recommendation: Start with Redis for simplicity (TTL automatic), move to DB if need persistence across restarts

2. **OAuth2 Scopes vs Roles: When to Use Which**
   - What we know: Scopes are fine-grained permissions, roles are user categories
   - What's unclear: Best practices for combining both in medium-sized APIs
   - Recommendation: Start with roles (simpler), add scopes if need API consumers with varying permissions

3. **Access Token in Redis for Blacklisting: Worth the State?**
   - What we know: Defeats JWT stateless benefit but enables instant revocation
   - What's unclear: Performance impact, whether short expiry is sufficient
   - Recommendation: Short-lived access tokens (15-30 min) + blacklisted refresh tokens covers most cases without access token blacklist

## Sources

### Primary (HIGH confidence)

- [FastAPI OAuth2 with JWT Official Docs](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - Complete JWT auth implementation
- [FastAPI OAuth2 Scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/) - Scope-based permissions pattern
- [PyJWT Official Docs](https://pyjwt.readthedocs.io/) - JWT encoding/decoding API
- [pwdlib GitHub](https://github.com/frankie567/pwdlib) - Modern password hashing
- [FastAPI Security Module](https://fastapi.tiangolo.com/tutorial/security/) - Built-in security utilities

### Secondary (MEDIUM confidence)

- [TestDriven.io FastAPI JWT Auth](https://testdriven.io/blog/fastapi-jwt-auth/) - Comprehensive JWT tutorial
- [Auth0 JWT Best Practices](https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/) - Token expiration and refresh patterns
- [Better Stack FastAPI Auth Guide](https://betterstack.com/community/guides/scaling-python/authentication-fastapi/) - Authentication and authorization patterns
- [Permit.io FastAPI RBAC Tutorial](https://www.permit.io/blog/fastapi-rbac-full-implementation-tutorial) - Role-based access control
- [GitHub Discussion: python-jose Abandonment](https://github.com/fastapi/fastapi/discussions/11345) - Migration to PyJWT
- [GitHub Discussion: passlib Maintenance](https://github.com/fastapi/fastapi/discussions/11773) - Migration to pwdlib

### Security Resources (MEDIUM-HIGH confidence)

- [Red Sentry JWT Vulnerabilities 2026](https://redsentry.com/resources/blog/jwt-vulnerabilities-list-2026-security-risks-mitigation-guide) - Security risks and mitigations
- [JWT Security Best Practices - Authgear](https://www.authgear.com/post/jwt-security-best-practices-common-vulnerabilities) - Common vulnerabilities
- [APIsec JWT Security](https://www.apisec.ai/blog/jwt-security-vulnerabilities-prevention) - Prevention strategies
- [42Crunch JWT Pitfalls](https://42crunch.com/7-ways-to-avoid-jwt-pitfalls/) - API security with JWT

### Implementation Examples (MEDIUM confidence)

- [FastAPI Permissions GitHub](https://github.com/holgi/fastapi-permissions) - Row-level security patterns
- [FastAPI Role and Permissions GitHub](https://github.com/00-Python/FastAPI-Role-and-Permissions) - Complete RBAC example
- [Redis Token Storage](https://dev.to/jacobsngoodwin/12-store-refresh-tokens-in-redis-1k5d) - Refresh token in Redis
- [FastAPI Users Redis](https://fastapi-users.github.io/fastapi-users/latest/configuration/authentication/strategies/redis/) - Token strategies

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official FastAPI docs and PyPI package status verified
- Architecture: HIGH - Patterns from official FastAPI docs and battle-tested tutorials
- Pitfalls: MEDIUM-HIGH - Security resources + community discussions, some patterns require real-world validation

**Research date:** 2026-02-26
**Valid until:** ~2026-03-28 (30 days - authentication patterns are stable)

**Note:** The authentication/authorization domain is relatively stable. PyJWT and pwdlib are actively maintained. Main changes expected: security vulnerability discoveries, new FastAPI features, potential new auth libraries.
