# Module 019: Security Best Practices

## Why This Module?

Security vulnerabilities can destroy your app and reputation. Learn to protect your API from common attacks.

## What You'll Learn

- OWASP Top 10
- Input validation
- SQL injection prevention
- XSS protection
- CORS configuration
- Secrets management
- Security headers

## Topics

### Theory
1. OWASP Top 10 for APIs
2. Input Validation (beyond Pydantic)
3. SQL Injection Prevention
4. CORS Explained
5. Rate Limiting
6. Secrets Management
7. Security Headers

### Project
Security audit and hardening of your API.

## Key Practices

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import bleach

app = FastAPI()

# CORS - be specific!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],  # Not "*" in production!
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
)

# Sanitize user input
class Comment(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def sanitize_html(cls, v: str) -> str:
        return bleach.clean(v)

# Use parameterized queries (SQLAlchemy does this)
# NEVER: f"SELECT * FROM users WHERE id = {user_id}"
# ALWAYS: session.execute(select(User).where(User.id == user_id))
```
