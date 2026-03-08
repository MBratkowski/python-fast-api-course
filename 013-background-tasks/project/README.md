# Project: Email Notification System

## Overview

Build a complete email notification system using FastAPI BackgroundTasks for simple notifications and Celery for bulk email, retries, and scheduled digests. This project combines everything from Module 013 into a production-like notification service.

## Requirements

### Core Features

1. **Notification Endpoint** -- `POST /notifications/send`
   - Accept: `to` (email), `subject`, `body`, `priority` (low/normal/high)
   - Low/normal priority: use FastAPI BackgroundTasks
   - High priority: use Celery task with retry logic
   - Return: notification ID and status

2. **Bulk Email Task** -- Celery task
   - Accept: list of recipients, subject, body template
   - Process in batches (10 at a time)
   - Track progress (X of Y sent)
   - Return: summary with success/failure counts

3. **Retry on SMTP Failures** -- Celery retry configuration
   - `autoretry_for=(SMTPError, ConnectionError, TimeoutError)`
   - Exponential backoff: `retry_backoff=True`
   - Max retries: 5
   - Jitter: `retry_jitter=True`
   - Error callback: log permanently failed emails

4. **Scheduled Daily Digest** -- Celery Beat
   - Collect all notifications from the past 24 hours
   - Generate digest email per user
   - Schedule: daily at 8 AM UTC
   - Configurable via environment variable

### Architecture

```
POST /notifications/send
    │
    ├── Low/Normal Priority
    │   └── BackgroundTasks.add_task(send_email, ...)
    │
    └── High Priority
        └── send_email_task.delay(...)
            │
            ├── Success → Store in notifications table
            │
            └── Failure → Retry with exponential backoff
                │
                └── Max retries exceeded → Error callback

Celery Beat (daily at 8 AM)
    └── generate_daily_digest.delay()
        └── For each user: collect notifications → send digest
```

## Starter Template

```python
# models.py
from enum import Enum
from datetime import datetime


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


# In-memory storage for simplicity (use a database in production)
notifications: list[dict] = []


def store_notification(
    to: str,
    subject: str,
    body: str,
    priority: Priority,
    status: NotificationStatus
) -> dict:
    """Store a notification record."""
    notification = {
        "id": len(notifications) + 1,
        "to": to,
        "subject": subject,
        "body": body,
        "priority": priority,
        "status": status,
        "created_at": datetime.utcnow().isoformat(),
    }
    notifications.append(notification)
    return notification


# celery_config.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "notifications",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    # TODO: Configure daily digest schedule
    "daily-digest": {
        "task": "tasks.generate_daily_digest",
        "schedule": crontab(hour=8, minute=0),
    },
}


# tasks.py
# TODO: Implement these Celery tasks

@celery_app.task(
    bind=True,
    autoretry_for=(),  # TODO: Add exception types
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def send_email_task(self, to: str, subject: str, body: str):
    """Send a single email with retry logic."""
    # TODO: Implement
    # - Simulate SMTP sending
    # - Store notification with status
    # - Handle errors
    pass


@celery_app.task(bind=True)
def send_bulk_emails(self, recipients: list, subject: str, body_template: str):
    """Send emails to multiple recipients in batches."""
    # TODO: Implement
    # - Process in batches of 10
    # - Track progress
    # - Return summary
    pass


@celery_app.task
def generate_daily_digest():
    """Generate and send daily digest emails."""
    # TODO: Implement
    # - Collect notifications from last 24 hours
    # - Group by recipient
    # - Send digest per user
    pass


# main.py
from fastapi import BackgroundTasks, FastAPI

app = FastAPI(title="Notification Service")


def send_email_simple(to: str, subject: str, body: str):
    """Simple email sender for BackgroundTasks (low/normal priority)."""
    # TODO: Implement
    pass


@app.post("/notifications/send")
async def send_notification(
    to: str,
    subject: str,
    body: str,
    priority: str = "normal",
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Send a notification with priority-based routing."""
    # TODO: Implement
    # - If priority is "high", use Celery task
    # - Otherwise, use BackgroundTasks
    # - Return notification ID and status
    pass


@app.get("/notifications/")
async def list_notifications(limit: int = 50):
    """List recent notifications."""
    # TODO: Implement
    pass


@app.get("/notifications/{notification_id}")
async def get_notification(notification_id: int):
    """Get notification status."""
    # TODO: Implement
    pass
```

## Success Criteria

- [ ] POST /notifications/send routes by priority (BackgroundTasks vs Celery)
- [ ] High-priority emails use Celery with autoretry_for configuration
- [ ] Bulk email task processes recipients in batches
- [ ] Retry logic uses exponential backoff with jitter
- [ ] Failed emails after max retries are logged with error callback
- [ ] Daily digest is configured with Celery Beat (crontab)
- [ ] Notification status is tracked (queued, sent, failed)
- [ ] All tasks pass only primitive arguments (no ORM objects)

## Stretch Goals

- [ ] **Priority Queues**: Route high-priority tasks to a dedicated Celery queue
- [ ] **Dead Letter Handling**: Store permanently failed emails in a dead letter table for manual review
- [ ] **Task Monitoring**: Add Flower dashboard configuration to docker-compose.yml
- [ ] **Rate Limiting**: Implement per-recipient rate limiting (max 10 emails/hour)
- [ ] **Templates**: Support email templates with variable substitution
- [ ] **Unsubscribe**: Track unsubscribe preferences and skip opted-out recipients

## Docker Compose

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8000

  celery-worker:
    build: .
    depends_on:
      - redis
    command: celery -A celery_config.celery_app worker --loglevel=info

  celery-beat:
    build: .
    depends_on:
      - redis
    command: celery -A celery_config.celery_app beat --loglevel=info

  # Stretch goal: monitoring
  # flower:
  #   build: .
  #   ports:
  #     - "5555:5555"
  #   depends_on:
  #     - redis
  #   command: celery -A celery_config.celery_app flower --port=5555
```

## Testing Checklist

- [ ] Unit test: send_email_task succeeds on first try
- [ ] Unit test: send_email_task retries on ConnectionError
- [ ] Unit test: send_email_task handles max retries exceeded
- [ ] Unit test: send_bulk_emails processes batches correctly
- [ ] Unit test: generate_daily_digest groups by recipient
- [ ] Integration test: POST /notifications/send with low priority uses BackgroundTasks
- [ ] Integration test: POST /notifications/send with high priority uses Celery
- [ ] Integration test: GET /notifications/{id} returns correct status
