# Module 017: Docker and Containers

## Why This Module?

As a mobile developer, you build an app, archive it, and submit the `.ipa` or `.aab` bundle to the App Store or Play Console. The app runs in a sandboxed environment the OS provides. Backend development has a similar concept: containers. Instead of shipping a binary to an app store, you package your entire application -- code, dependencies, runtime -- into a Docker image and deploy it anywhere.

The difference is that on mobile, Apple and Google define the sandbox. On the backend, you define it yourself with a Dockerfile. This module teaches you how.

## What You'll Learn

- What containers are and how they compare to mobile app packaging
- Writing Dockerfiles for FastAPI applications with proper layer caching
- Multi-stage builds to minimize production image size
- Docker Compose for multi-container setups (API + PostgreSQL + Redis)
- Docker networking and volume management
- Production optimizations (security scanning, health checks, Gunicorn)

## Mobile Developer Context

You already understand packaging and distribution. Docker is the backend equivalent.

**Docker Across Platforms:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Package format | `.ipa` bundle | `.apk` / `.aab` bundle | Docker image |
| Dependency management | Swift Package Manager | Gradle dependencies | `requirements.txt` + `pip install` |
| Build config | Xcode schemes | `build.gradle` | Dockerfile |
| Multi-env builds | Debug/Release configurations | `buildTypes` (debug/release) | Multi-stage builds (builder/runtime) |
| Distribution | App Store Connect | Google Play Console | Docker Hub / GitHub Container Registry |
| App sandbox | iOS sandbox (automatic) | Android sandbox (automatic) | Container isolation (you configure it) |

**Key Differences from Mobile:**
- On mobile, the OS provides the sandbox. With Docker, you define the sandbox yourself
- On mobile, dependencies are compiled into the binary. With Docker, dependencies are installed in layers (and cached)
- On mobile, you have one target device (phone). With Docker, you can run the same image on any Linux machine

## Prerequisites

- [ ] Docker Desktop installed ([docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/))
- [ ] Basic terminal/CLI skills (Module 001)
- [ ] A working FastAPI application (Modules 003-005)
- [ ] Understanding of `requirements.txt` and virtual environments (Module 001)

## Topics

### Theory
1. Container Concepts -- What containers are, Docker architecture, images vs containers
2. Dockerfile Basics -- FROM, WORKDIR, COPY, RUN, CMD, EXPOSE with layer caching
3. Multi-Stage Builds -- Builder pattern for smaller, more secure production images
4. Docker Compose -- Multi-container orchestration for local development
5. Networking and Volumes -- Service discovery, data persistence, volume types
6. Production Optimizations -- .dockerignore, health checks, Gunicorn, security

### Exercises
1. Write a Dockerfile -- Build a proper Dockerfile for a FastAPI app
2. Docker Compose Setup -- Configure multi-container orchestration
3. Multi-Stage Build -- Create an optimized production image

### Project
Containerize a complete FastAPI API with PostgreSQL and Redis using Docker Compose.

## Time Estimate

- Theory: ~90 minutes
- Exercises: ~45 minutes
- Project: ~90 minutes

## Example

```dockerfile
# A complete Dockerfile for FastAPI
FROM python:3.12-slim

WORKDIR /code

# Cache dependencies (this layer only rebuilds when requirements.txt changes)
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code (this layer rebuilds on every code change)
COPY ./app /code/app

# Use exec form for graceful shutdown support
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```
