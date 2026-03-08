# Phase 06: Production Part A - Research

**Researched:** 2026-03-08
**Domain:** Docker containerization, CI/CD pipelines, security hardening, performance optimization for FastAPI
**Confidence:** HIGH

## Summary

This research covers four production-readiness modules for FastAPI: Docker containerization (Module 017), CI/CD with GitHub Actions (Module 018), security best practices against OWASP Top 10 (Module 019), and performance optimization including N+1 queries and connection pooling (Module 020). These modules transition learners from building features to deploying and hardening production systems.

The ecosystem is mature across all four domains. FastAPI's official documentation provides detailed Docker deployment guidance with exec-form CMD for graceful shutdown. GitHub Actions is the standard CI/CD platform for Python projects with excellent Docker integration. Security follows OWASP API Security Top 10 with FastAPI's built-in CORS middleware, Pydantic validation, and third-party rate limiting (slowapi). Performance optimization leverages SQLAlchemy 2.0's eager loading strategies (selectinload, joinedload), built-in connection pooling, cProfile/line_profiler for profiling, and Locust for load testing.

All four modules produce educational content (theory files, exercises, project READMEs) following the established pattern from Phases 1-5. Exercises should be self-contained where possible -- Dockerfile/docker-compose exercises are text-based (write-and-validate), GitHub Actions workflows are YAML files, security exercises use FastAPI TestClient, and performance exercises use embedded SQLite databases with SQLAlchemy.

**Primary recommendation:** Use official FastAPI Docker docs for containerization patterns with multi-stage builds. Use GitHub Actions with standard Python/Docker workflows. Use slowapi for rate limiting, custom middleware for security headers, and FastAPI's built-in CORSMiddleware. Use SQLAlchemy selectinload/joinedload for N+1 fixes, cProfile for profiling, and Locust for load testing. Follow established module content patterns: 6-7 theory files, 3 exercises with embedded tests, 1 project README.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROD-01 | Module 017 -- Docker & Containers: 6 theory files (container concepts, Dockerfile, multi-stage builds, Docker Compose, networking, production optimizations), 3 exercises (write Dockerfile, compose setup, multi-stage build), 1 project (containerize API with PostgreSQL/Redis) | FastAPI official Docker docs, multi-stage build patterns, exec-form CMD, Docker Compose networking, non-root user patterns |
| PROD-02 | Module 018 -- CI/CD & Deployment: 6 theory files (CI/CD concepts, GitHub Actions, CI testing, Docker image building, cloud deployment, env vars/secrets), 3 exercises (workflow file, test pipeline, deployment config), 1 project (full CI/CD pipeline) | GitHub Actions workflow syntax, actions/setup-python, Docker build-push-action, secrets management, environment variables |
| PROD-03 | Module 019 -- Security Best Practices: 7 theory files (OWASP top 10, input validation, SQL injection, CORS, rate limiting, secrets management, security headers), 3 exercises (identify vulnerabilities, CORS config, input sanitization), 1 project (security audit and hardening) | OWASP API Security Top 10, FastAPI CORSMiddleware, slowapi rate limiting, Pydantic input validation, security headers middleware, SQLAlchemy parameterized queries |
| PROD-04 | Module 020 -- Performance Optimization: 6 theory files (profiling, query analysis, N+1 queries, connection pooling, async best practices, load testing), 3 exercises (profile code, fix N+1, load test), 1 project (profile and optimize slow endpoint) | cProfile/line_profiler, SQLAlchemy selectinload/joinedload, connection pool configuration, async patterns, Locust load testing |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Docker | latest | Container runtime | Industry standard for containerization; FastAPI official docs cover it |
| Docker Compose | v2+ | Multi-container orchestration | Standard for local dev with PostgreSQL/Redis; built into Docker Desktop |
| GitHub Actions | N/A (SaaS) | CI/CD pipeline | Most popular CI/CD for GitHub repos; free tier sufficient for learning |
| FastAPI CORSMiddleware | built-in | Cross-origin resource sharing | Built into FastAPI/Starlette; official docs provide configuration guide |
| slowapi | 0.1.9+ | Rate limiting | Most popular FastAPI rate limiter; based on flask-limiter; <1ms overhead |
| SQLAlchemy | 2.0+ | ORM with eager loading | Already in project stack; selectinload/joinedload solve N+1 queries |
| Locust | 2.29+ | Load testing | Python-native load testing; write tests in plain Python; web UI included |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| cProfile | stdlib | Python profiling | Built-in profiler for identifying bottleneck functions |
| line_profiler | 4.1+ | Line-by-line profiling | Detailed profiling of specific functions |
| secure | 1.0+ | Security headers | Apply CSP, HSTS, X-Frame-Options headers via middleware |
| Gunicorn | 22+ | Process manager | Production WSGI/ASGI server with worker management |
| bleach | 6.0+ | HTML sanitization | Sanitize user-provided HTML content |
| python-dotenv | 1.0+ | Environment variables | Load .env files for local development |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| slowapi | fastapi-limiter | slowapi is more mature, more features, better documented |
| Locust | k6, Artillery | Locust uses Python (matches course stack); k6 uses JavaScript |
| secure | Secweb, custom middleware | secure is lightweight with good defaults; custom is simpler for teaching |
| cProfile | py-spy | cProfile is stdlib, no install needed; py-spy is sampling profiler for production |
| GitHub Actions | GitLab CI, CircleCI | GitHub Actions is free, most popular, and learners likely use GitHub |

**Installation:**
```bash
# Module 017-018: Docker (no Python deps -- Docker CLI tools)
# Docker Desktop must be installed separately

# Module 019: Security
pip install slowapi>=0.1.9 secure>=1.0.0 bleach>=6.0.0

# Module 020: Performance
pip install locust>=2.29.0 line-profiler>=4.1.0
```

## Architecture Patterns

### Recommended Project Structure

```
017-docker-containers/
├── theory/
│   ├── 01-container-concepts.md
│   ├── 02-dockerfile-basics.md
│   ├── 03-multi-stage-builds.md
│   ├── 04-docker-compose.md
│   ├── 05-networking-volumes.md
│   └── 06-production-optimizations.md
├── exercises/
│   ├── 01_dockerfile.py
│   ├── 02_docker_compose.py
│   └── 03_multi_stage_build.py
├── project/
│   └── README.md
└── README.md

018-cicd-deployment/
├── theory/
│   ├── 01-cicd-concepts.md
│   ├── 02-github-actions-basics.md
│   ├── 03-ci-testing-pipeline.md
│   ├── 04-docker-image-building.md
│   ├── 05-cloud-deployment.md
│   └── 06-env-vars-secrets.md
├── exercises/
│   ├── 01_workflow_file.py
│   ├── 02_test_pipeline.py
│   └── 03_deployment_config.py
├── project/
│   └── README.md
└── README.md

019-security-best-practices/
├── theory/
│   ├── 01-owasp-top-10.md
│   ├── 02-input-validation-sanitization.md
│   ├── 03-sql-injection-prevention.md
│   ├── 04-cors-configuration.md
│   ├── 05-rate-limiting.md
│   ├── 06-secrets-management.md
│   └── 07-security-headers.md
├── exercises/
│   ├── 01_identify_vulnerabilities.py
│   ├── 02_cors_configuration.py
│   └── 03_input_sanitization.py
├── project/
│   └── README.md
└── README.md

020-performance-optimization/
├── theory/
│   ├── 01-profiling-basics.md
│   ├── 02-query-analysis.md
│   ├── 03-n-plus-one-queries.md
│   ├── 04-connection-pooling.md
│   ├── 05-async-best-practices.md
│   └── 06-load-testing.md
├── exercises/
│   ├── 01_profile_code.py
│   ├── 02_fix_n_plus_one.py
│   └── 03_load_test.py
├── project/
│   └── README.md
└── README.md
```

### Pattern 1: Multi-Stage Docker Build for FastAPI

**What:** Two-stage Dockerfile -- builder installs dependencies, final stage copies only what's needed
**When to use:** Production images to minimize size and attack surface

**Example:**
```dockerfile
# Source: FastAPI docs + community best practices
# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /code
COPY --from=builder /install /usr/local
COPY ./app /code/app

# Switch to non-root user
USER appuser

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

### Pattern 2: Docker Compose with PostgreSQL and Redis

**What:** Multi-container setup for FastAPI with database and cache
**When to use:** Local development and testing environments

**Example:**
```yaml
# Source: Docker Compose best practices
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Pattern 3: GitHub Actions CI Pipeline

**What:** Automated testing and Docker image building on push/PR
**When to use:** Every Python/FastAPI project

**Example:**
```yaml
# Source: GitHub Actions documentation
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest -v --tb=short
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/testdb

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: myapp:latest
```

### Pattern 4: CORS + Security Headers Middleware

**What:** Configure CORS and security response headers
**When to use:** Every production FastAPI application

**Example:**
```python
# Source: FastAPI CORS docs + secure library
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI()

# CORS -- specify exact origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "https://admin.myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### Pattern 5: SQLAlchemy Eager Loading to Fix N+1

**What:** Use selectinload/joinedload to load related objects in fewer queries
**When to use:** Whenever accessing relationships in query results

**Example:**
```python
# Source: SQLAlchemy 2.0 documentation
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

# BAD: N+1 queries (1 query for posts + N queries for authors)
stmt = select(Post)
posts = session.execute(stmt).scalars().all()
for post in posts:
    print(post.author.name)  # Each access triggers a lazy load query

# GOOD: 2 queries total (1 for posts + 1 for all authors via IN clause)
stmt = select(Post).options(selectinload(Post.author))
posts = session.execute(stmt).scalars().all()
for post in posts:
    print(post.author.name)  # Already loaded, no extra query

# GOOD: 1 query with JOIN (best for many-to-one / small collections)
stmt = select(Post).options(joinedload(Post.author))
posts = session.execute(stmt).scalars().unique().all()

# Combining strategies for complex models
stmt = (
    select(User)
    .options(
        joinedload(User.profile),           # One-to-one: JOIN
        selectinload(User.posts),           # One-to-many: SELECT IN
        selectinload(User.posts, Post.tags) # Nested: SELECT IN
    )
)
```

### Pattern 6: Rate Limiting with slowapi

**What:** Per-endpoint rate limiting using decorator pattern
**When to use:** Public-facing APIs, authentication endpoints, resource-intensive endpoints

**Example:**
```python
# Source: slowapi documentation
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/resource")
@limiter.limit("10/minute")
async def get_resource(request: Request):
    return {"data": "rate limited endpoint"}

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    return {"token": "..."}
```

### Anti-Patterns to Avoid

- **Using `tiangolo/uvicorn-gunicorn-fastapi` image:** Deprecated; build from official Python base image
- **Shell-form CMD in Dockerfile:** Prevents graceful shutdown; always use exec form `CMD ["fastapi", "run", ...]`
- **Running containers as root:** Create non-root user in Dockerfile for security
- **`allow_origins=["*"]` with `allow_credentials=True`:** Invalid CORS configuration; browsers reject it
- **Storing secrets in Docker image layers:** Use build args or runtime env vars, never COPY .env files
- **Lazy loading relationships in API endpoints:** Causes N+1 queries; use selectinload/joinedload
- **Using `echo=True` in production SQLAlchemy:** Logs all SQL queries; severe performance impact
- **Profiling in production without sampling:** Use cProfile locally; use py-spy for production sampling

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rate limiting | Custom counter with Redis | slowapi | Token bucket, sliding window, per-endpoint config, proper 429 responses |
| Security headers | Manual header setting per endpoint | Custom middleware or secure library | Easy to miss endpoints; middleware applies globally |
| CORS handling | Manual Access-Control headers | FastAPI CORSMiddleware | Preflight requests, credential handling, origin matching are complex |
| SQL injection prevention | String formatting in queries | SQLAlchemy parameterized queries | SQLAlchemy automatically parameterizes; string formatting is always vulnerable |
| Load testing | Custom concurrent request scripts | Locust | Proper statistical analysis, ramp-up patterns, web UI, report generation |
| Docker health checks | Custom monitoring scripts | Docker HEALTHCHECK + pg_isready | Built into Docker orchestration; automatic restart on failure |
| CI/CD pipeline | Custom scripts on server | GitHub Actions | Matrix testing, caching, secrets management, marketplace actions |
| N+1 query detection | Manual query counting | SQLAlchemy echo + selectinload | Eager loading is declarative; manual tracking is error-prone |

**Key insight:** Production concerns (security, performance, deployment) involve many subtle edge cases that have been solved by established tools. Rate limiting needs proper 429 headers and retry-after. CORS needs preflight handling. Docker needs graceful shutdown signals. Use the tools.

## Common Pitfalls

### Pitfall 1: Docker Build Cache Invalidation

**What goes wrong:** Every code change rebuilds all dependencies, making builds slow
**Why it happens:** Copying all files before `pip install` invalidates the dependency cache layer
**How to avoid:** Copy requirements.txt first, install deps, then copy application code. Requirements change rarely; code changes frequently
**Warning signs:** Docker builds taking 2+ minutes for small code changes

### Pitfall 2: Forgetting Exec Form CMD

**What goes wrong:** Container takes 10 seconds to stop; lifespan events don't fire
**Why it happens:** Shell form `CMD command args` wraps in `/bin/sh -c`, which doesn't forward signals
**How to avoid:** Always use exec form: `CMD ["fastapi", "run", "app/main.py", "--port", "8000"]`
**Warning signs:** `docker-compose down` hangs for 10 seconds per container

### Pitfall 3: Hardcoded Secrets in CI/CD

**What goes wrong:** Database passwords, API keys leak into git history or Docker layers
**Why it happens:** Copying .env files into Docker image or committing secrets to repo
**How to avoid:** Use GitHub Actions secrets (`${{ secrets.DB_PASSWORD }}`), Docker runtime env vars, never build-time COPY of secret files
**Warning signs:** Secrets visible in `docker history`, GitHub Actions logs showing sensitive values

### Pitfall 4: CORS Wildcard with Credentials

**What goes wrong:** Browser rejects responses; authentication cookies/headers not sent
**Why it happens:** Setting `allow_origins=["*"]` with `allow_credentials=True` violates CORS spec
**How to avoid:** When using credentials, list specific origins explicitly. In dev, use `["http://localhost:3000"]`
**Warning signs:** Browser console shows CORS errors despite middleware being configured

### Pitfall 5: N+1 Queries in List Endpoints

**What goes wrong:** Listing 100 items generates 101 database queries; response time degrades linearly
**Why it happens:** SQLAlchemy lazy loads relationships by default; accessing `.author` in a loop triggers individual queries
**How to avoid:** Use `selectinload()` for one-to-many, `joinedload()` for many-to-one. Add `.options()` to every query that accesses relationships
**Warning signs:** Response time grows linearly with result count; database log shows repeated similar queries

### Pitfall 6: Connection Pool Exhaustion

**What goes wrong:** API starts returning 500 errors under load; "QueuePool limit overflow" errors
**Why it happens:** Default pool size (5) is too small for concurrent requests; connections not properly returned
**How to avoid:** Configure pool_size, max_overflow, and pool_timeout. Ensure sessions are closed (use dependency injection with `finally` or context managers)
**Warning signs:** Errors under concurrent load that don't appear in single-request testing

### Pitfall 7: Profiling Wrong Layer

**What goes wrong:** Optimizing Python code when the bottleneck is database queries
**Why it happens:** Using cProfile shows Python function time, but actual I/O wait is in database
**How to avoid:** Profile database queries first (SQLAlchemy echo, EXPLAIN ANALYZE). Then profile Python code. Optimize the actual bottleneck
**Warning signs:** cProfile shows most time in SQLAlchemy internals; individual Python functions are fast

## Code Examples

Verified patterns from official sources:

### Dockerfile for FastAPI (Official Pattern)

```dockerfile
# Source: https://fastapi.tiangolo.com/deployment/docker/
FROM python:3.12-slim

WORKDIR /code

# Cache dependencies layer
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application
COPY ./app /code/app

# Exec form for graceful shutdown
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

### SQLAlchemy Connection Pool Configuration

```python
# Source: SQLAlchemy 2.0 engine configuration docs
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    pool_size=10,          # Number of persistent connections
    max_overflow=20,       # Extra connections allowed beyond pool_size
    pool_timeout=30,       # Seconds to wait for available connection
    pool_recycle=1800,     # Recycle connections after 30 minutes
    pool_pre_ping=True,    # Verify connection health before use
    echo=False,            # NEVER True in production
)
```

### cProfile Usage for Endpoint Profiling

```python
# Source: Python stdlib cProfile documentation
import cProfile
import pstats
from io import StringIO

def profile_endpoint():
    """Profile a function and print top bottlenecks."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Call the function to profile
    result = expensive_function()

    profiler.disable()
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(20)  # Top 20 functions
    print(stream.getvalue())
    return result
```

### Locust Load Test File

```python
# Source: Locust documentation
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task(3)  # Weight: 3x more likely than other tasks
    def list_items(self):
        self.client.get("/api/items?limit=20")

    @task(1)
    def get_item(self):
        self.client.get("/api/items/1")

    @task(1)
    def create_item(self):
        self.client.post("/api/items", json={
            "name": "Test Item",
            "price": 9.99
        })

# Run: locust -f locustfile.py --host http://localhost:8000
# Headless: locust -f locustfile.py --host http://localhost:8000 \
#   --users 100 --spawn-rate 10 --run-time 60s --headless --html report.html
```

### GitHub Actions Secrets Usage

```yaml
# Source: GitHub Actions documentation
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and push Docker image
        env:
          REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
        run: |
          echo "$REGISTRY_PASSWORD" | docker login -u user --password-stdin
          docker build -t myapp:${{ github.sha }} .
          docker push myapp:${{ github.sha }}
```

### Input Validation with Pydantic (Security)

```python
# Source: Pydantic v2 + OWASP input validation
from pydantic import BaseModel, field_validator, Field
import re
import bleach

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=254)
    bio: str = Field(default="", max_length=500)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric")
        return v

    @field_validator("bio")
    @classmethod
    def sanitize_bio(cls, v: str) -> str:
        # Strip all HTML tags from user input
        return bleach.clean(v, tags=[], strip=True)
```

### Mobile Developer Comparison Tables

```
Docker Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Package       | .ipa bundle         | .apk / .aab bundle  | Docker image        |
| format        |                     |                     |                     |
+---------------+---------------------+---------------------+---------------------+
| Dependency    | Swift Package       | Gradle dependencies | requirements.txt    |
| management    | Manager             |                     | + pip install       |
+---------------+---------------------+---------------------+---------------------+
| Build config  | Xcode schemes       | build.gradle        | Dockerfile          |
|               |                     |                     |                     |
+---------------+---------------------+---------------------+---------------------+
| Multi-env     | Debug/Release       | buildTypes           | Multi-stage builds  |
| builds        | configurations      | (debug/release)     | (builder/runtime)   |
+---------------+---------------------+---------------------+---------------------+
| Distribution  | App Store Connect   | Google Play Console | Docker Hub / GHCR   |
|               |                     |                     |                     |
+---------------+---------------------+---------------------+---------------------+

CI/CD Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| CI service    | Xcode Cloud /       | GitHub Actions /    | GitHub Actions      |
|               | Bitrise             | Bitrise             |                     |
+---------------+---------------------+---------------------+---------------------+
| Test runner   | XCTest              | JUnit / Espresso    | pytest              |
|               |                     |                     |                     |
+---------------+---------------------+---------------------+---------------------+
| Deploy        | TestFlight /        | Play Console /      | Docker push +       |
| pipeline      | App Store           | Firebase App Dist   | cloud deploy        |
+---------------+---------------------+---------------------+---------------------+

Security Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Input         | UITextField         | EditText input      | Pydantic validators |
| validation    | validation          | filters             | + field_validator   |
+---------------+---------------------+---------------------+---------------------+
| Secure        | Keychain            | EncryptedShared     | Environment vars /  |
| storage       |                     | Preferences         | secrets manager     |
+---------------+---------------------+---------------------+---------------------+
| Network       | App Transport       | Network Security    | CORS middleware +   |
| security      | Security (ATS)      | Config              | security headers    |
+---------------+---------------------+---------------------+---------------------+

Performance Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Profiling     | Instruments /       | Android Profiler /  | cProfile /          |
|               | Time Profiler       | CPU Profiler        | line_profiler       |
+---------------+---------------------+---------------------+---------------------+
| Query         | Core Data           | Room query          | SQLAlchemy echo +   |
| analysis      | debug logging       | logging             | EXPLAIN ANALYZE     |
+---------------+---------------------+---------------------+---------------------+
| Load testing  | XCTest performance  | Benchmark           | Locust              |
|               | tests               |                     |                     |
+---------------+---------------------+---------------------+---------------------+
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| tiangolo/uvicorn-gunicorn-fastapi image | Build from python:3.12-slim | 2024 (deprecated) | Simpler, smaller, more control |
| Shell-form CMD | Exec-form CMD array | Always recommended | Graceful shutdown, lifespan events work |
| Manual CORS headers | FastAPI CORSMiddleware | FastAPI 0.1+ | Handles preflight, credential rules automatically |
| SQLAlchemy 1.x query().join() | SQLAlchemy 2.0 select().options(selectinload()) | 2023 | Cleaner API, better async support |
| passlib for hashing | pwdlib with Argon2 | 2024 (passlib deprecated) | Already adopted in Phase 3 |
| Manual rate limit middleware | slowapi decorator pattern | 2021+ | Per-endpoint config, proper 429 responses |
| Docker Compose v1 (`docker-compose`) | Docker Compose v2 (`docker compose`) | 2023 | Built into Docker CLI, no separate install |

**Deprecated/outdated:**
- **tiangolo/uvicorn-gunicorn-fastapi**: Deprecated Docker image; build from official Python
- **docker-compose (v1)**: Use `docker compose` (v2, built into Docker CLI)
- **SQLAlchemy 1.x Query API**: Use SQLAlchemy 2.0 select() style
- **on_event("startup")**: Use lifespan context manager (already decided in Phase 5)

## Exercise Design Considerations

### Module 017 (Docker) -- Text-Based Exercises
Docker exercises are unique because they involve writing Dockerfiles and docker-compose.yml, not Python code with pytest. The exercises should:
- Provide skeleton files with TODO comments
- Include a validation script that checks Docker syntax or builds succeed
- Alternatively, use Python exercises that programmatically validate Dockerfile content (parsing the file, checking for required instructions)
- **Recommendation:** Write Python test files that read and validate Dockerfile/docker-compose.yml content. This follows the established pytest pattern while teaching Docker concepts. Learners write the Docker files; tests verify correctness.

### Module 018 (CI/CD) -- YAML-Based Exercises
Similar to Docker, CI/CD exercises involve writing GitHub Actions YAML. The exercises should:
- Provide workflow templates with missing steps
- Use Python tests that validate YAML structure and required keys
- **Recommendation:** Python exercises that parse YAML files and verify workflow structure. Learners write .yml files; pytest validates them.

### Module 019 (Security) -- FastAPI TestClient Exercises
Security exercises fit the standard pattern well:
- Provide vulnerable FastAPI apps for learners to identify and fix
- Use TestClient to verify that security measures work (CORS headers present, rate limits enforced, input sanitized)
- **Recommendation:** Standard Python exercises with embedded FastAPI apps and pytest tests, matching established patterns.

### Module 020 (Performance) -- Database + Profiling Exercises
Performance exercises need database fixtures:
- Use SQLite with SQLAlchemy for self-contained exercises (matching Module 007 pattern)
- Provide deliberately slow code for learners to optimize
- **Recommendation:** Python exercises with in-memory SQLite, pre-built models with N+1 problems, and tests that verify query count reduction.

## Open Questions

1. **Docker exercise validation approach**
   - What we know: Docker exercises involve writing Dockerfiles, not Python code. Previous modules used pytest exclusively.
   - What's unclear: Whether to parse Docker files with Python or use a different approach
   - Recommendation: Use Python exercises that read and validate Dockerfile/YAML content with pytest. This maintains the consistent testing pattern while teaching infrastructure concepts.

2. **Locust exercise scope**
   - What we know: Locust requires a running server and produces statistical results
   - What's unclear: How to make load testing exercises self-contained
   - Recommendation: Exercise 03 teaches writing Locust test files (locustfile.py) and validates their structure. The project README covers running actual load tests against a live API.

3. **OWASP scope for API-focused course**
   - What we know: OWASP has both Web Application Top 10 and API Security Top 10
   - What's unclear: Which to emphasize
   - Recommendation: Focus on OWASP API Security Top 10 since this is an API development course. Cover: Broken Object Level Authorization, Broken Authentication, Excessive Data Exposure, Lack of Resources & Rate Limiting, Broken Function Level Authorization, Mass Assignment, Security Misconfiguration, Injection.

## Sources

### Primary (HIGH confidence)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/) - Official Dockerfile patterns, exec form CMD, multi-stage builds
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/) - CORSMiddleware configuration and options
- [SQLAlchemy 2.0 Relationship Loading](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html) - selectinload, joinedload documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Workflow syntax, secrets, service containers

### Secondary (MEDIUM confidence)
- [Slimmer FastAPI Docker Images](https://davidmuraya.com/blog/slimmer-fastapi-docker-images-multistage-builds/) - Multi-stage build size comparisons
- [FastAPI Security Guide](https://davidmuraya.com/blog/fastapi-security-guide/) - OWASP coverage for FastAPI
- [SlowAPI Documentation](https://slowapi.readthedocs.io/) - Rate limiting configuration
- [FastAPI Performance Tuning](https://blog.greeden.me/en/2026/02/03/fastapi-performance-tuning-caching-strategy-101-a-practical-recipe-for-growing-a-slow-api-into-a-lightweight-fast-api/) - N+1, connection pooling, caching strategies
- [How to Defeat N+1 Problem](https://hevalhazalkurt.com/blog/how-to-defeat-the-n1-problem-with-joinedload-selectinload-and-subqueryload/) - Detailed eager loading comparison
- [Database Connection Pooling in FastAPI](https://asifmuhammad.com/articles/database-pooling-fastapi) - Pool configuration patterns

### Tertiary (LOW confidence)
- [Secure Library](https://github.com/TypeError/secure) - Security headers middleware (GitHub, not extensively verified)
- [Secweb](https://github.com/tmotagam/Secweb) - Alternative security headers package

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Docker, GitHub Actions, SQLAlchemy, and slowapi are well-documented with official sources
- Architecture: HIGH - Module structure follows established patterns from Phases 1-5; all code patterns from official docs
- Pitfalls: HIGH - Common production pitfalls verified across multiple sources and official documentation
- Exercise design: MEDIUM - Docker/CI/CD exercises need novel approach (YAML/Dockerfile validation via pytest); recommendation provided but untested

**Research date:** 2026-03-08
**Valid until:** ~2026-05-08 (60 days - production tooling is mature and stable)
