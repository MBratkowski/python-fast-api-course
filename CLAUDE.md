# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Backend Development Mastery - A hands-on course for mobile developers transitioning to backend development. Covers everything needed to build production-grade REST APIs with Python and FastAPI.

## Tech Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Auth**: JWT (python-jose)
- **Validation**: Pydantic v2
- **Testing**: pytest + httpx
- **Containers**: Docker

## Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run API server
uvicorn main:app --reload --port 8000

# Run tests
pytest -v
pytest tests/test_specific.py -v
pytest -k "test_name" -v

# Type checking
mypy src/

# Linting
ruff check . --fix
ruff format .

# Database
alembic upgrade head          # Run migrations
alembic revision --autogenerate -m "description"  # Create migration

# Docker
docker-compose up -d          # Start services (postgres, redis)
docker-compose down           # Stop services
```

## Architecture

```
project/
├── src/
│   ├── api/           # Route handlers (endpoints)
│   ├── core/          # Config, security, dependencies
│   ├── db/            # Database connection, base model
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic request/response schemas
│   ├── services/      # Business logic layer
│   └── main.py        # FastAPI app entry point
├── tests/
│   ├── conftest.py    # Fixtures
│   └── api/           # API endpoint tests
├── alembic/           # Database migrations
└── docker-compose.yml
```

## Patterns Used

- **Repository Pattern**: Database access abstracted in services
- **Dependency Injection**: FastAPI's `Depends()` for dependencies
- **Pydantic Schemas**: Separate schemas for Create, Update, Response
- **JWT Auth**: Access + Refresh token pattern

## Module Structure

Each numbered module (`0XX-topic/`) contains:
- `theory/` - Concepts with code examples
- `exercises/` - Hands-on coding tasks
- `project/` - Mini-project applying the concepts

## API Conventions

- REST endpoints: `GET /users`, `POST /users`, `GET /users/{id}`
- Response format: `{"data": {...}, "message": "..."}`
- Error format: `{"detail": "error message"}`
- Auth header: `Authorization: Bearer <token>`
