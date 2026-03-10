# Docker Image Building in CI

## Why This Matters

On iOS, you build an `.ipa` archive through Xcode's Product > Archive flow (or Xcode Cloud does it for you). The archive bundles your compiled binary, assets, and signing profile into a single distributable artifact. On Android, Gradle produces an `.apk` or `.aab` that contains your compiled code, resources, and manifest.

Docker image building is the backend equivalent. Instead of compiling Swift into a binary, you package your Python code, dependencies, and runtime configuration into a Docker image. Instead of uploading to TestFlight, you push the image to a container registry (Docker Hub or GitHub Container Registry). And just like Xcode Cloud automates archive builds, GitHub Actions automates Docker image builds.

The key difference: mobile builds take 15-30 minutes (compilation + code signing). Docker image builds for Python apps take 2-5 minutes. No compilation. No signing certificates. Just layer caching and `pip install`.

## Multi-Stage Docker Builds

A multi-stage build separates "build dependencies" from "runtime dependencies." This is like having a separate build machine that produces a lean artifact -- your final image only contains what the app needs to run.

```dockerfile
# Stage 1: Builder -- install dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime -- copy only what's needed
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY ./app ./app
COPY alembic.ini .
COPY alembic/ ./alembic/

# Non-root user for security
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Why Two Stages?

| Aspect | Single Stage | Multi-Stage |
|--------|-------------|-------------|
| Image size | ~800 MB (includes build tools) | ~250 MB (runtime only) |
| Attack surface | Larger (compilers, headers) | Smaller (just Python + your code) |
| Build cache | Less effective | Builder layer cached separately |
| Mobile analogy | Debug build with symbols | Release build stripped for App Store |

## Building and Pushing in GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            myuser/myapp:latest
            myuser/myapp:${{ github.sha }}
```

### Step by Step

1. **Checkout** -- clones your repository so Docker can access the Dockerfile
2. **Login** -- authenticates with Docker Hub using secrets (never hardcode credentials)
3. **Build and push** -- builds the image and pushes it to the registry in one step

## GitHub Container Registry (GHCR)

Instead of Docker Hub, you can push to GitHub's own registry. The advantage: your images live next to your code, with the same access controls.

```yaml
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push to GHCR
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
```

`GITHUB_TOKEN` is automatically provided by GitHub Actions -- no need to create a separate secret.

## Tagging Strategies

Tags identify which version of your image to deploy. Choose a strategy that works for your team.

| Strategy | Tag Example | When to Use |
|----------|------------|-------------|
| Git SHA | `myapp:a1b2c3d` | Always -- uniquely identifies the exact commit |
| `latest` | `myapp:latest` | Points to most recent build on main |
| Semver | `myapp:1.2.3` | Release-based deployments |
| Branch | `myapp:develop` | Feature branch testing |

**Best practice:** Always tag with the git SHA for traceability, plus `latest` for convenience.

```yaml
      tags: |
        myuser/myapp:latest
        myuser/myapp:${{ github.sha }}
        myuser/myapp:v1.2.3
```

Mobile analogy: Git SHA tags are like build numbers in Xcode (CFBundleVersion). Semver tags are like marketing versions (CFBundleShortVersionString).

## Build Caching

Docker builds are slow when every layer rebuilds from scratch. Caching reuses unchanged layers.

### GitHub Actions Cache

```yaml
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myuser/myapp:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

`type=gha` uses GitHub Actions' built-in cache. First build takes ~3 minutes. Subsequent builds with no dependency changes take ~30 seconds.

### What Gets Cached

```
Layer 1: FROM python:3.12-slim          -- cached (base image)
Layer 2: COPY requirements.txt .        -- cached (unless requirements change)
Layer 3: RUN pip install ...            -- cached (unless requirements change)
Layer 4: COPY ./app ./app               -- rebuilt (code changes every push)
Layer 5: CMD ["uvicorn", ...]           -- cached (rarely changes)
```

This is why `COPY requirements.txt` comes before `COPY ./app` -- it maximizes cache hits. If only your code changes (not dependencies), layers 1-3 are cached and only layer 4 rebuilds.

## Mobile vs Docker Image Build Comparison

| Aspect | Mobile (Xcode Archive) | Backend (Docker Build) |
|--------|----------------------|----------------------|
| Input | Swift/Kotlin source code | Python source + requirements.txt |
| Build tool | xcodebuild / Gradle | docker build |
| Output | .ipa / .aab | Docker image |
| Registry | App Store Connect / Play Console | Docker Hub / GHCR |
| Signing | Code signing certificates | No signing needed |
| Build time | 15-30 minutes | 2-5 minutes |
| Caching | DerivedData | Docker layer cache |
| Versioning | Build number + version | Git SHA + semver tags |
| CI action | xcode-build-action | docker/build-push-action |

## Key Takeaways

- Multi-stage Docker builds separate build dependencies from runtime, producing smaller and more secure images
- `docker/build-push-action@v5` builds and pushes images in one step -- no manual `docker push`
- `docker/login-action@v3` authenticates with Docker Hub or GHCR using repository secrets
- Always tag images with the git SHA for traceability (`myapp:a1b2c3d`)
- Use `cache-from: type=gha` to cache Docker layers between CI runs (30s vs 3min)
- Put `COPY requirements.txt` before `COPY ./app` in your Dockerfile to maximize layer cache hits
- GitHub Container Registry uses `GITHUB_TOKEN` automatically -- no extra secrets to configure
- Docker image builds are the backend equivalent of Xcode archives, but faster and without code signing
