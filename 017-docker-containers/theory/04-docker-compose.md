# Docker Compose

## Why This Matters

In Xcode, a multi-target project lets you build multiple related apps and frameworks together -- the main app, a widget extension, a watch app. You define how they relate in the project settings. Docker Compose is the same idea for containers.

A typical FastAPI application needs multiple services: the API itself, a PostgreSQL database, and maybe Redis for caching. Docker Compose lets you define all of these in a single file and start them with one command. It handles networking between them automatically -- your API can connect to PostgreSQL just by using the service name `db` as the hostname.

## What Is Docker Compose?

Docker Compose is a tool for defining and running multi-container applications. You describe your services in a `docker-compose.yml` file and manage them together.

```bash
# Start all services (use Docker Compose v2 syntax)
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Rebuild and restart
docker compose up -d --build
```

**Important:** Use `docker compose` (v2, space), NOT `docker-compose` (v1, hyphen). Docker Compose v1 is deprecated. v2 is built into Docker CLI.

## Basic docker-compose.yml

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
```

This defines a single service called `api` that:
- Builds from the Dockerfile in the current directory
- Maps port 8000 on your machine to port 8000 in the container
- Sets the `DATABASE_URL` environment variable

## Full Example: FastAPI + PostgreSQL + Redis

```yaml
services:
  # ---- API Service ----
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://appuser:apppass@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key-change-in-production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./app:/code/app  # Bind mount for hot reload in development

  # ---- PostgreSQL Service ----
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ---- Redis Service ----
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/var/lib/redis/data

# Named volumes for data persistence
volumes:
  postgres_data:
  redis_data:
```

### Anatomy of a Service

```yaml
services:
  api:                          # Service name (also its hostname on the Docker network)
    build: .                    # Build from Dockerfile in current directory
    # OR
    image: python:3.12-slim    # Use a pre-built image (mutually exclusive with build)

    ports:
      - "8000:8000"            # host_port:container_port

    environment:               # Environment variables
      - KEY=value              # List syntax
      # OR
      KEY: value               # Map syntax

    depends_on:                # Start order and health dependencies
      db:
        condition: service_healthy  # Wait for db to be healthy
      redis:
        condition: service_started  # Just wait for redis to start

    volumes:
      - ./app:/code/app        # Bind mount (for development)
      - data:/var/data         # Named volume (for persistence)
```

## depends_on with Health Checks

Without health checks, `depends_on` only waits for the container to start -- not for the service inside to be ready. PostgreSQL takes a few seconds to initialize, and your API will crash if it tries to connect before the database is ready.

```yaml
services:
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s      # Check every 5 seconds
      timeout: 5s       # Timeout after 5 seconds
      retries: 5        # Fail after 5 consecutive failures
      start_period: 10s # Give the container 10 seconds to start before checking

  api:
    depends_on:
      db:
        condition: service_healthy  # Wait for healthcheck to pass
```

Mobile analogy: This is like checking that a network service is reachable before making API calls. On iOS, you might use `NWPathMonitor`. Docker Compose uses healthchecks.

## Environment Variables

Three ways to set environment variables:

### 1. Inline in docker-compose.yml

```yaml
services:
  api:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
      - DEBUG=true
```

### 2. From an .env File

```yaml
services:
  api:
    env_file:
      - .env
```

```bash
# .env file
DATABASE_URL=postgresql://user:pass@db:5432/appdb
DEBUG=true
SECRET_KEY=my-secret-key
```

### 3. Compose Variable Substitution

```yaml
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:-defaultpass}
```

The `${DB_PASSWORD:-defaultpass}` syntax reads from the shell environment, falling back to `defaultpass`.

## Common Docker Compose Commands

```bash
# Start services in background
docker compose up -d

# Start with rebuild
docker compose up -d --build

# Stop services (keeps volumes)
docker compose down

# Stop services AND delete volumes (destroys data!)
docker compose down -v

# View running services
docker compose ps

# View logs (follow mode)
docker compose logs -f

# View logs for one service
docker compose logs -f api

# Execute command in a running container
docker compose exec api bash

# Run a one-off command
docker compose run --rm api python -c "print('hello')"

# Restart a single service
docker compose restart api
```

## Development vs Production Compose Files

Use a base file and override for different environments:

```yaml
# docker-compose.yml (base)
services:
  api:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```yaml
# docker-compose.override.yml (automatically loaded -- development overrides)
services:
  api:
    ports:
      - "8000:8000"
    volumes:
      - ./app:/code/app  # Hot reload
    environment:
      - DEBUG=true
```

The override file is automatically loaded when you run `docker compose up`. For production, use an explicit file:

```bash
# Development (loads docker-compose.yml + docker-compose.override.yml)
docker compose up

# Production (loads only the base + production overrides)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Key Takeaways

- Docker Compose defines multi-container applications in a single YAML file
- Use `docker compose` (v2, space) not `docker-compose` (v1, hyphen)
- Services communicate by name: `db` in the compose file = hostname `db` in your connection string
- Always use `healthcheck` with `condition: service_healthy` for databases
- Named volumes persist data across container restarts; bind mounts are for development hot-reload
- Use `.env` files for local configuration, never commit secrets to docker-compose.yml
- Use override files (`docker-compose.override.yml`) for development-specific settings
