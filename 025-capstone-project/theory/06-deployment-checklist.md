# Deployment Checklist

## Why This Matters

In mobile development, the App Store review process forces a quality gate: your app must meet specific criteria before it reaches users. There is no equivalent for backend deployments. You can push broken, insecure, unmonitored code to production with a single `git push`. Nobody will stop you.

This file IS your quality gate. It synthesizes everything from Modules 017-024 into checklists you walk through before deploying your capstone project. Every checkbox represents a lesson learned from real production incidents: data breaches from missing input validation, outages from missing health checks, debugging nightmares from missing logs.

Think of this as your backend App Store review checklist.

## Quick Review

- **Docker and containerization** (Module 017): Multi-stage builds, Docker Compose for development, container health checks, image optimization.
- **CI/CD pipelines** (Module 018): GitHub Actions runs tests on every push, builds Docker images, deploys to staging/production. Automated gates prevent broken code from reaching production.
- **Security hardening** (Module 019): CORS configuration, security headers, input validation, SQL injection prevention, secrets management. Defense in depth.
- **Performance optimization** (Module 020): N+1 query detection, connection pooling, response compression, database indexing. Profiling before optimizing.
- **Structured logging** (Module 021): JSON log format with structlog, request ID tracing, log levels, centralized log collection. Observability.
- **API versioning** (Module 022): URL prefix versioning (`/v1/`, `/v2/`), deprecation headers, backward compatibility. Evolution without breakage.
- **Rate limiting** (Module 023): Token bucket algorithm, per-endpoint limits, Redis-backed distributed rate limiting. Protection against abuse.
- **Service architecture** (Module 024): Modular monolith, service boundaries, when to split. Start simple, extract when needed.

## How They Compose

Each module taught one production concern in isolation. In reality, they interact:

```
Code Ready
  |
  v
[Security] --> [Performance] --> [Observability] --> [Deployment]
  |                |                  |                   |
  CORS, auth,      N+1 queries,      Logging,            Docker,
  validation,      indexes,          health checks,      CI/CD,
  secrets          caching           monitoring          versioning
```

**Security enables performance.** Rate limiting (Module 023) prevents abuse that would overwhelm your database. CORS (Module 019) prevents unauthorized cross-origin requests that waste resources.

**Performance enables observability.** If your API responds in 50ms, you can afford structured logging overhead. If it takes 5 seconds because of N+1 queries (Module 020), logging adds insult to injury.

**Observability enables deployment confidence.** Health checks (Module 021) tell your orchestrator when a container is ready. Structured logs (Module 021) tell you what went wrong after deployment. Without these, deploying is guessing.

**Deployment enables iteration.** CI/CD (Module 018) means every fix is one `git push` away from production. Without it, fixing a production bug takes hours of manual steps instead of minutes.

## Decision Framework

### "Is My API Ready for Production?"

Answer each question. If any answer is "No," fix it before deploying.

```
SECURITY
  Can an unauthenticated user access protected data?          --> Fix auth
  Can a user access another user's data?                      --> Fix authorization
  Are secrets hardcoded in source code?                       --> Move to env vars
  Is CORS set to allow all origins?                          --> Restrict to your domains
  Can malformed input cause errors or data corruption?        --> Add Pydantic validation

PERFORMANCE
  Do list endpoints load all results without pagination?      --> Add pagination
  Do you see N+1 query patterns in your ORM usage?           --> Add joinedload/selectinload
  Are frequently-read endpoints uncached?                    --> Add Redis caching
  Are database columns used in WHERE missing indexes?        --> Add indexes

RELIABILITY
  Does the app have a /health endpoint?                      --> Add one
  Do database connection failures crash the app?             --> Add connection retry
  Do external service failures cascade to users?             --> Add timeouts + fallbacks
  Is there a rate limit on auth endpoints?                   --> Add rate limiting

OBSERVABILITY
  Are logs in structured JSON format?                        --> Configure structlog
  Do requests have traceable IDs?                           --> Add request ID middleware
  Can you tell who did what from logs alone?                 --> Add user context to logs
  Are errors logged with stack traces?                      --> Configure exception logging

DEPLOYMENT
  Does the Docker image build and run?                       --> Test docker-compose up
  Do tests run automatically on push?                        --> Set up GitHub Actions
  Is there a staging environment?                           --> Deploy to staging first
  Can you roll back a bad deployment?                       --> Test your rollback process
```

## Capstone Application

**Universal Deployment Checklist -- All Three Project Options**

This checklist applies regardless of which capstone project you chose.

### Pre-Deployment Security Checklist

- [ ] All user input validated with Pydantic schemas (Module 005)
- [ ] SQL injection prevented: using SQLAlchemy parameterized queries, no raw SQL string concatenation (Module 006)
- [ ] Passwords hashed with Argon2 via pwdlib, never stored in plain text (Module 009)
- [ ] JWT tokens have expiration set (15-30 min for access, 7 days for refresh) (Module 009)
- [ ] Refresh token rotation: old refresh token invalidated when new one issued (Module 009)
- [ ] CORS configured for specific allowed origins, not `"*"` in production (Module 019)
- [ ] Security headers set: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (Module 019)
- [ ] Secrets stored in environment variables, not in code or config files (Module 017)
- [ ] `.env` file in `.gitignore` and never committed (Module 017)
- [ ] Rate limiting on `/auth/login` (prevent brute force) (Module 023)
- [ ] Rate limiting on `/auth/register` (prevent spam accounts) (Module 023)
- [ ] File uploads validated: content type, file size, magic bytes (Module 015, if applicable)

### Pre-Deployment Performance Checklist

- [ ] Database indexes on all foreign key columns (Module 006)
- [ ] Database indexes on columns used in WHERE and ORDER BY (Module 006)
- [ ] No N+1 queries: use `joinedload()` or `selectinload()` for relationships (Module 020)
- [ ] Connection pooling configured for SQLAlchemy engine (Module 020)
- [ ] List endpoints paginated (page/size or cursor-based) (Module 004)
- [ ] Redis caching for read-heavy endpoints (user profiles, feeds) (Module 014)
- [ ] Cache TTL set appropriately (not too long = stale data, not too short = no benefit) (Module 014)
- [ ] Background tasks for slow operations (email, image processing) (Module 013)
- [ ] Response models exclude unnecessary fields (do not send entire DB rows) (Module 005)
- [ ] Database queries use `select()` with specific columns where possible (Module 007)

### Pre-Deployment Observability Checklist

- [ ] Structured logging configured with structlog (JSON format) (Module 021)
- [ ] Request ID middleware adds unique ID to every request log (Module 021)
- [ ] Log levels used correctly: DEBUG for dev, INFO for production, ERROR for failures (Module 021)
- [ ] Exception handler logs full stack trace on 500 errors (Module 021)
- [ ] `GET /health` endpoint returns 200 when app is healthy (Module 021)
- [ ] Health check verifies database connectivity (not just "app is running") (Module 021)
- [ ] User actions logged (login, data modification) for audit trail (Module 021)

### Pre-Deployment Infrastructure Checklist

- [ ] Dockerfile uses multi-stage build (separate builder and runtime) (Module 017)
- [ ] Docker image does not contain `.env`, `.git`, `__pycache__`, or test files (Module 017)
- [ ] `docker-compose.yml` includes health checks for postgres and redis (Module 017)
- [ ] CI pipeline runs: lint, type check, test, build (Module 018)
- [ ] CI pipeline fails on test failure (blocks merge) (Module 018)
- [ ] API version prefix in URL (`/v1/`) for future evolution (Module 022)
- [ ] Deprecation headers planned for future endpoint retirement (Module 022)

### Pre-Deployment Documentation Checklist

- [ ] README has setup instructions (clone, env setup, docker-compose up)
- [ ] README has API overview (key endpoints, auth flow)
- [ ] OpenAPI docs accessible at `/docs` with endpoint descriptions
- [ ] All Pydantic schemas have `json_schema_extra` with examples (Module 005)
- [ ] Environment variables documented in `.env.example`

## Checklist

Meta-checklist -- use this to verify you have completed all section checklists:

- [ ] Security checklist: all items checked or justified as not applicable
- [ ] Performance checklist: all items checked or deferred with documented reason
- [ ] Observability checklist: all items checked
- [ ] Infrastructure checklist: all items checked
- [ ] Documentation checklist: all items checked
- [ ] Test suite passes with 80%+ coverage
- [ ] Application starts with `docker-compose up` and serves requests
- [ ] At least one team member (or yourself) has done a manual walkthrough of the core user flow

## Key Takeaways

1. **Checklists prevent omissions.** You will not remember to set CORS headers at 2 AM before a deadline. The checklist remembers for you.
2. **Security is not optional.** Every unchecked security item is a vulnerability. There is no "we will add auth later" in production.
3. **Observability is how you sleep at night.** Without structured logs and health checks, you learn about production issues from angry users, not from alerts.
4. **Performance problems are schema problems.** Most slow APIs trace back to missing indexes, N+1 queries, or missing caching -- all decisions made (or missed) during schema design.
5. **CI/CD is your safety net.** If tests run automatically on every push, broken code cannot reach production. If they do not, it will.
