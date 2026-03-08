# Health Checks

## Why This Matters

On iOS, the App Store review process checks if your app launches, doesn't crash immediately, and responds to user input. On Android, the Play Console runs pre-launch reports that test if your app starts correctly. Both platforms verify that your app is "healthy" before allowing distribution.

In backend infrastructure, health checks serve the same purpose but run continuously. Kubernetes (the most common container orchestration platform) pings your API every few seconds to check if it's alive and ready to handle traffic. If your API fails a health check, Kubernetes automatically restarts it or stops sending traffic to it.

Health checks answer two questions:
1. **Is the process running?** (liveness)
2. **Can it handle requests?** (readiness)

## Liveness vs Readiness

These are Kubernetes concepts, but they apply to any deployment:

### Liveness Probe

**Question:** "Is the process alive and not stuck?"

**What to check:** Can the process respond to an HTTP request at all?

**What happens when it fails:** Kubernetes kills the container and restarts it.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health/live")
async def liveness():
    """Liveness probe -- is the process running?"""
    return {"status": "alive"}
```

That's it. If the process can respond with 200, it's alive. If it can't (deadlock, infinite loop, out of memory), the health check times out and Kubernetes restarts the container.

**Mobile analogy:** When iOS kills a background app that's using too much memory, that's the OS acting as a liveness probe.

### Readiness Probe

**Question:** "Can this instance actually handle user traffic right now?"

**What to check:** Are all dependencies (database, Redis, external services) reachable?

**What happens when it fails:** Kubernetes stops sending traffic to this instance, but does NOT restart it. It waits for the instance to become ready again.

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


async def check_database() -> dict:
    """Check database connectivity."""
    try:
        # Execute a simple query to verify connection
        await db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_redis() -> dict:
    """Check Redis connectivity."""
    try:
        await redis_client.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/health/ready")
async def readiness():
    """Readiness probe -- can we handle traffic?"""
    db_status = await check_database()
    redis_status = await check_redis()

    all_healthy = all(
        check["status"] == "healthy"
        for check in [db_status, redis_status]
    )

    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": {
                "database": db_status,
                "redis": redis_status,
            },
        },
    )
```

**When database is healthy:**
```json
// HTTP 200 OK
{
    "status": "ready",
    "checks": {
        "database": {"status": "healthy"},
        "redis": {"status": "healthy"}
    }
}
```

**When database is down:**
```json
// HTTP 503 Service Unavailable
{
    "status": "not_ready",
    "checks": {
        "database": {"status": "unhealthy", "error": "Connection refused"},
        "redis": {"status": "healthy"}
    }
}
```

## Why Two Separate Endpoints?

| Scenario | Liveness | Readiness | Action |
|----------|----------|-----------|--------|
| App running, DB connected | 200 | 200 | Serve traffic normally |
| App running, DB disconnected | 200 | 503 | Stop sending traffic, wait for DB |
| App frozen / deadlocked | timeout | timeout | Kill and restart the container |
| App starting up, DB not ready yet | 200 | 503 | Wait for readiness before sending traffic |

If you used a single `/health` endpoint that checks the database, a database outage would cause Kubernetes to restart your app. But restarting won't fix the database -- it'll just create a restart loop. Separating liveness and readiness prevents this.

## Complete Implementation

Here's a production-ready health check setup:

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

app = FastAPI()

# Track when the app started (useful for debugging)
APP_START_TIME = datetime.now(timezone.utc).isoformat()


@app.get("/health/live")
async def liveness():
    """Liveness probe.

    Returns 200 if the process is running.
    Kubernetes uses this to detect deadlocked processes.
    """
    return {
        "status": "alive",
        "started_at": APP_START_TIME,
    }


async def check_database() -> dict:
    """Verify database connectivity."""
    try:
        async with db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_redis() -> dict:
    """Verify Redis connectivity."""
    try:
        await redis_client.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_external_api() -> dict:
    """Verify external API is reachable (optional)."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.payment-gateway.com/health",
                timeout=3.0,
            )
            response.raise_for_status()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/health/ready")
async def readiness():
    """Readiness probe.

    Returns 200 if all dependencies are healthy.
    Returns 503 if any dependency is unhealthy.
    Kubernetes uses this to decide whether to send traffic.
    """
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
    }

    all_healthy = all(
        check["status"] == "healthy"
        for check in checks.values()
    )

    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
```

## Health Check Best Practices

### 1. Keep Liveness Simple

The liveness probe should NEVER check external dependencies. If it does, a database outage causes a restart loop:

```python
# BAD: liveness depends on database
@app.get("/health/live")
async def liveness():
    await db.execute("SELECT 1")  # DB down = restart loop
    return {"status": "alive"}

# GOOD: liveness only checks the process itself
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}
```

### 2. Set Timeouts on Dependency Checks

Don't let a slow dependency hang the readiness probe:

```python
import asyncio


async def check_database() -> dict:
    try:
        await asyncio.wait_for(
            db.execute("SELECT 1"),
            timeout=3.0,  # Don't wait more than 3 seconds
        )
        return {"status": "healthy"}
    except asyncio.TimeoutError:
        return {"status": "unhealthy", "error": "Timeout after 3s"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### 3. Don't Expose Internal Details in Production

The detailed error messages above are useful for debugging but may leak information:

```python
@app.get("/health/ready")
async def readiness():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
    }

    all_healthy = all(c["status"] == "healthy" for c in checks.values())

    if all_healthy:
        return {"status": "ready"}
    else:
        # In production, don't expose error details to external callers
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"},
        )
```

Expose detailed health info only on internal networks or behind authentication.

## Docker HEALTHCHECK

Docker also supports health checks in the Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1
```

This tells Docker to check `/health/live` every 30 seconds. If it fails 3 times in a row, Docker marks the container as unhealthy.

## Kubernetes Configuration

When deploying to Kubernetes, you configure probes in the pod spec:

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: api
      image: myapp:latest
      livenessProbe:
        httpGet:
          path: /health/live
          port: 8000
        initialDelaySeconds: 5
        periodSeconds: 10
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8000
        initialDelaySeconds: 10
        periodSeconds: 5
        failureThreshold: 3
```

## Key Takeaways

1. **Liveness checks if the process is alive.** Keep it simple -- just return 200. Never check external dependencies in liveness.
2. **Readiness checks if the process can handle traffic.** Check database, Redis, and any critical dependencies. Return 503 if any are unhealthy.
3. **Separate liveness from readiness.** A database outage shouldn't cause your app to restart -- it should stop receiving traffic until the database recovers.
4. **Use `JSONResponse` to control status codes.** Return 200 for healthy, 503 for unhealthy. The status code is what Kubernetes uses -- the body is for debugging.
5. **Set timeouts on dependency checks.** A slow dependency shouldn't hang your health endpoint. Use `asyncio.wait_for()` with a timeout.
6. **Health checks run continuously in production.** Every 5-30 seconds, your infrastructure pings these endpoints. Make them fast and reliable.
