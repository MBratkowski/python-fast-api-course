# Custom Validators

## Why This Matters

Built-in validation (`min_length`, `ge`, `pattern`) covers common cases. But what about "password must contain uppercase, lowercase, and digit"? Or "end_date must be after start_date"? Custom validators let you add business rules that Field() can't express. Like custom form validation in your mobile app, but declarative.

## Field Validators

Validate individual fields with `@field_validator`:

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Username must be alphanumeric."""
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v

    @field_validator('password')
    @classmethod
    def password_strong(cls, v: str) -> str:
        """Password must be strong."""
        if len(v) < 8:
            raise ValueError('must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('must contain digit')
        return v

# Valid
user = User(username="alice123", password="Secret123")

# Invalid username
try:
    user = User(username="alice@123", password="Secret123")
except ValidationError:
    # username: must be alphanumeric
    pass
```

**Key points:**
- Use `@field_validator('field_name')`
- Must be `@classmethod`
- Takes `cls` and field value `v`
- Raise `ValueError` with error message
- Return the (possibly transformed) value

## Transforming Values

Validators can modify values:

```python
class User(BaseModel):
    username: str
    email: str

    @field_validator('username')
    @classmethod
    def username_lower(cls, v: str) -> str:
        """Convert username to lowercase."""
        return v.lower()

    @field_validator('email')
    @classmethod
    def email_strip(cls, v: str) -> str:
        """Strip whitespace from email."""
        return v.strip().lower()

# Input: "Alice", "  BOB@EXAMPLE.COM  "
user = User(username="Alice", email="  BOB@EXAMPLE.COM  ")

print(user.username)  # "alice"
print(user.email)  # "bob@example.com"
```

## Validating Multiple Fields

Use same validator for multiple fields:

```python
class Form(BaseModel):
    first_name: str
    last_name: str

    @field_validator('first_name', 'last_name')
    @classmethod
    def names_not_empty(cls, v: str) -> str:
        """Names cannot be empty or whitespace."""
        if not v.strip():
            raise ValueError('cannot be empty')
        return v.strip()
```

## Model Validators

Validate entire model (cross-field validation):

```python
from pydantic import BaseModel, model_validator
from typing import Self

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode='after')
    def check_dates(self) -> Self:
        """Ensure start_date is before end_date."""
        if self.start_date >= self.end_date:
            raise ValueError('start_date must be before end_date')
        return self

# Valid
range1 = DateRange(start_date="2026-01-01", end_date="2026-12-31")

# Invalid
try:
    range2 = DateRange(start_date="2026-12-31", end_date="2026-01-01")
except ValidationError:
    # start_date must be before end_date
    pass
```

**`mode='after'`** means validation runs after field validators. Use `'before'` for raw data.

## Password Confirmation Pattern

Common pattern for password confirmation:

```python
class Registration(BaseModel):
    username: str
    password: str
    password_confirm: str

    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        """Ensure passwords match."""
        if self.password != self.password_confirm:
            raise ValueError('passwords do not match')
        return self
```

## Before vs After Mode

```python
class Example(BaseModel):
    value: int

    @field_validator('value', mode='before')
    @classmethod
    def convert_before(cls, v):
        """Runs BEFORE type conversion."""
        # v might be string "123"
        if isinstance(v, str):
            return int(v) * 2
        return v

    @field_validator('value', mode='after')
    @classmethod
    def validate_after(cls, v: int) -> int:
        """Runs AFTER type conversion."""
        # v is definitely int
        if v < 0:
            raise ValueError('must be positive')
        return v
```

- `mode='before'` - runs before Pydantic's type conversion
- `mode='after'` - runs after type conversion (default)

## Validation Order

1. Field validators (`mode='before'`)
2. Type conversion
3. Field validators (`mode='after'`)
4. Model validators (`mode='before'`)
5. Model validators (`mode='after'`)

## Reusable Validators

Create validator functions:

```python
def validate_phone(v: str) -> str:
    """Validate US phone number format."""
    import re
    if not re.match(r'^\d{3}-\d{3}-\d{4}$', v):
        raise ValueError('must be format: 555-123-4567')
    return v

class Contact(BaseModel):
    name: str
    phone: str

    @field_validator('phone')
    @classmethod
    def check_phone(cls, v: str) -> str:
        return validate_phone(v)
```

## Mobile Developer Context

| Mobile | Pydantic |
|--------|----------|
| Custom form validator | `@field_validator` |
| Password confirmation check | `@model_validator(mode='after')` |
| Transform on input | Return modified value from validator |
| Cross-field validation | Model validator accessing `self` |

## Key Takeaways

1. **`@field_validator` for single fields** - validate one field at a time
2. **Must be `@classmethod`** - decorated with `@classmethod`
3. **Raise `ValueError` for failures** - don't use `HTTPException`
4. **Return value (possibly transformed)** - validators can modify data
5. **`@model_validator` for cross-field** - access multiple fields via `self`
6. **Use `mode='after'` for typed data** - default, runs after conversion
7. **Pydantic v2 uses `@field_validator`** - NOT `@validator` from v1
