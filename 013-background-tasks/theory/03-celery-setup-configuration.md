# Celery Setup and Configuration

## Why This Matters

On mobile, when you need background work that survives app restarts, retries on failure, and runs on a schedule, you reach for WorkManager (Android) or BGTaskScheduler (iOS). These systems persist tasks, manage retries, and handle constraints.

Celery is the Python equivalent -- but far more powerful. It's a distributed task queue that runs in separate worker processes, persists tasks in an external broker (Redis), supports retries with exponential backoff, and can scale horizontally across multiple servers. It's the industry standard for Python background processing.

## Core Concepts

```
Your FastAPI App                    Celery Worker(s)
┌──────────────┐                   ┌──────────────┐
│              │   task.delay()    │              │
│  API         │──────────────→   │  Worker      │
│  Endpoint    │   (enqueue)      │  Process     │
│              │                   │              │
└──────────────┘                   └──────┬───────┘
                                          │
         ┌────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│              Redis (Broker)                   │
│  Queue: task messages waiting to be processed │
│  Backend: task results stored after execution │
└──────────────────────────────────────────────┘
```

- **Broker**: Message queue where tasks are stored (Redis)
- **Backend**: Where task results are stored (also Redis)
- **Worker**: Separate process that picks up and executes tasks
- **Task**: A Python function decorated with `@celery_app.task`

## Creating a Celery App

```python
# celery_config.py
from celery import Celery

celery_app = Celery(
    "worker",                              # App name
    broker="redis://localhost:6379/0",      # Redis DB 0 for broker
    backend="redis://localhost:6379/1"      # Redis DB 1 for results
)

# Configuration
celery_app.conf.update(
    task_serializer="json",        # Serialize task args as JSON
    accept_content=["json"],       # Only accept JSON
    result_serializer="json",      # Serialize results as JSON
    timezone="UTC",                # Use UTC for scheduling
    enable_utc=True,               # Force UTC
)
```

## Defining Tasks

The `@celery_app.task` decorator turns a function into a Celery task:

```python
# tasks.py
from celery_config import celery_app

@celery_app.task
def add(x: int, y: int) -> int:
    """Simple task that adds two numbers."""
    return x + y

@celery_app.task
def send_welcome_email(user_id: int, email: str):
    """Task that sends a welcome email.

    Note: Pass primitives (int, str, dict), not objects.
    SQLAlchemy models and request objects are NOT serializable.
    """
    # Fetch user inside task if needed
    user = get_user_by_id(user_id)
    send_email(to=email, subject="Welcome!", body=f"Hello {user.name}!")
```

## Calling Tasks

### `.delay()` -- Simple Call

```python
# Enqueue task with positional arguments
result = add.delay(4, 6)

# Returns an AsyncResult immediately
print(result.id)       # Task UUID
print(result.status)   # "PENDING"
```

### `.apply_async()` -- Full Control

```python
# Full control over task execution
result = send_welcome_email.apply_async(
    args=[user_id, email],     # Positional arguments
    kwargs={},                  # Keyword arguments
    countdown=60,               # Delay execution by 60 seconds
    expires=3600,               # Task expires after 1 hour
    queue="emails",             # Send to specific queue
)
```

### `.apply()` -- Synchronous (Testing)

```python
# Execute synchronously (no worker needed) -- for testing
result = add.apply(args=[4, 6])
print(result.result)   # 10
print(result.status)   # "SUCCESS"
```

This is how exercises in this module test Celery tasks without requiring a running Redis server or worker process.

## Checking Task Results

```python
from celery.result import AsyncResult

# Get result by task ID
result = AsyncResult(task_id)

print(result.status)    # PENDING, STARTED, SUCCESS, FAILURE, RETRY
print(result.result)    # Return value (if SUCCESS) or exception (if FAILURE)
print(result.ready())   # True if task has finished
print(result.successful())  # True if task completed without error

# Block until result is ready (use sparingly)
value = result.get(timeout=10)
```

## Integration with FastAPI

```python
# main.py
from fastapi import FastAPI
from tasks import send_welcome_email, generate_report

app = FastAPI()

@app.post("/register")
async def register(user_data: UserCreate):
    user = await create_user(user_data)

    # Dispatch to Celery (returns immediately)
    send_welcome_email.delay(user.id, user.email)

    return {"id": user.id, "message": "Registration successful"}

@app.post("/reports")
async def create_report(request: ReportRequest):
    # Dispatch and return task ID for polling
    task = generate_report.delay(
        request.start_date.isoformat(),
        request.end_date.isoformat()
    )
    return {"task_id": task.id, "status": "queued"}

@app.get("/reports/{task_id}")
async def get_report_status(task_id: str):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

## Running Celery Workers

```bash
# Start a worker (from project root)
celery -A celery_config.celery_app worker --loglevel=info

# Start with concurrency control
celery -A celery_config.celery_app worker --loglevel=info --concurrency=4

# Start with specific queue
celery -A celery_config.celery_app worker --loglevel=info -Q emails,reports
```

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Celery |
|---------|-----------|----------------|---------------|
| Task definition | `BGTaskScheduler.register()` | `class MyWorker : Worker()` | `@celery_app.task` |
| Enqueue task | `BGTaskScheduler.submit()` | `WorkManager.enqueue()` | `task.delay()` |
| Full options | `BGProcessingTaskRequest` + constraints | `OneTimeWorkRequestBuilder` | `task.apply_async()` |
| Check status | N/A (callback-based) | `WorkInfo.state` | `AsyncResult.status` |
| Get result | Callback on completion | `WorkInfo.outputData` | `result.get()` |
| Persistence | System-managed | Room database | Redis broker |
| Worker process | Background execution context | Separate process/thread | Celery worker process |
| Configuration | `BGTaskRequest` properties | `Constraints`, `Data` | `celery_app.conf.update()` |

## Configuration Reference

```python
celery_app.conf.update(
    # Serialization
    task_serializer="json",          # How to serialize task args
    accept_content=["json"],         # Accepted content types
    result_serializer="json",        # How to serialize results

    # Time
    timezone="UTC",
    enable_utc=True,

    # Results
    result_expires=3600,             # Results expire after 1 hour

    # Execution
    task_always_eager=False,         # Set True for testing (run synchronously)
    task_acks_late=True,             # Acknowledge after execution (safer)
    worker_prefetch_multiplier=1,    # Fetch one task at a time

    # Limits
    task_time_limit=300,             # Hard kill after 5 minutes
    task_soft_time_limit=240,        # Raise SoftTimeLimitExceeded after 4 minutes
)
```

## Key Takeaways

- Celery is a distributed task queue -- tasks run in separate worker processes
- Tasks are Python functions decorated with `@celery_app.task`
- Call with `.delay()` (simple) or `.apply_async()` (full control)
- Use `.apply()` for synchronous testing without a running worker
- Pass only primitives (int, str, dict) as task arguments -- not ORM objects
- Redis serves as both the message broker and result backend
- `AsyncResult` lets you check task status and retrieve results
- Mobile parallel: Celery is like `WorkManager` (Android) or `BGTaskScheduler` (iOS) -- persistent, distributed, retryable
