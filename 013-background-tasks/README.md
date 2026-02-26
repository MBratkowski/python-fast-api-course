# Module 013: Background Tasks & Queues

## Why This Module?

Some operations shouldn't block the API response: sending emails, processing uploads, generating reports. Learn background task processing.

## What You'll Learn

- FastAPI BackgroundTasks
- Celery task queue
- Redis as message broker
- Task monitoring
- Retry strategies
- Scheduled tasks

## Topics

### Theory
1. When to Use Background Tasks
2. FastAPI BackgroundTasks (simple)
3. Celery Setup & Configuration
4. Redis as Broker
5. Task Retries & Error Handling
6. Scheduled Tasks with Celery Beat

### Project
Build email notification system with background processing.

## Example

```python
# Simple background task
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Slow operation
    ...

@router.post("/signup")
async def signup(
    user: UserCreate,
    background_tasks: BackgroundTasks
):
    user = await create_user(user)
    background_tasks.add_task(send_email, user.email, "Welcome!")
    return user  # Response sent immediately

# Celery for heavy tasks
from celery import Celery

celery = Celery("tasks", broker="redis://localhost:6379")

@celery.task(bind=True, max_retries=3)
def process_upload(self, file_id: int):
    try:
        # Heavy processing
        ...
    except Exception as e:
        self.retry(countdown=60)
```
