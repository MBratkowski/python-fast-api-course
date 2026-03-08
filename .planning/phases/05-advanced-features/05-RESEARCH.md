# Phase 05: Advanced Features - Research

**Researched:** 2026-03-08
**Domain:** Background tasks, Redis caching, file uploads, WebSockets in FastAPI
**Confidence:** HIGH

## Summary

This research covers four advanced FastAPI features: background task processing (Module 013), Redis caching (Module 014), file uploads and storage (Module 015), and WebSocket real-time communication (Module 016). These are production-critical patterns that mobile developers encounter when building backend services.

FastAPI provides built-in support for all four domains. BackgroundTasks handles lightweight post-response work, while Celery with Redis broker handles heavy distributed task processing. Redis serves dual duty as both a Celery broker and a caching layer with TTL and invalidation patterns. FastAPI's UploadFile provides memory-efficient file handling with spooled temporary files, and the WebSocket support includes a clean accept/receive/send lifecycle with a well-documented ConnectionManager pattern for broadcasting.

The ecosystem is mature and stable across all four modules. Celery 5.6.x is the undisputed task queue standard. redis-py 5.x+ (with built-in async via `redis.asyncio`) replaces the deprecated aioredis. File uploads use FastAPI's built-in UploadFile with optional python-magic for content validation. WebSocket support is built into FastAPI/Starlette with no additional dependencies needed.

**Primary recommendation:** Use FastAPI's built-in BackgroundTasks for simple tasks, Celery 5.6+ with Redis broker for heavy/distributed work. Use redis-py (not aioredis) for caching with `redis.asyncio` for async operations. Use UploadFile with content-type and magic-number validation for file uploads. Use FastAPI's built-in WebSocket support with ConnectionManager pattern for real-time features. Follow established module patterns from Phases 1-4: 6 theory files, 3 exercise files with embedded pytest tests, 1 project README.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FEAT-01 | Module 013 -- Background Tasks & Queues: 6 theory files (when to use, FastAPI BackgroundTasks, Celery setup, Redis broker, retries/errors, scheduled tasks), 3 exercises (background tasks, Celery tasks, retry logic), 1 project (email notification system) | FastAPI BackgroundTasks official docs, Celery 5.6.x with autoretry_for/retry_backoff, Redis as broker pattern, Celery Beat for scheduling |
| FEAT-02 | Module 014 -- Caching with Redis: 6 theory files (why cache, Redis setup, caching patterns, TTL/expiration, cache invalidation, data structures), 3 exercises (basic caching, TTL management, invalidation), 1 project (caching layer for API) | redis-py 5.x+ with redis.asyncio, cache-aside pattern, TTL management, tag-based invalidation, Redis data structures (strings, hashes, sets, sorted sets) |
| FEAT-03 | Module 015 -- File Uploads & Storage: 6 theory files (UploadFile, validation, local storage, S3 integration, presigned URLs, image processing), 3 exercises (file upload endpoint, validation, storage patterns), 1 project (file upload service) | FastAPI UploadFile official docs, content-type + magic-number validation, shutil.copyfileobj for streaming, boto3 presigned URLs, Pillow for image processing |
| FEAT-04 | Module 016 -- WebSockets & Real-Time: 6 theory files (WebSocket vs HTTP, FastAPI WebSocket, connection manager, broadcasting/rooms, WS auth, scaling with Redis), 3 exercises (basic WebSocket, connection manager, broadcasting), 1 project (real-time notification system) | FastAPI WebSocket official docs, ConnectionManager pattern, WebSocketDisconnect handling, Redis Pub/Sub for scaling, query-param/cookie auth for WS |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI BackgroundTasks | built-in | Simple post-response tasks | Built into FastAPI, no setup needed, handles async and sync functions |
| Celery | 5.6+ | Distributed task queue | Industry standard for Python task queues, retries, scheduling, monitoring |
| redis-py | 5.0+ | Redis client (sync + async) | Official Redis client, includes redis.asyncio (replaces deprecated aioredis) |
| FastAPI UploadFile | built-in | File upload handling | Built into FastAPI, spooled temp files, memory-efficient |
| FastAPI WebSocket | built-in | Real-time communication | Built into FastAPI/Starlette, clean async interface |
| boto3 | 1.35+ | AWS S3 integration | Official AWS SDK for Python, presigned URLs |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| celery[redis] | 5.6+ | Celery with Redis deps | Installing Celery with Redis broker/backend support |
| python-magic | 0.4+ | File type detection | Validating file content by magic numbers (requires libmagic) |
| filetype | 1.2+ | File type detection | Lightweight alternative to python-magic (no system deps) |
| Pillow | 10.0+ | Image processing | Resizing, thumbnails, format conversion |
| aiofiles | 24.1+ | Async file I/O | Writing uploaded files to disk asynchronously |
| flower | 2.0+ | Celery monitoring | Web dashboard for Celery task monitoring |
| fakeredis | 2.0+ | Redis testing mock | Testing Redis operations without a real Redis server |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Celery | Dramatiq, Huey, ARQ | Celery has largest ecosystem and community; others are lighter but less documented |
| redis-py | aioredis | aioredis is deprecated, merged into redis-py 4.2+ |
| python-magic | filetype | python-magic requires libmagic system dependency; filetype is pure Python but less comprehensive |
| boto3 (S3) | MinIO Python SDK | MinIO SDK works with S3-compatible storage; boto3 is more universal for AWS |
| Pillow | Wand (ImageMagick) | Pillow is lighter, more common; Wand offers more advanced processing |

**Installation:**
```bash
# Module 013: Background Tasks
pip install celery[redis]>=5.6.0 flower>=2.0.0

# Module 014: Caching
pip install redis>=5.0.0

# Module 015: File Uploads
pip install python-magic>=0.4.27 Pillow>=10.0.0 aiofiles>=24.1.0 boto3>=1.35.0

# Module 016: WebSockets (no extra deps needed)
# FastAPI includes WebSocket support via Starlette

# Testing
pip install fakeredis>=2.0.0
```

## Architecture Patterns

### Recommended Project Structure

```
013-background-tasks/
├── theory/
│   ├── 01-when-to-use-background-tasks.md
│   ├── 02-fastapi-background-tasks.md
│   ├── 03-celery-setup-configuration.md
│   ├── 04-redis-as-broker.md
│   ├── 05-retries-error-handling.md
│   └── 06-scheduled-tasks-celery-beat.md
├── exercises/
│   ├── 01_background_tasks.py
│   ├── 02_celery_tasks.py
│   └── 03_retry_logic.py
├── project/
│   └── README.md
└── README.md

014-caching-redis/
├── theory/
│   ├── 01-why-cache.md
│   ├── 02-redis-setup.md
│   ├── 03-caching-patterns.md
│   ├── 04-ttl-expiration.md
│   ├── 05-cache-invalidation.md
│   └── 06-redis-data-structures.md
├── exercises/
│   ├── 01_basic_caching.py
│   ├── 02_ttl_management.py
│   └── 03_cache_invalidation.py
├── project/
│   └── README.md
└── README.md

015-file-uploads/
├── theory/
│   ├── 01-upload-file-basics.md
│   ├── 02-file-validation.md
│   ├── 03-local-storage.md
│   ├── 04-s3-integration.md
│   ├── 05-presigned-urls.md
│   └── 06-image-processing.md
├── exercises/
│   ├── 01_file_upload.py
│   ├── 02_file_validation.py
│   └── 03_storage_patterns.py
├── project/
│   └── README.md
└── README.md

016-websockets/
├── theory/
│   ├── 01-websocket-vs-http.md
│   ├── 02-fastapi-websocket.md
│   ├── 03-connection-manager.md
│   ├── 04-broadcasting-rooms.md
│   ├── 05-websocket-authentication.md
│   └── 06-scaling-redis-pubsub.md
├── exercises/
│   ├── 01_basic_websocket.py
│   ├── 02_connection_manager.py
│   └── 03_broadcasting.py
├── project/
│   └── README.md
└── README.md
```

### Pattern 1: FastAPI BackgroundTasks

**What:** Lightweight post-response task execution built into FastAPI
**When to use:** Simple tasks like sending emails, writing logs, updating caches after response

**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_notification(email: str, message: str = ""):
    """Background task function (sync or async)."""
    with open("log.txt", mode="w") as f:
        f.write(f"notification for {email}: {message}")

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_notification, email, message="Welcome!")
    return {"message": "Notification sent in the background"}
```

### Pattern 2: Celery Task with Retry Logic

**What:** Distributed task queue with automatic retries and exponential backoff
**When to use:** Heavy processing, tasks needing persistence, retries, or horizontal scaling

**Example:**
```python
# Source: https://docs.celeryq.dev/en/stable/userguide/tasks.html
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,        # Exponential: 1s, 2s, 4s, 8s...
    retry_backoff_max=600,     # Max 10 minutes between retries
    retry_jitter=True,         # Random jitter to prevent thundering herd
    max_retries=5
)
def send_email(self, to: str, subject: str, body: str):
    """Send email with automatic retry on network errors."""
    # self.request.retries gives current retry count
    print(f"Attempt {self.request.retries + 1} of {self.max_retries + 1}")
    send_smtp_email(to, subject, body)

# Manual retry with custom countdown
@celery_app.task(bind=True, max_retries=3)
def process_upload(self, file_id: int):
    try:
        do_heavy_processing(file_id)
    except ProcessingError as exc:
        self.retry(exc=exc, countdown=60)  # Retry in 60 seconds
```

### Pattern 3: Redis Cache-Aside Pattern

**What:** Check cache first, fall back to database, store result in cache
**When to use:** Read-heavy endpoints where data doesn't change frequently

**Example:**
```python
# Source: redis-py docs + FastAPI patterns
import json
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379")

async def get_user_cached(user_id: int) -> dict:
    """Cache-aside pattern with TTL."""
    cache_key = f"user:{user_id}"

    # 1. Check cache
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss - fetch from database
    user = await db.get_user(user_id)
    if user:
        # 3. Store in cache with TTL
        await redis_client.setex(
            cache_key,
            3600,  # TTL: 1 hour
            json.dumps(user.dict())
        )
    return user

async def update_user(user_id: int, data: dict) -> dict:
    """Invalidate cache on write."""
    user = await db.update_user(user_id, data)
    # Delete cached version
    await redis_client.delete(f"user:{user_id}")
    return user
```

### Pattern 4: File Upload with Validation

**What:** Accept file uploads with content-type and size validation
**When to use:** Any endpoint accepting file uploads from clients

**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/request-files/
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}

@app.post("/upload/")
async def upload_file(file: UploadFile):
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type {file.content_type} not allowed")

    # Validate file size (read in chunks)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 5MB)")

    # Reset file position after reading
    await file.seek(0)

    # Save to disk
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"filename": file.filename, "size": len(contents)}
```

### Pattern 5: WebSocket ConnectionManager

**What:** Manage active WebSocket connections with connect/disconnect/broadcast
**When to use:** Any real-time feature requiring message distribution

**Example:**
```python
# Source: https://fastapi.tiangolo.com/advanced/websockets/
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

### Anti-Patterns to Avoid

- **Using BackgroundTasks for heavy computation:** BackgroundTasks runs in the same process; use Celery for CPU-intensive or long-running work
- **Hardcoding Redis URLs:** Use environment variables and configuration classes
- **Caching without TTL:** Always set expiration to prevent stale data accumulation
- **Trusting file extensions for validation:** Extensions can be spoofed; validate content-type and magic numbers
- **Reading entire file into memory:** Use `shutil.copyfileobj` to stream large files to disk
- **No error handling in WebSocket loops:** Always wrap the receive loop in try/except WebSocketDisconnect
- **Forgetting to close WebSocket connections:** Use ConnectionManager.disconnect on disconnect events
- **Using aioredis directly:** It is deprecated; use `redis.asyncio` from redis-py instead

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Task queuing with retries | Custom queue with database polling | Celery with Redis broker | Retry logic, exponential backoff, task routing, monitoring are deceptively complex |
| Scheduled/periodic tasks | Custom cron-like scheduler | Celery Beat | Timezone handling, missed task recovery, distributed scheduling |
| Redis connection pooling | Manual connection management | redis-py ConnectionPool | Connection lifecycle, health checks, reconnection logic |
| File type detection | Manual magic number checking | python-magic or filetype | Hundreds of file signatures, edge cases, binary parsing |
| S3 presigned URLs | Custom AWS signature generation | boto3 generate_presigned_url | AWS Signature V4 is complex; boto3 handles credential refresh, region routing |
| WebSocket connection tracking | Custom dict with manual cleanup | ConnectionManager class pattern | Disconnect handling, broadcast iteration, thread safety |
| Cache invalidation patterns | Custom timestamp checking | Redis TTL + explicit DELETE | TTL arithmetic, race conditions, memory management |

**Key insight:** Each of these domains has edge cases that take weeks to discover. Task retry with backoff needs jitter to prevent thundering herd. File validation needs magic numbers, not just extensions. WebSocket managers need graceful disconnect handling. Use proven patterns.

## Common Pitfalls

### Pitfall 1: BackgroundTasks vs Celery Confusion

**What goes wrong:** Using BackgroundTasks for heavy computation blocks the FastAPI worker process
**Why it happens:** BackgroundTasks runs in the same process after response; it shares the event loop
**How to avoid:** Use BackgroundTasks for lightweight tasks (send email, write log). Use Celery for anything CPU-intensive, long-running, or needing retries/persistence
**Warning signs:** API response times degrade under load; background tasks don't complete

### Pitfall 2: Forgetting Cache Invalidation on Writes

**What goes wrong:** Users see stale data after updates because cache still holds old values
**Why it happens:** Cache is set on read but not cleared on write/update/delete
**How to avoid:** Always invalidate (delete) cache keys when underlying data changes. Use consistent key naming patterns like `entity:{id}` to make invalidation predictable
**Warning signs:** Data inconsistency between cache and database; "refresh the page" fixes issues

### Pitfall 3: File Upload Memory Exhaustion

**What goes wrong:** Server runs out of memory when multiple large files are uploaded simultaneously
**Why it happens:** Reading entire file with `await file.read()` loads it all into memory
**How to avoid:** Use `shutil.copyfileobj(file.file, destination)` for streaming writes. Read in chunks for validation. Set size limits at the reverse proxy level (nginx `client_max_body_size`)
**Warning signs:** OOMKilled in production, slow uploads, high memory usage

### Pitfall 4: WebSocket Connection Leaks

**What goes wrong:** ConnectionManager accumulates dead connections, broadcast slows down
**Why it happens:** Client disconnects without sending close frame (network drop, app crash)
**How to avoid:** Always handle WebSocketDisconnect exception. Consider heartbeat/ping-pong to detect dead connections. Clean up connections in finally blocks
**Warning signs:** Growing memory usage, broadcast taking longer over time, stale connections in manager

### Pitfall 5: Redis Connection Without Pool

**What goes wrong:** Each request creates a new Redis connection, exhausting file descriptors
**Why it happens:** Creating `redis.Redis()` or `redis.asyncio.Redis()` per request instead of reusing
**How to avoid:** Create a single Redis client at startup with connection pooling. Use FastAPI lifespan events for setup/teardown
**Warning signs:** "Too many open files" errors, Redis "max clients reached"

### Pitfall 6: Celery Task Not Serializable

**What goes wrong:** Tasks fail with serialization errors when passing complex objects
**Why it happens:** Celery serializes task arguments (default: JSON). SQLAlchemy models, file objects, and request objects are not JSON-serializable
**How to avoid:** Pass only primitive types (int, str, dict) as task arguments. Pass IDs, not objects. Fetch the object inside the task
**Warning signs:** `kombu.exceptions.EncodeError`, tasks stuck in queue

### Pitfall 7: Trusting Content-Type Header for File Validation

**What goes wrong:** Malicious files bypass validation because content-type can be spoofed
**Why it happens:** Relying solely on the content-type MIME type sent by the client
**How to avoid:** Use content-type as first gate, then validate with magic numbers (python-magic or filetype library). For images, try opening with Pillow as additional validation
**Warning signs:** Unexpected file types stored on server despite validation

## Code Examples

Verified patterns from official sources:

### BackgroundTasks with Dependency Injection
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from typing import Annotated
from fastapi import BackgroundTasks, Depends, FastAPI

app = FastAPI()

def write_log(message: str):
    with open("log.txt", mode="a") as f:
        f.write(message)

def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    """Dependency that adds its own background tasks."""
    if q:
        background_tasks.add_task(write_log, f"Query received: {q}\n")
    return q

@app.post("/items/")
async def create_item(
    background_tasks: BackgroundTasks,
    q: Annotated[str, Depends(get_query)]
):
    # Both dependency and endpoint background tasks merged
    background_tasks.add_task(write_log, "Item created\n")
    return {"message": "Item created"}
```

### Celery with FastAPI Integration
```python
# celery_app.py
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# tasks.py
from celery_app import celery_app

@celery_app.task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    max_retries=3
)
def send_welcome_email(user_id: int, email: str):
    """Task receives primitives, not objects."""
    # Fetch user inside task if needed
    send_email(to=email, subject="Welcome!", body="...")

# api endpoint
from fastapi import FastAPI
from tasks import send_welcome_email

app = FastAPI()

@app.post("/register")
async def register(user_data: UserCreate):
    user = await create_user(user_data)
    # Dispatch to Celery (async, returns immediately)
    send_welcome_email.delay(user.id, user.email)
    return {"id": user.id, "message": "Registration successful"}
```

### Redis Async Caching with FastAPI Lifespan
```python
# Source: redis-py async docs
import json
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import FastAPI, Depends

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Redis connection lifecycle."""
    app.state.redis = redis.from_url(
        "redis://localhost:6379",
        decode_responses=True
    )
    yield
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

async def get_redis():
    """Dependency to get Redis client."""
    return app.state.redis

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    cache: redis.Redis = Depends(get_redis)
):
    # Check cache
    cached = await cache.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # Fetch from DB
    user = await fetch_user_from_db(user_id)

    # Cache with 1-hour TTL
    await cache.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

### WebSocket with Authentication via Query Parameter
```python
# Source: https://fastapi.tiangolo.com/advanced/websockets/
from fastapi import WebSocket, WebSocketException, Query, status
from typing import Annotated

async def verify_ws_token(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None
):
    """Verify JWT token passed as query parameter."""
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        payload = decode_jwt(token)
        return payload["sub"]  # user_id
    except Exception:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Depends(verify_ws_token)
):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Mobile Developer Comparison Tables

```
Background Processing Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Simple BG     | DispatchQueue       | Coroutines +        | BackgroundTasks     |
| task          | .global().async     | Dispatchers.IO      | .add_task()         |
+---------------+---------------------+---------------------+---------------------+
| Heavy BG      | BGTaskScheduler     | WorkManager         | Celery task queue   |
| processing    |                     |                     |                     |
+---------------+---------------------+---------------------+---------------------+
| Retry logic   | BGTaskScheduler     | WorkManager         | Celery autoretry    |
|               | with constraints    | .setBackoffPolicy() | retry_backoff=True  |
+---------------+---------------------+---------------------+---------------------+
| Scheduled     | BGAppRefreshTask    | PeriodicWorkRequest | Celery Beat         |
| tasks         | request             |                     |                     |
+---------------+---------------------+---------------------+---------------------+

Real-Time Communication Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| WebSocket     | URLSessionWebSocket | OkHttp WebSocket    | FastAPI @websocket  |
| client        | Task                | Listener            | endpoint            |
+---------------+---------------------+---------------------+---------------------+
| Push          | APNs                | FCM                 | Server-side WS      |
| notifications |                     |                     | broadcast           |
+---------------+---------------------+---------------------+---------------------+
| Real-time     | Combine Publisher   | StateFlow/          | WebSocket           |
| updates       |                     | SharedFlow          | send_text/send_json |
+---------------+---------------------+---------------------+---------------------+

Caching Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| In-memory     | NSCache             | LruCache            | Redis (external)    |
| cache         |                     |                     |                     |
+---------------+---------------------+---------------------+---------------------+
| Disk cache    | URLCache            | DiskLruCache        | Redis persistence   |
|               |                     |                     | (RDB/AOF)           |
+---------------+---------------------+---------------------+---------------------+
| TTL/expiry    | NSCache             | ExpiringMap         | Redis SETEX/EXPIRE  |
|               | countLimit          | (third-party)       | (built-in)          |
+---------------+---------------------+---------------------+---------------------+

File Upload Comparison:
+---------------+---------------------+---------------------+---------------------+
| Concept       | iOS/Swift           | Android/Kotlin      | Python/FastAPI      |
+---------------+---------------------+---------------------+---------------------+
| Upload API    | URLSession          | Retrofit            | UploadFile          |
|               | uploadTask          | @Multipart          | (multipart/form)    |
+---------------+---------------------+---------------------+---------------------+
| Validation    | UTType              | ContentResolver     | content_type +      |
|               |                     | .getType()          | magic numbers       |
+---------------+---------------------+---------------------+---------------------+
| Cloud storage | AWS Amplify         | Firebase Storage    | boto3 / S3          |
|               | Storage             |                     | presigned URLs      |
+---------------+---------------------+---------------------+---------------------+
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| aioredis for async Redis | redis.asyncio (redis-py) | 2022 (redis-py 4.2+) | Single library for sync and async Redis |
| Manual Celery retry with countdown | autoretry_for + retry_backoff | Celery 4.0+ | Declarative retry configuration |
| python-jose for JWT | PyJWT | 2024 (python-jose abandoned) | Already adopted in Phase 3 decisions |
| Saving files with raw write() | shutil.copyfileobj streaming | Always preferred | Memory-efficient large file handling |
| requests for HTTP in tasks | httpx with async | 2020+ | Async support, same API as FastAPI's TestClient |
| Manual WebSocket management | ConnectionManager pattern | FastAPI docs standard | Clean connect/disconnect/broadcast abstraction |
| on_event("startup") for Redis | lifespan context manager | FastAPI 0.93+ | Proper async resource cleanup |

**Deprecated/outdated:**

- **aioredis**: Merged into redis-py; do not install separately
- **python-jose**: Abandoned; use PyJWT (already decided in Phase 3)
- **on_event("startup"/"shutdown")**: Deprecated in FastAPI; use lifespan context manager
- **Celery 4.x manual retry patterns**: Use autoretry_for with retry_backoff in Celery 5.x

## Open Questions

1. **Exercise format for Celery tasks**
   - What we know: Celery requires a running Redis server and worker process, which complicates standalone exercises
   - What's unclear: Whether exercises should mock Celery or require Docker infrastructure
   - Recommendation: Exercise 02 (Celery tasks) should teach the task definition patterns and use `task.apply()` for synchronous testing without requiring a running worker. Theory covers full distributed setup. Exercise 01 uses BackgroundTasks (no external deps). Exercise 03 focuses on retry configuration patterns.

2. **Redis exercises: real Redis vs fakeredis**
   - What we know: fakeredis provides an in-memory Redis mock for testing. Real Redis requires Docker.
   - What's unclear: Whether learners should set up Redis via Docker or use fakeredis for exercises
   - Recommendation: Use fakeredis for exercises so they run without Docker. Theory covers real Redis setup. Project README instructs using Docker Compose with real Redis.

3. **File upload exercise scope: local vs S3**
   - What we know: S3 requires AWS credentials or MinIO setup
   - What's unclear: How deep to go with cloud storage in exercises
   - Recommendation: Exercises use local file storage (no cloud deps). Theory covers S3 patterns and presigned URLs. Project README covers both local and S3 options.

4. **WebSocket testing approach**
   - What we know: FastAPI provides TestClient with WebSocket support via `with client.websocket_connect("/ws") as ws:`
   - What's unclear: Best patterns for testing ConnectionManager broadcasting
   - Recommendation: Use FastAPI TestClient's websocket_connect for exercise tests. This keeps exercises self-contained like established patterns.

## Sources

### Primary (HIGH confidence)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) - Official BackgroundTasks documentation
- [FastAPI Request Files](https://fastapi.tiangolo.com/tutorial/request-files/) - Official UploadFile documentation
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) - Official WebSocket documentation with ConnectionManager
- [Celery Tasks Documentation](https://docs.celeryq.dev/en/stable/userguide/tasks.html) - autoretry_for, retry_backoff, task configuration
- [redis-py Async Examples](https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html) - redis.asyncio usage patterns

### Secondary (MEDIUM confidence)
- [Celery + Redis + FastAPI Production Guide](https://medium.com/@dewasheesh.rana/celery-redis-fastapi-the-ultimate-2025-production-guide-broker-vs-backend-explained-5b84ef508fa7) - Broker vs backend architecture
- [FastAPI Caching Guide](https://blog.greeden.me/en/2025/09/17/blazing-fast-rock-solid-a-complete-fastapi-caching-guide-redis-http-caching-etag-rate-limiting-and-compression/) - Cache patterns, TTL, invalidation strategies
- [Secure File Uploads in FastAPI](https://blog.greeden.me/en/2026/03/03/implementing-secure-file-uploads-in-fastapi-practical-patterns-for-uploadfile-size-limits-virus-scanning-s3-compatible-storage-and-presigned-urls/) - Validation, magic numbers, S3 presigned URLs
- [FastAPI WebSocket Beginner's Guide](https://blog.greeden.me/en/2026/01/13/fastapi-x-websocket-beginners-guide-implementation-patterns-for-real-time-communication-chat-and-dashboards/) - ConnectionManager, rooms, auth patterns
- [WebSocket/SSE with FastAPI](https://blog.greeden.me/en/2025/10/28/weaponizing-real-time-websocket-sse-notifications-with-fastapi-connection-management-rooms-reconnection-scale-out-and-observability/) - Scaling with Redis Pub/Sub
- [Redis FAQ: aioredis vs redis-py](https://redis.io/faq/doc/26366kjrif/what-is-the-difference-between-aioredis-v2-0-and-redis-py-asyncio) - Official confirmation aioredis merged into redis-py

### Tertiary (LOW confidence)
- [FastAPI Cache Invalidation Patterns](https://oneuptime.com/blog/post/2026-02-02-fastapi-cache-invalidation/view) - Tag-based invalidation strategy details
- [FastAPI + PostgreSQL + Celery Docker Setup](https://oneuptime.com/blog/post/2026-02-08-how-to-set-up-a-fastapi-postgresql-celery-stack-with-docker-compose/view) - Docker Compose configuration reference

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official docs and PyPI; FastAPI built-ins are well-documented
- Architecture: HIGH - Module structure follows established patterns from Phases 1-4; all code patterns from official FastAPI/Celery docs
- Pitfalls: HIGH - Common pitfalls verified across multiple sources and official documentation warnings
- Exercise approach: MEDIUM - Open questions around Celery/Redis exercise isolation; recommendations provided but untested

**Research date:** 2026-03-08
**Valid until:** ~2026-05-08 (60 days - these domains are mature and stable)
