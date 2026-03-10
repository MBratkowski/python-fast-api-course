# Requirements: Backend Development Mastery — Course Content

**Defined:** 2026-02-26
**Core Value:** Every module delivers practical, hands-on learning content that a mobile developer can work through independently

## v1 Requirements

Requirements for creating all course module content. Each module gets theory files, exercise files, and a project.

### Part 1: Foundations

- [ ] **FOUND-01**: Module 002 — HTTP & REST Fundamentals: 6 theory files (HTTP basics, methods, status codes, headers, REST principles, API design), 3 exercises (analyze requests, design REST API, identify violations), 1 project (design API spec for task management app)
- [ ] **FOUND-02**: Module 003 — FastAPI Basics: 6 theory files (intro, first endpoint, route decorators, dev server, Swagger/ReDoc, project structure), 3 exercises (hello world API, multiple endpoints, explore docs), 1 project (quotes API)
- [ ] **FOUND-03**: Module 004 — Request & Response Handling: 6 theory files (path params, query params, headers, response models, custom responses, status codes), 3 exercises (parameter types, optional/required params, response formats), 1 project (product catalog API with filtering/pagination)
- [ ] **FOUND-04**: Module 005 — Pydantic & Data Validation: 6 theory files (BaseModel, field validation, optional/required, custom validators, nested models, create/update/response schemas), 3 exercises (validation models, custom validators, nested data), 1 project (user registration with validation)

### Part 2: Data Layer

- [ ] **DATA-01**: Module 006 — SQL & Database Fundamentals: 6 theory files (relational concepts, SQL CRUD, relationships, joins, indexes, PostgreSQL setup), 3 exercises (SQL queries, schema design, index optimization), 1 project (blog platform database schema)
- [ ] **DATA-02**: Module 007 — SQLAlchemy ORM: 6 theory files (ORM concepts, models, relationships, CRUD with session, async SQLAlchemy, Alembic migrations), 3 exercises (models with relationships, CRUD operations, complex queries), 1 project (task management data layer)
- [ ] **DATA-03**: Module 008 — Building CRUD APIs: 6 theory files (CRUD design, Depends() for DB, service layer, error handling, pagination/filtering, bulk ops), 3 exercises (CRUD endpoints, service pattern, pagination), 1 project (notes application CRUD API)

### Part 3: Auth & Security

- [ ] **AUTH-01**: Module 009 — Authentication with JWT: 6 theory files (authn vs authz, password hashing, JWT structure, access/refresh tokens, expiration/rotation, OAuth2PasswordBearer), 3 exercises (password hashing, token creation/validation, protected routes), 1 project (complete auth system)
- [ ] **AUTH-02**: Module 010 — Authorization & Permissions: 6 theory files (RBAC concepts, roles/permissions, permission decorators, resource-level authz, admin routes, middleware), 3 exercises (role checking, resource ownership, admin endpoints), 1 project (add roles and permissions to API)

### Part 4: Testing & Async

- [x] **ADVN-01**: Module 011 — Testing APIs: 6 theory files (pytest basics, TestClient, async testing, DB fixtures, mocking, coverage), 3 exercises (basic tests, fixture usage, mocking), 1 project (comprehensive CRUD API tests)
- [x] **ADVN-02**: Module 012 — Advanced Async Python: 6 theory files (event loop, gather/wait/as_completed, semaphores, async context managers, async generators, exception handling), 3 exercises (concurrent operations, semaphore limiting, error handling), 1 project (data aggregation from multiple services)

### Part 5: Advanced Features

- [x] **FEAT-01**: Module 013 — Background Tasks & Queues: 6 theory files (when to use, FastAPI BackgroundTasks, Celery setup, Redis broker, retries/errors, scheduled tasks), 3 exercises (background tasks, Celery tasks, retry logic), 1 project (email notification system)
- [x] **FEAT-02**: Module 014 — Caching with Redis: 6 theory files (why cache, Redis setup, caching patterns, TTL/expiration, cache invalidation, data structures), 3 exercises (basic caching, TTL management, invalidation), 1 project (caching layer for API)
- [x] **FEAT-03**: Module 015 — File Uploads & Storage: 6 theory files (UploadFile, validation, local storage, S3 integration, presigned URLs, image processing), 3 exercises (file upload endpoint, validation, storage patterns), 1 project (file upload service)
- [x] **FEAT-04**: Module 016 — WebSockets & Real-Time: 6 theory files (WebSocket vs HTTP, FastAPI WebSocket, connection manager, broadcasting/rooms, WS auth, scaling with Redis), 3 exercises (basic WebSocket, connection manager, broadcasting), 1 project (real-time notification system)

### Part 6: Production

- [ ] **PROD-01**: Module 017 — Docker & Containers: 6 theory files (container concepts, Dockerfile, multi-stage builds, Docker Compose, networking, production optimizations), 3 exercises (write Dockerfile, compose setup, multi-stage build), 1 project (containerize API with PostgreSQL/Redis)
- [ ] **PROD-02**: Module 018 — CI/CD & Deployment: 6 theory files (CI/CD concepts, GitHub Actions, CI testing, Docker image building, cloud deployment, env vars/secrets), 3 exercises (workflow file, test pipeline, deployment config), 1 project (full CI/CD pipeline)
- [ ] **PROD-03**: Module 019 — Security Best Practices: 7 theory files (OWASP top 10, input validation, SQL injection, CORS, rate limiting, secrets management, security headers), 3 exercises (identify vulnerabilities, CORS config, input sanitization), 1 project (security audit and hardening)
- [ ] **PROD-04**: Module 020 — Performance Optimization: 6 theory files (profiling, query analysis, N+1 queries, connection pooling, async best practices, load testing), 3 exercises (profile code, fix N+1, load test), 1 project (profile and optimize slow endpoint)
- [x] **PROD-05**: Module 021 — Logging & Monitoring: 6 theory files (Python logging, structured logging, request tracing, Sentry, Prometheus metrics, health checks), 3 exercises (logging config, structured logs, health endpoint), 1 project (comprehensive logging/monitoring)
- [x] **PROD-06**: Module 022 — API Versioning: 6 theory files (why version, URL path versioning, header versioning, breaking vs non-breaking, deprecation, maintaining versions), 3 exercises (URL versioning, header versioning, deprecation), 1 project (add versioning with migration path)
- [x] **PROD-07**: Module 023 — Rate Limiting: 6 theory files (algorithms, Redis implementation, per-user vs per-IP, monthly quotas, response headers, client handling), 3 exercises (token bucket, sliding window, per-user limits), 1 project (implement rate limiting)
- [x] **PROD-08**: Module 024 — Microservices Basics: 6 theory files (when to use, service boundaries, sync communication, async communication, API gateway, data consistency), 3 exercises (service communication, message passing, gateway routing), 1 project (split monolith into two services)

### Part 7: Capstone

- [x] **CAPS-01**: Module 025 — Capstone Project: 6 theory files (API design planning, database schema design, architecture patterns review, project setup, testing strategy, deployment checklist), 3 exercises (design review, schema modeling, test planning), enhanced project (update existing README with detailed starter templates)

## v2 Requirements

None — this milestone covers all planned modules.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Solution files for exercises | Learners should work through stubs themselves |
| Video/interactive content | Text and code only for this milestone |
| Progressive project builds | Each module project is self-contained |
| Automated grading | Manual pytest verification is sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Complete |
| FOUND-02 | Phase 1 | Complete |
| FOUND-03 | Phase 1 | Complete |
| FOUND-04 | Phase 1 | Complete |
| DATA-01 | Phase 2 | Complete |
| DATA-02 | Phase 2 | Complete |
| DATA-03 | Phase 2 | Complete |
| AUTH-01 | Phase 3 | Complete |
| AUTH-02 | Phase 3 | Complete |
| ADVN-01 | Phase 4 | Complete |
| ADVN-02 | Phase 4 | Complete |
| FEAT-01 | Phase 5 | Complete |
| FEAT-02 | Phase 5 | Complete |
| FEAT-03 | Phase 5 | Complete |
| FEAT-04 | Phase 5 | Complete |
| PROD-01 | Phase 6 | Pending |
| PROD-02 | Phase 6 | Pending |
| PROD-03 | Phase 6 | Pending |
| PROD-04 | Phase 6 | Pending |
| PROD-05 | Phase 7 | Complete |
| PROD-06 | Phase 7 | Complete |
| PROD-07 | Phase 7 | Complete |
| PROD-08 | Phase 7 | Complete |
| CAPS-01 | Phase 8 | Complete |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0

---
*Requirements defined: 2026-02-26*
*Last updated: 2026-02-26 — Phase 3 requirements marked Complete*
