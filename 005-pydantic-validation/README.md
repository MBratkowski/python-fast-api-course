# Module 005: Pydantic & Data Validation

## Why This Module?

Pydantic is FastAPI's secret weapon. It validates request data automatically and generates clear error messages - like having a strongly-typed API contract.

## What You'll Learn

- Pydantic BaseModel
- Field validation
- Custom validators
- Request/Response schemas
- Nested models
- Model configuration

## Mobile Developer Context

Think of Pydantic models like your Swift Codable structs or Kotlin data classes - but with built-in validation.

## Topics

### Theory
1. Pydantic BaseModel Basics
2. Field Types & Validation
3. Optional vs Required Fields
4. Custom Validators
5. Nested Models
6. Create vs Update vs Response Schemas

### Exercises
- Create models with various validations
- Build custom validators
- Handle nested data structures

### Project
Build user registration with comprehensive validation.

## Examples

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v.lower()

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}
```
