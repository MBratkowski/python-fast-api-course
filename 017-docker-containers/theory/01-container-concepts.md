# Container Concepts

## Why This Matters

On iOS, every app runs in its own sandbox -- it has its own file system, its own memory space, and can't touch other apps. On Android, each app gets its own Linux user ID and runs in isolation. You've been building for sandboxed environments your entire career.

Docker containers are the same idea, but for servers. Instead of the OS enforcing the sandbox (like iOS/Android do), you define it yourself. A container packages your application with everything it needs -- Python runtime, libraries, config files -- into an isolated unit that runs the same way everywhere.

The mental model: **a Docker container is an app sandbox you build yourself.**

## What Is a Container?

A container is a lightweight, isolated process that runs on a host machine. It shares the host OS kernel but has its own file system, network, and process space.

```
Host Machine (your laptop or server)
+------------------------------------------+
|  Host OS (macOS / Linux)                 |
|  +----------+  +----------+  +--------+ |
|  |Container1|  |Container2|  |Contain3 | |
|  | FastAPI  |  | Postgres |  | Redis   | |
|  | Python   |  | Data     |  | Cache   | |
|  | Deps     |  | Config   |  | Config  | |
|  +----------+  +----------+  +--------+ |
+------------------------------------------+
```

Each container thinks it's running on its own machine, but they all share the same OS kernel.

## Containers vs Virtual Machines

You might have used VMs (Virtual Machines) before -- tools like Parallels or VMware on macOS. Containers are different.

| Aspect | Virtual Machine | Container |
|--------|----------------|-----------|
| What's virtualized | Entire OS (kernel + userspace) | Only userspace (shares host kernel) |
| Size | Gigabytes (full OS image) | Megabytes (just app + dependencies) |
| Startup time | Minutes | Seconds |
| Resource usage | Heavy (runs full OS) | Light (just the process) |
| Isolation | Complete (separate kernel) | Process-level (shared kernel) |
| Mobile analogy | Running Android emulator on Mac | Running an app in iOS Simulator |

**The key insight:** Containers are not tiny VMs. They're isolated processes that share the host's OS kernel. This is why they start in seconds, not minutes.

## Docker Architecture

Docker has three core concepts:

### 1. Images

An image is a read-only template that contains everything needed to run your application. Think of it like an `.ipa` or `.aab` file -- it's the packaged artifact.

```
Docker Image (read-only)
+---------------------+
| Layer 5: COPY ./app |  <-- Your application code
| Layer 4: RUN pip    |  <-- Installed dependencies
| Layer 3: COPY req   |  <-- requirements.txt
| Layer 2: WORKDIR    |  <-- Working directory set
| Layer 1: python:3.12|  <-- Base image (Python runtime)
+---------------------+
```

Images are built from **layers**. Each instruction in a Dockerfile creates a layer. Layers are cached -- if nothing changed in a layer, Docker reuses it from cache.

### 2. Containers

A container is a running instance of an image. If an image is like an `.ipa` file, a container is like the app actually running on a phone.

```bash
# Create and start a container from an image
docker run myapp:latest

# You can run multiple containers from the same image
docker run --name api-1 myapp:latest
docker run --name api-2 myapp:latest
```

Multiple containers from the same image are like multiple users installing the same app -- each gets their own data and state.

### 3. Registry

A registry is where you store and distribute images. Think of it like the App Store or Play Console.

| Registry | Purpose | Mobile Equivalent |
|----------|---------|-------------------|
| Docker Hub | Public/private image hosting | App Store / Play Console |
| GitHub Container Registry (GHCR) | GitHub-integrated hosting | TestFlight / Firebase App Distribution |
| Amazon ECR | AWS-integrated hosting | Enterprise distribution |
| Local registry | Development only | Running on simulator |

## Why Containers for Backend Development?

### Problem: "It Works on My Machine"

Without containers, deploying a FastAPI app means:
1. Install the right Python version on the server
2. Install system dependencies (libpq for PostgreSQL, etc.)
3. Create a virtual environment
4. Install pip packages
5. Configure environment variables
6. Hope everything matches your development setup

With containers:
1. Build an image (once)
2. Run it anywhere

### Problem: Multiple Services

A typical FastAPI application needs:
- Python runtime for your API
- PostgreSQL for the database
- Redis for caching
- Maybe Celery workers for background tasks

Without containers, you install all of these on the same machine and manage conflicts. With containers, each service runs in isolation with its own dependencies.

### Problem: Consistent Environments

On mobile, Xcode and Android Studio handle environment consistency. You don't worry about "which Swift runtime is on this phone?" -- the app bundles what it needs.

Docker gives you the same guarantee for servers. Your Docker image contains the exact Python version, exact library versions, and exact configuration. It runs identically on your laptop, in CI, and in production.

## Docker CLI Basics

```bash
# Check Docker is installed
docker --version

# Pull an image from Docker Hub
docker pull python:3.12-slim

# List local images
docker images

# Run a container (interactive, with terminal)
docker run -it python:3.12-slim python
# You're now inside a Python shell running in a container!

# Run a container in the background (detached)
docker run -d --name my-api -p 8000:8000 myapp:latest

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container logs
docker logs my-api

# Stop a container
docker stop my-api

# Remove a container
docker rm my-api

# Remove an image
docker rmi myapp:latest
```

## The Container Lifecycle

```
Dockerfile --> docker build --> Image --> docker run --> Container
   (recipe)     (build step)   (artifact)  (launch)     (running app)

Mobile equivalent:
Xcode project --> Archive --> .ipa --> Install --> Running app
```

1. **Write a Dockerfile** -- Define what goes into your image (like configuring an Xcode scheme)
2. **Build an image** -- Docker executes each instruction and creates layers (like archiving in Xcode)
3. **Run a container** -- Docker creates an isolated process from the image (like launching the app)
4. **Stop/remove** -- Clean up when done (like killing the app process)

## Key Takeaways

- Containers are isolated processes that share the host OS kernel -- they are not VMs
- Docker images are layered, read-only templates (like `.ipa`/`.aab` bundles)
- Containers are running instances of images (like an app running on a device)
- Registries store and distribute images (like the App Store/Play Console)
- Containers solve "works on my machine" by packaging everything the app needs
- The Docker workflow is: Dockerfile -> `docker build` -> image -> `docker run` -> container
