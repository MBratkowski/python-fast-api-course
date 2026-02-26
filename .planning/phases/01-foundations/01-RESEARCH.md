# Phase 1: Foundations - Research

**Researched:** 2026-02-26
**Domain:** FastAPI web framework, HTTP/REST fundamentals, Pydantic v2 validation, educational content for mobile developers
**Confidence:** HIGH

## Summary

Phase 1 focuses on teaching mobile developers the foundational concepts needed to build REST APIs with FastAPI: HTTP protocol basics, REST principles, FastAPI fundamentals, request/response handling, and Pydantic v2 data validation. The research reveals a mature, well-documented ecosystem with established best practices and a clear pedagogical progression.

**Key findings:**
- FastAPI and Pydantic v2 are the established standard for Python API development in 2026, with official Python 3.13 support and type-hint-driven development
- Educational content should progress from HTTP/REST theory (non-code) to FastAPI basics (minimal code) to request handling (more complex) to Pydantic validation (most complex)
- Mobile developers benefit from analogies to familiar concepts: type hints = Swift/Kotlin types, Pydantic models = mobile data classes, async/await = mobile concurrency patterns
- The "TODO stub with inline pytest" pattern is proven effective for hands-on learning

**Primary recommendation:** Follow the established FastAPI tutorial progression (first steps → path parameters → query parameters → request body → validation → response models) while framing each concept with mobile-dev analogies ("like URLSession parameters" or "like Retrofit annotations").

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.109.0+ | Web framework | Industry standard for Python APIs; type-hint-driven, auto-generates OpenAPI docs, async-first architecture |
| Pydantic | 2.5.0+ | Data validation | v2 is 5-50x faster than v1 (Rust core); integrated deeply with FastAPI; replaces manual validation code |
| Uvicorn | 0.27.0+ | ASGI server | Official recommended server for FastAPI; supports hot-reload for development |
| Python | 3.12+ (ideally 3.13) | Language | Python 3.12+ required for modern type hints (PEP 695); FastAPI 0.115.8+ supports Python 3.13 officially |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | 0.26.0+ | HTTP client | Testing FastAPI endpoints with TestClient; built on same concepts as requests |
| pytest | 8.0.0+ | Testing framework | Writing inline tests in exercise files; TestClient integration |
| pytest-asyncio | 0.23.0+ | Async testing | Testing async FastAPI endpoints |
| mypy | 1.8.0+ | Type checking | Validating type hints in learner code |
| email-validator | 2.1.0+ | Email validation | Pydantic email field validation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FastAPI | Flask | Flask has larger ecosystem but no built-in validation, no async-first design, manual OpenAPI generation |
| FastAPI | Django REST Framework | DRF is batteries-included but heavier, less intuitive for beginners, slower for async workloads |
| Pydantic v2 | Marshmallow | Marshmallow is mature but slower, requires separate validation layer, no type-hint integration |
| Uvicorn | Gunicorn | Gunicorn doesn't support ASGI natively; requires uvicorn workers anyway for FastAPI |

**Installation:**
```bash
# Already in requirements.txt
pip install fastapi>=0.109.0 uvicorn[standard]>=0.27.0 pydantic>=2.5.0
```

## Architecture Patterns

### Recommended Module Structure
Each module (002-005) follows the established pattern from module 001:

```
XXX-module-name/
├── README.md                    # Module overview, learning objectives, time estimates
├── theory/                      # Markdown files, numbered 01-06
│   ├── 01-topic.md             # "Why This Matters" + mobile analogy + code examples + "Key Takeaways"
│   ├── 02-topic.md
│   └── ...
├── exercises/                   # Python files, numbered 01-03
│   ├── 01_exercise.py          # TODO stubs + inline pytest tests
│   ├── 02_exercise.py
│   └── 03_exercise.py
└── project/                     # Self-contained project
    └── README.md               # Requirements + starter template + success criteria
```

### Pattern 1: Theory File Structure
**What:** Markdown files explaining concepts with mobile-dev framing
**When to use:** All theory content in theory/ directories
**Example:**
```markdown
# Topic Name

## Why This Matters

[Mobile developer analogy - e.g., "In iOS you use URLSession parameters,
in FastAPI you use query parameters - same concept, different syntax"]

## Core Concept

[Explanation with code examples]

## Practical Examples

[Runnable code snippets]

## Key Takeaways

1. [Bullet point summary]
2. [Connection to mobile development]
```
**Source:** Established in module 001, validated against FastAPI official tutorial structure

### Pattern 2: Exercise File with Inline Tests
**What:** Python file with TODO stubs and pytest tests that fail until completed
**When to use:** All exercises in exercises/ directories
**Example:**
```python
"""
Exercise N: Topic Name

Complete the functions below.
Run: pytest XXX-module-name/exercises/0N_topic.py -v
"""

# Exercise N.1: Subtask description
# TODO: Implement function
def function_name(param: type) -> return_type:
    """Docstring."""
    pass  # TODO: Implement

# ============= TESTS =============
# Run with: pytest XXX-module-name/exercises/0N_topic.py -v

def test_function_name():
    assert function_name("input") == "expected"
```
**Source:** Pattern established in module 001 exercises/01_types.py, 02_dataclasses.py, 03_async.py

### Pattern 3: Project Starter Template
**What:** README with requirements, code template, and success criteria
**When to use:** All projects in project/ directories
**Example:**
```markdown
# Project: Name

## Requirements
1. [Specific requirement]
2. [Specific requirement]

## Starter Template
\`\`\`python
# File structure and TODO comments
\`\`\`

## Success Criteria
- [ ] Checkbox item
- [ ] Feature works correctly
```
**Source:** Established in module 001 project/README.md

### Pattern 4: FastAPI Route Progression
**What:** Gradual introduction of FastAPI features following official tutorial
**When to use:** Module 003 (FastAPI Basics) through Module 004 (Request/Response)
**Progression:**
```python
# 1. First endpoint (simplest)
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# 2. Path parameters
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# 3. Query parameters
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# 4. Request body with Pydantic
@app.post("/users")
def create_user(user: UserCreate):
    return user

# 5. Response models
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return UserResponse(id=user_id, name="Alice")
```
**Source:** [FastAPI Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/)

### Pattern 5: Pydantic Model Progression
**What:** Gradual introduction of Pydantic v2 features
**When to use:** Module 005 (Pydantic & Data Validation)
**Progression:**
```python
# 1. Basic BaseModel
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

# 2. Optional and default fields
class User(BaseModel):
    name: str
    email: str
    is_active: bool = True
    bio: str | None = None

# 3. Field validators
from pydantic import field_validator

class User(BaseModel):
    name: str
    email: str

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('name cannot be empty')
        return v

# 4. Nested models
class Address(BaseModel):
    street: str
    city: str

class User(BaseModel):
    name: str
    address: Address
```
**Source:** [Pydantic v2 Documentation](https://docs.pydantic.com/latest/) and [Pydantic Complete Guide 2026](https://devtoolbox.dedyn.io/blog/pydantic-complete-guide)

### Anti-Patterns to Avoid
- **Don't mix request/response models:** Reusing one Pydantic model for both input and output breaks when you add server-generated fields (id, created_at) or need to hide sensitive fields (password)
- **Don't skip type hints:** FastAPI relies on type hints for validation, documentation, and IDE support - omitting them defeats the framework's purpose
- **Don't raise HTTPException in validators:** Keep validation logic pure; raise ValueError in Pydantic validators, not FastAPI HTTPException (leaky abstraction)
- **Don't teach sync-first:** FastAPI is async-first; teach async def from the start, not def with later migration
- **Don't return bare lists:** Always envelope collections in objects for future extensibility: `{"items": [...]}` not `[...]`

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Request validation | Manual dict access with try/except | Pydantic models + type hints | Handles type conversion, nested validation, error messages, OpenAPI generation automatically |
| Email validation | Regex patterns | `email-validator` library + Pydantic EmailStr | Handles complex edge cases (internationalized domains, quoted strings, IP addresses) |
| Query parameter parsing | Manual request.args parsing | FastAPI function parameters with types | Automatic conversion, validation, documentation, optional/required handling |
| API documentation | Manually written OpenAPI YAML | FastAPI auto-generation | Stays in sync with code, includes request/response schemas, generated from type hints |
| Response serialization | Manual dict creation | Pydantic response_model | Handles datetime, UUID, enum serialization; filters fields; validates output |
| Path parameter validation | Manual int() casting with try/except | Path() with ge, le, gt, lt constraints | Declarative, generates better error messages, documents constraints in OpenAPI |

**Key insight:** FastAPI + Pydantic eliminate most boilerplate through type-hint-driven code generation. If you're writing manual validation or serialization code, you're fighting the framework.

## Common Pitfalls

### Pitfall 1: Confusing Path vs Query Parameters
**What goes wrong:** Learners put required parameters in query strings or optional parameters in the path
**Why it happens:** Mobile developers are used to "all parameters are equal" (e.g., Retrofit @Path vs @Query is just annotation choice)
**How to avoid:**
- Path parameters = resource identifiers (required, part of URL structure): `/users/{user_id}`
- Query parameters = filters/options (optional, after ?): `/users?role=admin&limit=10`
- Body = complex data (POST/PUT/PATCH)
**Warning signs:** URLs like `/search?query=required` (should be POST with body) or `/users/{role}` (should be query param)

### Pitfall 2: Pydantic v1 vs v2 Confusion
**What goes wrong:** Using deprecated `@validator` decorator instead of `@field_validator`, or using `class Config:` instead of `model_config`
**Why it happens:** Old tutorials and Stack Overflow answers still reference Pydantic v1 patterns
**How to avoid:**
- v2 uses `@field_validator` and `@model_validator` decorators
- v2 uses `model_config = ConfigDict(...)` not `class Config:`
- v2 uses `model_dump()` not `dict()`
- Always check tutorial publication date (2024+ for v2)
**Warning signs:** `@validator` decorator, `class Config:`, `.dict()` method calls

### Pitfall 3: Not Understanding Type Coercion
**What goes wrong:** Expecting strict validation but getting automatic type conversion (e.g., "123" becomes 123)
**Why it happens:** Pydantic v2 has "lax mode" (default) that coerces types, unlike mobile languages with strict typing
**How to avoid:**
- Explain that `user_id: int` accepts both `123` and `"123"` (coerced)
- Teach `strict=True` for strict validation: `Field(..., strict=True)`
- Show validation errors vs successful coercion in examples
**Warning signs:** Surprise that string "123" works where int expected

### Pitfall 4: Sync vs Async Function Confusion
**What goes wrong:** Mixing `def` and `async def` without understanding when to use each
**Why it happens:** Mobile developers know async/await but don't understand Python's event loop blocking
**How to avoid:**
- Use `async def` for all endpoints by default (FastAPI best practice)
- Only use `def` if doing CPU-bound work or blocking I/O
- Explain that FastAPI runs `def` in threadpool, `async def` in event loop
- Show how mixing wrongly causes performance degradation
**Warning signs:** Using `def` everywhere (loses async benefits) or using `async def` with blocking calls like `time.sleep()`

### Pitfall 5: HTTPException in Wrong Layer
**What goes wrong:** Raising `HTTPException` in Pydantic validators or service functions
**Why it happens:** Convenient to raise directly where error occurs
**How to avoid:**
- Raise `ValueError` in validators (domain layer)
- Raise `HTTPException` only in route handlers (presentation layer)
- Teach separation of concerns: validation errors ≠ HTTP errors
**Warning signs:** `from fastapi import HTTPException` in model files

### Pitfall 6: Not Using Response Models
**What goes wrong:** Returning raw dictionaries or ORM objects from endpoints
**Why it happens:** "It works" - FastAPI serializes dicts automatically
**How to avoid:**
- Always use `response_model` parameter for consistency
- Prevents accidental exposure of sensitive fields (password hashes, internal IDs)
- Provides response validation and better OpenAPI docs
- Show how returning ORM object exposes all fields including secrets
**Warning signs:** No `response_model` in decorators, returning ORM objects directly

### Pitfall 7: Misunderstanding Optional vs Default
**What goes wrong:** Using `Optional[str]` without default value, thinking it makes field optional
**Why it happens:** In mobile languages, `String?` means both nullable and optional
**How to avoid:**
- `field: str | None` = required field that can be null (must send `null`)
- `field: str | None = None` = optional field (can omit from request)
- `field: str = "default"` = optional field with default
- Teach the difference with clear examples
**Warning signs:** Confusion when required `Optional` fields throw validation errors

## Code Examples

Verified patterns from official sources:

### HTTP Request/Response Flow (Module 002)
```python
# Conceptual example - no FastAPI yet
# HTTP Request (what the client sends)
"""
GET /api/users/123?include=profile HTTP/1.1
Host: example.com
Authorization: Bearer token123
Accept: application/json
"""

# HTTP Response (what the server sends)
"""
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=300

{"id": 123, "name": "Alice", "profile": {...}}
"""
```
**Source:** REST API fundamentals, not FastAPI-specific yet

### First FastAPI Endpoint (Module 003)
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    """Your first endpoint - notice the decorator and async."""
    return {"message": "Hello World"}

# Run with: uvicorn main:app --reload
# Visit: http://localhost:8000/docs for Swagger UI
```
**Source:** [FastAPI Tutorial - First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)

### Path and Query Parameters (Module 004)
```python
from fastapi import FastAPI, Query, Path
from typing import Annotated

app = FastAPI()

# Path parameter (required, part of URL)
@app.get("/users/{user_id}")
async def get_user(
    user_id: Annotated[int, Path(ge=1, description="User ID must be positive")]
):
    return {"user_id": user_id}

# Query parameters (optional filters)
@app.get("/items")
async def list_items(
    skip: int = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: str | None = None
):
    return {"skip": skip, "limit": limit, "search": search}
```
**Source:** [FastAPI Tutorial - Path Parameters and Numeric Validations](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/)

### Request Body with Pydantic (Module 004/005)
```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import Annotated

app = FastAPI()

class UserCreate(BaseModel):
    """Request schema for creating a user."""
    name: str
    email: EmailStr
    age: int | None = None

class UserResponse(BaseModel):
    """Response schema - includes server-generated fields."""
    id: int
    name: str
    email: str
    is_active: bool = True

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Notice: separate request and response models."""
    # Simulate database save
    user_data = user.model_dump()
    user_data["id"] = 123  # Server-generated
    return UserResponse(**user_data)
```
**Source:** [FastAPI Tutorial - Request Body](https://fastapi.tiangolo.com/tutorial/body/)

### Pydantic Field Validation (Module 005)
```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Self

class User(BaseModel):
    """Demonstrates Pydantic v2 validation patterns."""
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)
    password_confirm: str

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Field validator - runs on single field."""
        if not v.isalnum():
            raise ValueError('username must be alphanumeric')
        return v

    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        """Model validator - runs on whole model, can check multiple fields."""
        if self.password != self.password_confirm:
            raise ValueError('passwords do not match')
        return self

# Usage
try:
    user = User(
        username="alice123",
        email="alice@example.com",
        password="secret123",
        password_confirm="secret123"
    )
except ValueError as e:
    print(e)
```
**Source:** [Pydantic v2 Validators Documentation](https://docs.pydantic.dev/latest/concepts/validators/)

### Response Models and Status Codes (Module 004)
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    price: float

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Response model ensures only specified fields are returned."""
    # Simulate database lookup
    if item_id > 100:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return Item(id=item_id, name="Widget", price=9.99)

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    """Use 201 for resource creation."""
    return item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Use 204 for successful deletion (no content returned)."""
    # Simulate deletion
    return None
```
**Source:** [FastAPI Tutorial - Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/)

### Testing with TestClient (Module 003 project)
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Test inline in exercise files
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```
**Source:** [FastAPI Tutorial - Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 | Pydantic v2 | June 2023 | 5-50x performance improvement; breaking API changes (@validator → @field_validator, Config → model_config) |
| `Optional[T]` import from typing | `T \| None` syntax | Python 3.10 (Oct 2021) | Cleaner syntax; preferred in modern codebases |
| `List[str]`, `Dict[str, int]` | `list[str]`, `dict[str, int]` | Python 3.9 (Oct 2020) | No need to import from typing for built-in types |
| FastAPI without Annotated | `Annotated[T, Depends(...)]` pattern | FastAPI 0.95+ (Mar 2023) | Better IDE support; clearer dependency declarations |
| Gunicorn for ASGI | Uvicorn directly | 2018-2019 | Native ASGI support; better async performance |
| Manual OpenAPI generation | Auto-generation from type hints | FastAPI inception (2018) | Docs always in sync with code |

**Deprecated/outdated:**
- **Pydantic v1 patterns:** `@validator`, `class Config:`, `.dict()` method (use `@field_validator`, `model_config`, `.model_dump()`)
- **`from typing import List, Dict`** for Python 3.9+ (use built-in `list`, `dict`)
- **Using `def` for I/O-bound endpoints** (use `async def` for async-first architecture)
- **Bare list responses** from APIs (use envelope objects for extensibility)

## Open Questions

1. **How deep should HTTP theory go in Module 002?**
   - What we know: Mobile developers have used HTTP but may not understand headers, methods, status codes deeply
   - What's unclear: Should we cover HTTP/1.1 vs HTTP/2? How much detail on headers (Cache-Control, ETag)?
   - Recommendation: Cover practical essentials (methods, status codes, common headers, content negotiation) but skip protocol-level details (keep/alive, chunked encoding). Save caching for Module 014 (Redis).

2. **Should exercises use async/await from the start?**
   - What we know: FastAPI is async-first; mobile devs understand async/await concept
   - What's unclear: Module 001 teaches async basics, but some exercises might be clearer with sync code initially
   - Recommendation: Use `async def` from Module 003 onwards consistently. The mental model should be "FastAPI = async" from day one.

3. **How to handle incomplete coverage of FastAPI features?**
   - What we know: Phase 1 covers basics; advanced features (dependencies, middleware, background tasks) come in later phases
   - What's unclear: Should we mention "there's more" or let learners discover progressively?
   - Recommendation: Add "What's Next" section to each module README pointing to future modules. Don't overwhelm but set expectations.

4. **Should projects be cumulative or standalone?**
   - What we know: Requirements say "self-contained projects per module"
   - What's unclear: Is building 4 separate projects better than evolving one project across modules?
   - Recommendation: Keep self-contained as specified. Allows learners to skip modules if needed, focus on specific topics. Capstone (Phase 8) integrates everything.

## Sources

### Primary (HIGH confidence)
- [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/) - Complete learning progression
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/) - Validators, models, fields
- [FastAPI Python Types Intro](https://fastapi.tiangolo.com/python-types/) - Type hints in FastAPI context
- [FastAPI PyPI Page](https://pypi.org/project/fastapi/) - Version compatibility, Python 3.13 support
- [Pydantic Migration Guide](https://docs.pydantic.dev/latest/migration/) - v1 to v2 changes
- [REST API Tutorial - HTTP Status Codes](https://restfulapi.net/http-status-codes/) - Standard status codes
- [REST API URI Naming Conventions](https://restfulapi.net/resource-naming/) - Resource naming best practices

### Secondary (MEDIUM confidence)
- [GitHub: FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices) - Community-vetted patterns
- [FastAPI Best Practices 2026 Guide](https://developer-service.blog/fastapi-best-practices-a-condensed-guide-with-examples/) - Current practices
- [Pydantic Complete Guide for 2026](https://devtoolbox.dedyn.io/blog/pydantic-complete-guide) - Comprehensive v2 patterns
- [FastAPI Response Models 2026](https://thelinuxcode.com/fastapi-response-models-in-2026-typed-responses-safer-apis-better-docs/) - Response model patterns
- [Building Robust Error Handling in FastAPI](https://dev.to/buffolander/building-robust-error-handling-in-fastapi-and-avoiding-rookie-mistakes-ifg) - Common mistakes
- [The Complete FastAPI × pytest Guide 2026](https://blog.greeden.me/en/2026/01/06/the-complete-fastapi-x-pytest-guide-building-fearless-to-change-apis-with-unit-tests-api-tests-integration-tests-and-mocking-strategies/) - Testing patterns
- [Python 3.12/3.13 Type Hints Features](https://www.zestminds.com/blog/fastapi-requirements-setup-guide-2025/) - Python version requirements
- [Mastering FastAPI Dependencies](https://medium.com/@ddias.olv/mastering-depends-in-fastapi-unlocking-the-power-of-dependency-injection-e529c99386ea) - Dependency injection patterns

### Tertiary (LOW confidence)
- [FastAPI Production Deployment](https://render.com/articles/fastapi-production-deployment-best-practices) - Production patterns (not needed for Phase 1)
- [REST API Design Best Practices](https://blog.postman.com/rest-api-best-practices/) - General REST guidance

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - FastAPI and Pydantic v2 are clearly dominant, official documentation is authoritative
- Architecture: HIGH - Module 001 pattern is established, FastAPI tutorial structure is well-documented
- Pitfalls: HIGH - Common mistakes are well-documented across multiple sources and official guides
- Educational patterns: MEDIUM - Mobile-dev-specific framing is inferred from general pedagogical practices, not explicitly documented

**Research date:** 2026-02-26
**Valid until:** 2026-04-26 (60 days - stable ecosystem, incremental updates expected)

**Key uncertainties resolved:**
- Pydantic v2 is standard (v1 deprecated): Confirmed via official docs and multiple 2026 tutorials
- Python 3.12+ is recommended, 3.13 supported: Confirmed via FastAPI 0.115.8 release notes
- `async def` should be default: Confirmed via FastAPI best practices and official tutorials
- Separate request/response models: Confirmed as best practice across multiple sources
