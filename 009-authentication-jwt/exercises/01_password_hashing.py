"""
Exercise 1: Password Hashing with pwdlib

Learn secure password hashing using pwdlib and Argon2.

Run: pytest 009-authentication-jwt/exercises/01_password_hashing.py -v
"""

from pwdlib import PasswordHash

# Initialize password hasher
password_hash = PasswordHash.recommended()

# Dummy hash for timing attack prevention
DUMMY_HASH = password_hash.hash("dummy-password-for-timing-attacks")


# ============= TODO: Exercise 1.1 =============
# Hash a password using pwdlib
# - Use password_hash.hash()
# - Return the hash string

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.2 =============
# Verify a password against a hash
# - Use password_hash.verify()
# - Return True if password matches, False otherwise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.3 =============
# Create a user dict with hashed password
# - Return dict with: id=1, username (from param), hashed_password (NOT plain password)
# - Use hash_password() function

def create_user_with_password(username: str, password: str) -> dict:
    """Create a user dict with hashed password."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.4 =============
# Authenticate a user with timing attack prevention
# - Find user by username in users list
# - If user not found: hash password anyway (use DUMMY_HASH), return None
# - If user found: verify password
# - Return user dict (without hashed_password field) if valid, None if invalid
# - This prevents timing attacks by ensuring constant-time response

def authenticate_user(users: list[dict], username: str, password: str) -> dict | None:
    """Authenticate user with timing attack prevention."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 009-authentication-jwt/exercises/01_password_hashing.py -v

def test_hash_password():
    """Test that hashing produces a different value than input."""
    password = "SecurePass123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 50  # Argon2 hashes are long
    assert hashed.startswith("$argon2")  # Argon2 hash format


def test_verify_password_correct():
    """Test verifying correct password."""
    password = "MyPassword456"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test verifying incorrect password."""
    password = "MyPassword456"
    hashed = hash_password(password)

    assert verify_password("WrongPassword", hashed) is False


def test_different_hashes_for_same_password():
    """Test that salt produces different hashes."""
    password = "SamePassword"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Different hashes due to random salt
    assert hash1 != hash2

    # But both verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_user_with_password():
    """Test creating user with hashed password."""
    user = create_user_with_password("alice", "SecurePass123")

    assert user["id"] == 1
    assert user["username"] == "alice"
    assert "hashed_password" in user
    assert user["hashed_password"] != "SecurePass123"  # Not plain text
    assert user["hashed_password"].startswith("$argon2")  # Hashed


def test_authenticate_user_valid_credentials():
    """Test authenticating with correct credentials."""
    users = [
        {
            "id": 1,
            "username": "alice",
            "hashed_password": hash_password("password123")
        },
        {
            "id": 2,
            "username": "bob",
            "hashed_password": hash_password("secret456")
        }
    ]

    user = authenticate_user(users, "alice", "password123")

    assert user is not None
    assert user["id"] == 1
    assert user["username"] == "alice"
    assert "hashed_password" not in user  # Should not include hash in return


def test_authenticate_user_wrong_password():
    """Test authentication fails with wrong password."""
    users = [
        {
            "id": 1,
            "username": "alice",
            "hashed_password": hash_password("password123")
        }
    ]

    user = authenticate_user(users, "alice", "wrongpassword")

    assert user is None


def test_authenticate_user_unknown_username():
    """Test authentication fails with unknown username."""
    users = [
        {
            "id": 1,
            "username": "alice",
            "hashed_password": hash_password("password123")
        }
    ]

    user = authenticate_user(users, "bob", "password123")

    assert user is None


def test_timing_attack_prevention():
    """
    Test that authentication takes similar time for valid and invalid usernames.
    This is a conceptual test - the implementation should hash even for invalid users.
    """
    users = [
        {
            "id": 1,
            "username": "alice",
            "hashed_password": hash_password("password123")
        }
    ]

    # Both should hash the password (one real, one dummy)
    # We can't easily test timing, but we verify it doesn't fail
    result1 = authenticate_user(users, "alice", "wrongpass")
    result2 = authenticate_user(users, "bob", "anypass")

    assert result1 is None
    assert result2 is None
