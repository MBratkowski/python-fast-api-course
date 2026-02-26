# Access and Refresh Tokens

## Why This Matters

In mobile development, you implement this flow: store the refresh token securely in Keychain/Keystore, store the access token in memory, and silently refresh when you get a 401. Now you're building the server that issues and validates both tokens.

## Why Two Tokens?

Using a single long-lived token is risky — if it's stolen, an attacker has access until it expires (which could be weeks or months).

The solution: **two-token pattern**

- **Access token**: Short-lived (15-30 min), sent with every request
- **Refresh token**: Long-lived (7-14 days), used ONLY to get new access tokens

If an access token is stolen, it's only valid for minutes. The refresh token lives in secure storage and is rarely transmitted.

## Access Token

**Purpose**: Prove identity on every API request

**Characteristics**:
- Short expiration (15-30 minutes)
- Contains user identity (`sub` claim with user ID)
- Sent in `Authorization: Bearer <token>` header
- Validated on every protected endpoint

**Example payload**:
```json
{
  "sub": "12345",
  "username": "alice",
  "exp": 1735687800,
  "iat": 1735686000
}
```

## Refresh Token

**Purpose**: Get a new access token without re-login

**Characteristics**:
- Long expiration (7-14 days)
- Contains minimal data (just user ID)
- Used ONLY at `/auth/refresh` endpoint
- Stored securely (database or Redis)
- Can be revoked (for logout or security)

**Example payload**:
```json
{
  "sub": "12345",
  "type": "refresh",
  "exp": 1736294400,
  "iat": 1735686000
}
```

## The Refresh Flow

```
1. User logs in
   ← Server returns: access token (30 min) + refresh token (7 days)

2. User makes API requests
   → Send: Authorization: Bearer <access_token>
   ← Server validates and responds

3. Access token expires (30 minutes later)
   → API request with expired access token
   ← Server returns: 401 Unauthorized

4. Client refreshes token
   → POST /auth/refresh with refresh token
   ← Server validates refresh token
   ← Server returns: new access token (30 min)
   ← Optionally: new refresh token (rotation)

5. Repeat from step 2
```

## Creating Both Tokens

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(user_id: int, username: str) -> str:
    """Create short-lived access token."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    """Create long-lived refresh token."""
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

## Login Endpoint

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and issue tokens."""
    # Authenticate user
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

## Refresh Endpoint

```python
@router.post("/refresh")
async def refresh(refresh_token: str):
    """Exchange refresh token for new access token."""
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = int(payload.get("sub"))

        # Get user from database
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Issue new access token
        new_access_token = create_access_token(user.id, user.username)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

## Why Short-Lived Access Tokens?

**Scenario**: An attacker steals an access token (from network sniffing, XSS, compromised device).

With a **long-lived token** (e.g., 30 days):
- Attacker has access for 30 days
- User can't revoke it (JWT is stateless)
- No way to detect abuse

With a **short-lived token** (e.g., 30 min):
- Attacker has access for only 30 minutes
- User refreshes with secure refresh token
- Compromise window is minimal

## Token Rotation (Advanced)

Each time a refresh token is used, issue a **new refresh token** and invalidate the old one.

**Benefits**:
- Detects token theft (if both client and attacker use the same refresh token, the second use fails)
- Limits damage from stolen refresh tokens

```python
@router.post("/refresh")
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh with rotation."""
    # Validate refresh token
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = int(payload.get("sub"))

    # Check if token is revoked (database check)
    if is_token_revoked(db, refresh_token):
        raise HTTPException(status_code=401, detail="Token revoked")

    user = get_user_by_id(db, user_id)

    # Create new tokens
    new_access_token = create_access_token(user.id, user.username)
    new_refresh_token = create_refresh_token(user.id)

    # Revoke old refresh token
    revoke_token(db, refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
```

## Mobile Client Flow

In your mobile app, the flow looks like this:

```swift
// iOS example
class AuthManager {
    func login(username: String, password: String) async throws {
        let response = try await api.post("/auth/login", body: [
            "username": username,
            "password": password
        ])

        // Store tokens securely
        try keychain.save(response.accessToken, for: "access_token")
        try keychain.save(response.refreshToken, for: "refresh_token")
    }

    func makeAuthenticatedRequest() async throws {
        var accessToken = try keychain.load("access_token")

        // Try request with current access token
        do {
            return try await api.get("/protected", token: accessToken)
        } catch APIError.unauthorized {
            // Token expired, refresh it
            accessToken = try await refreshAccessToken()
            return try await api.get("/protected", token: accessToken)
        }
    }

    func refreshAccessToken() async throws -> String {
        let refreshToken = try keychain.load("refresh_token")

        let response = try await api.post("/auth/refresh", body: [
            "refresh_token": refreshToken
        ])

        // Update stored access token
        try keychain.save(response.accessToken, for: "access_token")

        return response.accessToken
    }
}
```

## Key Takeaways

1. **Access tokens**: Short-lived (15-30 min), sent with every request
2. **Refresh tokens**: Long-lived (7-14 days), used only to get new access tokens
3. Short-lived access tokens limit damage from token theft
4. Refresh tokens live in secure storage (Keychain/Keystore on mobile)
5. The refresh flow: access expires → client sends refresh → server issues new access
6. **Token rotation**: Issue new refresh token on each refresh for added security
