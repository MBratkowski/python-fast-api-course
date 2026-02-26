# JWT Structure and Claims

## Why This Matters

You've probably decoded JWTs in your mobile app — maybe to check expiration before making a request, or to display the username without an API call. The payload is just base64-encoded JSON. Now you understand why: **JWT is transparent by design**. Security comes from the signature, not encryption.

## What is a JWT?

**JWT (JSON Web Token)** is a compact, URL-safe token format consisting of three parts separated by dots:

```
header.payload.signature
```

Example JWT:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Decode the first two parts (base64) and you get JSON. The third part is a cryptographic signature.

## JWT Parts Explained

### Part 1: Header

Describes the token type and signing algorithm:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- `alg`: Algorithm used for signing (HS256 = HMAC-SHA256)
- `typ`: Token type (always "JWT")

### Part 2: Payload (Claims)

Contains the data — called **claims**:

```json
{
  "sub": "1234567890",
  "username": "john_doe",
  "exp": 1735689600,
  "iat": 1735686000
}
```

Claims are key-value pairs. Some are standard (reserved), others are custom.

### Part 3: Signature

HMAC-SHA256 hash of `header + payload` using a secret key:

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

**This signature proves:**
- The token was created by someone with the SECRET_KEY
- The header and payload haven't been tampered with

## Standard Claims

| Claim | Name | Description | Example |
|-------|------|-------------|---------|
| `sub` | Subject | User identifier (usually user ID) | `"12345"` |
| `exp` | Expiration | Expiration timestamp (Unix time) | `1735689600` |
| `iat` | Issued At | Creation timestamp | `1735686000` |
| `iss` | Issuer | Who issued the token | `"my-api.com"` |
| `aud` | Audience | Who should accept the token | `"mobile-app"` |
| `jti` | JWT ID | Unique token identifier | `"abc123"` |

**Custom claims** can be anything:

```json
{
  "sub": "42",
  "username": "alice",
  "role": "admin",
  "premium": true
}
```

## JWT is Signed, NOT Encrypted

**Critical security insight**: Anyone can decode the payload.

```python
import base64
import json

token = "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
decoded = base64.urlsafe_b64decode(token + "==")
payload = json.loads(decoded)
# {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
```

**Never put sensitive data in JWT** (passwords, credit cards, PII). Only put data that's okay to be public.

The signature ensures **integrity** (token hasn't been modified), not **confidentiality** (token can't be read).

## Creating and Validating JWTs with PyJWT

**Installation:**
```bash
pip install pyjwt
```

**Create a token:**

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-secret-key"  # Generate with: openssl rand -hex 32
ALGORITHM = "HS256"

# Create token
payload = {
    "sub": "12345",
    "username": "alice",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
}
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
# "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Validate and decode a token:**

```python
try:
    # Decode and validate
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    # {"sub": "12345", "username": "alice", "exp": 1735689600}

    user_id = payload.get("sub")
    username = payload.get("username")

except jwt.ExpiredSignatureError:
    # Token has expired
    print("Token expired")

except jwt.InvalidTokenError:
    # Invalid signature or malformed token
    print("Invalid token")
```

**CRITICAL**: Always specify `algorithms=["HS256"]` in `decode()` to prevent **algorithm confusion attacks** where an attacker changes the algorithm to "none".

## Generating Strong Secrets

Never use weak secrets like `"secret"` or `"my-secret-key"`. Generate cryptographically strong keys:

```bash
openssl rand -hex 32
# 09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

Store in environment variables, never commit to git:

```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")
```

## Example: Complete Token Flow

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-generated-secret-key"
ALGORITHM = "HS256"

def create_access_token(user_id: int, username: str) -> str:
    """Create JWT access token."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

# Create token
token = create_access_token(user_id=42, username="alice")

# Verify token
try:
    payload = verify_token(token)
    print(f"User: {payload['username']}, ID: {payload['sub']}")
except ValueError as e:
    print(f"Error: {e}")
```

## Key Takeaways

1. JWT has three parts: **header.payload.signature**
2. The payload is **base64-encoded JSON** — anyone can read it
3. The signature **proves authenticity**, not confidentiality
4. Use **PyJWT** for encoding/decoding (not python-jose, which is abandoned)
5. Always specify `algorithms=["HS256"]` in decode to prevent attacks
6. Generate strong secrets with `openssl rand -hex 32`
7. Never put sensitive data in JWT — only user identifiers and metadata
