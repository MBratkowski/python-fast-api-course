# OWASP API Security Top 10

## Why This Matters

On mobile, platform security features protect you automatically -- iOS sandboxes your app, Android requires permissions, and neither lets one app access another's data. On the server, there are no such guardrails. Every endpoint you expose is accessible to anyone who can reach your API, and the most common vulnerabilities are shockingly simple: forgetting to check if a user owns a resource, returning too much data in a response, or allowing unlimited requests.

The OWASP API Security Top 10 is the definitive list of the most critical API security risks. Unlike the OWASP Web Application Top 10 (which focuses on browser-based attacks like XSS), the API Security list targets the vulnerabilities specific to REST APIs -- exactly what you're building with FastAPI.

## The OWASP API Security Top 10

### API1: Broken Object Level Authorization (BOLA)

The most common API vulnerability. It occurs when an API endpoint lets a user access objects belonging to other users by manipulating the object ID.

**Vulnerable code:**

```python
@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    # Anyone can access any order by guessing the ID!
    order = db.execute(
        select(Order).where(Order.id == order_id)
    ).scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")
    return order
```

**Secure code:**

```python
@app.get("/api/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check that the order belongs to the requesting user
    order = db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id,  # Ownership check
        )
    ).scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")
    return order
```

**Mobile analogy:** This is like if your banking app let you change the account number in the URL to see other people's accounts. On mobile, the app only shows your data. On the server, you must enforce this.

### API2: Broken Authentication

Authentication mechanisms are implemented incorrectly, allowing attackers to compromise authentication tokens or exploit implementation flaws.

**Common mistakes:**

```python
# BAD: Weak JWT secret
SECRET_KEY = "secret"  # Easily guessable

# BAD: No token expiration
token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")
# Missing "exp" claim -- token never expires

# BAD: No rate limiting on login
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    # Attackers can try unlimited passwords
    ...
```

**Secure implementation:**

```python
import secrets
from datetime import datetime, timedelta, timezone

# Strong secret key (at least 32 bytes of randomness)
SECRET_KEY = secrets.token_urlsafe(32)

# Tokens with expiration
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode(
        {"user_id": user_id, "exp": expire},
        SECRET_KEY,
        algorithm="HS256",
    )
```

### API3: Broken Object Property Level Authorization

The API exposes properties that the user should not be able to read or modify.

**Excessive Data Exposure (reading too much):**

```python
# BAD: Returns everything, including sensitive fields
@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one()
    return user  # Exposes password_hash, email, phone, is_admin, etc.
```

```python
# GOOD: Use a response model to control what's exposed
class UserResponse(BaseModel):
    id: int
    username: str
    avatar_url: str | None

    model_config = ConfigDict(from_attributes=True)

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one()
    return user  # Only id, username, avatar_url are returned
```

**Mass Assignment (writing too much):**

```python
# BAD: Accepts any field the client sends
@app.put("/api/users/me")
async def update_profile(data: dict, db: Session = Depends(get_db)):
    # Attacker sends: {"username": "hacker", "is_admin": true}
    for key, value in data.items():
        setattr(current_user, key, value)  # Sets is_admin = True!
```

```python
# GOOD: Strict update schema
class UserUpdate(BaseModel):
    username: str | None = None
    bio: str | None = None
    # is_admin is NOT in this schema -- cannot be set by users

@app.put("/api/users/me")
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    db.commit()
```

### API4: Unrestricted Resource Consumption

The API does not limit the size or number of resources a client can request, enabling Denial of Service.

```python
# BAD: No pagination limits
@app.get("/api/posts")
async def list_posts(db: Session = Depends(get_db)):
    # Returns ALL posts -- could be millions
    return db.execute(select(Post)).scalars().all()
```

```python
# GOOD: Enforce maximum page size
@app.get("/api/posts")
async def list_posts(
    skip: int = 0,
    limit: int = Query(default=20, le=100),  # Max 100 per page
    db: Session = Depends(get_db),
):
    posts = db.execute(
        select(Post).offset(skip).limit(limit)
    ).scalars().all()
    return posts
```

### API5: Broken Function Level Authorization

The API does not properly check that the user has the right role or permission for the requested action.

```python
# BAD: No role check on admin endpoint
@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Any authenticated user can delete any user!
    user = db.execute(select(User).where(User.id == user_id)).scalar_one()
    db.delete(user)
    db.commit()
```

```python
# GOOD: Require admin role
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(403, "Admin access required")
    return current_user

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one()
    db.delete(user)
    db.commit()
```

### API6: Unrestricted Access to Sensitive Business Flows

Attackers automate access to business flows that are meant for human interaction (e.g., signup, purchases, reviews).

**Mitigation strategies:**
- Rate limiting on sensitive endpoints (see Module 019, theory 05)
- CAPTCHA for signup and login flows
- Device fingerprinting
- Monitoring for unusual patterns (100 signups from one IP)

### API7: Server-Side Request Forgery (SSRF)

The API fetches a URL provided by the user without validation, allowing internal network access.

```python
# BAD: Fetches any URL the user provides
@app.post("/api/fetch-url")
async def fetch_url(url: str):
    import httpx
    response = await httpx.get(url)  # Attacker sends http://169.254.169.254/metadata
    return {"content": response.text}
```

```python
# GOOD: Validate and restrict URLs
from urllib.parse import urlparse
import ipaddress

ALLOWED_SCHEMES = {"http", "https"}

def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise HTTPException(400, "Invalid URL scheme")
    # Block internal/private IPs
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback:
            raise HTTPException(400, "Internal URLs not allowed")
    except ValueError:
        pass  # Hostname is not an IP -- allow DNS resolution
    return url
```

### API8: Security Misconfiguration

The API or its supporting infrastructure is misconfigured, leaving it vulnerable.

**Common misconfigurations in FastAPI:**

```python
# BAD: Debug mode in production
app = FastAPI(debug=True)  # Exposes stack traces

# BAD: Default CORS (too permissive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Invalid with wildcard!
)

# BAD: Verbose error messages
@app.exception_handler(Exception)
async def handle_error(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},  # Leaks internal details
    )
```

```python
# GOOD: Production configuration
app = FastAPI(
    debug=False,
    docs_url=None if PRODUCTION else "/docs",  # Hide docs in production
    redoc_url=None if PRODUCTION else "/redoc",
)
```

### API9: Improper Inventory Management

Old API versions or unused endpoints remain active and unpatched.

**Best practices:**
- Version your API (`/api/v1/`, `/api/v2/`)
- Remove deprecated endpoints when they are no longer needed
- Document all exposed endpoints
- Monitor for traffic to deprecated endpoints

### API10: Unsafe Consumption of APIs

The API trusts data from third-party APIs without validation.

```python
# BAD: Trusting third-party response blindly
async def get_weather(city: str):
    response = await httpx.get(f"https://weather-api.com/city/{city}")
    data = response.json()
    return data["temperature"]  # What if the API returns unexpected data?
```

```python
# GOOD: Validate third-party responses
class WeatherResponse(BaseModel):
    temperature: float
    humidity: float = Field(ge=0, le=100)

async def get_weather(city: str):
    response = await httpx.get(f"https://weather-api.com/city/{city}")
    response.raise_for_status()
    data = WeatherResponse.model_validate(response.json())
    return data.temperature
```

## Summary Table

| # | Vulnerability | FastAPI Mitigation |
|---|---------------|-------------------|
| API1 | BOLA | Add ownership checks in queries |
| API2 | Broken Auth | Strong secrets, token expiration, rate limiting |
| API3 | Broken Property Auth | Response models, strict update schemas |
| API4 | Unrestricted Resources | Pagination limits, max upload sizes |
| API5 | Broken Function Auth | Role-based dependency injection |
| API6 | Sensitive Flow Abuse | Rate limiting, CAPTCHA |
| API7 | SSRF | URL validation, block private IPs |
| API8 | Misconfiguration | Disable debug, proper CORS, hide docs |
| API9 | Improper Inventory | API versioning, remove old endpoints |
| API10 | Unsafe API Consumption | Validate third-party responses with Pydantic |

## Key Takeaways

1. **BOLA is the #1 API vulnerability** -- always check resource ownership in your queries
2. **Use Pydantic response models** to prevent data exposure -- never return raw database objects
3. **Use separate schemas for create/update** to prevent mass assignment
4. **Enforce pagination limits** with `Query(default=20, le=100)` on list endpoints
5. **Role-based access control** belongs in FastAPI dependencies, not in endpoint logic
6. **Never trust client input** -- not URLs, not IDs, not data from third-party APIs
