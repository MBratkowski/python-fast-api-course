# Token Expiration and Rotation

## Why This Matters

This is like managing session tokens in your mobile app's auth manager — but server-side. You decide the lifecycle: when tokens are born, when they expire, and when they die. Understanding token expiration prevents security holes and creates a smooth user experience.

## Setting Token Expiration

Expiration is controlled by the `exp` claim (Unix timestamp):

```python
from datetime import datetime, timedelta, timezone
import jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_token_with_expiration(user_id: int, expires_delta: timedelta):
    """Create token with specific expiration."""
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(user_id),
        "exp": expire,  # Unix timestamp
        "iat": now      # Issued at timestamp
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Access token: expires in 30 minutes
access_token = create_token_with_expiration(
    user_id=42,
    expires_delta=timedelta(minutes=30)
)

# Refresh token: expires in 7 days
refresh_token = create_token_with_expiration(
    user_id=42,
    expires_delta=timedelta(days=7)
)
```

## Automatic Expiration Validation

PyJWT automatically validates the `exp` claim when decoding:

```python
import jwt

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    # Token is valid and not expired
    print(f"User: {payload['sub']}")

except jwt.ExpiredSignatureError:
    # Token has expired
    print("Token expired - please refresh")

except jwt.InvalidTokenError:
    # Token is malformed or signature invalid
    print("Invalid token")
```

**No manual time comparison needed** — PyJWT handles it.

## Handling Expired Tokens in FastAPI

Return clear error messages when tokens expire:

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate token and return user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Get user from database
        user = get_user_by_id(int(user_id))
        if user is None:
            raise credentials_exception

        return user

    except jwt.ExpiredSignatureError:
        # Return 401 with specific message
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise credentials_exception
```

## Refresh Token Rotation

**Problem**: Refresh tokens are long-lived. If one is stolen, the attacker has persistent access.

**Solution**: **Token rotation** — issue a new refresh token each time it's used, and invalidate the old one.

### How Rotation Works

```
1. User logs in
   ← Server: access token + refresh token (v1)

2. Access token expires
   → Client sends: refresh token (v1)
   ← Server: new access token + new refresh token (v2)
   ← Server: invalidate refresh token (v1)

3. Access token expires again
   → Client sends: refresh token (v2)
   ← Server: new access token + new refresh token (v3)
   ← Server: invalidate refresh token (v2)
```

**Benefit**: If an attacker steals refresh token v1 and uses it after the legitimate user got v2, the server detects it (v1 is revoked) and can lock the account.

### Implementing Rotation

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import jwt

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/refresh")
async def refresh_with_rotation(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh with token rotation."""
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))

        # Check if token is revoked (database or Redis)
        if is_token_revoked(db, refresh_token):
            # Token already used - possible theft!
            raise HTTPException(
                status_code=401,
                detail="Refresh token has been revoked"
            )

        # Get user
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Create new tokens
        new_access_token = create_access_token(user.id, user.username)
        new_refresh_token = create_refresh_token(user.id)

        # Revoke old refresh token
        revoke_token(db, refresh_token)

        # Store new refresh token
        store_refresh_token(db, user.id, new_refresh_token)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

## Token Revocation Strategies

### Strategy 1: Redis Blacklist with TTL

Store revoked tokens in Redis with automatic expiration:

```python
import redis
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def revoke_token(token: str, expires_in: timedelta):
    """Add token to blacklist with TTL."""
    # Store for the remaining lifetime of the token
    redis_client.setex(
        f"revoked:{token}",
        expires_in,
        "1"
    )

def is_token_revoked(token: str) -> bool:
    """Check if token is blacklisted."""
    return redis_client.exists(f"revoked:{token}") > 0
```

**Pros**: Automatic cleanup (TTL), fast lookups
**Cons**: Requires Redis

### Strategy 2: Database Storage

Store refresh tokens in a database table:

```python
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

def store_refresh_token(db: Session, user_id: int, token: str):
    """Store refresh token in database."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(refresh_token)
    db.commit()

def is_token_revoked(db: Session, token: str) -> bool:
    """Check if token is revoked."""
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token
    ).first()

    if not refresh_token:
        return True  # Token doesn't exist = revoked

    return refresh_token.is_revoked
```

**Pros**: Persistent, can track token usage
**Cons**: Database overhead, manual cleanup of expired tokens

## Logout: Revoking Refresh Tokens

```python
@router.post("/logout")
async def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout by revoking refresh token."""
    # Revoke the refresh token
    revoke_token(db, refresh_token)

    return {"message": "Logged out successfully"}
```

**Note**: Access tokens can't be revoked (they're stateless). They'll remain valid until expiration. That's why short expiration times are critical.

## Force Logout All Sessions

To log out a user from all devices, revoke all their refresh tokens:

```python
def revoke_all_user_tokens(db: Session, user_id: int):
    """Revoke all refresh tokens for a user."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).update({"is_revoked": True})
    db.commit()
```

Or change the user's secret (advanced):

```python
# User model with token_version
class User(Base):
    token_version: Mapped[int] = mapped_column(default=0)

# Include version in token
def create_access_token(user):
    payload = {
        "sub": str(user.id),
        "token_version": user.token_version,
        "exp": ...
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Validate version
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user = get_user_by_id(int(payload["sub"]))

    if payload["token_version"] != user.token_version:
        raise HTTPException(status_code=401, detail="Token invalidated")

    return user

# Logout all sessions by incrementing version
def force_logout_all(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    user.token_version += 1
    db.commit()
```

## Key Takeaways

1. **Set expiration** with `exp` claim and `timedelta`
2. PyJWT **automatically validates** expiration on decode
3. **Short access tokens** (15-30 min) limit damage from theft
4. **Refresh token rotation**: Issue new refresh token on each use
5. **Revocation strategies**: Redis blacklist (fast) or database (persistent)
6. **Logout**: Revoke refresh token, access token expires naturally
7. **Force logout**: Revoke all user's refresh tokens or increment token version
