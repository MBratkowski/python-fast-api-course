# Module 013: Background Tasks and Queues

## Why This Module?

Learn how to handle work that doesn't need to happen during the request/response cycle. Background tasks let your API respond instantly while processing emails, reports, image resizing, and other heavy operations behind the scenes.

## What You'll Learn

- When to offload work from the request/response cycle
- FastAPI's built-in BackgroundTasks for lightweight post-response work
- Celery task queue for distributed, persistent, and retryable tasks
- Redis as a message broker for Celery
- Retry patterns with exponential backoff and jitter
- Scheduled/periodic tasks with Celery Beat

## Mobile Developer Context

You've handled background processing on mobile: GCD queues and BGTaskScheduler (iOS), WorkManager and Coroutine Dispatchers (Android). Backend background processing is the same concept but with a critical difference: you have full control over the task lifecycle -- no OS-imposed limits on execution time, no battery optimization killing your tasks.

**Background Processing Across Platforms:**

| Concept | iOS/Swift | Android/Kotlin | Python/FastAPI |
|---------|-----------|----------------|----------------|
| Simple background task | `DispatchQueue.global().async` | `Dispatchers.IO` / `withContext` | `BackgroundTasks.add_task()` |
| Heavy background processing | `BGTaskScheduler` | `WorkManager` | Celery task queue |
| Retry with backoff | `BGTaskScheduler` with constraints | `WorkManager.setBackoffPolicy()` | `autoretry_for` + `retry_backoff=True` |
| Scheduled/periodic tasks | `BGAppRefreshTaskRequest` | `PeriodicWorkRequest` | Celery Beat |
| Task persistence | System-managed | Room DB (WorkManager) | Redis broker |
| Task monitoring | Xcode console | WorkManager Inspector | Flower dashboard |

**Key Differences from Mobile:**

1. **No OS restrictions**: Mobile OS limits background time (30s on iOS). Backend tasks can run for hours
2. **External broker**: Mobile tasks queue in-process or in local DB. Backend tasks use Redis/RabbitMQ as external queue
3. **Horizontal scaling**: Mobile runs on one device. Celery workers can scale across multiple servers
4. **Full lifecycle control**: You manage retries, timeouts, and failure handling -- no OS doing it for you
5. **Two tiers**: FastAPI has lightweight (BackgroundTasks) and heavyweight (Celery) -- mobile typically has one system

## Topics

### Theory
1. When to Use Background Tasks
2. FastAPI BackgroundTasks
3. Celery Setup and Configuration
4. Redis as Message Broker
5. Retries and Error Handling
6. Scheduled Tasks with Celery Beat

### Exercises
1. FastAPI BackgroundTasks
2. Celery Task Definitions
3. Retry Logic Patterns

### Project
Email notification system with background processing, retries, and scheduled digests.

## Example

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def send_welcome_email(email: str, name: str):
    """Runs after the response is sent."""
    # Simulate sending email (this could take seconds)
    print(f"Sending welcome email to {email}")

@app.post("/register")
async def register_user(
    email: str,
    name: str,
    background_tasks: BackgroundTasks
):
    # Create user in DB (fast)
    user = {"email": email, "name": name}

    # Queue email for after response (non-blocking)
    background_tasks.add_task(send_welcome_email, email, name)

    # Response returns immediately
    return {"message": "User registered", "user": user}
```

## Quick Assessment

Before starting this module, ask yourself:
- Have you used GCD/Dispatch queues (iOS) or Coroutine Dispatchers (Android)?
- Do you understand why sending an email shouldn't block an API response?
- Have you worked with WorkManager (Android) or BGTaskScheduler (iOS)?

If yes, you're ready. You already understand why background processing exists -- now you'll learn the backend tools.

## Time Estimate

6-8 hours total:
- Theory: 2-3 hours
- Exercises: 2-3 hours
- Project: 2-3 hours

## Key Differences from Mobile

1. **Two-tier system**: BackgroundTasks (in-process, lightweight) vs Celery (external, heavyweight) -- choose based on complexity
2. **No battery constraints**: Backend tasks don't compete with user experience for resources
3. **External state**: Task state lives in Redis, not in app memory -- survives restarts
4. **Worker processes**: Celery tasks run in separate worker processes, not in your API process
5. **Monitoring**: Flower provides a web dashboard for task monitoring (like WorkManager Inspector but for production)
