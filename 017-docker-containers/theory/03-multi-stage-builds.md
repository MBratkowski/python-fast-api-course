# Multi-Stage Builds

## Why This Matters

In iOS development, your Debug build includes debug symbols, logging frameworks, and development tools. Your Release build strips all of that out -- it's smaller, faster, and more secure. You would never ship a Debug build to the App Store.

Docker multi-stage builds are the same concept. The "builder" stage installs everything needed to compile and set up your app. The "runtime" stage copies only what's needed to run it. The result: smaller images, fewer security vulnerabilities, and faster deployments.

## The Problem with Single-Stage Builds

A single-stage Dockerfile includes everything used during the build process in the final image:

```dockerfile
# Single stage -- everything stays in the final image
FROM python:3.12-slim

WORKDIR /code

# This installs pip, wheel, setuptools, build tools...
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

This works, but the final image contains:
- pip itself (not needed at runtime)
- Cached build artifacts
- Any build dependencies that were pulled in

## Multi-Stage Build Pattern

Use two `FROM` statements to create separate stages:

```dockerfile
# ==========================================
# Stage 1: Builder -- install dependencies
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

# Install to a custom prefix so we can copy just the installed packages
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# Stage 2: Runtime -- copy only what's needed
# ==========================================
FROM python:3.12-slim

# Create a non-root user (security best practice)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /code

# Copy ONLY the installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY ./app /code/app

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

### How It Works

1. **Stage 1 (builder):** Installs all Python packages into `/install`
2. **Stage 2 (runtime):** Starts fresh from `python:3.12-slim`, copies only the installed packages
3. **Result:** The final image has no pip cache, no build tools, no intermediate files

### Size Comparison

| Build Type | Typical Image Size | Contents |
|-----------|-------------------|----------|
| Single stage | ~250 MB | Python + pip + deps + build artifacts + app |
| Multi-stage | ~180 MB | Python + deps + app (no pip, no build artifacts) |
| Multi-stage + compiled deps | ~300 MB vs ~200 MB | Savings even larger with C extensions |

The savings are more dramatic when your dependencies include packages that need C compilation (like `psycopg2`, `cryptography`, or `Pillow`).

## Non-Root User

By default, containers run as root. This is a security risk -- if an attacker breaks into your container, they have root access.

```dockerfile
# Create a system group and user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# ... copy files ...

# Switch to the non-root user
USER appuser
```

Mobile analogy: On iOS, apps run with restricted privileges (no root access to the filesystem). Running containers as non-root follows the same principle of least privilege.

### Key Points About Non-Root Users

```dockerfile
# Create user BEFORE copying files
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy files (owned by root, readable by all -- this is fine)
COPY --from=builder /install /usr/local
COPY ./app /code/app

# If your app needs to write to a directory, set ownership:
RUN mkdir -p /code/uploads && chown appuser:appuser /code/uploads

# Switch to non-root user AFTER all RUN commands that need root
USER appuser
```

## Real-World Example: FastAPI with PostgreSQL Dependencies

```dockerfile
# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.12-slim

# Install ONLY runtime dependency (libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /code

# Copy installed Python packages
COPY --from=builder /install /usr/local

# Copy application
COPY ./app /code/app

USER appuser
EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

Notice:
- **Builder stage** has `gcc` and `libpq-dev` (needed to compile psycopg2)
- **Runtime stage** only has `libpq5` (the runtime library psycopg2 needs)
- The compiler (`gcc`) is NOT in the final image

## Debugging Multi-Stage Builds

You can build up to a specific stage for debugging:

```bash
# Build only the builder stage
docker build --target builder -t myapp-builder .

# Inspect what's in the builder stage
docker run -it myapp-builder /bin/bash

# Build the full image (both stages)
docker build -t myapp .
```

## When to Use Multi-Stage Builds

| Scenario | Single Stage | Multi-Stage |
|----------|-------------|-------------|
| Quick prototyping | Use this | Overkill |
| Production deployment | Too large | Use this |
| Dependencies need compilation | Image bloat | Eliminates build tools |
| Security scanning required | More vulnerabilities | Smaller attack surface |
| CI/CD pipeline | Slower pushes | Faster pushes |

## Key Takeaways

- Multi-stage builds separate the build environment from the runtime environment (like Debug vs Release builds)
- Use `AS builder` to name stages and `COPY --from=builder` to copy between them
- The final image only contains what was explicitly copied from builder stages
- Always create a non-root user with `groupadd`/`useradd` and switch with `USER`
- Install build tools (gcc, dev headers) only in the builder stage; install runtime libraries in the final stage
- Use `--target` to build specific stages for debugging
- Multi-stage builds reduce image size, improve security, and speed up deployments
