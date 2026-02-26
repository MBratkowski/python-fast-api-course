# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-26)

**Core value:** Every module delivers practical, hands-on learning content that a mobile developer can work through independently
**Current focus:** Phase 3 complete — ready for Phase 4 (Testing and Async)

## Current Position

Phase: 3 of 8 (Auth and Security) — COMPLETE ✓
Plan: 1 of 1 in current phase
Status: Phase verified and complete
Last activity: 2026-02-26 — Phase 3 verified (10/10 must-haves passed)

Progress: [████░░░░░░] 37%

## Performance Metrics

**Velocity:**
- Total plans completed: 5
- Average duration: 12 min
- Total execution time: 1.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 - Foundations | 2/2 | 19 min | 10 min |
| 2 - Data Layer | 2/2 | 25 min | 13 min |
| 3 - Auth and Security | 1/1 | 21 min | 21 min |

**Recent Trend:**
- Last 3 plans: 16 min, 13 min, 21 min
- Trend: Increasing with content complexity (~17 min avg)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: 8 phases derived from 7 course parts (Part 6 split into two phases due to 8 modules)
- [Roadmap]: Each plan covers 1-2 modules to keep execution scope manageable
- [01-01]: Module 002 exercises are pure Python (no FastAPI) to focus on HTTP/REST concepts
- [01-01]: Module 003 exercises use TestClient and async def throughout
- [01-01]: All theory files include mobile-dev analogies in Why This Matters sections
- [01-02]: Annotated pattern used consistently in Module 004 exercises for Path/Query/Header
- [01-02]: Enforced Pydantic v2 patterns exclusively (@field_validator, model_validator, model_dump)
- [01-02]: Exercise stubs use pass or minimal code to ensure tests fail until implemented
- [02-01]: Module 006 exercises are pure Python (no database connection, no SQLAlchemy) to build SQL fundamentals
- [02-01]: PostgreSQL setup via Docker Compose as primary method (isolated environment pattern)
- [02-02]: Module 007 exercises use sync SQLAlchemy with SQLite for simplicity (no async setup required)
- [02-02]: Module 008 exercises use TestClient with sync SQLAlchemy to keep tests simple
- [02-02]: All theory files enforce SQLAlchemy 2.0 patterns exclusively (Mapped, mapped_column, DeclarativeBase)
- [02-02]: Service layer pattern introduced early as standard architecture in Module 008
- [03-01]: Use PyJWT (not python-jose which is abandoned) for all JWT operations
- [03-01]: Use pwdlib with Argon2 (not passlib which is deprecated) for password hashing
- [03-01]: OAuth2PasswordBearer uses form data not JSON per OAuth2 spec
- [03-01]: Use 403 for authorization failures, 401 for authentication failures
- [03-01]: Module 010 exercises provide working auth so learners focus on authorization logic

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-26
Stopped at: Phase 3 complete and verified — ready for Phase 4 planning
Resume file: None
