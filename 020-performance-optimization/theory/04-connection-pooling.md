# Connection Pooling

## Why This Matters

On iOS, `URLSession` reuses TCP connections automatically -- you create a session once, and it maintains a pool of connections to your server. On Android, OkHttp's `ConnectionPool` keeps idle connections alive for reuse, avoiding the overhead of a TCP handshake on every request. You probably never had to configure this because the HTTP client libraries handle it by default.

Database connections are different. Opening a connection to PostgreSQL involves a TCP handshake, SSL negotiation, authentication, and session setup -- typically 50-100ms. If every API request opens a new database connection, you waste 50-100ms before any query runs. Connection pooling solves this by maintaining a set of pre-established connections that requests can borrow and return. SQLAlchemy has a built-in connection pool, but it needs proper configuration for production workloads.

## What Connection Pooling Is

Without pooling:

```
Request 1: [Open conn 50ms] [Query 5ms] [Close conn] = 55ms
Request 2: [Open conn 50ms] [Query 5ms] [Close conn] = 55ms
Request 3: [Open conn 50ms] [Query 5ms] [Close conn] = 55ms
```

With pooling:

```
Startup: [Open 5 connections]
Request 1: [Borrow conn 0ms] [Query 5ms] [Return conn] = 5ms
Request 2: [Borrow conn 0ms] [Query 5ms] [Return conn] = 5ms
Request 3: [Borrow conn 0ms] [Query 5ms] [Return conn] = 5ms
```

The pool maintains a fixed number of open connections. When a request needs a database connection, it borrows one from the pool. When done, it returns the connection to the pool instead of closing it.

## SQLAlchemy Pool Configuration

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/mydb",
    pool_size=5,          # Number of permanent connections
    max_overflow=10,      # Extra connections allowed when pool is full
    pool_timeout=30,      # Seconds to wait for a connection before error
    pool_recycle=1800,    # Recycle connections after 30 minutes
    pool_pre_ping=True,   # Test connections before using them
)
```

### Configuration Parameters Explained

| Parameter | Default | What It Does |
|-----------|---------|-------------|
| `pool_size` | 5 | Number of connections kept open permanently |
| `max_overflow` | 10 | Extra connections created when all `pool_size` are in use |
| `pool_timeout` | 30 | Seconds to wait for an available connection. Raises `TimeoutError` if exceeded |
| `pool_recycle` | -1 (off) | Seconds before a connection is recycled (replaced). Set to prevent stale connections |
| `pool_pre_ping` | False | If True, tests each connection with a SELECT 1 before use. Prevents "connection closed" errors |

**Total max connections** = `pool_size` + `max_overflow` = 15 with defaults.

**Mobile analogy:** `pool_size` is like OkHttp's `maxIdleConnections`. `max_overflow` is like allowing temporary extra connections when you're under load. `pool_timeout` is like a connection timeout on URLSession.

## Pool Types

SQLAlchemy supports several pool implementations:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, NullPool, StaticPool

# QueuePool (default) -- production use
engine = create_engine("postgresql://...", poolclass=QueuePool)

# NullPool -- no pooling, new connection every time
# Use for testing or short-lived scripts
engine = create_engine("postgresql://...", poolclass=NullPool)

# StaticPool -- single connection shared by all threads
# Use ONLY for SQLite in-memory databases in tests
engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)
```

| Pool Type | Connections | Use Case |
|-----------|------------|----------|
| `QueuePool` | Reusable pool with overflow | Production (default) |
| `NullPool` | New connection every time | Testing, short scripts, serverless |
| `StaticPool` | Single shared connection | SQLite in-memory tests |
| `AsyncAdaptedQueuePool` | Async version of QueuePool | Async SQLAlchemy with asyncpg |

## Monitoring Pool Usage

### Check pool status

```python
# See current pool state
print(engine.pool.status())
# Pool size: 5  Connections in pool: 3  Current overflow: 2  Current checked out: 4
```

### Pool events

```python
import logging
from sqlalchemy import event

logger = logging.getLogger("pool")


@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    logger.debug("Connection returned to pool")


@event.listens_for(engine, "connect")
def on_connect(dbapi_conn, connection_record):
    logger.info("New database connection created")
```

## Common Issues

### Pool Exhaustion

**Symptom:** Requests hang for `pool_timeout` seconds, then raise `TimeoutError`.

**Cause:** All connections are checked out and none are returned. Usually caused by:
- Not closing sessions properly
- Long-running queries holding connections
- Missing `session.close()` or context manager

**Fix:**

```python
# Always use context managers or FastAPI's Depends()
from sqlalchemy.orm import Session


# Good: context manager closes session automatically
with Session(engine) as session:
    users = session.execute(select(User)).scalars().all()
# Connection returned to pool here


# Good: FastAPI dependency injection
def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()  # Returns connection to pool
```

### Stale Connections

**Symptom:** Random "connection closed" or "server closed the connection unexpectedly" errors.

**Cause:** Database server closed idle connections (common after network changes or PostgreSQL restarts), but the pool still holds references to them.

**Fix:** Enable `pool_pre_ping` and set `pool_recycle`:

```python
engine = create_engine(
    "postgresql://...",
    pool_pre_ping=True,   # Tests connection before use
    pool_recycle=1800,    # Replace connections older than 30 minutes
)
```

## Production Settings for PostgreSQL

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/mydb",
    pool_size=10,          # Match your expected concurrent requests
    max_overflow=20,       # Allow bursts up to 30 total connections
    pool_timeout=30,       # Don't wait forever for a connection
    pool_recycle=1800,     # Recycle every 30 minutes
    pool_pre_ping=True,    # Always test before use
)
```

**Sizing guidelines:**
- `pool_size` should roughly match your typical concurrent request count
- `pool_size + max_overflow` should not exceed PostgreSQL's `max_connections` (default 100)
- If running multiple application instances, divide the pool across them: 4 instances x 25 connections = 100 total
- Monitor pool exhaustion and adjust based on actual usage

### Async Engine Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/mydb",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)
```

The parameters are identical. The async engine uses `AsyncAdaptedQueuePool` internally.

## Key Takeaways

1. **Connection pooling is essential for production.** Opening a new database connection per request wastes 50-100ms. The pool reuses existing connections.
2. **Configure `pool_size` based on your concurrency.** Default of 5 is fine for development but may be too small for production under load.
3. **Always enable `pool_pre_ping=True`.** This prevents stale connection errors with minimal overhead (one extra SELECT 1 per checkout).
4. **Set `pool_recycle`** to prevent connections from growing stale. 1800 seconds (30 minutes) is a common value.
5. **Use context managers or dependency injection** to ensure connections are always returned to the pool. Never leave a session unclosed.
6. **Monitor with `engine.pool.status()`** during development to understand your pool usage patterns.
