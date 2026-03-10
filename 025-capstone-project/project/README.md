# Capstone Project: Build a Production-Ready API

## Overview

This is the culmination of everything you have learned in Modules 002-024. You will design, build, test, and prepare for deployment a complete REST API. The goal is not just to write code that works, but to make architectural decisions, handle edge cases, and produce something you would be confident deploying to production.

## Start Here

Before writing any code:

1. **Read the theory files** (theory/01 through theory/06) -- they synthesize concepts from prior modules into a project planning context
2. **Complete the exercises** (exercises/01 through exercises/03) -- they produce your API spec, database schema, and test plan
3. **Choose a project option** below and follow the phased implementation guide

Your exercise outputs become the planning documents for your project.

## Project Options

### Option A: Social Media API

Build a Twitter/Instagram-like backend with these resources:

- **Users** -- Registration, profiles, authentication
- **Posts** -- Create, read, update, delete with optional images
- **Comments** -- Threaded comments on posts
- **Follows** -- Follow/unfollow users, generate a feed

Features: JWT auth, feed generation from followed users, like/unlike posts, pagination on feeds and comment threads.

### Option B: E-Commerce API

Build a shopping backend with these resources:

- **Users** -- Accounts, addresses, authentication
- **Products** -- Catalog with categories and search
- **Cart** -- Add/remove items, calculate totals
- **Orders** -- Place orders, track status, order history

Features: JWT auth, inventory management, order state machine (pending/confirmed/shipped/delivered), product search with filters.

> **Note:** Payment integration (Stripe) is a **bonus feature**, not a core requirement. This keeps Option B comparable in scope to Options A and C.

### Option C: Task Management API

Build a Trello/Asana-like backend with these resources:

- **Users** -- Registration, team membership, authentication
- **Workspaces** -- Team workspaces with member roles
- **Projects** -- Projects within workspaces
- **Tasks** -- Tasks with assignees, due dates, priorities, status

Features: JWT auth, role-based access (admin/member/viewer), task filtering and sorting, activity log for task changes.

All three options are designed to have comparable difficulty: 3-4 main resources, similar relationship complexity, and equivalent authentication/authorization needs. Choose based on your interest.

## Grading Rubric (100 points total)

### Functionality (30 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Authentication system | 8 | Registration, login, JWT access + refresh tokens |
| CRUD operations | 8 | Complete CRUD for all main resources |
| Input validation | 5 | Pydantic schemas validate all inputs with meaningful errors |
| Error handling | 5 | Consistent error responses, proper HTTP status codes |
| Resource relationships | 4 | Correct foreign keys, cascade behavior, nested queries |

### Code Quality (20 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Project structure | 5 | Clean separation: api/, models/, schemas/, services/ |
| Service layer | 5 | Business logic in services, not route handlers |
| Type hints | 5 | Consistent type annotations throughout codebase |
| Clean code | 5 | Readable names, no duplication, small functions |

### Testing (20 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Test coverage | 5 | 80%+ line coverage across the project |
| Auth tests | 5 | Registration, login, token refresh, protected routes |
| CRUD tests | 5 | Happy path + error cases (400, 401, 403, 404) |
| Test fixtures | 5 | Proper isolation, reusable fixtures, no test interdependence |

### Documentation (15 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Project README | 5 | Setup instructions, architecture overview, API summary |
| API documentation | 5 | Swagger/OpenAPI descriptions on all endpoints |
| Code comments | 5 | Docstrings on services, complex logic explained |

### Production Readiness (15 points)

| Criteria | Points | Description |
|----------|--------|-------------|
| Docker setup | 4 | Dockerfile + docker-compose for full stack |
| CI pipeline | 4 | GitHub Actions running tests and linting |
| Structured logging | 4 | structlog with JSON output, request context |
| Health check | 3 | /health endpoint checking database and Redis connectivity |

### Bonus Points (up to 10 extra)

| Feature | Points | Description |
|---------|--------|-------------|
| WebSocket feature | 3 | Real-time notifications or live updates |
| File uploads | 2 | Image/file upload with validation (type, size) |
| Background tasks | 3 | Celery or FastAPI background tasks for async work |
| API versioning | 2 | /v1/ prefix with versioned routers |

## Phased Implementation Guide

### Phase 1: Planning (Week 1)

**Deliverables:** API design document, database schema, test plan

**Checkpoint:** Complete all three Module 025 exercises

- [ ] Define all API endpoints with methods, paths, request/response schemas, and auth requirements
- [ ] Design database schema with all tables, relationships, indexes, and constraints
- [ ] Create test plan with at least 15 test cases covering auth, CRUD, and error scenarios

Reference: Theory files 01 (API Design), 02 (Schema Design), 05 (Testing Strategy)

### Phase 2: Foundation (Week 2)

**Deliverables:** Project structure, Docker setup, database models, auth system

- [ ] Create project directory structure (see Starter Templates below)
- [ ] Set up Docker Compose with PostgreSQL and Redis
- [ ] Create SQLAlchemy models with Alembic migrations
- [ ] Implement user registration and JWT authentication (access + refresh tokens)
- [ ] Write first auth tests (register, login, token refresh, protected route)

Reference: Modules 003 (FastAPI basics), 007 (SQLAlchemy), 009 (JWT auth), 017 (Docker)

### Phase 3: Core Features (Week 3)

**Deliverables:** CRUD endpoints for all main resources

- [ ] Implement service layer for each resource
- [ ] Create Pydantic schemas (Create, Update, Response) for each resource
- [ ] Build CRUD endpoints with proper error handling
- [ ] Add role-based authorization where needed
- [ ] Write CRUD tests for happy path and error cases (400, 401, 403, 404)

Reference: Modules 004 (requests), 005 (responses), 008 (DB integration), 010 (authorization)

### Phase 4: Advanced Features (Week 4)

**Deliverables:** Caching, background tasks, additional features

- [ ] Add Redis caching for frequently accessed data (lists, user profiles)
- [ ] Implement background tasks for async operations (email notifications, cleanup)
- [ ] Add pagination and filtering to list endpoints
- [ ] Add file uploads if applicable to chosen project

Reference: Modules 013 (background tasks), 014 (Redis caching), 015 (file handling)

### Phase 5: Production Hardening (Week 5)

**Deliverables:** Logging, rate limiting, security review, performance

- [ ] Configure structured logging with structlog (JSON output, request IDs)
- [ ] Add health check endpoint (database + Redis connectivity)
- [ ] Implement rate limiting on auth endpoints (login, register)
- [ ] Review OWASP security checklist (CORS, input sanitization, SQL injection prevention)
- [ ] Fix any N+1 query issues (use joinedload/selectinload)

Reference: Modules 019 (logging), 020 (health checks), 021 (versioning), 023 (rate limiting)

### Phase 6: Polish and Deploy (Week 6)

**Deliverables:** CI/CD, documentation, final testing

- [ ] Create GitHub Actions CI workflow (tests, linting, type checking)
- [ ] Ensure 80%+ test coverage
- [ ] Write API documentation (Swagger descriptions on all endpoints)
- [ ] Create comprehensive project README (setup, architecture, API summary)
- [ ] Final code review against the grading rubric above

Reference: Modules 018 (CI/CD), 022 (API documentation)

## Starter Templates

These templates provide project structure without implementing business logic. Copy them as starting points and fill in your project-specific code.

### Project Structure

```
capstone/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   └── [resources].py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── api/
│       └── v1/
├── alembic/
│   └── env.py
├── docker-compose.yml
├── Dockerfile
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

### docker-compose.yml Template

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: capstone
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: capstone_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

> The application service is intentionally omitted. You will create a Dockerfile and add it here once your app is ready to containerize.

### Dockerfile Template

```dockerfile
# Build stage: install dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage: copy only what's needed
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### GitHub Actions CI Template

```yaml
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
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DATABASE_URL: postgresql://test:test@localhost:5432/test_db

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run linting
        run: ruff check .

      - name: Run tests
        run: pytest -v --tb=short
```

### pyproject.toml Template

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.mypy]
python_version = "3.12"
strict = true
```

## Common Mistakes

### Planning Phase
- Designing too many endpoints before building any -- start with auth + one resource, then iterate
- Skipping the schema design exercise -- leads to migration headaches later when you realize relationships are wrong

### Implementation Phase
- Putting business logic in route handlers instead of services (review Module 008 pattern)
- Using plain dict responses instead of Pydantic response models
- Forgetting to add `created_at` / `updated_at` timestamps to models
- Not handling the case where a referenced resource does not exist (return 404, not 500)

### Testing Phase
- Only testing happy paths -- test 400, 401, 403, and 404 responses too
- Not using fixtures for test data isolation (tests pass individually but fail together)
- Testing implementation details instead of behavior (testing SQL queries instead of API responses)

### Deployment Phase
- Hardcoding secrets instead of using environment variables
- Missing health check endpoint (load balancers need it)
- Not configuring CORS for frontend integration
- Forgetting to run migrations in the CI pipeline

## Self-Assessment Checklist

Use this checklist before submitting. Each item maps to the grading rubric above.

### Functionality (30 pts)
- [ ] Users can register and log in (8 pts)
- [ ] All main resources have full CRUD (8 pts)
- [ ] Invalid inputs return 422 with clear error messages (5 pts)
- [ ] Errors return consistent JSON format with proper status codes (5 pts)
- [ ] Related resources are properly linked (4 pts)

### Code Quality (20 pts)
- [ ] Code is organized into api/, models/, schemas/, services/ (5 pts)
- [ ] Route handlers call service functions, not raw SQL (5 pts)
- [ ] All functions have type hints (5 pts)
- [ ] No copy-pasted code blocks, functions are small and focused (5 pts)

### Testing (20 pts)
- [ ] `pytest --cov` reports 80%+ coverage (5 pts)
- [ ] Auth flow is fully tested (register, login, refresh, protected) (5 pts)
- [ ] Each resource has happy path + error tests (5 pts)
- [ ] Tests use fixtures and are independent (5 pts)

### Documentation (15 pts)
- [ ] README explains how to set up and run the project (5 pts)
- [ ] Every endpoint has a Swagger description (5 pts)
- [ ] Complex functions have docstrings (5 pts)

### Production Readiness (15 pts)
- [ ] `docker-compose up` starts the full stack (4 pts)
- [ ] `git push` triggers CI with tests and linting (4 pts)
- [ ] Requests are logged with structlog in JSON format (4 pts)
- [ ] `/health` endpoint returns database and Redis status (3 pts)

## Resources

Review these modules when you need a refresher on specific topics:

- **API Design:** Module 002 (HTTP/REST), Module 003 (FastAPI), Module 004 (Requests), Module 005 (Responses)
- **Database:** Module 006 (SQL), Module 007 (SQLAlchemy), Module 008 (DB Integration)
- **Auth:** Module 009 (JWT Authentication), Module 010 (Authorization)
- **Testing:** Module 011 (Testing FastAPI)
- **Async:** Module 012 (Async Python), Module 013 (Background Tasks)
- **Infrastructure:** Module 014 (Redis), Module 017 (Docker), Module 018 (CI/CD)
- **Production:** Module 019 (Logging), Module 020 (Health Checks), Module 023 (Rate Limiting)
- **Advanced:** Module 015 (File Handling), Module 016 (WebSockets), Module 021 (Versioning), Module 024 (Microservices)
