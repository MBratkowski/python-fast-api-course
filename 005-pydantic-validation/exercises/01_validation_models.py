"""
Exercise 1: Validation Models

Create Pydantic models with various field validations.
Run: pytest 005-pydantic-validation/exercises/01_validation_models.py -v
"""

from pydantic import BaseModel, Field, ValidationError
import pytest


# Exercise 1.1: Product model with validation
# TODO: Create Product model with the following fields:
# - name: str (min_length=1, max_length=100)
# - price: float (gt=0) - must be greater than 0
# - quantity: int (ge=0) - must be greater than or equal to 0
# - category: str
class Product(BaseModel):
    pass  # TODO: Implement


# Exercise 1.2: Email model with validation
# TODO: Create Email model with the following fields:
# - address: str (must contain "@" - use pattern r'.*@.*')
# - subject: str (max_length=200)
# - body: str
# - priority: int (ge=1, le=5) - between 1 and 5
class Email(BaseModel):
    pass  # TODO: Implement


# Exercise 1.3: Config model with defaults and ranges
# TODO: Create Config model with the following fields:
# - debug: bool = False (default)
# - port: int = 8000 (default, must be ge=1024, le=65535)
# - host: str = "localhost" (default)
# - workers: int = 1 (default, must be ge=1, le=32)
class Config(BaseModel):
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 005-pydantic-validation/exercises/01_validation_models.py -v

def test_product_valid():
    """Test creating product with valid data."""
    product = Product(
        name="Laptop",
        price=999.99,
        quantity=10,
        category="electronics"
    )
    assert product.name == "Laptop"
    assert product.price == 999.99
    assert product.quantity == 10


def test_product_name_too_long():
    """Test that name exceeding max_length raises error."""
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="x" * 101,  # Exceeds max_length
            price=10.0,
            quantity=5,
            category="test"
        )
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('name',) for e in errors)


def test_product_negative_price():
    """Test that negative price raises error."""
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Item",
            price=-10.0,  # Must be > 0
            quantity=5,
            category="test"
        )
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('price',) for e in errors)


def test_product_negative_quantity():
    """Test that negative quantity raises error."""
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Item",
            price=10.0,
            quantity=-5,  # Must be >= 0
            category="test"
        )
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('quantity',) for e in errors)


def test_email_valid():
    """Test creating email with valid data."""
    email = Email(
        address="user@example.com",
        subject="Hello",
        body="Test message",
        priority=3
    )
    assert "@" in email.address
    assert email.priority == 3


def test_email_missing_at():
    """Test that address without @ raises error."""
    with pytest.raises(ValidationError) as exc_info:
        Email(
            address="userexample.com",  # Missing @
            subject="Test",
            body="Body",
            priority=1
        )
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('address',) for e in errors)


def test_email_subject_too_long():
    """Test that subject exceeding max_length raises error."""
    with pytest.raises(ValidationError):
        Email(
            address="user@example.com",
            subject="x" * 201,  # Exceeds max_length
            body="Body",
            priority=1
        )


def test_email_priority_out_of_range():
    """Test that priority outside 1-5 raises error."""
    with pytest.raises(ValidationError):
        Email(
            address="user@example.com",
            subject="Test",
            body="Body",
            priority=10  # Must be 1-5
        )


def test_config_defaults():
    """Test that config uses default values."""
    config = Config()
    assert config.debug is False
    assert config.port == 8000
    assert config.host == "localhost"
    assert config.workers == 1


def test_config_override_defaults():
    """Test overriding config defaults."""
    config = Config(
        debug=True,
        port=3000,
        host="0.0.0.0",
        workers=4
    )
    assert config.debug is True
    assert config.port == 3000
    assert config.host == "0.0.0.0"
    assert config.workers == 4


def test_config_port_too_low():
    """Test that port below 1024 raises error."""
    with pytest.raises(ValidationError):
        Config(port=80)  # Must be >= 1024


def test_config_port_too_high():
    """Test that port above 65535 raises error."""
    with pytest.raises(ValidationError):
        Config(port=70000)  # Must be <= 65535


def test_config_workers_out_of_range():
    """Test that workers outside 1-32 raises error."""
    with pytest.raises(ValidationError):
        Config(workers=0)  # Must be >= 1

    with pytest.raises(ValidationError):
        Config(workers=50)  # Must be <= 32
