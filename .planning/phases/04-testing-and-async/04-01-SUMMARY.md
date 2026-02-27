---
phase: 04-testing-and-async
plan: 01
subsystem: course-content
tags: [testing, async, pytest, asyncio, mobile-parallels]
dependency-graph:
  requires: [03-01-SUMMARY]
  provides: [testing-fundamentals, async-patterns]
  affects: [course-content]
tech-stack:
  added: [pytest, pytest-asyncio, pytest-cov, respx, httpx]
  patterns: [TestClient, AsyncClient, fixtures, mocking, semaphores, async-generators]
key-files:
  created:
    - 011-testing-apis/README.md
    - 011-testing-apis/theory/*.md (6 files)
    - 011-testing-apis/exercises/*.py (3 files)
    - 011-testing-apis/project/README.md
    - 012-advanced-async-python/README.md
    - 012-advanced-async-python/theory/*.md (6 files)
    - 012-advanced-async-python/exercises/*.py (3 files)
    - 012-advanced-async-python/project/README.md
  modified: []
decisions:
  - Pytest chosen over unittest for cleaner syntax and fixture system
  - Module 011 exercises provide pre-built apps for students to test against
  - Module 012 exercises are standalone runnable async scripts with embedded tests
  - All theory files include mobile-dev analogies with comparison tables
  - Async testing introduced in Module 011 as bridge to Module 012
  - TaskGroup (Python 3.11+) included with version checks for compatibility
metrics:
  duration: 16
  completed_date: 2026-02-27
  tasks_completed: 2
  files_created: 22
  lines_of_content: ~6200
---

# Phase 04 Plan 01: Testing and Async Modules Summary

Testing APIs (Module 011) and Advanced Async Python (Module 012) — comprehensive learning content with mobile developer context.

## One-Liner

Created 22-file curriculum covering pytest fundamentals through async concurrency patterns with mobile-dev analogies (XCTest/JUnit/flutter_test → Swift/Kotlin/Dart async patterns), theory-exercise-project structure, and embedded pytest tests.

## Completed Tasks

### Task 1: Module 011 — Testing APIs

Created complete testing curriculum for mobile developers transitioning to backend:

**Module README:**
- Why This Module, What You'll Learn, Mobile Developer Context
- Cross-platform testing comparison table (Swift/Kotlin/Dart/Python)
- Quick Assessment, Time Estimate, Key Differences from Mobile

**Theory files (6):**
1. `01-pytest-fundamentals.md` — Test discovery, native assertions, comparison to XCTest/JUnit/flutter_test
2. `02-testclient-basics.md` — FastAPI TestClient, CRUD operations, validation testing
3. `03-async-testing.md` — pytest-asyncio, AsyncClient, bridging to Module 012
4. `04-fixtures-conftest.md` — Fixture patterns, database isolation, setup/teardown
5. `05-mocking-strategies.md` — unittest.mock, respx, dependency override pattern
6. `06-test-coverage.md` — pytest-cov, systematic CRUD testing, meaningful coverage

**Exercise files (3):**
1. `01_basic_tests.py` — Pre-built items API, students write tests for CRUD operations
2. `02_fixtures_and_db.py` — Pre-built User/Post API with SQLite, students write fixtures and tests
3. `03_mocking_external.py` — Pre-built weather API, students mock external calls with respx

**Project README:**
- Comprehensive CRUD API test suite (User/Post/Comment resources)
- Requirements: conftest.py fixtures, test files per resource, mocking, async tests
- Success criteria: >80% coverage, tests run in any order, all tests pass
- Stretch goals: pagination, search, rate limiting tests

### Task 2: Module 012 — Advanced Async Python

Created complete async curriculum connecting to mobile async patterns:

**Module README:**
- Async patterns comparison table (Swift/Kotlin/Dart/Python)
- Side-by-side code examples for each platform
- Why This Matters for APIs (10 req/s → 1000+ req/s)

**Theory files (6):**
1. `01-event-loop-basics.md` — Event loop vs threads, coroutines, await mechanics
2. `02-gather-wait-completed.md` — Concurrent execution, gather(), TaskGroup (Python 3.11+)
3. `03-semaphores-limiting.md` — Rate limiting, connection pooling, choosing limits
4. `04-async-context-managers.md` — Resource cleanup, @asynccontextmanager pattern
5. `05-async-generators.md` — Streaming data, paginated APIs, memory efficiency
6. `06-exception-handling.md` — gather() errors, timeout, retry, circuit breaker

**Exercise files (3):**
1. `01_concurrent_gather.py` — gather(), as_completed(), TaskGroup, timing comparisons
2. `02_semaphores.py` — Rate limiting, tracking concurrency, error handling
3. `03_error_handling.py` — return_exceptions, timeouts, retry logic, fallback pattern

**Project README:**
- Async data aggregation pipeline with concurrent API calls
- Requirements: APIAggregator class, rate limiting, error handling, metrics
- Success criteria: concurrent fetching, partial failures handled, proper cleanup
- Stretch goals: retry logic, async generator, progress reporting, circuit breaker

## Deviations from Plan

None — plan executed exactly as written.

## Key Patterns Established

### Testing Module Patterns

**Theory structure:**
- Why This Matters (mobile-dev analogy)
- Content with code examples
- Mobile platform comparison tables
- Key Takeaways (bullet list)

**Exercise structure:**
- Pre-built FastAPI app (students write tests, not apps)
- TODO stubs with `pass` (tests fail until implemented)
- `# ============= TESTS =============` separator
- Inline pytest tests verifying student implementations

**Project structure:**
- Overview → Requirements → Starter Template → Success Criteria → Stretch Goals
- Starter template with TODO comments
- Testing checklist for verification

### Async Module Patterns

**Theory structure:**
- Mobile parallel section with side-by-side code (Swift/Kotlin/Dart/Python)
- ASCII diagrams for event loop visualization
- Real-world examples with timing comparisons

**Exercise structure:**
- Standalone runnable async scripts
- Helper functions provided
- TODO stubs with pytest-asyncio tests
- Timing assertions to verify concurrent execution

**Mobile analogies:**
- Every theory file connects to Swift/Kotlin/Dart equivalents
- Comparison tables show syntax differences
- "Like mobile X but Python Y" explanations

## Quality Metrics

**Content coverage:**
- 22 files created (11 per module)
- ~6200 lines of educational content
- 12 theory files (100% with mobile analogies)
- 6 exercise files (100% with embedded tests)
- 2 project READMEs with comprehensive specs

**Mobile developer context:**
- 15+ comparison tables across theory files
- XCTest/JUnit/flutter_test coverage in Module 011
- Swift/Kotlin/Dart async patterns in Module 012
- Every concept connected to mobile equivalent

**Exercise quality:**
- All Module 011 exercises provide pre-built apps to test
- All Module 012 exercises are standalone runnable scripts
- All TODO stubs use `pass` to ensure tests fail
- All exercises have inline pytest tests

## Self-Check: PASSED

All files verified to exist:

```bash
$ find 011-testing-apis 012-advanced-async-python -type f | wc -l
22

$ ls 011-testing-apis/
README.md  exercises/  project/  theory/

$ ls 011-testing-apis/theory/
01-pytest-fundamentals.md    04-fixtures-conftest.md
02-testclient-basics.md      05-mocking-strategies.md
03-async-testing.md          06-test-coverage.md

$ ls 011-testing-apis/exercises/
01_basic_tests.py  02_fixtures_and_db.py  03_mocking_external.py

$ ls 012-advanced-async-python/
README.md  exercises/  project/  theory/

$ ls 012-advanced-async-python/theory/
01-event-loop-basics.md        04-async-context-managers.md
02-gather-wait-completed.md    05-async-generators.md
03-semaphores-limiting.md      06-exception-handling.md

$ ls 012-advanced-async-python/exercises/
01_concurrent_gather.py  02_semaphores.py  03_error_handling.py
```

All commits verified:

```bash
$ git log --oneline -3
9d1d97b feat(04-01): create Module 012 Advanced Async Python content
a7f79ff feat(04-01): create Module 011 Testing APIs content
6be71d4 docs(04): create phase plan
```

## Next Steps

Phase 04 plan 01 complete. Ready to continue with:
- Phase 04 plan 02 (if exists) or
- Phase 05 planning (Real-World Features)

## Related Files

- Plan: `.planning/phases/04-testing-and-async/04-01-PLAN.md`
- Context: `.planning/phases/04-testing-and-async/04-CONTEXT.md`
- Research: `.planning/phases/04-testing-and-async/04-RESEARCH.md`
