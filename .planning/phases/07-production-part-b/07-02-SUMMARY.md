---
phase: 07-production-part-b
plan: 02
subsystem: api
tags: [rate-limiting, redis, token-bucket, sliding-window, microservices, pub-sub, api-gateway, httpx, fakeredis]

# Dependency graph
requires:
  - phase: 05-advanced-features
    provides: Redis caching patterns with fakeredis (Module 014)
  - phase: 03-auth-security
    provides: JWT authentication for per-user rate limiting
provides:
  - Module 023 Rate Limiting content (6 theory, 3 exercises, 1 project)
  - Module 024 Microservices Basics content (6 theory, 3 exercises, 1 project)
affects: [08-capstone]

# Tech tracking
tech-stack:
  added: []
  patterns: [token-bucket-algorithm, sliding-window-algorithm, httpx-asgi-transport, redis-pub-sub]

key-files:
  created:
    - 023-rate-limiting/theory/01-rate-limiting-algorithms.md
    - 023-rate-limiting/theory/02-redis-implementation.md
    - 023-rate-limiting/exercises/01_token_bucket.py
    - 023-rate-limiting/exercises/02_sliding_window.py
    - 023-rate-limiting/exercises/03_per_user_limits.py
    - 024-microservices-basics/theory/03-sync-communication.md
    - 024-microservices-basics/theory/04-async-communication.md
    - 024-microservices-basics/exercises/01_service_communication.py
    - 024-microservices-basics/exercises/02_message_passing.py
    - 024-microservices-basics/exercises/03_gateway_routing.py
  modified:
    - 023-rate-limiting/README.md
    - 024-microservices-basics/README.md

key-decisions:
  - "Rate limiting exercises implement algorithms from scratch (not slowapi) for deeper understanding"
  - "Module 024 exercises use httpx.ASGITransport to simulate multi-service architectures in single files"
  - "Redis pub/sub exercise uses fakeredis with decode_responses=True for string handling"

patterns-established:
  - "Token bucket with Redis hash (tokens + last_refill fields)"
  - "Sliding window with Redis sorted sets (ZADD/ZREMRANGEBYSCORE/ZCARD pipeline)"
  - "ASGITransport pattern for testing service-to-service calls without running servers"

requirements-completed: [PROD-07, PROD-08]

# Metrics
duration: 14min
completed: 2026-03-08
---

# Phase 07 Plan 02: Rate Limiting and Microservices Basics Summary

**Token bucket and sliding window rate limiters with fakeredis, plus microservices communication patterns using httpx ASGITransport and Redis pub/sub**

## Performance

- **Duration:** 14 min
- **Started:** 2026-03-08T18:19:41Z
- **Completed:** 2026-03-08T18:34:32Z
- **Tasks:** 2
- **Files modified:** 22

## Accomplishments
- Module 023: Complete rate limiting curriculum covering algorithms (token bucket, sliding window, fixed window, leaky bucket), Redis implementation, per-user/IP limits, monthly quotas, response headers, and client-side handling
- Module 024: Complete microservices curriculum covering when to decompose, service boundaries, sync/async communication, API gateway, and data consistency (CAP theorem, sagas)
- All 6 exercises are fully self-contained with embedded pytest tests using fakeredis and httpx.ASGITransport -- no Docker or running servers required

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Module 023 Rate Limiting content** - `7471d6b` (feat)
2. **Task 2: Create Module 024 Microservices Basics content** - `bc353fd` (feat)

## Files Created/Modified

### Module 023: Rate Limiting (11 files)
- `023-rate-limiting/README.md` - Module overview with mobile developer context
- `023-rate-limiting/theory/01-rate-limiting-algorithms.md` - Token bucket, sliding window, fixed window, leaky bucket with ASCII diagrams
- `023-rate-limiting/theory/02-redis-implementation.md` - Atomic Redis operations, pipeline safety, sorted sets
- `023-rate-limiting/theory/03-per-user-vs-per-ip.md` - Rate limit keys, tier-based limits, JWT user extraction
- `023-rate-limiting/theory/04-monthly-quotas.md` - Redis INCR with EXPIREAT, quota tiers, percentage warnings
- `023-rate-limiting/theory/05-response-headers.md` - X-RateLimit headers, 429 responses, middleware
- `023-rate-limiting/theory/06-client-side-handling.md` - Exponential backoff, Retry-After, iOS/Android patterns
- `023-rate-limiting/exercises/01_token_bucket.py` - Token bucket with fakeredis and time mocking
- `023-rate-limiting/exercises/02_sliding_window.py` - Sliding window with sorted sets and pipeline
- `023-rate-limiting/exercises/03_per_user_limits.py` - Per-user rate limiting with FastAPI and auth
- `023-rate-limiting/project/README.md` - Comprehensive rate limiting project

### Module 024: Microservices Basics (11 files)
- `024-microservices-basics/README.md` - Module overview with mobile developer context
- `024-microservices-basics/theory/01-when-to-use-microservices.md` - Monolith vs microservices, premature decomposition anti-pattern
- `024-microservices-basics/theory/02-service-boundaries.md` - DDD bounded contexts, database per service rule
- `024-microservices-basics/theory/03-sync-communication.md` - httpx AsyncClient, timeout handling, circuit breaker
- `024-microservices-basics/theory/04-async-communication.md` - Redis pub/sub, event format, eventual consistency
- `024-microservices-basics/theory/05-api-gateway.md` - Routing, auth, request aggregation
- `024-microservices-basics/theory/06-data-consistency.md` - CAP theorem, saga pattern, idempotency
- `024-microservices-basics/exercises/01_service_communication.py` - Cross-service HTTP calls with ASGITransport
- `024-microservices-basics/exercises/02_message_passing.py` - Redis pub/sub with fakeredis
- `024-microservices-basics/exercises/03_gateway_routing.py` - API gateway routing to backend services
- `024-microservices-basics/project/README.md` - Monolith decomposition project

## Decisions Made
- Rate limiting exercises implement algorithms from scratch using fakeredis (not slowapi, which is covered in Module 019) to give learners deeper algorithmic understanding
- Module 024 exercises use httpx.ASGITransport to mount FastAPI apps as "remote services" within single test files, avoiding Docker or running servers
- Redis pub/sub exercise uses decode_responses=True for the async client to simplify string handling in event JSON serialization

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. All exercises use fakeredis and httpx.ASGITransport for self-contained execution.

## Next Phase Readiness
- Modules 023 and 024 complete the production readiness curriculum (Phase 07)
- All content is ready for Phase 08 (Capstone Project)
- Learners now have coverage of: rate limiting algorithms, Redis-backed rate limiting, microservices architecture, service communication, and event-driven patterns

---
*Phase: 07-production-part-b*
*Completed: 2026-03-08*
