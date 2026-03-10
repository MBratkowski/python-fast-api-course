# Module 020: Performance Optimization

## Why This Module?

On iOS, you open Instruments, attach to your app, and the Time Profiler shows you exactly which method is eating 80% of your CPU time. On Android, you open Android Studio's CPU Profiler, record a trace, and see the flame chart pinpointing the slow function. You've been profiling code your entire career -- you just did it with different tools.

Backend performance optimization is the same discipline. Instead of Instruments, you use cProfile. Instead of Core Data fetch request tuning, you use SQLAlchemy eager loading. Instead of URLSession connection reuse, you configure SQLAlchemy's connection pool. The concepts transfer directly -- this module teaches you the Python-specific tools.

## What You'll Learn

- Profiling Python code with cProfile, line_profiler, and snakeviz
- Analyzing database queries with EXPLAIN ANALYZE and SQLAlchemy echo mode
- Identifying and fixing N+1 query problems with eager loading strategies
- Configuring SQLAlchemy connection pooling for production workloads
- Choosing between async and sync FastAPI endpoints for optimal throughput
- Load testing your API with Locust and micro-benchmarking with timeit

## Mobile Developer Context

You've optimized mobile apps. Now you optimize backend services.

**Performance Optimization Across Platforms:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| CPU profiling | Instruments Time Profiler | Android Studio CPU Profiler | cProfile + snakeviz |
| Memory profiling | Instruments Allocations | Android Studio Memory Profiler | memory_profiler / tracemalloc |
| Query optimization | Core Data fetch requests, NSFetchedResultsController | Room @Query with EXPLAIN | SQLAlchemy echo, EXPLAIN ANALYZE |
| Lazy vs eager loading | Core Data faulting / prefetching | Room @Relation / @Transaction | SQLAlchemy selectinload / joinedload |
| Connection reuse | URLSession connection pool | OkHttp ConnectionPool | SQLAlchemy engine pool (QueuePool) |
| Concurrency | GCD / Swift async-await | Kotlin coroutines | asyncio / FastAPI async endpoints |
| Performance testing | XCTest measure blocks | Android Benchmark library | Locust / timeit / time.perf_counter |

**Key Differences from Mobile Profiling:**
- Mobile profiling focuses on UI thread (main thread) responsiveness. Backend profiling focuses on request throughput and latency percentiles
- Mobile N+1 problems happen with Core Data faults or Room lazy relations. Backend N+1 problems happen with ORM lazy loading across network round-trips to a database -- much more expensive
- Mobile connection pooling is mostly handled by the HTTP client. Backend connection pooling to PostgreSQL must be explicitly configured
- Backend performance is measured in requests per second and p95/p99 latency, not frame drops

## Prerequisites

- [ ] SQLAlchemy knowledge from Module 007-008
- [ ] FastAPI fundamentals from Modules 003-005
- [ ] Async/await understanding from Module 012
- [ ] Basic understanding of database queries (Module 006)

## Topics

### Theory
1. Profiling with cProfile -- Python profiling tools, reading profiler output, snakeviz visualization
2. Database Query Analysis -- SQLAlchemy echo, EXPLAIN ANALYZE, index strategies
3. Solving N+1 Queries -- The N+1 problem, selectinload, joinedload, subqueryload
4. Connection Pooling -- SQLAlchemy pool configuration, pool types, production settings
5. Async Best Practices -- When async helps, blocking pitfalls, asyncio.gather
6. Load Testing with Locust -- Locustfiles, interpreting results, CI integration

### Exercises
1. Profile Code -- Use cProfile to find bottlenecks and optimize
2. Fix N+1 Queries -- Apply eager loading to eliminate N+1 problems
3. Benchmarking -- Measure and compare function performance

### Project
Profile and optimize a deliberately slow FastAPI application.

## Time Estimate

- Theory: ~90 minutes
- Exercises: ~60 minutes
- Project: ~120 minutes

## Example: Fixing an N+1 Query

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# N+1 Problem -- BAD: 1 query for authors + N queries for books
authors = session.execute(select(Author)).scalars().all()
for author in authors:
    print(author.books)  # Each access triggers a separate query!

# N+1 Fix -- GOOD: 2 queries total (authors + books with IN clause)
authors = session.execute(
    select(Author).options(selectinload(Author.books))
).scalars().all()
for author in authors:
    print(author.books)  # Already loaded, no extra query
```

## Example: Profiling a Slow Function

```python
import cProfile
import pstats

def slow_function():
    total = 0
    for i in range(10000):
        total += sum(range(i))
    return total

# Profile it
profiler = cProfile.Profile()
profiler.enable()
slow_function()
profiler.disable()

# See the top bottlenecks
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(5)
```

## Example: Concurrent I/O with asyncio.gather

```python
import asyncio

async def get_dashboard(user_id: int):
    # Run 3 independent queries concurrently instead of sequentially
    user, posts, stats = await asyncio.gather(
        get_user(user_id),      # 100ms
        get_posts(user_id),     # 200ms
        get_stats(user_id),     # 150ms
    )
    # Total: ~200ms (slowest call) instead of ~450ms (sum of all)
    return {"user": user, "posts": posts, "stats": stats}
```
