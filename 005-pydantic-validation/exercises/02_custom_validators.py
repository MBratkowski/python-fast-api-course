"""
Exercise 2: Custom Validators

Build custom validators with @field_validator and @model_validator.
Run: pytest 005-pydantic-validation/exercises/02_custom_validators.py -v
"""

from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Self
import pytest


# Exercise 2.1: Username validation with transformation
# TODO: Create Username model with field_validator that:
# - Ensures username is alphanumeric only (use .isalnum())
# - Ensures username is between 3-20 characters
# - Converts username to lowercase before returning
class Username(BaseModel):
    username: str

    # TODO: Add @field_validator for username


# Exercise 2.2: Password strength validation
# TODO: Create Password model with field_validator that ensures:
# - At least 8 characters
# - At least one uppercase letter
# - At least one lowercase letter
# - At least one digit
# Raise ValueError with descriptive message for each failed check
class Password(BaseModel):
    password: str

    # TODO: Add @field_validator for password


# Exercise 2.3: Date range validation (model validator)
# TODO: Create DateRange model with model_validator that ensures:
# - start_date is before end_date
# - Use @model_validator(mode='after')
# - Access self.start_date and self.end_date
# - Raise ValueError if start_date >= end_date
class DateRange(BaseModel):
    start_date: str
    end_date: str

    # TODO: Add @model_validator


# Exercise 2.4: Password confirmation (model validator)
# TODO: Create Registration model with model_validator that ensures:
# - password matches password_confirm
# - Use @model_validator(mode='after')
# - Raise ValueError if they don't match
class Registration(BaseModel):
    username: str
    password: str
    password_confirm: str

    # TODO: Add @model_validator


# ============= TESTS =============
# Run with: pytest 005-pydantic-validation/exercises/02_custom_validators.py -v

def test_username_valid():
    """Test valid username."""
    user = Username(username="alice123")
    assert user.username == "alice123"


def test_username_to_lowercase():
    """Test username conversion to lowercase."""
    user = Username(username="ALICE123")
    assert user.username == "alice123"


def test_username_non_alphanumeric():
    """Test username with non-alphanumeric characters."""
    with pytest.raises(ValidationError) as exc_info:
        Username(username="alice@123")
    errors = exc_info.value.errors()
    assert any('alphanumeric' in str(e['msg']).lower() for e in errors)


def test_username_too_short():
    """Test username too short."""
    with pytest.raises(ValidationError):
        Username(username="ab")  # Less than 3 characters


def test_username_too_long():
    """Test username too long."""
    with pytest.raises(ValidationError):
        Username(username="a" * 21)  # More than 20 characters


def test_password_valid():
    """Test valid password."""
    pwd = Password(password="Secret123")
    assert pwd.password == "Secret123"


def test_password_too_short():
    """Test password less than 8 characters."""
    with pytest.raises(ValidationError) as exc_info:
        Password(password="Sec123")
    errors = exc_info.value.errors()
    assert any('8' in str(e['msg']) for e in errors)


def test_password_no_uppercase():
    """Test password without uppercase letter."""
    with pytest.raises(ValidationError) as exc_info:
        Password(password="secret123")
    errors = exc_info.value.errors()
    assert any('uppercase' in str(e['msg']).lower() for e in errors)


def test_password_no_lowercase():
    """Test password without lowercase letter."""
    with pytest.raises(ValidationError) as exc_info:
        Password(password="SECRET123")
    errors = exc_info.value.errors()
    assert any('lowercase' in str(e['msg']).lower() for e in errors)


def test_password_no_digit():
    """Test password without digit."""
    with pytest.raises(ValidationError) as exc_info:
        Password(password="SecretPass")
    errors = exc_info.value.errors()
    assert any('digit' in str(e['msg']).lower() for e in errors)


def test_date_range_valid():
    """Test valid date range."""
    date_range = DateRange(
        start_date="2026-01-01",
        end_date="2026-12-31"
    )
    assert date_range.start_date < date_range.end_date


def test_date_range_invalid():
    """Test invalid date range (start after end)."""
    with pytest.raises(ValidationError) as exc_info:
        DateRange(
            start_date="2026-12-31",
            end_date="2026-01-01"
        )
    errors = exc_info.value.errors()
    assert any('before' in str(e['msg']).lower() for e in errors)


def test_date_range_equal():
    """Test date range with equal dates."""
    with pytest.raises(ValidationError):
        DateRange(
            start_date="2026-01-01",
            end_date="2026-01-01"
        )


def test_registration_valid():
    """Test valid registration with matching passwords."""
    reg = Registration(
        username="alice",
        password="Secret123",
        password_confirm="Secret123"
    )
    assert reg.password == reg.password_confirm


def test_registration_password_mismatch():
    """Test registration with non-matching passwords."""
    with pytest.raises(ValidationError) as exc_info:
        Registration(
            username="alice",
            password="Secret123",
            password_confirm="Different123"
        )
    errors = exc_info.value.errors()
    assert any('match' in str(e['msg']).lower() for e in errors)


def test_validators_transform_data():
    """Test that validators can transform data."""
    # Username should be converted to lowercase
    user = Username(username="MixedCase123")
    assert user.username == "mixedcase123"
    assert user.username.islower()
