# Password Hashing

## Why This Matters

In mobile development, you send the user's password to the server and trust it's handled securely. Now YOU are that server. One breach of plain-text passwords and your users are compromised everywhere they reused that password.

**Never store passwords in plain text.** Ever. Hash them with a proper password hashing algorithm.

## What is Hashing?

A hash function is a **one-way transformation**: easy to compute, impossible to reverse.

```python
password = "SecurePass123"
hash = hash_function(password)
# hash = "$argon2id$v=19$m=65536,t=3,p=4$..."

# Can verify:
verify(password, hash)  # True

# Cannot reverse:
reverse(hash)  # Impossible!
```

## Why NOT Use MD5/SHA-256?

MD5 and SHA are designed for speed — great for checksums, terrible for passwords.

- **Too fast**: Attackers can try billions of passwords per second
- **Rainbow tables**: Precomputed hash databases for common passwords
- **No salt**: Same password → same hash (reveals duplicates)

```python
# BAD - MD5 is crackable in seconds
import hashlib
hash = hashlib.md5(b"password123").hexdigest()
# "482c811da5d5b4bc6d497ffa98491e38"
# Google this hash → "password123" revealed
```

## Modern Password Hashing Algorithms

| Algorithm | Speed | Security | When to Use |
|-----------|-------|----------|-------------|
| **Argon2** | Slow (memory-hard) | Highest | **Recommended for all new projects** |
| **bcrypt** | Slow | High | Time-tested, widely supported |
| **scrypt** | Slow (memory-hard) | High | Alternative to Argon2 |
| PBKDF2 | Configurable | Moderate | Legacy systems |

**Argon2** is the winner of the Password Hashing Competition (2015) and the current best practice.

## Using pwdlib with Argon2

`pwdlib` is the modern Python library for password hashing (replaces the deprecated `passlib`).

```python
from pwdlib import PasswordHash

# Create hasher (Argon2 by default)
password_hash = PasswordHash.recommended()

# Hash a password
hashed = password_hash.hash("SecurePass123")
# "$argon2id$v=19$m=65536,t=3,p=4$abc123..."

# Verify password
is_valid = password_hash.verify("SecurePass123", hashed)  # True
is_valid = password_hash.verify("WrongPassword", hashed)  # False
```

## Salt: Automatic Protection

A **salt** is random data added to the password before hashing. This ensures that the same password produces different hashes.

```python
hash1 = password_hash.hash("password123")
hash2 = password_hash.hash("password123")

# Different hashes!
# hash1: "$argon2id$v=19$m=65536,t=3,p=4$abc123..."
# hash2: "$argon2id$v=19$m=65536,t=3,p=4$xyz789..."
```

`pwdlib` (and all modern hashers) generate salt automatically. You don't need to manage it — it's embedded in the hash string.

## Timing Attack Prevention

**Problem**: If you check "does user exist?" before hashing the password, attackers can measure response times to discover valid usernames.

```python
# BAD - Timing attack reveals valid usernames
def authenticate(username, password):
    user = get_user(username)
    if not user:
        return None  # Fast response (no hashing)
    if not verify_password(password, user.hashed_password):
        return None  # Slow response (hashing occurred)
    return user
```

**Solution**: Always hash the password, even if the user doesn't exist.

```python
# GOOD - Constant-time authentication
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# Hash a dummy password once at startup
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")

def authenticate(username, password):
    user = get_user(username)

    if not user:
        # Hash anyway to prevent timing attacks
        password_hash.verify(password, DUMMY_HASH)
        return None

    # Verify actual password
    if not password_hash.verify(password, user.hashed_password):
        return None

    return user
```

Both code paths hash the password, so response times are consistent.

## Complete Example

```python
from pwdlib import PasswordHash

# Initialize hasher
pwd_hasher = PasswordHash.recommended()

# Signup: Hash password before storing
def create_user(username: str, password: str):
    hashed_password = pwd_hasher.hash(password)
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return user

# Login: Verify password
def authenticate_user(username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        # Timing attack prevention
        pwd_hasher.verify(password, DUMMY_HASH)
        return None

    if not pwd_hasher.verify(password, user.hashed_password):
        return None

    return user
```

## Key Takeaways

1. **Never store plain-text passwords** — hash them with Argon2
2. Use **pwdlib** with `PasswordHash.recommended()` (not passlib, which is deprecated)
3. Hashing is one-way — you can verify but never decrypt
4. Salt is automatic with modern hashers
5. **Prevent timing attacks** — always hash even for invalid usernames
