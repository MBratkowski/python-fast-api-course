# Project: Containerize a Full API

## Overview

Containerize a complete FastAPI application with PostgreSQL and Redis using Docker Compose. You'll create a production-ready Docker setup with multi-stage builds, health checks, non-root user, and proper environment configuration.

This project ties together everything from Module 017 -- Dockerfiles, multi-stage builds, Docker Compose, networking, volumes, and production optimizations.

## Requirements

### 1. Multi-Stage Dockerfile
- [ ] Stage 1 (builder): Install Python dependencies to a custom prefix
- [ ] Stage 2 (runtime): Copy only installed packages from builder
- [ ] Use `python:3.12-slim` as base image (NOT the deprecated tiangolo image)
- [ ] Create and switch to a non-root user
- [ ] Use exec-form CMD for graceful shutdown
- [ ] Include a HEALTHCHECK instruction

### 2. Docker Compose Configuration
- [ ] Define three services: `api`, `db` (PostgreSQL), `redis`
- [ ] PostgreSQL service with healthcheck using `pg_isready`
- [ ] API depends on `db` with `condition: service_healthy`
- [ ] Named volumes for PostgreSQL and Redis data persistence
- [ ] Environment variables for DATABASE_URL, REDIS_URL, SECRET_KEY
- [ ] Use Docker Compose v2 syntax (`docker compose`, no `version:` key)

### 3. .dockerignore
- [ ] Exclude `.git`, `__pycache__`, `.venv`, `.env`, `tests/`, `*.md`
- [ ] Exclude Docker-related files (Dockerfile, docker-compose.yml)
- [ ] Exclude IDE files (.vscode, .idea)

### 4. Environment Configuration
- [ ] No hardcoded secrets in Dockerfile or docker-compose.yml comments
- [ ] Use environment variables for all configuration
- [ ] Provide a `.env.example` file with placeholder values

## Starter Template

Create the following file structure:

```
my-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app with /health endpoint
│   └── core/
│       └── config.py    # Settings from environment variables
├── requirements.txt
├── Dockerfile           # Multi-stage build
├── docker-compose.yml   # API + PostgreSQL + Redis
├── .dockerignore
└── .env.example
```

### app/main.py (starter)

```python
from fastapi import FastAPI

app = FastAPI(title="Containerized API")


@app.get("/")
async def root():
    return {"message": "Hello from Docker!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### requirements.txt (starter)

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
gunicorn>=22.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
redis>=5.0.0
pydantic-settings>=2.0.0
```

### .env.example (starter)

```bash
DATABASE_URL=postgresql://appuser:apppass@db:5432/appdb
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-this-in-production
DEBUG=true
```

## Success Criteria

```bash
# 1. Build and start all services
docker compose up -d --build

# 2. Verify all containers are running and healthy
docker compose ps
# Expected: api (healthy), db (healthy), redis (running)

# 3. API responds
curl http://localhost:8000/
# Expected: {"message": "Hello from Docker!"}

# 4. Health check works
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 5. Verify non-root user
docker compose exec api whoami
# Expected: appuser (not root)

# 6. Verify data persists
docker compose down
docker compose up -d
# Data should still be in PostgreSQL

# 7. Clean up
docker compose down -v
```

## Stretch Goals

- [ ] Add a `docker-compose.prod.yml` override for production (Gunicorn workers, no debug)
- [ ] Add an Nginx reverse proxy service
- [ ] Implement Docker layer caching in CI (GitHub Actions)
- [ ] Add database migration support (Alembic) as a startup step
- [ ] Scan the image for vulnerabilities with `docker scout cves`
