---
phase: 03-auth-and-security
plan: 01
type: execute
completed: 2026-02-26
duration: 13min
subsystem: authentication-authorization
tags: [jwt, rbac, oauth2, pyjwt, pwdlib, argon2, roles, permissions]

dependency_graph:
  requires:
    - phase-02 (data layer with SQLAlchemy patterns)
    - module-008 (CRUD operations with service layer)
  provides:
    - complete-authentication-system (signup, login, refresh, logout with JWT)
    - role-based-access-control (admin, user, moderator roles)
    - resource-ownership-verification (users can only modify own resources)
    - admin-panel-patterns (user management, stats, privilege escalation prevention)
  affects:
    - future-phases-requiring-authentication
    - module-011-onwards (all modules can use auth patterns)

tech_stack:
  added:
    - PyJWT (jwt encoding/decoding, replaces abandoned python-jose)
    - pwdlib (password hashing with Argon2, replaces deprecated passlib)
    - FastAPI OAuth2PasswordBearer (built-in OAuth2 support)
  patterns:
    - JWT access/refresh tokens with rotation
    - Timing attack prevention (DUMMY_HASH pattern)
    - Dependency factories for role checking (require_role, require_any_role)
    - Resource ownership dependencies (get_X_or_403 pattern)
    - Router-level admin protection (dependencies on APIRouter)

key_files:
  created:
    - 009-authentication-jwt/theory/*.md (6 files: authn vs authz, password hashing, JWT structure, access/refresh tokens, expiration/rotation, OAuth2PasswordBearer)
    - 009-authentication-jwt/exercises/*.py (3 files: password hashing, JWT tokens, protected routes)
    - 009-authentication-jwt/project/README.md (complete auth system project)
    - 010-authorization-permissions/theory/*.md (6 files: RBAC concepts, roles/permissions, permission dependencies, resource authorization, admin routes, middleware)
    - 010-authorization-permissions/exercises/*.py (3 files: role checking, resource ownership, admin endpoints)
    - 010-authorization-permissions/project/README.md (add RBAC to notes API project)
  modified: []

decisions:
  - decision: Use PyJWT instead of python-jose
    rationale: python-jose abandoned (3+ years no updates), PyJWT actively maintained and recommended by FastAPI team
    impact: All JWT code uses `import jwt` from PyJWT, not python-jose
  - decision: Use pwdlib with Argon2 instead of passlib with bcrypt
    rationale: passlib deprecated in Python 3.13+, pwdlib actively maintained, Argon2 more resistant to GPU cracking than bcrypt
    impact: All password hashing uses `PasswordHash.recommended()` from pwdlib
  - decision: OAuth2PasswordBearer uses form data, not JSON
    rationale: OAuth2 spec requires application/x-www-form-urlencoded for token endpoints
    impact: Login endpoints use OAuth2PasswordRequestForm with form data, not JSON body
  - decision: Use 403 for authorization failures, 401 for authentication failures
    rationale: Clear distinction — 401 means "who are you?" failed, 403 means "you can't do this"
    impact: Role check failures return 403, token validation failures return 401
  - decision: Provide working auth in Module 010 exercises
    rationale: Learners should focus on authorization logic, not reimplement authentication
    impact: Module 010 exercises include complete auth setup, only authorization is TODO

metrics:
  files_created: 20
  lines_of_code: ~5400
  theory_pages: 12
  exercises: 6
  projects: 2
---

# Phase 03 Plan 01: Authentication and Authorization Modules — Summary

JWT authentication and RBAC authorization content for modules 009-010.

## One-Liner

JWT authentication (PyJWT + pwdlib/Argon2) with OAuth2PasswordBearer and role-based access control (require_role dependencies, resource ownership verification, admin panels with privilege escalation prevention).

## What Was Built

Created complete learning content for Module 009 (Authentication with JWT) and Module 010 (Authorization & Permissions):

**Module 009: Authentication with JWT**
- 6 theory files covering authentication vs authorization, password hashing with pwdlib/Argon2, JWT structure/claims with PyJWT, access/refresh tokens, token expiration/rotation, and FastAPI's OAuth2PasswordBearer
- 3 exercise files with TODO stubs: password hashing (pure Python), JWT token creation/validation (pure Python), and protected routes (FastAPI + TestClient)
- 1 project README: complete authentication system with signup, login, refresh, logout, and token rotation

**Module 010: Authorization & Permissions**
- 6 theory files covering RBAC concepts, roles/permissions modeling, permission dependencies (require_role factory pattern), resource-level authorization (ownership verification), admin routes (privilege escalation prevention), and middleware vs dependencies for auth
- 3 exercise files with TODO stubs: role checking (admin/moderator/user), resource ownership (get_post_or_403 pattern), and admin endpoints (user management with safeguards)
- 1 project README: add RBAC to notes API with roles, ownership checks, and admin panel

All content uses:
- **Modern auth stack**: PyJWT (not abandoned python-jose), pwdlib (not deprecated passlib), Argon2 (not bcrypt)
- **SQLAlchemy 2.0 patterns**: Mapped, mapped_column, DeclarativeBase
- **Pydantic v2 patterns**: ConfigDict, field_validator, model_dump
- **Mobile-dev framing**: Every theory file includes "Why This Matters" with mobile development analogies
- **Inline pytest tests**: All exercises include tests that fail until learner implements TODOs

## How It Works

**Authentication Flow (Module 009)**:
1. User signs up → password hashed with Argon2 via pwdlib → stored in database
2. User logs in → password verified (with timing attack prevention) → JWT tokens issued (access 30min, refresh 7 days)
3. User makes API request → `OAuth2PasswordBearer` extracts token → `get_current_user` dependency validates JWT → endpoint executes
4. Access token expires → client sends refresh token → server issues new access token (with optional rotation)
5. User logs out → refresh token revoked in database/Redis

**Authorization Flow (Module 010)**:
1. Authenticated user attempts admin operation → `require_role(Role.ADMIN)` dependency checks user.role → raises 403 if not admin
2. User tries to update another user's post → `get_post_or_403` dependency fetches post → checks ownership or admin role → raises 403 if unauthorized
3. Admin manages users → router-level dependency (`dependencies=[Depends(require_role(Role.ADMIN))]`) protects all routes → privilege escalation prevented (can't promote to admin, can't change own role)

**Key Patterns**:
- **Dependency factories**: `require_role(Role.ADMIN)` returns a dependency function that checks the role
- **Resource ownership**: `get_X_or_403(id, current_user, db)` fetches resource and verifies ownership OR admin
- **Timing attack prevention**: Always hash password even for invalid usernames using DUMMY_HASH
- **Status codes**: 401 for auth failures (invalid token), 403 for authorization failures (valid token, insufficient permissions)

## Deviations from Plan

None — plan executed exactly as written.

All must-haves verified:
- Module 009: 6 theory files, 3 exercises with pytest tests, 1 project README covering JWT authentication
- Module 010: 6 theory files, 3 exercises with pytest tests, 1 project README covering RBAC authorization
- All theory files include mobile-dev framing ("Why This Matters") and key takeaways
- All code uses PyJWT and pwdlib (not python-jose or passlib)
- All code uses SQLAlchemy 2.0 and Pydantic v2 patterns
- Exercise stubs use `pass` so tests fail until learner implements
- Module 010 exercises provide working authentication (from Module 009 patterns)

## What Works

✅ **Module 009 Authentication**:
- Password hashing exercise demonstrates pwdlib with Argon2, timing attack prevention
- JWT tokens exercise shows token creation/validation with PyJWT, expiration handling
- Protected routes exercise integrates OAuth2PasswordBearer, get_current_user dependency, and FastAPI security
- Project defines complete auth system with signup, login, refresh, logout, and token rotation

✅ **Module 010 Authorization**:
- Role checking exercise demonstrates dependency factory pattern, admin/moderator/user roles
- Resource ownership exercise shows get_post_or_403 pattern with admin bypass
- Admin endpoints exercise covers router-level protection, privilege escalation prevention, user management
- Project defines RBAC for notes API with ownership verification and admin panel

✅ **Modern Stack**:
- All JWT code uses PyJWT (`import jwt`), not python-jose
- All password hashing uses pwdlib (`PasswordHash.recommended()`), not passlib
- Research findings on abandoned/deprecated libraries fully incorporated

✅ **Learning Patterns**:
- Theory files progress logically (authentication → authorization)
- Exercises build on each other (Module 009 auth → Module 010 uses that auth)
- Mobile-dev analogies make concepts relatable (Keychain/Keystore, OkHttp Interceptor, AVCaptureDevice permissions)
- Inline tests provide immediate feedback loop

## Next Phase Readiness

**Phase 03 Plan 02**: Module 011 (Rate Limiting & Throttling) and Module 012 (Input Validation & Security) are ready for execution.

**Dependencies satisfied**:
- Authentication and authorization patterns established
- Modern security libraries (PyJWT, pwdlib) documented
- Dependency injection patterns for security checks demonstrated

**Potential concerns**:
- None identified

**Recommendations**:
- Module 011/012 can reference Module 009/010 auth patterns
- Consider showing how rate limiting applies differently per role (admin vs user)
- Input validation module should build on Pydantic v2 patterns already established

## Open Items

None — phase complete.

## Performance Notes

**Duration**: 13 minutes
- Task 1 (Module 009): ~7 minutes (6 theory + 3 exercises + 1 project)
- Task 2 (Module 010): ~6 minutes (6 theory + 3 exercises + 1 project)

**Efficiency**:
- Used established patterns from Module 001/008 (theory structure, exercise format, project README layout)
- Minimal refactoring needed — research findings were incorporated directly into content
- No deviation handling required — plan was clear and complete

**Files created**: 20 total
- 12 theory files (~40 KB combined)
- 6 exercise files (~26 KB combined)
- 2 project READMEs (~21 KB combined)

## Lessons Learned

1. **Research phase value**: Having clear research findings on PyJWT vs python-jose and pwdlib vs passlib prevented backtracking
2. **Exercise pattern evolution**: Providing working auth in Module 010 exercises (not stubs) lets learners focus on authorization — this pattern works well for layered concepts
3. **Mobile-dev analogies effectiveness**: Framing server-side auth in terms of client-side concepts (Keychain, Interceptors) makes theory accessible to target audience
4. **Dependency factory pattern clarity**: The `require_role()` factory pattern is powerful but needs clear explanation — theory + exercises combo works well

## Tags

`authentication` `authorization` `jwt` `rbac` `oauth2` `pyjwt` `pwdlib` `argon2` `roles` `permissions` `fastapi-security` `dependency-injection` `resource-ownership` `admin-panel` `module-009` `module-010`
