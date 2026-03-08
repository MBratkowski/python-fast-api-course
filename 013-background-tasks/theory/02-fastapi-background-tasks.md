# FastAPI BackgroundTasks

## Why This Matters

On mobile, when you need to fire off a quick operation after returning to the user -- like logging an analytics event or updating a local cache -- you'd use something like `Task { ... }` in Swift or `launch(Dispatchers.IO) { ... }` in Kotlin. The user sees the result immediately, and the background work happens silently.

FastAPI's `BackgroundTasks` does exactly this for HTTP endpoints. After the response is sent to the client, your background task functions execute. The client never waits for them, and the API stays responsive.

## How BackgroundTasks Works

FastAPI's `BackgroundTasks` is a parameter you inject into your endpoint. You add task functions to it, and they execute **after** the response is sent.

```
Client Request
     │
     ▼
┌─────────────┐
│  Endpoint    │
│  handler     │──→ background_tasks.add_task(fn, args...)
│  runs        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Response    │──→ Client receives response HERE
│  sent        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Background  │──→ Task functions execute after response
│  tasks run   │
└─────────────┘
```

## Basic Usage

### Injecting BackgroundTasks

FastAPI automatically provides `BackgroundTasks` when you include it as a parameter:

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_notification(email: str, message: str = ""):
    """A regular function that runs in the background."""
    with open("notifications.log", mode="a") as f:
        f.write(f"Notification for {email}: {message}\n")

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    # Add task with positional and keyword arguments
    background_tasks.add_task(write_notification, email, message="Welcome!")

    # Response returns immediately -- task runs after
    return {"message": "Notification will be sent"}
```

### Sync and Async Task Functions

Background task functions can be either sync or async:

```python
# Sync function -- runs in a thread pool
def sync_task(data: str):
    """Sync tasks are automatically run in a thread pool."""
    import time
    time.sleep(1)  # Safe -- runs in thread, not event loop
    print(f"Processed: {data}")

# Async function -- runs on the event loop
async def async_task(data: str):
    """Async tasks run on the event loop."""
    import asyncio
    await asyncio.sleep(1)
    print(f"Processed: {data}")

@app.post("/process")
async def process(background_tasks: BackgroundTasks):
    # Both work the same way
    background_tasks.add_task(sync_task, "sync-data")
    background_tasks.add_task(async_task, "async-data")
    return {"message": "Processing"}
```

### Multiple Tasks

You can add multiple background tasks. They execute sequentially in the order they were added:

```python
@app.post("/orders")
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_order = create_order_in_db(db, order)

    # All three run sequentially after response
    background_tasks.add_task(send_order_confirmation, db_order.id)
    background_tasks.add_task(update_inventory, db_order.items)
    background_tasks.add_task(log_analytics, "order_created", db_order.id)

    return db_order
```

## BackgroundTasks in Dependencies

A powerful feature: dependencies can add their own background tasks. FastAPI **merges** all background tasks from the endpoint and its dependencies into a single list.

```python
from typing import Annotated
from fastapi import BackgroundTasks, Depends, FastAPI

app = FastAPI()

def write_log(message: str):
    with open("log.txt", mode="a") as f:
        f.write(f"{message}\n")

def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    """Dependency that adds its own background task."""
    if q:
        # This task gets merged with endpoint's tasks
        background_tasks.add_task(write_log, f"Query received: {q}")
    return q

@app.post("/items/")
async def create_item(
    background_tasks: BackgroundTasks,
    q: Annotated[str | None, Depends(get_query)] = None
):
    # Endpoint adds its own task
    background_tasks.add_task(write_log, "Item created")
    return {"message": "Item created", "query": q}
```

When called with `?q=search`, both `"Query received: search"` and `"Item created"` are logged -- the dependency's task and the endpoint's task are merged.

## Passing Arguments

`add_task()` accepts the function followed by positional and keyword arguments:

```python
def process_data(item_id: int, action: str, notify: bool = False):
    """Task function with multiple parameters."""
    print(f"Processing {action} for item {item_id}")
    if notify:
        send_notification(item_id)

@app.post("/items/{item_id}")
async def update_item(
    item_id: int,
    background_tasks: BackgroundTasks
):
    # Positional args after function, keyword args too
    background_tasks.add_task(
        process_data,      # function
        item_id,           # positional arg
        "update",          # positional arg
        notify=True        # keyword arg
    )
    return {"message": "Updated"}
```

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | FastAPI |
|---------|-----------|----------------|---------|
| Fire-and-forget | `Task { work() }` | `scope.launch { work() }` | `background_tasks.add_task(work)` |
| Thread handling | `DispatchQueue.global().async` | `withContext(Dispatchers.IO)` | Sync tasks auto-use thread pool |
| Multiple tasks | Multiple `Task { }` blocks | Multiple `launch { }` calls | Multiple `add_task()` calls |
| After response | N/A (no HTTP) | N/A (no HTTP) | Tasks run after response sent |
| Merge from deps | N/A | N/A | Dependency tasks merge with endpoint tasks |

## Common Patterns

### Audit Logging

```python
def log_audit_event(
    user_id: int,
    action: str,
    resource: str,
    resource_id: int
):
    """Log user actions for audit trail."""
    event = {
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    # Write to audit log (file, database, or external service)
    save_audit_event(event)

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    delete_user_from_db(user_id)
    background_tasks.add_task(
        log_audit_event,
        current_user.id,
        "delete",
        "user",
        user_id
    )
    return {"message": "User deleted"}
```

### Cache Warming

```python
def warm_cache(user_id: int):
    """Pre-populate cache after data change."""
    user = get_user_from_db(user_id)
    cache.set(f"user:{user_id}", user, ttl=3600)

@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdate,
    background_tasks: BackgroundTasks
):
    user = update_user_in_db(user_id, data)
    background_tasks.add_task(warm_cache, user_id)
    return user
```

## Anti-Patterns

### CPU-Heavy Work in BackgroundTasks

```python
# BAD: Blocks the FastAPI worker
def generate_report(data: list[dict]):
    """CPU-intensive work -- don't do this in BackgroundTasks."""
    for row in data:  # 100,000 rows
        process_row(row)  # Heavy computation

# GOOD: Use Celery for CPU-intensive work
generate_report_task.delay(data)
```

### Relying on BackgroundTasks for Critical Work

```python
# BAD: If the server crashes, the task is lost
background_tasks.add_task(charge_credit_card, order_id)

# GOOD: Use Celery with persistence for critical operations
charge_credit_card_task.delay(order_id)
```

### Accessing Request-Scoped Objects

```python
# BAD: DB session may be closed by the time task runs
def update_stats(db: Session, user_id: int):
    db.query(User).filter(User.id == user_id).update({"visits": User.visits + 1})
    db.commit()

background_tasks.add_task(update_stats, db, user_id)  # db session closed!

# GOOD: Create a new session inside the task
def update_stats(user_id: int):
    with SessionLocal() as db:
        db.query(User).filter(User.id == user_id).update({"visits": User.visits + 1})
        db.commit()

background_tasks.add_task(update_stats, user_id)
```

## Key Takeaways

- `BackgroundTasks` is injected as a parameter -- FastAPI provides it automatically
- Tasks execute **after** the response is sent to the client
- Sync task functions run in a thread pool; async functions run on the event loop
- Multiple `add_task()` calls execute sequentially in order
- Dependencies can add their own tasks -- FastAPI merges them all
- Pass arguments after the function in `add_task(fn, arg1, arg2, key=val)`
- Never use BackgroundTasks for CPU-heavy work (blocks the worker process)
- Never rely on BackgroundTasks for critical operations (no persistence, no retries)
- For heavy, persistent, or retryable work, use Celery (next topic)
