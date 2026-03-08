# When to Use Background Tasks

## Why This Matters

On mobile, you routinely push work off the main thread: network calls go on a background queue, image processing happens on a utility thread, analytics events fire asynchronously. The goal is always the same -- keep the UI responsive.

Backend APIs have the exact same goal: **keep the response fast**. If your endpoint needs to send an email, generate a PDF, or update a search index, those operations shouldn't block the HTTP response. The user doesn't need to wait for an email to be sent before seeing "Registration successful."

This is the backend equivalent of `DispatchQueue.global().async {}` in Swift or `withContext(Dispatchers.IO) {}` in Kotlin -- except you have much more powerful tools for managing these background operations.

## The Decision Tree

When a request triggers work, ask yourself:

```
Does the response need the result of this work?
│
├── YES → Do it synchronously (in the request handler)
│         Example: Fetch user profile from DB to return it
│
└── NO → Is the work lightweight and fire-and-forget?
         │
         ├── YES → Use FastAPI BackgroundTasks
         │         Example: Send notification email, write audit log
         │
         └── NO → Use Celery
                   Example: Generate report, process video, retry on failure
```

## When to Use Each Approach

### Synchronous (In Request)

Do the work during the request when the response **depends on the result**.

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # Must fetch user to return it -- synchronous
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

### FastAPI BackgroundTasks

Use when the work is:
- Lightweight (completes in seconds)
- Fire-and-forget (no need to track success/failure)
- Not CPU-intensive (runs in the same process)

```python
@app.post("/orders")
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Create order (synchronous -- response needs the result)
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()

    # Send confirmation email (background -- response doesn't need this)
    background_tasks.add_task(send_order_confirmation, db_order.id)

    # Log analytics event (background -- response doesn't need this)
    background_tasks.add_task(log_analytics, "order_created", db_order.id)

    return db_order
```

### Celery Task Queue

Use when the work is:
- Heavy or long-running (minutes, not seconds)
- Needs retry logic (network calls, external APIs)
- Needs persistence (must complete even if server restarts)
- CPU-intensive (image processing, report generation)
- Needs scheduling (run every hour, every day)

```python
@app.post("/reports")
async def generate_report(report_request: ReportRequest):
    # Dispatch to Celery -- runs in a separate worker process
    task = generate_report_task.delay(
        report_request.start_date,
        report_request.end_date,
        report_request.format
    )
    # Return task ID for status polling
    return {"task_id": task.id, "status": "queued"}
```

## Common Background Task Examples

| Task | Approach | Why |
|------|----------|-----|
| Send email | BackgroundTasks | Quick, fire-and-forget |
| Write audit log | BackgroundTasks | Quick, non-critical |
| Update cache | BackgroundTasks | Quick, fire-and-forget |
| Generate PDF report | Celery | Long-running, CPU-intensive |
| Process uploaded video | Celery | Very long-running, needs progress tracking |
| Sync with external API | Celery | Needs retries on failure |
| Send bulk emails (1000+) | Celery | Long-running, needs rate limiting |
| Daily database cleanup | Celery Beat | Scheduled, periodic |
| Weekly analytics report | Celery Beat | Scheduled, long-running |

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python Backend |
|---------|-----------|----------------|----------------|
| Quick background work | `DispatchQueue.global().async` | `withContext(Dispatchers.IO)` | `BackgroundTasks.add_task()` |
| Heavy background work | `BGProcessingTaskRequest` | `WorkManager.enqueue()` | `celery_task.delay()` |
| Fire-and-forget | `Task { ... }` | `launch(Dispatchers.IO)` | `BackgroundTasks` |
| Track completion | `async let result = ...` | `WorkInfo.state` | `AsyncResult.status` |
| Persist across restart | `BGTaskScheduler` | `WorkManager` (Room DB) | Celery + Redis broker |
| Schedule periodic | `BGAppRefreshTaskRequest` | `PeriodicWorkRequest` | `Celery Beat` |

## Anti-Patterns

### Using BackgroundTasks for CPU-Heavy Work

```python
# BAD: Blocks the FastAPI worker process
@app.post("/process-image")
async def process_image(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(resize_all_thumbnails, file)  # CPU-bound!
    return {"message": "Processing"}

# GOOD: Offload to Celery worker
@app.post("/process-image")
async def process_image(file: UploadFile):
    file_path = save_temp_file(file)
    resize_thumbnails_task.delay(file_path)  # Runs in separate process
    return {"message": "Processing"}
```

### Not Using Background Tasks When You Should

```python
# BAD: User waits 3 seconds for email to send
@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    send_welcome_email(db_user.email)  # 3 seconds of waiting!
    return db_user

# GOOD: Response is instant
@app.post("/register")
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_user = create_user(db, user)
    background_tasks.add_task(send_welcome_email, db_user.email)
    return db_user  # Returns immediately
```

## Key Takeaways

- **If the response needs the result** -- do it synchronously in the request handler
- **If it's lightweight and fire-and-forget** -- use FastAPI `BackgroundTasks`
- **If it's heavy, needs retries, or needs scheduling** -- use Celery
- BackgroundTasks runs in the same process (shares the event loop)
- Celery runs in separate worker processes (true isolation)
- Never use BackgroundTasks for CPU-intensive work -- it blocks your API
- Mobile parallel: BackgroundTasks is like `DispatchQueue.global().async`, Celery is like `WorkManager`
