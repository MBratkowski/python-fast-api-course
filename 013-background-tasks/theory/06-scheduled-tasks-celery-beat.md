# Scheduled Tasks with Celery Beat

## Why This Matters

On mobile, scheduled work is limited. iOS gives you `BGAppRefreshTaskRequest` for periodic background refreshes (system decides when). Android has `PeriodicWorkRequest` (minimum 15-minute interval). Both are constrained by battery optimization.

On the backend, you have **full control over scheduling**. Celery Beat is a scheduler that kicks off tasks at specified intervals -- every minute, every hour, every day at 3 AM, or on a custom cron schedule. No OS restrictions, no battery concerns, no minimum intervals.

## How Celery Beat Works

```
┌──────────────┐     sends task at     ┌───────────┐     picks up     ┌──────────────┐
│  Celery Beat │────scheduled time────→│   Redis   │────────────────→│  Celery      │
│  (Scheduler) │                       │  (Broker) │                  │  Worker      │
│              │                       │           │                  │              │
│  Checks      │                       └───────────┘                  │  Executes    │
│  schedule    │                                                      │  the task    │
│  every sec   │                                                      │              │
└──────────────┘                                                      └──────────────┘
```

Celery Beat is a separate process that checks its schedule table every second. When a task is due, it sends a message to the broker just like `.delay()` would. A regular Celery worker picks it up and executes it.

## Configuring the Schedule

### Using `beat_schedule`

```python
# celery_config.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.beat_schedule = {
    # Run every 30 seconds
    "cleanup-expired-tokens": {
        "task": "tasks.cleanup_expired_tokens",
        "schedule": 30.0,  # seconds
    },

    # Run every 5 minutes
    "update-stats": {
        "task": "tasks.update_dashboard_stats",
        "schedule": 300.0,
    },

    # Run every day at midnight UTC
    "daily-cleanup": {
        "task": "tasks.daily_database_cleanup",
        "schedule": crontab(hour=0, minute=0),
    },

    # Run every Monday at 9 AM
    "weekly-report": {
        "task": "tasks.generate_weekly_report",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },

    # Run first day of every month
    "monthly-billing": {
        "task": "tasks.process_monthly_billing",
        "schedule": crontab(hour=0, minute=0, day_of_month=1),
    },
}

celery_app.conf.timezone = "UTC"
```

### Using `timedelta`

```python
from datetime import timedelta

celery_app.conf.beat_schedule = {
    "check-health": {
        "task": "tasks.health_check",
        "schedule": timedelta(minutes=5),
    },
    "sync-data": {
        "task": "tasks.sync_external_data",
        "schedule": timedelta(hours=1),
    },
}
```

### Using `crontab`

The `crontab` schedule follows the same pattern as Unix cron:

```python
from celery.schedules import crontab

# crontab(minute, hour, day_of_week, day_of_month, month_of_year)

crontab()                           # Every minute
crontab(minute=0)                   # Every hour (at :00)
crontab(minute=0, hour=0)          # Every day at midnight
crontab(minute=0, hour="*/3")      # Every 3 hours
crontab(minute=30, hour=8)         # Daily at 8:30 AM
crontab(hour=9, minute=0, day_of_week=1)      # Monday at 9 AM
crontab(hour=0, minute=0, day_of_month=1)     # 1st of each month
crontab(hour=0, minute=0, day_of_month=1, month_of_year=1)  # Jan 1st
```

## Defining Scheduled Tasks

```python
# tasks.py
from celery_config import celery_app
from datetime import datetime, timedelta

@celery_app.task
def cleanup_expired_tokens():
    """Remove expired JWT refresh tokens from database."""
    cutoff = datetime.utcnow() - timedelta(days=7)
    count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < cutoff
    ).delete()
    db.commit()
    return f"Cleaned up {count} expired tokens"

@celery_app.task
def daily_database_cleanup():
    """Daily maintenance: clean old logs, sessions, temp files."""
    # Clean old audit logs (> 90 days)
    old_logs = db.query(AuditLog).filter(
        AuditLog.created_at < datetime.utcnow() - timedelta(days=90)
    ).delete()

    # Clean expired sessions
    expired = db.query(Session).filter(
        Session.expires_at < datetime.utcnow()
    ).delete()

    db.commit()
    return {
        "old_logs_removed": old_logs,
        "expired_sessions_removed": expired
    }

@celery_app.task
def generate_weekly_report():
    """Generate and email weekly analytics report."""
    report_data = calculate_weekly_metrics()
    pdf_path = render_report_pdf(report_data)
    send_report_email(
        to="team@company.com",
        subject=f"Weekly Report - {datetime.utcnow().strftime('%Y-%m-%d')}",
        attachment=pdf_path
    )
    return f"Report sent: {pdf_path}"
```

## Passing Arguments to Scheduled Tasks

```python
celery_app.conf.beat_schedule = {
    "backup-database": {
        "task": "tasks.backup_database",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        "args": ("production",),                 # Positional args
    },
    "send-daily-digest": {
        "task": "tasks.send_digest",
        "schedule": crontab(hour=8, minute=0),
        "kwargs": {"digest_type": "daily", "include_stats": True},
    },
}
```

## Timezone Handling

```python
celery_app.conf.update(
    timezone="UTC",        # Always use UTC internally
    enable_utc=True,       # Force UTC
)

# Schedule in UTC -- let your application handle timezone display
celery_app.conf.beat_schedule = {
    # This runs at midnight UTC, not midnight local time
    "daily-report": {
        "task": "tasks.daily_report",
        "schedule": crontab(hour=0, minute=0),
    },
}
```

Always schedule in UTC and convert for display. Avoid scheduling in local timezones -- daylight saving time causes missed or double executions.

## Running Celery Beat

```bash
# Start Beat scheduler (separate from worker)
celery -A celery_config.celery_app beat --loglevel=info

# Start worker (in another terminal)
celery -A celery_config.celery_app worker --loglevel=info

# Or run both in one process (development only)
celery -A celery_config.celery_app worker --beat --loglevel=info
```

In production, Beat and workers are separate processes (often separate containers).

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Celery Beat |
|---------|-----------|----------------|---------------------|
| Periodic tasks | `BGAppRefreshTaskRequest` | `PeriodicWorkRequest` | `beat_schedule` + `crontab` |
| Minimum interval | ~15 min (system decides) | 15 minutes | No minimum (can be seconds) |
| Exact timing | No (system decides) | No (approximate) | Yes (crontab precision) |
| Timezone | Device timezone | Device timezone | Configurable (use UTC) |
| Survives restart | Yes (system-managed) | Yes (Room DB) | Yes (Redis persistence) |
| Battery constraints | Yes (aggressive) | Yes (Doze mode) | No (server has unlimited power) |
| Custom schedule | Limited | Limited | Full cron syntax |
| Monitoring | Xcode console | WorkManager Inspector | Flower dashboard |

## Example: Complete Scheduled Setup

```python
# celery_config.py
from celery import Celery
from celery.schedules import crontab

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

celery_app.conf.beat_schedule = {
    # Health monitoring
    "health-check": {
        "task": "tasks.health_check",
        "schedule": 60.0,  # Every minute
    },

    # Data maintenance
    "cleanup-expired-tokens": {
        "task": "tasks.cleanup_expired_tokens",
        "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
    },

    # Reports
    "daily-metrics": {
        "task": "tasks.calculate_daily_metrics",
        "schedule": crontab(hour=1, minute=0),  # 1 AM UTC
    },

    "weekly-report": {
        "task": "tasks.generate_weekly_report",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),  # Monday 9 AM
    },
}
```

```bash
# docker-compose.yml additions
services:
  celery-worker:
    build: .
    command: celery -A celery_config.celery_app worker --loglevel=info
    depends_on:
      - redis

  celery-beat:
    build: .
    command: celery -A celery_config.celery_app beat --loglevel=info
    depends_on:
      - redis
```

## Key Takeaways

- Celery Beat is a scheduler process that sends tasks to the broker at configured times
- Use `timedelta` for interval-based schedules (every N seconds/minutes/hours)
- Use `crontab()` for calendar-based schedules (every Monday, 1st of month)
- Always schedule in UTC -- daylight saving time causes issues with local timezones
- Beat and workers are separate processes (separate containers in production)
- Unlike mobile, there are no minimum intervals or battery constraints
- Scheduled tasks must be defined as regular Celery tasks (`@celery_app.task`)
- Pass arguments via `args` and `kwargs` in the schedule configuration
- Mobile parallel: Celery Beat is like `PeriodicWorkRequest` (Android) or `BGAppRefreshTaskRequest` (iOS), but with exact timing and no OS restrictions
