# Database Query Analysis

## Why This Matters

On iOS, you optimize Core Data fetch requests by setting `fetchBatchSize`, adding `NSFetchedResultsController` prefetching, and using the Core Data Performance instrument to see actual SQL queries. On Android, you use Room's `@Query` annotations with EXPLAIN to verify your queries use indexes. In both cases, you look at the actual queries your ORM generates to find the slow ones.

Python backend development is the same. SQLAlchemy generates SQL queries for you, and you need to see what it actually sends to PostgreSQL. A single missing index can turn a 5ms query into a 5-second query once your table grows past a few thousand rows. This chapter teaches you how to see, analyze, and optimize your database queries.

## SQLAlchemy Query Logging

The fastest way to see what queries SQLAlchemy generates is to enable echo mode on the engine:

```python
from sqlalchemy import create_engine

# Echo ALL SQL queries to the console
engine = create_engine("postgresql://user:pass@localhost/mydb", echo=True)
```

With `echo=True`, every query appears in your console:

```sql
INFO sqlalchemy.engine.Engine SELECT users.id, users.name, users.email
FROM users
WHERE users.id = %(id_1)s
INFO sqlalchemy.engine.Engine [generated in 0.00015s] {'id_1': 42}
```

**For production**, don't use `echo=True` (too noisy). Instead, configure Python's logging module:

```python
import logging

# Show only SQL queries at WARNING level or above
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

## EXPLAIN ANALYZE

EXPLAIN ANALYZE is PostgreSQL's profiler. It runs your query and shows exactly how the database executed it:

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';
```

Output:

```
Seq Scan on users  (cost=0.00..12.50 rows=1 width=64) (actual time=0.012..0.150 rows=1 loops=1)
  Filter: (email = 'alice@example.com'::text)
  Rows Removed by Filter: 499
Planning Time: 0.050 ms
Execution Time: 0.180 ms
```

### Reading Query Plans

| Term | Meaning | Good or Bad? |
|------|---------|-------------|
| **Seq Scan** | Full table scan -- reads every row | Bad for large tables |
| **Index Scan** | Uses an index to find rows directly | Good |
| **Index Only Scan** | Gets data from the index alone | Best |
| **Bitmap Index Scan** | Uses index to build a bitmap, then fetches | Good for medium selectivity |
| **Nested Loop** | For each outer row, scan inner table | Bad if inner table is large |
| **Hash Join** | Builds hash table of one side, probes with other | Good for equi-joins |
| **Sort** | Sorts rows (for ORDER BY or merge join) | Check if an index could avoid it |

**The key numbers:**
- `cost=0.00..12.50` -- Estimated cost (arbitrary units). Lower is better
- `rows=1` -- Estimated row count
- `actual time=0.012..0.150` -- Real time in milliseconds (startup..total)
- `Rows Removed by Filter: 499` -- Rows scanned but not returned (wasted work)

**Mobile analogy:** This is like Core Data's `-com.apple.CoreData.SQLDebug 1` flag that shows you the actual SQL and execution plan, or Room's query validation at compile time.

## Running EXPLAIN ANALYZE from SQLAlchemy

```python
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("EXPLAIN ANALYZE SELECT * FROM users WHERE email = :email"),
        {"email": "alice@example.com"},
    )
    for row in result:
        print(row[0])
```

Or for ORM queries:

```python
from sqlalchemy import select

stmt = select(User).where(User.email == "alice@example.com")

# Print the SQL without executing
print(stmt.compile(engine, compile_kwargs={"literal_binds": True}))
```

## Common Slow Query Patterns

### 1. Missing index on a filtered column

```python
# This query does a Seq Scan if 'email' has no index
session.execute(select(User).where(User.email == "alice@example.com"))
```

**Fix:** Add an index.

### 2. Full table scan on a large table

```python
# Returns ALL users then filters in Python -- terrible
users = session.execute(select(User)).scalars().all()
active_users = [u for u in users if u.is_active]
```

**Fix:** Filter in the database.

```python
active_users = session.execute(
    select(User).where(User.is_active == True)
).scalars().all()
```

### 3. Unnecessary columns in SELECT

```python
# Fetches all columns when you only need id and name
users = session.execute(select(User)).scalars().all()
names = [(u.id, u.name) for u in users]
```

**Fix:** Select only the columns you need.

```python
results = session.execute(select(User.id, User.name)).all()
```

### 4. ORDER BY without an index

```python
# If 'created_at' has no index, this requires a full sort
session.execute(select(User).order_by(User.created_at.desc()))
```

**Fix:** Add an index on columns used in ORDER BY.

## Adding Indexes with SQLAlchemy

### In the model definition

```python
from sqlalchemy import Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)  # Single column index
    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(index=True)

    # Composite index for queries that filter on both columns
    __table_args__ = (
        Index("ix_users_name_email", "name", "email"),
    )
```

### With Alembic migrations

```bash
alembic revision --autogenerate -m "add index on users.email"
alembic upgrade head
```

The migration file:

```python
def upgrade() -> None:
    op.create_index("ix_users_email", "users", ["email"])

def downgrade() -> None:
    op.drop_index("ix_users_email", "users")
```

## Logging Slow Queries with SQLAlchemy Events

Track queries that take too long using SQLAlchemy's event system:

```python
import time
import logging
from sqlalchemy import event

logger = logging.getLogger("slow_queries")
SLOW_QUERY_THRESHOLD = 0.5  # seconds


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start_time"] = time.perf_counter()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    duration = time.perf_counter() - conn.info["query_start_time"]
    if duration > SLOW_QUERY_THRESHOLD:
        logger.warning(
            "Slow query (%.3fs): %s | params: %s",
            duration,
            statement,
            parameters,
        )
```

**Mobile analogy:** This is like setting a breakpoint in Core Data's `executeFetchRequest` to log any fetch that takes longer than expected, or using StrictMode on Android to detect slow disk reads.

## Indexing Strategy

**When to add an index:**
- Columns used in `WHERE` clauses frequently
- Columns used in `ORDER BY`
- Foreign key columns (SQLAlchemy does NOT auto-index these)
- Columns used in `JOIN` conditions

**When NOT to add an index:**
- Small tables (< 1000 rows) -- Seq Scan is fine
- Columns with very low cardinality (e.g., boolean `is_active` with 50/50 split)
- Tables with heavy write workloads (indexes slow down INSERT/UPDATE)
- Columns rarely used in queries

## Key Takeaways

1. **Enable `echo=True` during development** to see every SQL query SQLAlchemy generates. Disable it in production.
2. **Use EXPLAIN ANALYZE** to see how PostgreSQL actually executes a query. Look for Seq Scan on large tables -- that usually means a missing index.
3. **Index foreign keys.** SQLAlchemy does not create indexes on foreign key columns automatically. Add them explicitly.
4. **Filter in the database, not in Python.** Never fetch all rows and filter in a loop. Use `WHERE` clauses.
5. **Log slow queries** using SQLAlchemy events. Set a threshold (e.g., 500ms) and log anything slower.
6. **Measure after adding indexes.** Run EXPLAIN ANALYZE before and after to confirm the index is actually used.
