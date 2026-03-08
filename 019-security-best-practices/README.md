# Module 019: Security Best Practices

## Why This Module?

As a mobile developer, you've dealt with security from the client side -- storing tokens in the Keychain, configuring App Transport Security (ATS), validating user input in text fields. But server-side security is a fundamentally different challenge. On mobile, you protect one user's data on one device. On the server, you protect every user's data from every possible attacker.

A single missing authorization check on your API lets any authenticated user access any other user's data. A misconfigured CORS policy leaks credentials to malicious websites. An unvalidated input field opens the door to SQL injection. These are not theoretical risks -- they are the most common vulnerabilities found in production APIs, documented in the OWASP API Security Top 10.

This module teaches you to think like an attacker so you can build like a defender.

## What You'll Learn

- OWASP API Security Top 10 vulnerabilities and how they apply to FastAPI
- Input validation and sanitization with Pydantic v2
- SQL injection prevention with SQLAlchemy parameterized queries
- CORS configuration with FastAPI's CORSMiddleware
- Rate limiting with slowapi to prevent abuse
- Secrets management with environment variables and .env files
- Security headers middleware for defense-in-depth

## Mobile Developer Context

You've secured mobile apps. Now you secure the API they talk to.

**Security Across Platforms:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Input validation | `UITextField` validation | EditText input filters | Pydantic `field_validator` |
| Secure storage | Keychain | EncryptedSharedPreferences | Environment vars / secrets manager |
| Network security | App Transport Security (ATS) | Network Security Config | CORS middleware + security headers |
| Rate limiting | App-side throttling | API quota management | slowapi `@limiter.limit()` |
| Auth tokens | Secure Enclave storage | Android Keystore | JWT with proper signing (PyJWT) |

**Key Differences from Mobile:**
- On mobile, the OS enforces many security rules for you (ATS, sandboxing). On the server, you must configure everything explicitly
- On mobile, you worry about one user's data. On the server, you must prevent any user from accessing another's data
- On mobile, you trust the server's responses. On the server, you trust nothing from the client

## Prerequisites

Before starting, you should be comfortable with:
- [ ] FastAPI route handlers and dependency injection (Modules 003-005)
- [ ] JWT authentication and authorization (Modules 009-010)
- [ ] Pydantic v2 models and validators (Module 004)
- [ ] SQLAlchemy queries (Module 007)

## Topics

### Theory
1. OWASP API Security Top 10 -- The most common API vulnerabilities
2. Input Validation and Sanitization -- Pydantic as your first line of defense
3. SQL Injection Prevention -- Why parameterized queries matter
4. CORS Configuration -- Cross-origin resource sharing done right
5. Rate Limiting -- Protecting against abuse with slowapi
6. Secrets Management -- Never hardcode credentials
7. Security Headers -- Defense-in-depth with HTTP headers

### Exercises
1. Identify and Fix Vulnerabilities -- Patch OWASP vulnerabilities in a FastAPI app
2. CORS Configuration -- Configure CORSMiddleware correctly
3. Input Sanitization -- Add Pydantic validators and HTML sanitization

### Project
Security audit and hardening of a vulnerable FastAPI application.

## Time Estimate

- Theory: ~120 minutes
- Exercises: ~75 minutes
- Project: ~90 minutes

## Example

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
import bleach

app = FastAPI()

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        return bleach.clean(v, tags=[], strip=True)

@app.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, comment: CommentCreate):
    # Input is already validated and sanitized by Pydantic
    return {"post_id": post_id, "content": comment.content}
```
