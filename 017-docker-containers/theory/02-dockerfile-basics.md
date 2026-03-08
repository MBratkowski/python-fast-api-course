# Dockerfile Basics

## Why This Matters

On iOS, you configure your build with Xcode schemes -- which targets to build, which signing certificate to use, which entitlements to include. On Android, `build.gradle` defines dependencies, build types, and packaging rules.

A Dockerfile is the backend equivalent. It's a text file that tells Docker exactly how to build your application image: what base to start from, what to install, what to copy in, and how to run it. Master the Dockerfile and you control your deployment artifact completely.

## Dockerfile Syntax

A Dockerfile is a sequence of instructions, each creating a layer in the final image. Instructions are executed top to bottom.

```dockerfile
# Comment -- starts with #
INSTRUCTION arguments
```

### The Essential Instructions

#### FROM -- Choose Your Base Image

Every Dockerfile starts with `FROM`. It defines the base image you're building on.

```dockerfile
# Use the official Python 3.12 slim image (Debian-based, minimal)
FROM python:3.12-slim
```

**Always use `python:3.12-slim`** -- not the full `python:3.12` image (which includes build tools you don't need) and not the deprecated `tiangolo/uvicorn-gunicorn-fastapi` image.

| Base Image | Size | Use Case |
|-----------|------|----------|
| `python:3.12` | ~1 GB | When you need C compilers for building packages |
| `python:3.12-slim` | ~150 MB | Production (recommended) |
| `python:3.12-alpine` | ~50 MB | Smallest, but can have compatibility issues with some Python packages |

#### WORKDIR -- Set the Working Directory

Sets the working directory for subsequent instructions. Like `cd` but creates the directory if it doesn't exist.

```dockerfile
WORKDIR /code
```

All subsequent `COPY`, `RUN`, and `CMD` instructions execute relative to this directory.

#### COPY -- Add Files to the Image

Copies files from your local machine into the image.

```dockerfile
# Copy a single file
COPY ./requirements.txt /code/requirements.txt

# Copy a directory
COPY ./app /code/app

# Copy everything (usually NOT what you want -- see .dockerignore)
COPY . /code/
```

#### RUN -- Execute Commands During Build

Runs a command during the build process. The result becomes a new layer.

```dockerfile
# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Install system packages (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

**Note:** `--no-cache-dir` prevents pip from caching downloaded packages in the image, keeping it smaller.

#### CMD -- Define the Default Command

Specifies what runs when a container starts. There can only be one `CMD` per Dockerfile (the last one wins).

```dockerfile
# CORRECT: Exec form (always use this)
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]

# WRONG: Shell form (never use this for production)
CMD fastapi run app/main.py --port 8000
```

**Always use exec form** (the JSON array syntax). Shell form wraps your command in `/bin/sh -c`, which:
- Prevents graceful shutdown (SIGTERM goes to shell, not your app)
- Breaks FastAPI's lifespan events (startup/shutdown don't fire)
- Causes `docker stop` to wait 10 seconds then force-kill

Mobile analogy: exec form is like launching your app directly. Shell form is like launching a terminal that launches your app -- the terminal intercepts all OS signals.

#### EXPOSE -- Document the Port

Documents which port the container listens on. This is metadata only -- it doesn't actually publish the port.

```dockerfile
EXPOSE 8000
```

To actually make the port accessible, use `-p` when running: `docker run -p 8000:8000 myapp`.

## Layer Caching Strategy

This is the single most important optimization for Docker builds. Docker caches each layer and reuses it if nothing changed.

**The rule:** Put things that change rarely at the top, things that change often at the bottom.

### Bad: Invalidates Cache on Every Code Change

```dockerfile
FROM python:3.12-slim
WORKDIR /code

# BAD: Copying everything first means ANY file change
# invalidates the pip install cache
COPY . /code/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

Every time you change a single line of Python code, Docker reinstalls all dependencies. This can take minutes.

### Good: Cache Dependencies Separately

```dockerfile
FROM python:3.12-slim
WORKDIR /code

# GOOD: Copy requirements.txt FIRST (changes rarely)
COPY ./requirements.txt /code/requirements.txt

# GOOD: Install dependencies (cached unless requirements.txt changes)
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# GOOD: Copy application code LAST (changes often)
COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

Now when you change application code, Docker reuses the cached dependency layer. The build only copies new code and restarts -- taking seconds instead of minutes.

Mobile analogy: This is like how Xcode caches compiled Swift modules. If you only change one file, it doesn't recompile the entire project. Docker works the same way with layers.

## Complete Dockerfile Example

```dockerfile
# Use official Python slim image (NOT the deprecated tiangolo image)
FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Install dependencies first (layer caching)
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code
COPY ./app /code/app

# Document the port (informational)
EXPOSE 8000

# Run with exec form for graceful shutdown
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

## Building and Running

```bash
# Build the image (. means "use current directory as build context")
docker build -t myapp:latest .

# Run the container
docker run -d --name my-api -p 8000:8000 myapp:latest

# Visit http://localhost:8000/docs to see your API

# View logs
docker logs -f my-api

# Stop and remove
docker stop my-api && docker rm my-api
```

### Build Context

The `.` at the end of `docker build -t myapp .` specifies the **build context** -- the directory Docker sends to the build daemon. All `COPY` instructions are relative to this context.

```bash
# Build with current directory as context
docker build -t myapp .

# Build with a specific directory
docker build -t myapp ./backend

# Build with a specific Dockerfile
docker build -t myapp -f deploy/Dockerfile .
```

## Environment Variables

Pass configuration to your container at runtime:

```dockerfile
# Set default environment variables in Dockerfile
ENV APP_ENV=production
ENV LOG_LEVEL=info

# These can be overridden at runtime
# docker run -e APP_ENV=development myapp
```

```bash
# Override at runtime
docker run -e DATABASE_URL=postgresql://... -e SECRET_KEY=mysecret myapp

# Or use an env file
docker run --env-file .env myapp
```

**Never put secrets in the Dockerfile** -- they become part of the image layers and are visible with `docker history`. Always pass secrets at runtime with `-e` or `--env-file`.

## Key Takeaways

- Always use `python:3.12-slim` as base image -- not the deprecated tiangolo image
- Layer caching is critical: copy `requirements.txt` first, then install deps, then copy app code
- Always use exec-form CMD `["command", "args"]` -- shell form prevents graceful shutdown
- `EXPOSE` is documentation only -- use `-p` flag to actually publish ports
- Never put secrets in the Dockerfile -- pass them at runtime with `-e`
- Each Dockerfile instruction creates a layer -- order them from least-changing to most-changing
