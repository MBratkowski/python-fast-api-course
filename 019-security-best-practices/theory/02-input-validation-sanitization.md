# Input Validation and Sanitization

## Why This Matters

On mobile, you validate input with `UITextField` delegates (iOS) or EditText `InputFilter` (Android) to give users immediate feedback. But that validation only protects the UI -- a determined attacker bypasses your mobile app entirely and sends raw HTTP requests to your API. Server-side validation is your actual security boundary.

Pydantic v2 is your first line of defense in FastAPI. Every request body is validated against a Pydantic model before your endpoint code runs. If validation fails, FastAPI returns a 422 error automatically. But Pydantic alone is not enough -- you also need to sanitize input to strip malicious content like HTML tags and script injections.

## Pydantic v2 as Your First Line of Defense

### Field Constraints

Use `Field()` to enforce constraints declaratively:

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Alphanumeric username",
    )
    email: str = Field(
        ...,
        max_length=254,  # RFC 5321 max email length
        description="Valid email address",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Strong password",
    )
    bio: str = Field(
        default="",
        max_length=500,
        description="User biography",
    )
    age: int | None = Field(
        default=None,
        ge=13,      # Greater than or equal to 13
        le=150,     # Less than or equal to 150
    )
```

**Why max_length matters:** Without it, an attacker can send a 10MB string in a single field, consuming memory and potentially crashing your server. Always set reasonable maximums.

### Custom Validators with field_validator

For validation logic that goes beyond simple constraints:

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Only allow alphanumeric characters and underscores."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username must contain only letters, numbers, and underscores"
            )
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email format validation."""
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Invalid email format")
        return v.lower()  # Normalize to lowercase

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets strength requirements."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
```

### Cross-Field Validation with model_validator

When validation depends on multiple fields:

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def validate_date_range(self) -> "DateRange":
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordChange":
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirmation do not match")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from old password")
        return self
```

## HTML Sanitization with bleach

User input that will be displayed in a web context must be sanitized to prevent Cross-Site Scripting (XSS):

```python
import bleach
from pydantic import BaseModel, Field, field_validator

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10000)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Strip ALL HTML from title."""
        return bleach.clean(v, tags=[], strip=True)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Allow only safe HTML tags in content."""
        allowed_tags = ["p", "br", "strong", "em", "ul", "ol", "li", "a"]
        allowed_attrs = {"a": ["href"]}
        return bleach.clean(
            v,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True,
        )
```

### What bleach.clean() Does

```python
import bleach

# Strips dangerous tags
bleach.clean("<script>alert('xss')</script>Hello")
# Result: "&lt;script&gt;alert('xss')&lt;/script&gt;Hello"

# With strip=True, removes tags entirely
bleach.clean("<script>alert('xss')</script>Hello", tags=[], strip=True)
# Result: "alert('xss')Hello"

# Allows specific safe tags
bleach.clean(
    "<p>Hello <script>bad</script> <strong>world</strong></p>",
    tags=["p", "strong"],
    strip=True,
)
# Result: "<p>Hello bad <strong>world</strong></p>"
```

## Vulnerable vs. Secure Models

### Vulnerable -- No Validation

```python
class UserCreateBad(BaseModel):
    username: str          # Any string, any length
    email: str             # Not validated as email
    bio: str = ""          # No sanitization, unlimited length
    role: str = "user"     # Client can set role to "admin"!
```

### Secure -- Validated and Sanitized

```python
class UserCreateSecure(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=254)
    bio: str = Field(default="", max_length=500)
    # Note: "role" is NOT in the schema -- server sets it

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric with underscores")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("bio")
    @classmethod
    def sanitize_bio(cls, v: str) -> str:
        return bleach.clean(v, tags=[], strip=True)
```

## Common Validation Patterns

### Preventing SQL-Like Strings in Text Fields

```python
@field_validator("search_query")
@classmethod
def no_sql_injection_patterns(cls, v: str) -> str:
    """Reject obviously malicious input."""
    dangerous_patterns = [
        "';", "--", "/*", "*/", "xp_", "UNION SELECT",
        "DROP TABLE", "DELETE FROM", "INSERT INTO",
    ]
    v_upper = v.upper()
    for pattern in dangerous_patterns:
        if pattern.upper() in v_upper:
            raise ValueError("Invalid characters in search query")
    return v
```

Note: This is defense-in-depth. SQLAlchemy's parameterized queries are your primary SQL injection defense (see theory 03). Input validation is an additional layer.

### Validating File-Like Input

```python
class AvatarUploadMeta(BaseModel):
    filename: str = Field(..., max_length=255)
    content_type: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Prevent path traversal attacks."""
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Invalid filename")
        return v

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if v not in allowed:
            raise ValueError(f"Content type must be one of: {allowed}")
        return v
```

## Validation Error Responses

FastAPI automatically returns 422 Unprocessable Entity with details when validation fails:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "input": "ab",
      "ctx": {"min_length": 3}
    }
  ]
}
```

This gives your mobile client enough information to display field-specific error messages -- just like you would with local validation on the app side.

## Key Takeaways

1. **Always set `max_length`** on string fields -- unbounded strings are a DoS vector
2. **Use `field_validator`** for format validation (regex, allowed characters)
3. **Use `model_validator`** for cross-field validation (password confirmation, date ranges)
4. **Sanitize HTML** with `bleach.clean()` before storing user content
5. **Never include sensitive fields** in create/update schemas (like `role` or `is_admin`)
6. **Server-side validation is mandatory** -- mobile validation is only for UX, not security
