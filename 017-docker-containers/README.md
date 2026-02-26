# Module 017: Docker & Containers

## Why This Module?

Package your API for consistent deployment. Docker ensures "works on my machine" becomes "works everywhere."

## What You'll Learn

- Docker fundamentals
- Writing Dockerfiles
- Docker Compose for multi-service
- Container networking
- Volume management
- Production Docker practices

## Topics

### Theory
1. Container Concepts
2. Dockerfile Best Practices
3. Multi-stage Builds
4. Docker Compose for Development
5. Container Networking
6. Production Optimizations

### Project
Containerize your API with PostgreSQL and Redis.

## Example

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Run
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7
```
