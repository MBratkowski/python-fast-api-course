# Redis as Message Broker

## Why This Matters

On mobile, task queues use local storage -- WorkManager stores tasks in a Room database, BGTaskScheduler uses the system's internal scheduling. There's no need for an external message broker because everything runs on one device.

On the backend, your API server and your task workers are **separate processes** (often on separate machines). They need a shared message queue to communicate. Redis is the most popular choice for this role -- it's fast, simple, and you'll use it for caching too (Module 014).

## Broker vs Backend

Redis serves two distinct roles in a Celery setup:

```
┌───────────┐     task message     ┌───────────┐     picks up task     ┌───────────┐
│  FastAPI   │────────────────────→│   Redis    │────────────────────→  │  Celery   │
│  App       │                     │  (Broker)  │                       │  Worker   │
│            │                     │  DB 0      │                       │           │
└───────────┘                      └───────────┘                        └─────┬─────┘
                                                                              │
                                   ┌───────────┐     stores result      │
                                   │   Redis    │←────────────────────────────┘
                                   │ (Backend)  │
                                   │  DB 1      │
                                   └───────────┘
```

| Role | What It Does | Redis DB | Example URL |
|------|-------------|----------|-------------|
| **Broker** | Stores task messages waiting to be picked up | DB 0 | `redis://localhost:6379/0` |
| **Backend** | Stores task results after execution | DB 1 | `redis://localhost:6379/1` |

Using separate Redis databases (0 and 1) keeps broker messages and results isolated.

## Why Redis (vs RabbitMQ)

| Feature | Redis | RabbitMQ |
|---------|-------|----------|
| Setup complexity | Minimal (single binary) | More complex (Erlang runtime) |
| Dual-purpose | Also a cache (Module 014) | Only a message broker |
| Performance | Excellent for small-medium queues | Better for very high-volume queues |
| Persistence | Optional (RDB/AOF) | Built-in (durable queues) |
| Message routing | Basic | Advanced (exchanges, bindings) |
| Learning curve | Low | Medium |
| Docker image size | ~30 MB | ~180 MB |

**For most projects, Redis is the right choice.** You already need it for caching, it's simple to set up, and it handles task queuing well. Use RabbitMQ only if you need advanced message routing or guaranteed delivery for millions of messages per second.

## Docker Compose Setup

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes  # Enable persistence
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  redis_data:
```

```bash
# Start Redis
docker-compose up -d redis

# Verify it's running
docker-compose exec redis redis-cli ping
# Output: PONG
```

## Redis URL Format

```
redis://[password@]host:port/db_number

# Examples:
redis://localhost:6379/0          # Local, no password, DB 0
redis://localhost:6379/1          # Local, no password, DB 1
redis://:mypassword@localhost:6379/0  # With password
redis://redis-server:6379/0      # Docker service name

# With SSL (production)
rediss://user:password@redis-host:6380/0
```

## Celery Configuration with Redis

```python
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",   # Broker: DB 0
    backend="redis://localhost:6379/1"   # Backend: DB 1
)

# Or use environment variables (recommended for production)
import os

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
)
```

## Connection Configuration

```python
celery_app.conf.update(
    # Broker connection
    broker_connection_retry_on_startup=True,   # Retry if Redis not ready
    broker_connection_max_retries=10,           # Max connection retries

    # Broker transport options
    broker_transport_options={
        "visibility_timeout": 3600,   # Re-queue if not ack'd in 1 hour
        "max_retries": 3,             # Retry delivery 3 times
    },

    # Result backend
    result_expires=3600,              # Results expire after 1 hour
    result_backend_transport_options={
        "retry_policy": {
            "timeout": 5.0            # Backend connection timeout
        }
    }
)
```

## Monitoring with Flower

Flower is a web dashboard for monitoring Celery tasks -- like Android's WorkManager Inspector, but for production.

```bash
# Install
pip install flower

# Start Flower (connects to same broker)
celery -A celery_config.celery_app flower --port=5555

# Open http://localhost:5555
```

Flower shows:
- Active/completed/failed tasks
- Worker status and resource usage
- Task execution times and success rates
- Real-time task progress

## Verifying the Setup

```python
# verify_redis.py
import redis

# Test direct Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)
r.ping()  # Returns True if connected
print("Redis connection: OK")

# Test Celery connection
from celery_config import celery_app
inspector = celery_app.control.inspect()
print(f"Active workers: {inspector.active()}")
```

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Celery+Redis |
|---------|-----------|----------------|---------------------|
| Task storage | System internal | Room database | Redis (external) |
| Message format | System internal | Serialized `Data` | JSON (configurable) |
| Broker setup | None (system manages) | None (system manages) | Redis Docker container |
| Multiple workers | Single device | Single device | Multiple servers |
| Monitoring | Xcode console | WorkManager Inspector | Flower dashboard |
| Persistence | System-managed | Automatic (Room) | Redis AOF/RDB |

## Production Considerations

### Environment Variables

```bash
# .env
CELERY_BROKER_URL=redis://:password@redis-host:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis-host:6379/1
```

### Redis Memory Limits

```yaml
# docker-compose.yml (production)
services:
  redis:
    image: redis:7-alpine
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """Check Redis and Celery worker health."""
    try:
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    return {
        "redis": "ok" if redis_ok else "down",
        "api": "ok"
    }
```

## Key Takeaways

- Redis serves dual duty: message broker (task queue) and result backend
- Use separate Redis databases for broker (DB 0) and backend (DB 1)
- Docker Compose is the simplest way to run Redis locally
- Use environment variables for Redis URLs in production
- Flower provides a web dashboard for monitoring Celery tasks
- Redis is simpler than RabbitMQ and covers most use cases
- Cross-reference Module 014 for using Redis as a cache (same server, different purpose)
- Mobile parallel: Redis replaces the system-managed task persistence that WorkManager/BGTaskScheduler provide
