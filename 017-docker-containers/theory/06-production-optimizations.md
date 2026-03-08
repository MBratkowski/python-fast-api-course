# Production Optimizations

## Why This Matters

Shipping a Debug build to the App Store would be embarrassing -- larger binary, slower performance, debug logs exposed to users. The same applies to Docker images in production. A development-optimized image with unnecessary files, no security hardening, and no health monitoring is a liability.

This section covers the final steps to make your Docker images production-ready: reducing image size, hardening security, adding health checks, and running with a production-grade server.

## .dockerignore

The `.dockerignore` file excludes files from the build context, just like `.gitignore` excludes files from git. Without it, `COPY . .` sends everything to the Docker daemon -- including `.git/`, `__pycache__/`, `.env` files, and your virtual environment.

```
# .dockerignore

# Version control
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
.venv
venv
*.egg-info

# IDE
.vscode
.idea
*.swp
*.swo

# Docker (don't copy Docker configs into the image)
Dockerfile
docker-compose*.yml
.dockerignore

# Environment and secrets (NEVER include in image)
.env
.env.*
*.pem
*.key

# Testing and CI
tests/
pytest.ini
.pytest_cache
.coverage
htmlcov/
.github/

# Documentation
*.md
docs/
LICENSE
```

### Why .dockerignore Matters

```
Without .dockerignore:
  Build context: 500 MB (includes .git, .venv, node_modules)
  Build time: 30 seconds (sending context to daemon)

With .dockerignore:
  Build context: 5 MB (only application code + requirements.txt)
  Build time: 2 seconds
```

Also: excluding `.env` and `*.key` prevents secrets from ending up in Docker image layers.

## Minimizing Layers

Each `RUN` instruction creates a layer. Combine related commands to reduce layer count and image size.

```dockerfile
# BAD: 3 separate layers, apt cache remains in first layer
RUN apt-get update
RUN apt-get install -y libpq-dev
RUN rm -rf /var/lib/apt/lists/*

# GOOD: 1 layer, apt cache cleaned in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*
```

Why this matters: Docker layers are additive. If you create a file in one layer and delete it in the next, the file still exists in the first layer (it's just hidden). Combining commands into one `RUN` means the cleanup actually reduces image size.

## Health Checks in Dockerfile

Health checks let Docker monitor whether your application is actually working, not just whether the process is running.

```dockerfile
FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

# Health check -- Docker will call this periodically
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

You'll also need a health endpoint in your FastAPI app:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Health Check States

| State | Meaning | Docker Action |
|-------|---------|---------------|
| Starting | Container just started, within `start-period` | No action |
| Healthy | Health check passed | Normal operation |
| Unhealthy | Health check failed `retries` times | Depends on orchestrator (restart, alert) |

## Gunicorn with Uvicorn Workers

FastAPI runs on Uvicorn by default. For production, use Gunicorn as a process manager that spawns multiple Uvicorn workers:

```dockerfile
# Production CMD with Gunicorn
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-"]
```

```
# requirements.txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
gunicorn>=22.0.0
```

### Why Gunicorn?

| Single Uvicorn | Gunicorn + Uvicorn Workers |
|---------------|--------------------------|
| 1 process | Multiple worker processes |
| 1 CPU core utilized | Multiple CPU cores utilized |
| If it crashes, service is down | If a worker crashes, others continue |
| Fine for development | Recommended for production |

### Worker Count

A common formula: `workers = 2 * CPU_cores + 1`

```dockerfile
# For a 2-core machine: 2 * 2 + 1 = 5 workers
CMD ["gunicorn", "app.main:app", \
     "--workers", "5", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

Or use environment variables for flexibility:

```dockerfile
ENV WORKERS=4
CMD gunicorn app.main:app --workers $WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Note: When using variable substitution, you must use shell form for CMD. Alternatively, use a startup script.

## Security Scanning

Scan your Docker images for known vulnerabilities:

```bash
# Docker Scout (built into Docker Desktop)
docker scout cves myapp:latest

# Quick overview
docker scout quickview myapp:latest

# Trivy (open source scanner)
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image myapp:latest
```

### Reducing Vulnerabilities

1. **Use slim images:** `python:3.12-slim` has fewer packages = fewer potential vulnerabilities
2. **Multi-stage builds:** Final image has no build tools
3. **Non-root user:** Limits damage if the container is compromised
4. **Update base images regularly:** `docker pull python:3.12-slim` to get security patches

## Environment Variable Configuration

Configure your application through environment variables, not hardcoded values:

```python
# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    debug: bool = False
    workers: int = 4

    model_config = {"env_file": ".env"}


settings = Settings()
```

```yaml
# docker-compose.yml (development)
services:
  api:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret-change-in-production
      - DEBUG=true
```

```bash
# Production (pass via docker run or orchestrator)
docker run -e DATABASE_URL=postgresql://... \
           -e SECRET_KEY=$(cat /run/secrets/api_key) \
           -e DEBUG=false \
           myapp:latest
```

## Production Dockerfile Checklist

```dockerfile
# 1. Multi-stage build
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 2. Minimal runtime image
FROM python:3.12-slim

# 3. Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /code

# 4. Only copy what's needed
COPY --from=builder /install /usr/local
COPY ./app /code/app

# 5. Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

# 6. Switch to non-root user
USER appuser

# 7. Document the port
EXPOSE 8000

# 8. Production server with exec form
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-"]
```

## Key Takeaways

- Always include a `.dockerignore` to exclude `.git`, `.venv`, `.env`, and other unnecessary files
- Combine `RUN` commands to minimize layers and remove temporary files in the same layer
- Add `HEALTHCHECK` to let Docker monitor your application's actual health, not just process status
- Use Gunicorn with Uvicorn workers for production (multiple processes, graceful restarts)
- Scan images for vulnerabilities with Docker Scout or Trivy before deploying
- Configure through environment variables, not hardcoded values or `.env` files in the image
- Follow the production checklist: multi-stage, non-root user, health check, production server
