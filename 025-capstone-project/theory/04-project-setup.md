# Project Setup

## Why This Matters

In mobile development, Xcode and Android Studio generate your project structure. You run "New Project," choose a template, and start coding. Backend development has no equivalent wizard. You create every directory, every config file, every Docker service from scratch -- or from experience.

This is the backend equivalent of learning to configure your Xcode build settings instead of relying on defaults. It is not glamorous, but getting the setup right means your project builds, tests, and deploys reliably from day one. Getting it wrong means fighting configuration issues for the entire project.

This file synthesizes Modules 003, 007, and 017 into a step-by-step project scaffolding guide.

## Quick Review

- **FastAPI project structure** (Module 003): The `src/` directory pattern separates API routes, models, schemas, services, and configuration. The `main.py` entry point creates the FastAPI app and includes routers.
- **Alembic migrations** (Module 007): `alembic init alembic` creates the migration directory. `alembic revision --autogenerate -m "description"` generates migrations from model changes. `alembic upgrade head` applies all pending migrations.
- **Docker and Docker Compose** (Module 017): Multi-stage Dockerfiles separate build from runtime. Docker Compose orchestrates the app, PostgreSQL, and Redis containers. Environment variables configure each service.

## How They Compose

Project setup is a sequence of decisions that build on each other:

**Structure --> Configuration --> Database --> Containers --> First Run**

1. **Structure.** Create the directory layout. This determines import paths and where every file lives. Change it later and you rewrite every import.

2. **Configuration.** Set up `pyproject.toml` (dependencies, tool config), `.env` files (secrets, connection strings), and `core/config.py` (Pydantic Settings for typed configuration). Configuration feeds into every other component.

3. **Database.** Initialize Alembic, create the base model class, write the database session factory. Your first migration creates the initial schema.

4. **Containers.** Write `Dockerfile` for the app, `docker-compose.yml` for the full stack. Map ports, mount volumes, set environment variables.

5. **First run.** `docker-compose up` starts everything. Alembic migrates the database. The API responds on `localhost:8000`. Tests run against a test database.

### The Configuration Chain

Configuration flows through three layers:

```
.env file (secrets, per-environment values)
  |
  v
Pydantic Settings (typed, validated, with defaults)
  |
  v
Depends(get_settings) (injected into routes and services)
```

```python
# core/config.py (Module 003 + Module 017)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:pass@localhost:5432/app"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    debug: bool = False

    model_config = {"env_file": ".env"}
```

This pattern means: secrets stay in `.env` (never committed), defaults work for development, and production overrides via environment variables in Docker.

## Decision Framework

### Setting Up a New FastAPI Project from Zero

```
Step 1: Create project structure
  mkdir -p src/{api,core,db,models,schemas,services} tests/api alembic

Step 2: Initialize Python environment
  python -m venv .venv
  source .venv/bin/activate
  pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic-settings
  pip install pytest httpx pytest-asyncio  # dev dependencies
  pip freeze > requirements.txt

Step 3: Create configuration
  - src/core/config.py  (Pydantic Settings)
  - .env                (DATABASE_URL, SECRET_KEY, etc.)
  - .env.example        (same keys, no real values -- committed to git)

Step 4: Set up database
  - src/db/session.py   (engine, SessionLocal, get_db dependency)
  - src/db/base.py      (DeclarativeBase)
  - alembic init alembic
  - Edit alembic/env.py to import your Base and read DATABASE_URL from Settings

Step 5: Create FastAPI app
  - src/main.py          (create_app(), include routers, add exception handlers)
  - src/api/health.py    (GET /health -- proves the app runs)

Step 6: Set up Docker
  - Dockerfile           (multi-stage: builder + runtime)
  - docker-compose.yml   (app + postgres + redis)
  - .dockerignore        (.venv, .git, __pycache__)

Step 7: Verify
  docker-compose up -d
  curl http://localhost:8000/health
  pytest -v
```

### File-by-File Decisions

| File | Purpose | Key Decision |
|------|---------|-------------|
| `pyproject.toml` | Project metadata, tool config | Use for ruff, mypy, pytest config |
| `.env` | Runtime secrets | Never commit. Add to `.gitignore` |
| `.env.example` | Template for developers | Commit this. Document required variables |
| `Dockerfile` | App container | Multi-stage: builder installs deps, runtime copies only what is needed |
| `docker-compose.yml` | Full stack | Map ports, set health checks, use volumes for data persistence |
| `alembic.ini` | Migration config | Point `sqlalchemy.url` to Settings, not hardcoded |
| `conftest.py` | Test fixtures | Override `get_db` to use test database, provide `client` fixture |

## Capstone Application

**Common Setup -- Shared Across All Three Project Options**

Regardless of which capstone option you choose (Social Media, E-Commerce, or Task Management), the project setup is identical:

**Directory structure:**
```
capstone/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # get_db, get_current_user, get_settings
│   │   ├── health.py        # GET /health
│   │   └── auth.py          # POST /auth/register, /auth/login, /auth/refresh
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Pydantic Settings
│   │   ├── security.py      # JWT + password hashing (PyJWT, pwdlib)
│   │   └── exceptions.py    # Domain exception classes
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # DeclarativeBase
│   │   └── session.py       # engine, SessionLocal, get_db
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User model (every project needs users)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # UserCreate, UserResponse, Token schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py  # Register, login, token logic
│   └── main.py              # create_app(), include routers
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # client fixture, test DB override
│   └── api/
│       ├── __init__.py
│       └── test_health.py   # Smoke test
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

**docker-compose.yml:**
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: capstone
      POSTGRES_PASSWORD: capstone
      POSTGRES_DB: capstone
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U capstone"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

**Dockerfile (multi-stage):**
```dockerfile
# Builder stage: install dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage: copy only what's needed
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Checklist

Before writing any business logic, verify your project setup:

- [ ] Directory structure follows `src/` layout with api, core, db, models, schemas, services
- [ ] `pyproject.toml` or `requirements.txt` lists all dependencies with versions
- [ ] `.env.example` committed with all required variable names (no real secrets)
- [ ] `.env` added to `.gitignore`
- [ ] Pydantic Settings class reads from `.env` with sensible defaults
- [ ] Database session factory created with `get_db` dependency
- [ ] Alembic initialized and `env.py` configured to read from Settings
- [ ] `GET /health` endpoint responds with 200
- [ ] `docker-compose up` starts app + postgres + redis without errors
- [ ] `pytest` runs at least one smoke test successfully

## Key Takeaways

1. **Set up the project structure once, correctly.** Changing directory layout after writing 50 files means rewriting 50 import statements. Get it right on day one.
2. **Configuration has three layers: .env, Settings, Depends().** Secrets in `.env`, validation in Settings, injection via Depends(). Never hardcode connection strings.
3. **Docker Compose is your development environment.** It guarantees every developer (and CI) runs the same PostgreSQL version, same Redis version, same configuration.
4. **Health check endpoint is your first feature.** It proves the app starts, the database connects, and the deployment pipeline works -- all before you write any business logic.
5. **Alembic from the start, not as an afterthought.** Initialize Alembic before your first model. Every schema change gets a migration. No exceptions.
