# Roadmap: Backend Development Mastery — Course Content

## Overview

This roadmap delivers 24 modules of hands-on course content for mobile developers learning backend development with Python and FastAPI. The work progresses from foundational web concepts through data persistence, authentication, testing, advanced features, and production readiness, culminating in a capstone that ties everything together. Each phase produces complete, self-contained modules following the established pattern from module 001: theory files with mobile-dev analogies, exercise files with TODO stubs and inline pytest tests, and project READMEs with starter templates.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundations** - HTTP, REST, FastAPI basics, request/response handling, and data validation
- [ ] **Phase 2: Data Layer** - SQL fundamentals, SQLAlchemy ORM, and complete CRUD API construction
- [ ] **Phase 3: Auth and Security** - JWT authentication and role-based authorization
- [ ] **Phase 4: Testing and Async** - API testing with pytest and advanced async patterns
- [ ] **Phase 5: Advanced Features** - Background tasks, caching, file uploads, and WebSockets
- [ ] **Phase 6: Production Part A** - Docker, CI/CD, security hardening, and performance optimization
- [ ] **Phase 7: Production Part B** - Logging, API versioning, rate limiting, and microservices
- [ ] **Phase 8: Capstone** - Comprehensive project integrating all prior concepts

## Phase Details

### Phase 1: Foundations
**Goal**: A learner can understand HTTP/REST, build FastAPI endpoints, handle requests/responses, and validate data with Pydantic
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04
**Success Criteria** (what must be TRUE):
  1. Each module (002-005) contains a theory/ directory with all specified theory markdown files, each including "Why This Matters" mobile-dev framing and "Key Takeaways"
  2. Each module (002-005) contains an exercises/ directory with Python files that have TODO stubs and inline pytest tests that fail until the learner fills in the stubs
  3. Each module (002-005) contains a project/ directory with a README.md that includes requirements, a starter code template, and success criteria
  4. Theory files progress logically from HTTP basics through Pydantic validation, with code examples a mobile developer can follow
**Plans**: 2 plans

Plans:
- [x] 01-01-PLAN.md — Modules 002-003: HTTP/REST Fundamentals theory+exercises+project, FastAPI Basics theory+exercises+project (Wave 1)
- [x] 01-02-PLAN.md — Modules 004-005: Request/Response Handling theory+exercises+project, Pydantic Validation theory+exercises+project (Wave 1)

### Phase 2: Data Layer
**Goal**: A learner can design database schemas, use SQLAlchemy for data access, and build complete CRUD APIs with service layers
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria** (what must be TRUE):
  1. Each module (006-008) contains theory/, exercises/, and project/ directories following the established content pattern
  2. Module 006 exercises involve writing and analyzing SQL queries against relational schemas
  3. Module 007 exercises cover SQLAlchemy model definitions, relationships, and migration concepts
  4. Module 008 exercises demonstrate the service layer pattern, dependency injection with Depends(), and pagination
  5. Project READMEs describe self-contained data-driven applications (blog schema, task manager, notes API)
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — Module 006: SQL & Database Fundamentals theory+exercises+project (Wave 1)
- [ ] 02-02-PLAN.md — Modules 007-008: SQLAlchemy ORM theory+exercises+project, Building CRUD APIs theory+exercises+project (Wave 1)

### Phase 3: Auth and Security
**Goal**: A learner can implement JWT-based authentication and role-based access control in a FastAPI application
**Depends on**: Phase 2
**Requirements**: AUTH-01, AUTH-02
**Success Criteria** (what must be TRUE):
  1. Each module (009-010) contains theory/, exercises/, and project/ directories following the established content pattern
  2. Module 009 exercises cover password hashing, JWT token creation/validation, and protecting routes
  3. Module 010 exercises cover role checking, resource ownership verification, and admin-only endpoints
  4. Theory files explain authentication vs authorization with analogies to mobile app auth flows (biometrics, OAuth, token storage)
**Plans**: TBD

Plans:
- [ ] 03-01: Modules 009-010 (Authentication with JWT and Authorization/Permissions)

### Phase 4: Testing and Async
**Goal**: A learner can write comprehensive API tests with pytest and use advanced async patterns for concurrent operations
**Depends on**: Phase 3
**Requirements**: ADVN-01, ADVN-02
**Success Criteria** (what must be TRUE):
  1. Each module (011-012) contains theory/, exercises/, and project/ directories following the established content pattern
  2. Module 011 exercises use TestClient and async testing patterns, with exercises that test CRUD operations, fixtures, and mocking
  3. Module 012 exercises demonstrate asyncio.gather, semaphores, and async error handling with runnable code
  4. Theory files connect async concepts to mobile parallels (coroutines in Kotlin, async/await in Swift, Dart futures)
**Plans**: TBD

Plans:
- [ ] 04-01: Modules 011-012 (Testing APIs and Advanced Async Python)

### Phase 5: Advanced Features
**Goal**: A learner can implement background tasks, caching, file uploads, and real-time WebSocket communication
**Depends on**: Phase 4
**Requirements**: FEAT-01, FEAT-02, FEAT-03, FEAT-04
**Success Criteria** (what must be TRUE):
  1. Each module (013-016) contains theory/, exercises/, and project/ directories following the established content pattern
  2. Module 013 exercises cover FastAPI BackgroundTasks and Celery task patterns with retry logic
  3. Module 014 exercises demonstrate Redis caching with TTL management and cache invalidation strategies
  4. Module 015 exercises handle file upload validation, storage patterns, and UploadFile usage
  5. Module 016 exercises implement WebSocket connections, a connection manager, and broadcasting
**Plans**: TBD

Plans:
- [ ] 05-01: Modules 013-014 (Background Tasks and Caching with Redis)
- [ ] 05-02: Modules 015-016 (File Uploads and WebSockets)

### Phase 6: Production Part A
**Goal**: A learner can containerize applications, set up CI/CD pipelines, apply security best practices, and optimize API performance
**Depends on**: Phase 5
**Requirements**: PROD-01, PROD-02, PROD-03, PROD-04
**Success Criteria** (what must be TRUE):
  1. Each module (017-020) contains theory/, exercises/, and project/ directories following the established content pattern
  2. Module 017 exercises involve writing Dockerfiles, docker-compose configs, and multi-stage builds
  3. Module 018 exercises create GitHub Actions workflow files and deployment configurations
  4. Module 019 exercises identify vulnerabilities, configure CORS, and sanitize inputs against OWASP top 10
  5. Module 020 exercises profile code, fix N+1 query problems, and configure connection pooling
**Plans**: TBD

Plans:
- [ ] 06-01: Modules 017-018 (Docker and CI/CD)
- [ ] 06-02: Modules 019-020 (Security Best Practices and Performance)

### Phase 7: Production Part B
**Goal**: A learner can add observability, version APIs, implement rate limiting, and understand microservice decomposition
**Depends on**: Phase 6
**Requirements**: PROD-05, PROD-06, PROD-07, PROD-08
**Success Criteria** (what must be TRUE):
  1. Each module (021-024) contains theory/, exercises/, and project/ directories following the established content pattern
  2. Module 021 exercises configure structured logging, health check endpoints, and request tracing
  3. Module 022 exercises implement URL path versioning and header-based versioning with deprecation handling
  4. Module 023 exercises implement token bucket and sliding window rate limiting algorithms
  5. Module 024 exercises demonstrate service-to-service communication and message passing patterns
**Plans**: TBD

Plans:
- [ ] 07-01: Modules 021-022 (Logging/Monitoring and API Versioning)
- [ ] 07-02: Modules 023-024 (Rate Limiting and Microservices Basics)

### Phase 8: Capstone
**Goal**: A learner can synthesize all course concepts into a planned, designed, and structured full-stack API project
**Depends on**: Phase 7
**Requirements**: CAPS-01
**Success Criteria** (what must be TRUE):
  1. Module 025 contains theory/, exercises/, and project/ directories following the established content pattern
  2. Theory files cover API design planning, schema design, architecture review, and deployment checklists as synthesis of prior modules
  3. Exercises guide learners through design review, schema modeling, and test planning for a capstone-scale project
  4. The existing project README is enhanced with detailed starter templates, grading rubrics, and phased implementation guidance
**Plans**: TBD

Plans:
- [ ] 08-01: Module 025 (Capstone Project content)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundations | 2/2 | ✓ Complete | 2026-02-26 |
| 2. Data Layer | 0/2 | Not started | - |
| 3. Auth and Security | 0/1 | Not started | - |
| 4. Testing and Async | 0/1 | Not started | - |
| 5. Advanced Features | 0/2 | Not started | - |
| 6. Production Part A | 0/2 | Not started | - |
| 7. Production Part B | 0/2 | Not started | - |
| 8. Capstone | 0/1 | Not started | - |

---
*Roadmap created: 2026-02-26*
*Last updated: 2026-02-26 — Phase 2 planned (2 plans in 1 wave)*
