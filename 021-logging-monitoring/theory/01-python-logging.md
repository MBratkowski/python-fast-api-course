# Python Logging

## Why This Matters

On iOS, you call `os_log(.info, "User tapped login")` and the message appears in Console.app with a timestamp, log level, and subsystem tag. On Android, you call `Timber.i("User tapped login")` and it shows up in Logcat with a tag and priority level. Both platforms give you leveled, filterable logging out of the box.

Python has the same thing: the `logging` module in the standard library. It's been there since Python 2.3, and every serious Python application uses it. When you see `print()` statements scattered through backend code, that's the equivalent of shipping an iOS app with `print()` instead of `os.Logger` -- it works during development but fails you in production.

## The Problem with print()

```python
# This is what beginners do
print("Starting server...")
print(f"User {user_id} logged in")
print(f"Error: {e}")
```

Why this fails in production:

| Problem | print() | logging |
|---------|---------|---------|
| Log levels | Everything is the same | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| Filtering | Can't filter by severity | Filter by level, logger name, module |
| Output destination | stdout only | Console, files, network, email, anything |
| Timestamps | Manual (if you add them) | Automatic via formatters |
| Performance | Always runs | Level check before string formatting |
| Thread safety | Not guaranteed | Built-in thread safety |

**The rule:** `print()` is for scripts. `logging` is for applications.

## Core Concepts

Python's logging module has four key components:

```
Logger --> Handler --> Formatter --> Output
  |           |            |
  |           |            +-- Controls the message format
  |           +-- Controls WHERE the message goes (file, console, network)
  +-- Controls WHAT gets logged (name, level filtering)
```

### 1. Loggers

A logger is a named channel for log messages. You create one with `getLogger()`:

```python
import logging

# Get a logger named after the current module
logger = logging.getLogger(__name__)

# Use it
logger.debug("Low-level detail")
logger.info("Normal operation")
logger.warning("Something unexpected")
logger.error("Something failed")
logger.critical("System is broken")
```

**Mobile analogy:** On iOS, each subsystem has its own `os.Logger(subsystem:category:)`. On Android, each class uses its own Timber tag. Python loggers work the same way -- each module gets its own named logger.

### 2. Log Levels

Every log message has a severity level:

| Level | Value | When to Use | Mobile Equivalent |
|-------|-------|-------------|-------------------|
| `DEBUG` | 10 | Detailed diagnostic info | `.debug` / `Log.d()` |
| `INFO` | 20 | Normal operation events | `.info` / `Log.i()` |
| `WARNING` | 30 | Something unexpected but not an error | `.default` / `Log.w()` |
| `ERROR` | 40 | An operation failed | `.error` / `Log.e()` |
| `CRITICAL` | 50 | System is unusable | `.fault` / `Log.wtf()` |

A logger's level acts as a filter. If you set it to `WARNING`, only `WARNING`, `ERROR`, and `CRITICAL` messages get through:

```python
logger = logging.getLogger("myapp")
logger.setLevel(logging.WARNING)

logger.debug("Won't appear")    # Level 10 < 30: filtered
logger.info("Won't appear")     # Level 20 < 30: filtered
logger.warning("Will appear")   # Level 30 >= 30: passes
logger.error("Will appear")     # Level 40 >= 30: passes
```

### 3. Handlers

A handler controls WHERE log messages go. You can attach multiple handlers to a single logger:

```python
import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)  # Logger accepts everything

# Handler 1: Console output (INFO and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Handler 2: File output (DEBUG and above)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Handler 3: Error file (ERROR and above)
error_handler = logging.FileHandler("errors.log")
error_handler.setLevel(logging.ERROR)
logger.addHandler(error_handler)
```

Now `logger.info("hello")` goes to console and `app.log`, but `logger.error("failed")` goes to all three destinations.

**Mobile analogy:** On iOS, you can log to Console.app and a file simultaneously. On Android, Logcat is the default but you can add Timber trees that write to files or Crashlytics. Python handlers are the same concept.

### 4. Formatters

A formatter controls the message format:

```python
import logging

formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("myapp")
logger.addHandler(handler)

logger.info("Server started on port 8000")
# Output: 2026-03-08 12:00:00 [INFO] myapp: Server started on port 8000
```

Common format placeholders:

| Placeholder | What It Shows | Example |
|-------------|--------------|---------|
| `%(asctime)s` | Timestamp | `2026-03-08 12:00:00` |
| `%(levelname)s` | Log level name | `INFO` |
| `%(name)s` | Logger name | `myapp.auth` |
| `%(message)s` | The log message | `User logged in` |
| `%(module)s` | Module name | `auth` |
| `%(funcName)s` | Function name | `login` |
| `%(lineno)d` | Line number | `42` |

## Putting It All Together

Here's a complete logging setup for a FastAPI application:

```python
import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """Configure application-wide logging."""

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Console handler with readable format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # File handler with detailed format
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Attach handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


# In your FastAPI app:
# setup_logging()
# logger = logging.getLogger(__name__)
# logger.info("Application started")
```

## The getLogger(__name__) Pattern

Always use `__name__` as the logger name:

```python
# In src/api/users.py
logger = logging.getLogger(__name__)  # Logger named "src.api.users"

# In src/services/auth.py
logger = logging.getLogger(__name__)  # Logger named "src.services.auth"
```

This creates a hierarchy based on your package structure. You can then configure logging for an entire package:

```python
# Set all "src.api" loggers to DEBUG
logging.getLogger("src.api").setLevel(logging.DEBUG)

# But keep "src.services" at INFO
logging.getLogger("src.services").setLevel(logging.INFO)
```

**Mobile analogy:** This is like using `Logger(subsystem: "com.myapp.networking", category: "api")` on iOS -- a hierarchical naming scheme that lets you filter logs by subsystem.

## Logging in FastAPI

```python
import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info("Fetching user %d", user_id)

    try:
        user = await fetch_user(user_id)
        logger.debug("Found user: %s", user.name)
        return user
    except UserNotFoundError:
        logger.warning("User %d not found", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error("Failed to fetch user %d: %s", user_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Important:** Use `%s` and `%d` placeholders, not f-strings:

```python
# Good: string formatting is deferred (skipped if level is filtered)
logger.debug("Processing user %d", user_id)

# Bad: f-string is always evaluated, even if DEBUG is filtered out
logger.debug(f"Processing user {user_id}")
```

## Key Takeaways

1. **Never use `print()` in production code.** Use `logging.getLogger(__name__)` instead.
2. **Loggers are named and hierarchical.** Use `__name__` so the logger name matches your module path.
3. **Handlers control output destination.** Use `StreamHandler` for console, `FileHandler` for files. You can attach multiple handlers.
4. **Formatters control message shape.** Include timestamp, level, logger name, and message at minimum.
5. **Log levels are filters.** Set the logger level to control what gets through. In production, use `INFO`; in development, use `DEBUG`.
6. **Use lazy formatting** (`logger.info("user %d", user_id)`) instead of f-strings to avoid unnecessary string construction.
