# Optional vs Required Fields

## Why This Matters

In mobile APIs, you send: required fields (name), optional fields (bio might be empty), and nullable fields (middle_name can be null). Pydantic v2 makes a three-way distinction: required, optional (can omit), and nullable (can send null). Understanding this prevents validation errors.

## Required Fields

No default value = required:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str  # Required
    email: str  # Required

# Must provide both
user = User(name="Alice", email="alice@example.com")

# Missing field raises ValidationError
try:
    user = User(name="Alice")  # ❌ email missing
except ValidationError:
    pass
```

## Optional with Default

Provide default value = optional to send:

```python
class User(BaseModel):
    name: str  # Required
    bio: str = ""  # Optional, defaults to empty string
    role: str = "user"  # Optional, defaults to "user"

# Can omit optional fields
user = User(name="Alice")
print(user.bio)  # ""
print(user.role)  # "user"

# Or provide them
user2 = User(name="Bob", bio="Developer", role="admin")
```

## Nullable Fields

Use `| None` for fields that can be null:

```python
class User(BaseModel):
    name: str  # Required, not nullable
    middle_name: str | None  # Required, must send null or string
    bio: str | None = None  # Optional, can omit or send null

# middle_name is REQUIRED but can be null
user = User(name="Alice", middle_name=None)  # ✓ Valid

# bio is OPTIONAL
user2 = User(name="Bob", middle_name="James")  # ✓ Valid (bio omitted)
user3 = User(name="Charlie", middle_name=None, bio=None)  # ✓ Valid
```

**Key distinction:**
- `field: str | None` = required, must send `null` or value
- `field: str | None = None` = optional, can omit entirely

## The Three Cases

```python
class Example(BaseModel):
    # Case 1: Required, not nullable
    required_field: str

    # Case 2: Required, nullable (must send null or value)
    nullable_field: str | None

    # Case 3: Optional, nullable (can omit or send null)
    optional_field: str | None = None
```

**Request examples:**
```json
// Case 1 - Valid
{"required_field": "value", "nullable_field": null}

// Case 1 - Invalid (missing required_field)
{"nullable_field": null}

// Case 2 - Invalid (nullable_field missing)
{"required_field": "value"}

// Case 3 - Valid (optional_field omitted)
{"required_field": "value", "nullable_field": null}
```

## Mutable Defaults

Use `default_factory` for mutable defaults:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

# Safe - each instance gets new list/dict
user1 = User()
user1.tags.append("admin")

user2 = User()
print(user2.tags)  # [] (not ["admin"])
```

**Don't do this:**
```python
class User(BaseModel):
    tags: list[str] = []  # ❌ Shared across all instances!
```

## Mobile Developer Context

| Mobile | Pydantic |
|--------|----------|
| `let name: String` | `name: str` |
| `let bio: String?` (Swift) | `bio: str \| None = None` |
| `val middleName: String?` (Kotlin) | `middle_name: str \| None` |
| Optional with default | `role: str = "user"` |

## Key Takeaways

1. **No default = required** - must provide value
2. **With default = optional** - can omit from request
3. **`| None` without default = required nullable** - must send null or value
4. **`| None` with `= None` = optional nullable** - can omit or send null
5. **Use `default_factory` for lists/dicts** - prevents shared state
6. **Don't use `Optional[T]`** - use `T | None` in modern Python
