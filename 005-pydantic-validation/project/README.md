# Project: User Registration with Comprehensive Validation

## Overview

Build a complete user registration system that validates every field thoroughly using Pydantic v2. This project demonstrates real-world validation patterns: password strength, email format, date validation, and cross-field checks.

## Requirements

Create a `user_registration.py` file with:

### 1. Pydantic Models

**UserCreate Schema:**
- `username`: 3-50 characters, alphanumeric only, converted to lowercase
- `email`: Valid email format
- `password`: Min 8 chars, must have uppercase, lowercase, and digit
- `password_confirm`: Must match password
- `display_name`: 1-100 characters
- `bio`: Optional, max 500 characters
- `date_of_birth`: String format YYYY-MM-DD, must be in the past
- `address`: Nested Address model

**Address Model:**
- `street`: Required string
- `city`: Required string
- `state`: 2 uppercase letters (US states)
- `zip_code`: 5 digits
- `country`: Default "US"

**UserResponse Schema:**
- All fields from UserCreate except passwords
- Add: `id` (int), `created_at` (string), `is_active` (bool)
- Excludes: `password`, `password_confirm`

### 2. FastAPI Endpoint

**POST /register**
- Accepts `UserCreate` model
- Returns `UserResponse` model (201 status)
- Simulates saving to database (in-memory dict)
- Generates ID and timestamp

### 3. Custom Validation

All validation happens in Pydantic models:
- Username: alphanumeric check + lowercase conversion
- Password: strength check (uppercase, lowercase, digit)
- Password confirmation: model validator
- Date of birth: must be in past
- Email: use Pydantic's built-in validation

## Starter Template

```python
"""
User Registration API with Comprehensive Validation

Run: uvicorn user_registration:app --reload
Test: pytest user_registration.py -v
"""

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Annotated, Self
from datetime import datetime

app = FastAPI(title="User Registration API")

# ============= MODELS =============

class Address(BaseModel):
    """Address model with validation."""
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    state: str = Field(pattern=r'^[A-Z]{2}$')  # Two uppercase letters
    zip_code: str = Field(pattern=r'^\d{5}$')  # Five digits
    country: str = "US"


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr  # Requires: pip install email-validator
    password: str = Field(min_length=8)
    password_confirm: str
    display_name: str = Field(min_length=1, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    date_of_birth: str  # Format: YYYY-MM-DD
    address: Address

    # TODO: Add @field_validator for username
    # - Check alphanumeric with .isalnum()
    # - Convert to lowercase
    # - Return transformed value

    # TODO: Add @field_validator for password
    # - Check min length 8
    # - Check has uppercase letter
    # - Check has lowercase letter
    # - Check has digit
    # - Raise ValueError with clear message for each failure

    # TODO: Add @field_validator for date_of_birth
    # - Parse date string to datetime
    # - Check that date is in the past (< today)
    # - Raise ValueError if in future

    # TODO: Add @model_validator to check passwords match
    # - Use mode='after'
    # - Compare self.password with self.password_confirm
    # - Raise ValueError if they don't match


class UserResponse(BaseModel):
    """Schema for user response (no passwords)."""
    id: int
    username: str
    email: str
    display_name: str
    bio: str | None
    date_of_birth: str
    address: Address
    is_active: bool
    created_at: str


# ============= DATA =============

# In-memory "database"
users_db: dict[int, dict] = {}
next_user_id = 1


# ============= ENDPOINTS =============

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Register new user with comprehensive validation.

    TODO: Implement registration logic:
    1. Generate ID (use global next_user_id)
    2. Hash password (simulate with "hashed_" + password for this exercise)
    3. Create user dict with all fields
    4. Add server-generated fields: id, created_at, is_active
    5. Save to users_db
    6. Increment next_user_id
    7. Return user data (response_model filters out password fields)
    """
    pass


# ============= TESTS (Optional) =============
# Uncomment to test with pytest

# client = TestClient(app)
#
# def test_register_valid_user():
#     """Test registering with valid data."""
#     user_data = {
#         "username": "alice123",
#         "email": "alice@example.com",
#         "password": "Secret123",
#         "password_confirm": "Secret123",
#         "display_name": "Alice Smith",
#         "bio": "Software developer",
#         "date_of_birth": "1990-01-01",
#         "address": {
#             "street": "123 Main St",
#             "city": "Springfield",
#             "state": "IL",
#             "zip_code": "62701"
#         }
#     }
#
#     response = client.post("/register", json=user_data)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["username"] == "alice123"
#     assert "password" not in data  # Filtered out
#     assert "id" in data  # Server-generated
#     assert "created_at" in data  # Server-generated
#
# def test_username_non_alphanumeric():
#     """Test that non-alphanumeric username fails."""
#     user_data = {
#         "username": "alice@123",  # Invalid
#         "email": "alice@example.com",
#         "password": "Secret123",
#         "password_confirm": "Secret123",
#         "display_name": "Alice",
#         "date_of_birth": "1990-01-01",
#         "address": {
#             "street": "123 Main St",
#             "city": "Springfield",
#             "state": "IL",
#             "zip_code": "62701"
#         }
#     }
#
#     response = client.post("/register", json=user_data)
#     assert response.status_code == 422
#
# def test_weak_password():
#     """Test that weak password fails validation."""
#     user_data = {
#         "username": "alice",
#         "email": "alice@example.com",
#         "password": "weak",  # No uppercase, no digit
#         "password_confirm": "weak",
#         "display_name": "Alice",
#         "date_of_birth": "1990-01-01",
#         "address": {
#             "street": "123 Main St",
#             "city": "Springfield",
#             "state": "IL",
#             "zip_code": "62701"
#         }
#     }
#
#     response = client.post("/register", json=user_data)
#     assert response.status_code == 422
#
# def test_password_mismatch():
#     """Test that mismatched passwords fail."""
#     user_data = {
#         "username": "alice",
#         "email": "alice@example.com",
#         "password": "Secret123",
#         "password_confirm": "Different123",  # Doesn't match
#         "display_name": "Alice",
#         "date_of_birth": "1990-01-01",
#         "address": {
#             "street": "123 Main St",
#             "city": "Springfield",
#             "state": "IL",
#             "zip_code": "62701"
#         }
#     }
#
#     response = client.post("/register", json=user_data)
#     assert response.status_code == 422
#
# def test_future_date_of_birth():
#     """Test that future date of birth fails."""
#     user_data = {
#         "username": "alice",
#         "email": "alice@example.com",
#         "password": "Secret123",
#         "password_confirm": "Secret123",
#         "display_name": "Alice",
#         "date_of_birth": "2030-01-01",  # Future date
#         "address": {
#             "street": "123 Main St",
#             "city": "Springfield",
#             "state": "IL",
#             "zip_code": "62701"
#         }
#     }
#
#     response = client.post("/register", json=user_data)
#     assert response.status_code == 422
#
# def test_invalid_address():
#     """Test that invalid address fails validation."""
#     user_data = {
#         "username": "alice",
#         "email": "alice@example.com",
#         "password": "Secret123",
#         "password_confirm": "Secret123",
#         "display_name": "Alice",
#         "date_of_birth": "1990-01-01",
#         "address": {
#             "street": "123 Main St",
#             "city": "Springfield",
#             "state": "Illinois",  # Should be 2 letters
#             "zip_code": "62701"
#         }
#     }
#
#     response = client.post("/register", json=user_data)
#     assert response.status_code == 422
```

## Success Criteria

- [ ] Username is validated and converted to lowercase
- [ ] Password strength is enforced (8+ chars, upper, lower, digit)
- [ ] Password confirmation check works
- [ ] Email validation works (use EmailStr)
- [ ] Date of birth must be in past
- [ ] Address validation works (state 2 letters, zip 5 digits)
- [ ] Nested Address model validates correctly
- [ ] Response excludes password fields
- [ ] Response includes server-generated fields (id, created_at, is_active)
- [ ] Endpoint returns 201 on success
- [ ] Endpoint returns 422 with clear errors on validation failure

## Testing

Run the API:
```bash
uvicorn user_registration:app --reload
```

Test with curl:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice123",
    "email": "alice@example.com",
    "password": "Secret123",
    "password_confirm": "Secret123",
    "display_name": "Alice Smith",
    "bio": "Software developer",
    "date_of_birth": "1990-01-01",
    "address": {
      "street": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "zip_code": "62701"
    }
  }'
```

Visit docs: http://localhost:8000/docs

## Stretch Goals

1. **Add phone number validation** - Support international formats (E.164)
2. **Add profile picture URL validation** - Check URL format and allowed domains
3. **Custom error messages** - Return user-friendly messages instead of Pydantic defaults
4. **Age validation** - Add field validator to ensure user is 13+ years old
5. **Prevent duplicate emails** - Check users_db before creating user
6. **Add nickname field** - Optional, 2-20 chars, alphanumeric + underscore
