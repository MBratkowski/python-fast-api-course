# Project: Profile and Optimize a Slow API

## Overview

You are given a deliberately slow FastAPI application with multiple performance problems: N+1 queries, missing indexes, no connection pool configuration, blocking sync calls in async endpoints, and unoptimized data processing. Your job is to profile the application, identify the bottlenecks, and fix them -- measuring before and after performance for each optimization.

This project ties together everything from Module 020: profiling, query analysis, N+1 fixes, connection pooling, async best practices, and benchmarking.

## Requirements

### 1. Profiling

- [ ] Profile the `/users` endpoint with cProfile to identify the top 3 bottlenecks
- [ ] Profile the `/users/{id}/posts` endpoint to find the N+1 query
- [ ] Create a timing middleware that logs request duration for every endpoint
- [ ] Document findings in a `PROFILING_REPORT.md` with function names and cumulative times

### 2. Query Optimization

- [ ] Fix all N+1 queries using `selectinload` or `joinedload`
- [ ] Add database indexes on columns used in WHERE and ORDER BY clauses
- [ ] Add an index on the `posts.author_id` foreign key column
- [ ] Verify query improvements with EXPLAIN ANALYZE (or echo=True for SQLite)

### 3. Connection Pooling

- [ ] Configure SQLAlchemy engine with production pool settings
- [ ] Set `pool_size`, `max_overflow`, `pool_timeout`, and `pool_recycle`
- [ ] Enable `pool_pre_ping` for connection health checks
- [ ] Add pool status logging on application startup

### 4. Async Optimization

- [ ] Identify endpoints that block the event loop with sync code
- [ ] Convert blocking endpoints to use `async def` with async I/O, or move them to `def` (sync)
- [ ] Use `asyncio.gather` for the `/dashboard` endpoint that fetches multiple resources
- [ ] Verify no sync sleep or sync HTTP calls exist in async endpoints

### 5. Benchmarking

- [ ] Measure response time for each endpoint before and after optimization
- [ ] Record min, avg, and p95 latency for the top 3 endpoints
- [ ] Document results in `BENCHMARK_RESULTS.md` with before/after comparison
- [ ] Verify at least 50% improvement on the slowest endpoint

## Starter Template

Create the following file structure:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with timing middleware
│   ├── database.py          # Engine, session, pool configuration
│   ├── models.py            # User, Post, Comment models (SQLAlchemy)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py         # /users endpoints (has N+1 queries)
│   │   ├── posts.py         # /posts endpoints (missing indexes)
│   │   └── dashboard.py     # /dashboard endpoint (sequential I/O)
│   └── services/
│       ├── __init__.py
│       ├── user_service.py  # User business logic
│       └── post_service.py  # Post business logic
├── benchmarks/
│   ├── profile_endpoints.py # cProfile scripts
│   └── benchmark_results.py # Before/after timing
├── PROFILING_REPORT.md
├── BENCHMARK_RESULTS.md
└── tests/
    ├── __init__.py
    ├── test_performance.py  # Query count assertions
    └── conftest.py          # Test fixtures
```

### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# TODO: Configure pool settings for production
engine = create_engine(
    "sqlite:///./app.db",
    # Add: pool_size, max_overflow, pool_timeout, pool_recycle, pool_pre_ping
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### models.py

```python
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()  # TODO: Add index
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # TODO: Add index
    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post")


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))  # TODO: Add index
    post: Mapped["Post"] = relationship(back_populates="comments")
```

### routes/users.py (intentionally slow)

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

router = APIRouter()


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    # BUG: N+1 query -- fetches users then accesses .posts on each
    users = db.execute(select(User)).scalars().all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "post_count": len(user.posts),  # Triggers N separate queries!
        }
        for user in users
    ]
```

## Success Criteria

When complete, you should be able to:

1. All N+1 queries are eliminated (verified by query counting in tests)
2. Database indexes exist on `users.email`, `posts.author_id`, and `comments.post_id`
3. Connection pool is configured with explicit `pool_size`, `max_overflow`, and `pool_pre_ping`
4. No blocking sync calls exist inside `async def` endpoints
5. The `/dashboard` endpoint uses `asyncio.gather` for concurrent data fetching
6. Response time for the slowest endpoint is reduced by at least 50% (documented in BENCHMARK_RESULTS.md)

## Stretch Goals

- Add a Locust load test file (`locustfile.py`) that simulates realistic user traffic
- Add memory profiling with `tracemalloc` to detect memory leaks under load
- Add a slow query logging middleware using SQLAlchemy events (log queries > 100ms)
- Add a `/metrics` endpoint that reports pool status and request timing histograms
