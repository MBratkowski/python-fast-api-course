"""
Exercise 3: Nested Data

Handle nested Pydantic models and schema separation.
Run: pytest 005-pydantic-validation/exercises/03_nested_data.py -v
"""

from pydantic import BaseModel, Field, ValidationError
import pytest


# Exercise 3.1: Address model
# TODO: Create Address model with validation:
# - street: str
# - city: str
# - state: str (exactly 2 uppercase letters, use pattern r'^[A-Z]{2}$')
# - zip_code: str (5 digits, use pattern r'^\d{5}$')
class Address(BaseModel):
    pass  # TODO: Implement


# Exercise 3.2: ContactInfo model with nested Address
# TODO: Create ContactInfo model:
# - email: str
# - phone: str | None = None (optional)
# - address: Address (nested Address model)
class ContactInfo(BaseModel):
    pass  # TODO: Implement


# Exercise 3.3: Person model with list of contacts
# TODO: Create Person model:
# - name: str
# - age: int (ge=0)
# - contacts: list[ContactInfo] (list of ContactInfo models)
class Person(BaseModel):
    pass  # TODO: Implement


# Exercise 3.4: Schema separation - Create vs Response
# TODO: Create two models for person data:
# - PersonCreate: name, age, email (fields for creating person)
# - PersonResponse: id, name, age, email, created_at (fields for API response)
# PersonResponse should include server-generated fields that PersonCreate doesn't have
class PersonCreate(BaseModel):
    pass  # TODO: Implement


class PersonResponse(BaseModel):
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 005-pydantic-validation/exercises/03_nested_data.py -v

def test_address_valid():
    """Test creating valid address."""
    address = Address(
        street="123 Main St",
        city="Springfield",
        state="IL",
        zip_code="62701"
    )
    assert address.state == "IL"
    assert address.zip_code == "62701"


def test_address_invalid_state():
    """Test that invalid state format raises error."""
    with pytest.raises(ValidationError) as exc_info:
        Address(
            street="123 Main St",
            city="Springfield",
            state="Illinois",  # Should be 2 letters
            zip_code="62701"
        )
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('state',) for e in errors)


def test_address_invalid_zip():
    """Test that invalid zip code raises error."""
    with pytest.raises(ValidationError) as exc_info:
        Address(
            street="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="1234"  # Should be 5 digits
        )
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('zip_code',) for e in errors)


def test_contact_info_with_phone():
    """Test contact info with optional phone."""
    contact = ContactInfo(
        email="alice@example.com",
        phone="555-1234",
        address={
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701"
        }
    )
    assert contact.phone == "555-1234"
    assert contact.address.city == "Springfield"


def test_contact_info_without_phone():
    """Test contact info without optional phone."""
    contact = ContactInfo(
        email="bob@example.com",
        address={
            "street": "456 Oak Ave",
            "city": "Chicago",
            "state": "IL",
            "zip_code="60601"
        }
    )
    assert contact.phone is None
    assert contact.address.city == "Chicago"


def test_contact_info_nested_validation():
    """Test that nested address validation works."""
    with pytest.raises(ValidationError) as exc_info:
        ContactInfo(
            email="alice@example.com",
            address={
                "street": "123 Main St",
                "city": "Springfield",
                "state": "Illinois",  # Invalid state format
                "zip_code": "62701"
            }
        )
    # Error should reference nested path
    errors = exc_info.value.errors()
    assert any('address' in str(e['loc']) for e in errors)


def test_person_with_contacts():
    """Test person with list of contacts."""
    person = Person(
        name="Alice",
        age=30,
        contacts=[
            {
                "email": "alice@home.com",
                "address": {
                    "street": "123 Main St",
                    "city": "Springfield",
                    "state": "IL",
                    "zip_code": "62701"
                }
            },
            {
                "email": "alice@work.com",
                "phone": "555-9999",
                "address": {
                    "street": "456 Work Plaza",
                    "city": "Chicago",
                    "state": "IL",
                    "zip_code": "60601"
                }
            }
        ]
    )
    assert len(person.contacts) == 2
    assert person.contacts[0].email == "alice@home.com"
    assert person.contacts[1].phone == "555-9999"


def test_person_negative_age():
    """Test that negative age raises error."""
    with pytest.raises(ValidationError):
        Person(
            name="Alice",
            age=-5,  # Must be >= 0
            contacts=[]
        )


def test_person_invalid_nested_contact():
    """Test that invalid nested contact raises error."""
    with pytest.raises(ValidationError) as exc_info:
        Person(
            name="Bob",
            age=25,
            contacts=[
                {
                    "email": "bob@example.com",
                    "address": {
                        "street": "123 Main",
                        "city": "City",
                        "state": "XYZ",  # Invalid - should be 2 letters
                        "zip_code": "12345"
                    }
                }
            ]
        )
    errors = exc_info.value.errors()
    # Should reference deeply nested path
    assert any('contacts' in str(e['loc']) for e in errors)


def test_person_create_schema():
    """Test PersonCreate schema."""
    person = PersonCreate(
        name="Alice",
        age=30,
        email="alice@example.com"
    )
    assert person.name == "Alice"
    assert person.age == 30
    assert person.email == "alice@example.com"


def test_person_response_schema():
    """Test PersonResponse schema includes server fields."""
    person = PersonResponse(
        id=123,
        name="Alice",
        age=30,
        email="alice@example.com",
        created_at="2026-02-26T10:00:00Z"
    )
    assert person.id == 123
    assert person.created_at == "2026-02-26T10:00:00Z"


def test_schema_separation():
    """Test that Create and Response schemas are different."""
    # PersonCreate should NOT have id or created_at in required fields
    create_data = {
        "name": "Bob",
        "age": 25,
        "email": "bob@example.com"
    }
    person_create = PersonCreate(**create_data)

    # PersonResponse SHOULD have id and created_at
    response_data = {
        "id": 456,
        "name": "Bob",
        "age": 25,
        "email": "bob@example.com",
        "created_at": "2026-02-26T11:00:00Z"
    }
    person_response = PersonResponse(**response_data)

    # Verify PersonResponse has fields that PersonCreate doesn't
    assert hasattr(person_response, 'id')
    assert hasattr(person_response, 'created_at')
