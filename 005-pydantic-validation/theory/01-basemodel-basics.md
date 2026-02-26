# Pydantic BaseModel Basics

## Why This Matters

In Swift, you have `Codable` structs. In Kotlin, you have `data class` with serialization. In Python/FastAPI, you have **Pydantic BaseModel** - but with a superpower: automatic validation. When you create a model instance, Pydantic validates all the data immediately and gives clear error messages if something's wrong. It's like having a type-safe API contract that enforces itself.

## What is BaseModel?

`BaseModel` is the foundation of Pydantic models. You inherit from it to create data classes with automatic validation.

```python
from pydantic import BaseModel

class User(BaseModel):
    """A simple user model."""
    id: int
    name: str
    email: str
    is_active: bool = True  # Default value

# Create an instance
user = User(
    id=1,
    name="Alice",
    email="alice@example.com"
)

print(user.id)  # 1
print(user.name)  # Alice
print(user.is_active)  # True (default)
```

## Automatic Validation

Pydantic validates data types automatically:

```python
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

# Valid data - works fine
product = Product(
    id=1,
    name="Laptop",
    price=999.99,
    in_stock=True
)

# Invalid data - raises ValidationError
try:
    product = Product(
        id="not_a_number",  # ❌ Should be int
        name="Laptop",
        price=999.99,
        in_stock=True
    )
except ValidationError as e:
    print(e)
    # Shows exactly what's wrong:
    # id: Input should be a valid integer
```

Pydantic tells you:
- Which field failed
- What type was expected
- What value was provided
- The exact validation rule that failed

## Type Coercion (Lax Mode)

By default, Pydantic tries to convert compatible types:

```python
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    price: float
    active: bool

# String numbers get converted
item = Item(
    id="123",  # ✅ Converted to int(123)
    price="99.99",  # ✅ Converted to float(99.99)
    active="true"  # ✅ Converted to bool(True)
)

print(item.id)  # 123 (int)
print(item.price)  # 99.99 (float)
print(item.active)  # True (bool)
```

**What gets coerced:**
- `"123"` → `123` (str to int)
- `"99.99"` → `99.99` (str to float)
- `"true"`, `"1"` → `True` (str to bool)
- `"false"`, `"0"` → `False` (str to bool)

**What doesn't:**
- `"abc"` → int (raises ValidationError)
- `"not_a_number"` → float (raises ValidationError)
- `"maybe"` → bool (raises ValidationError)

## Model Serialization

Convert models to dictionaries or JSON:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

user = User(id=1, name="Alice", email="alice@example.com")

# Convert to dictionary
user_dict = user.model_dump()
print(user_dict)
# {"id": 1, "name": "Alice", "email": "alice@example.com"}

# Convert to JSON string
user_json = user.model_dump_json()
print(user_json)
# '{"id":1,"name":"Alice","email":"alice@example.com"}'
```

**Pydantic v2 methods:**
- `model_dump()` - convert to dict (replaces v1's `.dict()`)
- `model_dump_json()` - convert to JSON string (replaces v1's `.json()`)

## Model Deserialization

Create models from dictionaries or JSON:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# From dictionary
user_data = {"id": 1, "name": "Alice", "email": "alice@example.com"}
user = User(**user_data)  # Unpack dict as kwargs

# Or use model_validate()
user = User.model_validate(user_data)

# From JSON string
json_string = '{"id": 2, "name": "Bob", "email": "bob@example.com"}'
user = User.model_validate_json(json_string)
```

**Pydantic v2 methods:**
- `User(**dict)` or `User.model_validate(dict)` - from dict
- `User.model_validate_json(json_str)` - from JSON (replaces v1's `.parse_raw()`)

## Accessing Fields

Access model fields like regular Python attributes:

```python
user = User(id=1, name="Alice", email="alice@example.com")

# Read fields
print(user.id)  # 1
print(user.name)  # Alice

# Modify fields
user.name = "Alice Smith"
user.email = "alice.smith@example.com"

# Fields are validated on assignment (in some cases)
try:
    user.id = "not_a_number"  # May raise ValidationError
except ValidationError:
    print("Invalid value")
```

## Default Values

Fields can have default values:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True  # Default
    role: str = "user"  # Default

# Provide only required fields
user = User(id=1, name="Alice", email="alice@example.com")

print(user.is_active)  # True (default)
print(user.role)  # "user" (default)

# Or override defaults
user2 = User(
    id=2,
    name="Bob",
    email="bob@example.com",
    is_active=False,
    role="admin"
)
```

## Model Configuration

Configure model behavior with `model_config`:

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    """User model with custom config."""
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_to_lower=True,  # Convert strings to lowercase
        validate_assignment=True,  # Validate on field assignment
    )

    id: int
    username: str
    email: str

# Automatic whitespace stripping and lowercasing
user = User(
    id=1,
    username="  Alice  ",  # Stripped to "alice"
    email="ALICE@EXAMPLE.COM"  # Lowercased to "alice@example.com"
)

print(user.username)  # "alice"
print(user.email)  # "alice@example.com"
```

## Comparing to Mobile Data Classes

| Swift Codable | Kotlin Data Class | Pydantic BaseModel |
|---------------|-------------------|--------------------|
| `struct User: Codable` | `data class User` | `class User(BaseModel)` |
| Manual validation | Manual validation | Automatic validation |
| Type-safe | Type-safe | Type-safe + validated |
| `JSONDecoder()` | `Json.decodeFromString()` | `model_validate_json()` |
| `JSONEncoder()` | `Json.encodeToString()` | `model_dump_json()` |
| Runtime crashes on bad data | Runtime crashes on bad data | ValidationError before use |

## Common Patterns

**API Request Model:**
```python
class UserCreate(BaseModel):
    """Data client sends to create user."""
    name: str
    email: str
    password: str
```

**API Response Model:**
```python
class UserResponse(BaseModel):
    """Data server sends back."""
    id: int
    name: str
    email: str
    created_at: str
    # Note: no password field
```

**Database Model Conversion:**
```python
from pydantic import BaseModel, ConfigDict

class UserDB(BaseModel):
    """Model that can read from ORM objects."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str

# Can create from SQLAlchemy model
db_user = database.get_user(1)  # SQLAlchemy object
user = UserDB.model_validate(db_user)  # Reads db_user.id, db_user.name, etc.
```

## Key Takeaways

1. **BaseModel provides automatic validation** - type checking happens when you create instances
2. **Type coercion is default** - `"123"` becomes `123`, but `"abc"` raises error
3. **Clear error messages** - ValidationError tells you exactly what's wrong
4. **Serialization is built-in** - `model_dump()` for dict, `model_dump_json()` for JSON
5. **Deserialization is built-in** - `model_validate()` from dict, `model_validate_json()` from JSON
6. **Default values work like dataclasses** - `field: type = default_value`
7. **Pydantic v2 methods** - use `model_*` methods, not v1's `.dict()`, `.json()`, `.parse_obj()`
