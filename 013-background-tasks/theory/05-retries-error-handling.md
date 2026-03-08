# Retries and Error Handling

## Why This Matters

On mobile, WorkManager's `setBackoffPolicy()` handles retries automatically -- if a network call fails, the system retries with exponential backoff. BGTaskScheduler re-schedules failed tasks. You configure the policy, and the system handles the rest.

Celery provides the same pattern: **automatic retries with exponential backoff and jitter**. But since you're building the backend, you have much more control -- you decide which exceptions trigger retries, how long to wait, and what happens when all retries are exhausted.

## Automatic Retries with `autoretry_for`

The simplest way to add retries: tell Celery which exceptions should trigger a retry.

```python
from celery import Celery

celery_app = Celery("worker", broker="redis://localhost:6379/0")

@celery_app.task(
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,        # Exponential backoff: 1s, 2s, 4s, 8s...
    retry_backoff_max=600,     # Max wait: 10 minutes
    retry_jitter=True,         # Add randomness to prevent thundering herd
    max_retries=5              # Give up after 5 retries
)
def send_email(to: str, subject: str, body: str):
    """Send email with automatic retry on network errors."""
    smtp_client = connect_to_smtp()
    smtp_client.send(to=to, subject=subject, body=body)
```

### How Exponential Backoff Works

```
Attempt 1: Immediate
Attempt 2: Wait 1 second
Attempt 3: Wait 2 seconds
Attempt 4: Wait 4 seconds
Attempt 5: Wait 8 seconds
Attempt 6: Wait 16 seconds (capped at retry_backoff_max)
```

With `retry_jitter=True`, each wait time has randomness added (e.g., 1s becomes 0.7s-1.3s). This prevents the **thundering herd problem** -- if 100 tasks all fail at the same time, they won't all retry at the exact same moment.

### Retry Parameters Explained

| Parameter | Default | Description |
|-----------|---------|-------------|
| `autoretry_for` | `()` | Tuple of exception types that trigger retry |
| `retry_backoff` | `False` | `True` for exponential backoff, or int for fixed seconds |
| `retry_backoff_max` | `600` | Maximum seconds between retries |
| `retry_jitter` | `True` | Add randomness to backoff |
| `max_retries` | `3` | Maximum retry attempts (None for unlimited) |
| `default_retry_delay` | `180` | Seconds between retries when backoff is False |

## Manual Retry with `self.retry()`

For more control, use `bind=True` to access `self` and call `self.retry()` manually:

```python
@celery_app.task(bind=True, max_retries=3)
def process_payment(self, order_id: int):
    """Process payment with manual retry logic."""
    try:
        result = payment_gateway.charge(order_id)
        return {"order_id": order_id, "status": "charged"}

    except PaymentGatewayTimeout as exc:
        # Retry with custom countdown
        raise self.retry(
            exc=exc,        # Original exception (for logging)
            countdown=60    # Wait 60 seconds before retry
        )

    except PaymentDeclined:
        # Don't retry -- this is a business logic failure
        return {"order_id": order_id, "status": "declined"}
```

### `bind=True` and `self`

When `bind=True`, the task receives `self` as the first argument, giving access to:

```python
@celery_app.task(bind=True, max_retries=5)
def my_task(self, data: str):
    # Current retry count
    print(f"Attempt {self.request.retries + 1} of {self.max_retries + 1}")

    # Task ID
    print(f"Task ID: {self.request.id}")

    # Manual retry
    try:
        do_work(data)
    except TransientError as exc:
        raise self.retry(exc=exc, countdown=30)
```

## Combining Automatic and Manual Retry

```python
@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError,),    # Auto-retry network errors
    retry_backoff=True,
    max_retries=5
)
def sync_external_api(self, resource_id: int):
    """Mix of automatic and manual retry."""
    try:
        data = fetch_from_api(resource_id)  # ConnectionError auto-retried

        if data.get("status") == "processing":
            # Not an error, but not ready -- retry manually
            raise self.retry(countdown=30)

        return save_data(data)

    except ValidationError:
        # Don't retry validation errors -- they won't fix themselves
        log_error(f"Invalid data for resource {resource_id}")
        return {"status": "failed", "reason": "invalid_data"}
```

## Error Callbacks

Handle the case when all retries are exhausted:

```python
@celery_app.task
def on_task_failure(request, exc, traceback):
    """Called when a task fails after all retries."""
    print(f"Task {request.id} failed permanently: {exc}")
    # Send alert, log to error tracking, etc.
    send_alert_to_ops(
        task_id=request.id,
        error=str(exc),
        task_name=request.task
    )

@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    max_retries=3,
    link_error=on_task_failure.s()  # Call this on final failure
)
def critical_task(self, data: str):
    """Task with error callback."""
    process_critical_data(data)
```

### Using `on_failure` Handler

```python
@celery_app.task(bind=True, max_retries=3)
def send_notification(self, user_id: int, message: str):
    """Task with built-in failure handler."""
    try:
        push_notification(user_id, message)
    except NotificationServiceDown as exc:
        raise self.retry(exc=exc, countdown=60)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries."""
        user_id = args[0]
        # Fall back to email notification
        send_email_fallback(user_id, f"Notification failed: {args[1]}")
```

## Retry-Safe (Idempotent) Tasks

Tasks may execute more than once due to retries. Make them **idempotent** -- running them twice should produce the same result.

```python
# BAD: Not idempotent -- double-charges on retry
@celery_app.task(autoretry_for=(TimeoutError,), max_retries=3)
def charge_user(user_id: int, amount: float):
    payment_service.charge(user_id, amount)

# GOOD: Idempotent -- uses unique key to prevent duplicates
@celery_app.task(autoretry_for=(TimeoutError,), max_retries=3)
def charge_user(user_id: int, amount: float, idempotency_key: str):
    # Payment service checks if this key was already processed
    payment_service.charge(
        user_id,
        amount,
        idempotency_key=idempotency_key
    )
```

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Celery |
|---------|-----------|----------------|---------------|
| Auto retry | BGTaskScheduler re-schedules | `WorkManager` auto-retries | `autoretry_for=(Exception,)` |
| Exponential backoff | Custom implementation | `BackoffPolicy.EXPONENTIAL` | `retry_backoff=True` |
| Max retries | Custom counter | `setBackoffCriteria(maxRetries)` | `max_retries=5` |
| Jitter | Custom implementation | Built-in with `BackoffPolicy` | `retry_jitter=True` |
| Manual retry | Re-submit task | `Result.retry()` | `self.retry(exc=exc)` |
| Retry countdown | Custom delay | `setInitialDelay()` | `countdown=60` |
| Failure callback | Completion handler | `WorkInfo.State.FAILED` observer | `link_error` / `on_failure` |
| Idempotency | Developer responsibility | Developer responsibility | Developer responsibility |

## Common Patterns

### Retry with Logging

```python
@celery_app.task(bind=True, max_retries=5, retry_backoff=True)
def fetch_external_data(self, url: str):
    """Fetch with detailed retry logging."""
    attempt = self.request.retries + 1
    print(f"[Attempt {attempt}/{self.max_retries + 1}] Fetching {url}")

    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as exc:
        print(f"[Attempt {attempt}] Timeout, retrying...")
        raise self.retry(exc=exc)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code >= 500:
            print(f"[Attempt {attempt}] Server error {exc.response.status_code}, retrying...")
            raise self.retry(exc=exc)
        # Don't retry 4xx errors
        raise
```

### Different Retry Strategies per Exception

```python
@celery_app.task(bind=True, max_retries=5)
def process_webhook(self, payload: dict):
    """Different retry behavior for different failures."""
    try:
        validate_and_process(payload)
    except RateLimitError as exc:
        # Rate limited -- wait longer
        raise self.retry(exc=exc, countdown=120)
    except ServiceUnavailable as exc:
        # Service down -- exponential backoff
        countdown = 2 ** self.request.retries * 10
        raise self.retry(exc=exc, countdown=min(countdown, 600))
    except ValidationError:
        # Bad data -- don't retry
        log_invalid_webhook(payload)
        return {"status": "invalid"}
```

## Key Takeaways

- `autoretry_for` + `retry_backoff=True` is the standard pattern for automatic retries
- Always use `retry_jitter=True` to prevent thundering herd
- Use `bind=True` + `self.retry()` when you need custom retry logic per exception
- Make tasks idempotent -- they may run more than once due to retries
- Use `link_error` or `on_failure` to handle permanent failures
- Don't retry business logic failures (validation errors, declined payments)
- Do retry transient failures (network timeouts, service unavailable, rate limits)
- Mobile parallel: `autoretry_for` is like `WorkManager.setBackoffPolicy()` -- declare the policy, Celery handles the rest
