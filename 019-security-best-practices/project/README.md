# Project: Security Audit and Hardening

## Overview

You have inherited a FastAPI application with multiple security vulnerabilities. Your mission: perform a security audit, identify the issues, and harden the application to meet production security standards.

This project brings together all the security concepts from Module 019: OWASP API Security Top 10, input validation, CORS configuration, rate limiting, secrets management, and security headers.

## The Vulnerable Application

Below is a FastAPI application with **at least 8 security vulnerabilities**. Your job is to find and fix them all.

```python
import jwt
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.orm import Session

# Vulnerability: Hardcoded secret
SECRET_KEY = "mysecret123"

app = FastAPI(debug=True)  # Vulnerability: Debug mode in production

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    bio: str | None = None
    is_admin: bool | None = None  # Vulnerability: Mass assignment

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # Vulnerability: No response model (excessive data exposure)
    user = db.execute(select(User).where(User.id == user_id)).scalar_one()
    return user

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    # Vulnerability: No ownership check (BOLA)
    order = db.execute(select(Order).where(Order.id == order_id)).scalar_one()
    return order

@app.get("/api/search")
async def search(q: str, db: Session = Depends(get_db)):
    # Vulnerability: SQL injection via f-string
    query = text(f"SELECT * FROM posts WHERE title LIKE '%{q}%'")
    return db.execute(query).fetchall()

@app.post("/api/posts")
async def create_post(title: str, content: str, db: Session = Depends(get_db)):
    # Vulnerability: No input validation or sanitization
    post = Post(title=title, content=content)
    db.add(post)
    db.commit()
    return post

@app.post("/auth/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    # Vulnerability: No rate limiting on login
    user = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")
    return {"token": token}
```

**Missing from the application:**
- No CORS middleware configured
- No security headers middleware
- No rate limiting on any endpoint
- No pagination on list endpoints

## Requirements

### 1. Fix OWASP Vulnerabilities

- [ ] **BOLA (API1):** Add ownership checks to the orders endpoint
- [ ] **Broken Auth (API2):** Use environment variables for SECRET_KEY, add token expiration
- [ ] **Excessive Data Exposure (API3):** Create response models for User (hide password_hash, is_admin)
- [ ] **Mass Assignment (API3):** Remove is_admin from UserUpdate schema
- [ ] **SQL Injection (API8/Injection):** Replace f-string query with parameterized query

### 2. Configure CORS

- [ ] Add CORSMiddleware with specific origins (not wildcard with credentials)
- [ ] Allow Authorization and Content-Type headers
- [ ] Configure appropriate methods (GET, POST, PUT, DELETE)

### 3. Add Rate Limiting

- [ ] Install and configure slowapi
- [ ] Add strict rate limiting to `/auth/login` (5/minute)
- [ ] Add moderate rate limiting to POST endpoints (20/minute)
- [ ] Add relaxed rate limiting to GET endpoints (60/minute)

### 4. Add Security Headers

- [ ] Create SecurityHeadersMiddleware using BaseHTTPMiddleware
- [ ] Add X-Content-Type-Options: nosniff
- [ ] Add X-Frame-Options: DENY
- [ ] Add Strict-Transport-Security with includeSubDomains
- [ ] Add Content-Security-Policy: default-src 'none'
- [ ] Add X-XSS-Protection: 1; mode=block

### 5. Input Validation and Sanitization

- [ ] Add Pydantic schemas with Field constraints (min_length, max_length)
- [ ] Add field_validator for username format (alphanumeric only)
- [ ] Sanitize HTML in user-provided content with bleach
- [ ] Add pagination limits with Query(default=20, le=100)

### 6. Secrets Management

- [ ] Move SECRET_KEY to environment variable
- [ ] Create .env.example with required variables
- [ ] Ensure .env is in .gitignore
- [ ] Disable debug mode (or make it configurable via environment)

## Starter Template

```python
import os
from datetime import datetime, timedelta, timezone

import bleach
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# TODO: Create the FastAPI app (debug=False)
# TODO: Configure CORS middleware
# TODO: Create SecurityHeadersMiddleware and add it
# TODO: Configure slowapi rate limiter
# TODO: Create secure Pydantic schemas
# TODO: Implement secure endpoints
```

## Success Criteria

1. **No hardcoded secrets** -- all sensitive values come from environment variables
2. **CORS properly configured** -- specific origins, credentials allowed, appropriate methods/headers
3. **Rate limiting active** -- login endpoint limited to 5/minute, returns 429 when exceeded
4. **Security headers present** -- every response includes all required security headers
5. **No data exposure** -- user responses never include password_hash or is_admin
6. **No BOLA** -- users can only access their own resources
7. **No SQL injection** -- all queries use parameterized parameters
8. **Input sanitized** -- HTML stripped from user input, max lengths enforced

## Verification

Test your hardened application:

```bash
# Run the app
uvicorn project.main:app --reload --port 8000

# Check security headers
curl -I http://localhost:8000/api/health

# Test CORS preflight
curl -X OPTIONS http://localhost:8000/api/users \
  -H "Origin: https://myapp.com" \
  -H "Access-Control-Request-Method: GET" -v

# Test rate limiting (run 6 times quickly)
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
  echo
done
# The 6th request should return 429

# Test SQL injection is blocked
curl "http://localhost:8000/api/search?q=test'%20UNION%20SELECT%20*%20FROM%20users%20--"
# Should return 422 (validation error), not data
```

## Bonus Challenges

1. Add API key authentication for public endpoints (in addition to JWT)
2. Implement request logging middleware that logs IP, method, path, and status (but never logs request bodies containing passwords)
3. Add CSRF protection for cookie-based authentication
4. Implement an IP allowlist for admin endpoints
