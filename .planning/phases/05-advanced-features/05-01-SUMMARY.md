---
phase: 05-advanced-features
plan: 01
subsystem: content
tags: [celery, redis, background-tasks, caching, ttl, fakeredis]

# Dependency graph
requires:
  - phase: 04-testing-and-async
    provides: Module structure pattern with theory/exercises/project layout
provides:
  - Module 013 Background Tasks and Queues (11 files)
  - Module 014 Caching with Redis (11 files)
affects: [05-02, 06-advanced-features]

# Tech tracking
tech-stack:
  added: [celery, redis-py, fakeredis, celery-beat, flower]
  patterns: [cache-aside, write-through, tag-based-invalidation, celery-autoretry, fastapi-lifespan]

key-files:
  created:
    - 013-background-tasks/README.md
    - 013-background-tasks/theory/01-when-to-use-background-tasks.md
    - 013-background-tasks/theory/02-fastapi-background-tasks.md
    - 013-background-tasks/theory/03-celery-setup-configuration.md
    - 013-background-tasks/theory/04-redis-as-broker.md
    - 013-background-tasks/theory/05-retries-error-handling.md
    - 013-background-tasks/theory/06-scheduled-tasks-celery-beat.md
    - 013-background-tasks/exercises/01_background_tasks.py
    - 013-background-tasks/exercises/02_celery_tasks.py
    - 013-background-tasks/exercises/03_retry_logic.py
    - 013-background-tasks/project/README.md
    - 014-caching-redis/README.md
    - 014-caching-redis/theory/01-why-cache.md
    - 014-caching-redis/theory/02-redis-setup.md
    - 014-caching-redis/theory/03-caching-patterns.md
    - 014-caching-redis/theory/04-ttl-expiration.md
    - 014-caching-redis/theory/05-cache-invalidation.md
    - 014-caching-redis/theory/06-redis-data-structures.md
    - 014-caching-redis/exercises/01_basic_caching.py
    - 014-caching-redis/exercises/02_ttl_management.py
    - 014-caching-redis/exercises/03_cache_invalidation.py
    - 014-caching-redis/project/README.md
  modified: []

key-decisions:
  - "Module 013 exercises use task.apply() for synchronous testing without running Celery worker"
  - "Module 014 exercises use fakeredis for all Redis operations (no Docker required)"
  - "Use redis-py (not aioredis) with redis.asyncio for async operations"
  - "Use FastAPI lifespan context manager (not deprecated on_event) for Redis lifecycle"

patterns-established:
  - "Cache-aside pattern: check cache, fall back to DB, store result"
  - "Tag-based invalidation: group cache keys by category using Redis sets"
  - "Consistent cache key naming: entity:id (e.g., user:42, product:100)"
  - "Celery autoretry_for with retry_backoff=True for automatic exponential backoff"

requirements-completed: [FEAT-01, FEAT-02]

# Metrics
duration: 8min
completed: 2026-03-08
---

# Phase 05 Plan 01: Background Tasks and Caching Summary

**BackgroundTasks vs Celery decision tree, Redis cache-aside with TTL/invalidation, 22 files across 2 modules with mobile-dev analogies and fakeredis exercises**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-08T17:17:57Z
- **Completed:** 2026-03-08T17:25:36Z
- **Tasks:** 2
- **Files modified:** 22

## Accomplishments

- Module 013: Complete background tasks coverage from FastAPI BackgroundTasks through Celery setup, Redis broker, retry logic, and Celery Beat scheduling
- Module 014: Complete Redis caching coverage from setup through cache-aside pattern, TTL management, cache invalidation strategies, and data structures
- All 12 theory files include mobile-dev analogies (iOS/Android/Python comparison tables)
- All 6 exercise files use inline pytest tests with TODO stubs; Module 014 uses fakeredis for zero-Docker exercises

## Task Commits

Each task was committed atomically:

1. **Task 1: Module 013 -- Background Tasks and Queues** - `36f0608` (feat) -- pre-existing commit
2. **Task 2: Module 014 -- Caching with Redis** - `4c21950` (feat)

## Files Created/Modified

- `013-background-tasks/README.md` - Module overview with mobile-dev context and comparison table
- `013-background-tasks/theory/*.md` (6 files) - BackgroundTasks, Celery, Redis broker, retries, scheduling
- `013-background-tasks/exercises/*.py` (3 files) - BackgroundTasks, Celery tasks with apply(), retry logic
- `013-background-tasks/project/README.md` - Email notification system project spec
- `014-caching-redis/README.md` - Module overview with mobile-dev context and comparison table
- `014-caching-redis/theory/*.md` (6 files) - Why cache, Redis setup, patterns, TTL, invalidation, data structures
- `014-caching-redis/exercises/*.py` (3 files) - Basic caching, TTL management, cache invalidation with fakeredis
- `014-caching-redis/project/README.md` - Caching layer API project spec with starter template

## Decisions Made

- Module 013 exercises use `task.apply()` for synchronous Celery task testing without requiring a running worker or Redis
- Module 014 exercises use `fakeredis` library so learners can run exercises without Docker
- Used `redis.asyncio` (from redis-py 5.x) instead of deprecated `aioredis` throughout
- Used FastAPI `lifespan` context manager instead of deprecated `on_event` for Redis connection lifecycle
- Project READMEs use real Redis via Docker Compose (unlike exercises) to teach production setup

## Deviations from Plan

None - plan executed exactly as written. Module 013 was already committed from a prior execution; Module 014 was created fresh.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Modules 013 and 014 complete, ready for Plan 02 (File Uploads and WebSockets)
- Redis concepts in Module 014 cross-reference Module 013's broker usage
- No blockers for next plan

## Self-Check: PASSED

- All 22 files verified present
- Commit 36f0608 (Task 1) verified
- Commit 4c21950 (Task 2) verified

---
*Phase: 05-advanced-features*
*Completed: 2026-03-08*
