"""
Exercise 2: JWT Token Creation and Validation

Learn to create and validate JWT tokens using PyJWT.

Run: pytest 009-authentication-jwt/exercises/02_jwt_tokens.py -v
"""

import jwt
from datetime import datetime, timedelta, timezone

# Secret key for signing tokens (use openssl rand -hex 32 in production)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


# ============= TODO: Exercise 2.1 =============
# Create a JWT access token
# - Accept data dict and optional expires_delta
# - If expires_delta not provided, use timedelta(minutes=15)
# - Add "exp" claim: datetime.now(timezone.utc) + expires_delta
# - Add "iat" claim: datetime.now(timezone.utc)
# - Encode with jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
# - Return token string

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.2 =============
# Decode and validate a JWT token
# - Use jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# - Return the payload dict
# - If token is invalid or expired, raise ValueError with appropriate message

def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.3 =============
# Create a user-specific token
# - Create token with "sub" claim set to str(user_id)
# - Add "username" as custom claim
# - Use 30-minute expiration
# - Return token string

def create_user_token(user_id: int, username: str) -> str:
    """Create access token for a specific user."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.4 =============
# Check if a token is expired
# - Try to decode the token
# - Return True if expired (jwt.ExpiredSignatureError)
# - Return False if still valid
# - Do NOT raise exceptions - return boolean

def is_token_expired(token: str) -> bool:
    """Check if token is expired."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 009-authentication-jwt/exercises/02_jwt_tokens.py -v

def test_create_token():
    """Test creating a token returns a string."""
    token = create_access_token({"sub": "testuser"})

    assert isinstance(token, str)
    assert len(token) > 50
    # JWT has three parts: header.payload.signature
    assert token.count(".") == 2


def test_decode_valid_token():
    """Test decoding a valid token."""
    data = {"sub": "testuser", "user_id": 123}
    token = create_access_token(data)

    payload = decode_token(token)

    assert payload["sub"] == "testuser"
    assert payload["user_id"] == 123
    assert "exp" in payload
    assert "iat" in payload


def test_decode_expired_token():
    """Test decoding expired token raises ValueError."""
    # Create token that expires in -1 second (already expired)
    token = create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(seconds=-1)
    )

    try:
        decode_token(token)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "expired" in str(e).lower() or "invalid" in str(e).lower()


def test_decode_tampered_token():
    """Test decoding tampered token raises ValueError."""
    token = create_access_token({"sub": "testuser"})

    # Tamper with the token
    tampered_token = token[:-10] + "tampered12"

    try:
        decode_token(tampered_token)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_create_user_token():
    """Test creating user-specific token."""
    token = create_user_token(user_id=42, username="alice")

    payload = decode_token(token)

    assert payload["sub"] == "42"  # Should be string
    assert payload["username"] == "alice"
    assert "exp" in payload
    assert "iat" in payload

    # Check expiration is ~30 minutes
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
    duration = exp_time - iat_time

    # Should be close to 30 minutes (allow some tolerance)
    assert 29 * 60 < duration.total_seconds() < 31 * 60


def test_is_token_expired_fresh():
    """Test is_token_expired returns False for fresh token."""
    token = create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(minutes=30)
    )

    assert is_token_expired(token) is False


def test_is_token_expired_old():
    """Test is_token_expired returns True for expired token."""
    token = create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )

    assert is_token_expired(token) is True


def test_default_expiration():
    """Test default expiration is 15 minutes."""
    token = create_access_token({"sub": "testuser"})
    payload = decode_token(token)

    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
    duration = exp_time - iat_time

    # Should be close to 15 minutes
    assert 14 * 60 < duration.total_seconds() < 16 * 60


def test_custom_expiration():
    """Test custom expiration delta."""
    token = create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(hours=2)
    )
    payload = decode_token(token)

    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
    duration = exp_time - iat_time

    # Should be close to 2 hours
    assert 119 * 60 < duration.total_seconds() < 121 * 60
