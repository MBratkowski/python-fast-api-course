---
phase: 10-verify-fix-crossrefs
plan: 02
subsystem: docs
tags: [cross-references, module-mappings, PyJWT, pwdlib, cleanup]

# Dependency graph
requires:
  - phase: 10-verify-fix-crossrefs
    provides: research audit identifying 7 cross-reference errors
provides:
  - Corrected module-to-topic mappings in capstone READMEs (019-022)
  - Updated Module 009 library references (PyJWT, pwdlib+Argon2)
  - Updated CLAUDE.md auth reference to PyJWT
  - Removed duplicate 012-async-python directory
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - 025-capstone-project/README.md
    - 025-capstone-project/project/README.md
    - 009-authentication-jwt/README.md
    - CLAUDE.md

key-decisions:
  - "Also fixed Module 017 name from 'Docker and Deployment' to 'Docker and Containers' in capstone prerequisites"
  - "Fixed additional incorrect module references in project/README.md Phase 5 and Phase 6 reference lines"
  - "Updated Module 009 theory topic from 'Password Hashing with bcrypt' to 'Password Hashing with Argon2'"

patterns-established: []

requirements-completed: [PROD-01, PROD-03]

# Metrics
duration: 3min
completed: 2026-03-11
---

# Phase 10 Plan 02: Fix Cross-References Summary

**Corrected 10+ module-to-topic mapping errors across capstone READMEs, updated Module 009 to reference PyJWT/pwdlib+Argon2, updated CLAUDE.md, and removed duplicate 012-async-python directory**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-11T17:27:12Z
- **Completed:** 2026-03-11T17:30:00Z
- **Tasks:** 2
- **Files modified:** 4 files modified, 1 directory removed

## Accomplishments
- Fixed Module 019-022 topic mappings in capstone README prerequisites and project README resources/references
- Updated Module 009 README code example from python-jose to PyJWT and bcrypt to pwdlib+Argon2
- Updated CLAUDE.md auth tech stack reference from python-jose to PyJWT
- Removed empty duplicate 012-async-python/ directory (content lives in 012-advanced-async-python/)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix capstone cross-references and Module 009 library refs** - `a31b0a8` (fix)
2. **Task 2: Remove duplicate 012-async-python directory** - `2062076` (chore)

## Files Created/Modified
- `025-capstone-project/README.md` - Fixed prerequisites: Module 017 name, Modules 019-022 topic mappings
- `025-capstone-project/project/README.md` - Fixed resources section and Phase 5/6 reference lines for Modules 019-022
- `009-authentication-jwt/README.md` - Updated to PyJWT import, pwdlib+Argon2 hashing, jwt.InvalidTokenError
- `CLAUDE.md` - Changed auth reference from python-jose to PyJWT
- `012-async-python/` - Removed (duplicate directory with only a README.md)

## Decisions Made
- Also fixed Module 017 name from "Docker and Deployment" to "Docker and Containers" (matched actual directory name 017-docker-containers)
- Fixed additional incorrect module references in project/README.md Phase 5 and Phase 6 "Reference:" lines beyond the 7 originally identified
- Updated Module 009 theory topic title from "Password Hashing with bcrypt" to "Password Hashing with Argon2" for consistency

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed additional incorrect module references in project/README.md**
- **Found during:** Task 1
- **Issue:** Phase 5 reference line said "019 (logging), 020 (health checks), 021 (versioning)" and Phase 6 said "022 (API documentation)" -- all shifted by one
- **Fix:** Updated to "019 (security), 020 (performance), 021 (logging)" and "022 (versioning)"
- **Files modified:** 025-capstone-project/project/README.md
- **Verification:** grep confirmed correct mappings
- **Committed in:** a31b0a8

**2. [Rule 1 - Bug] Fixed Module 017 name in capstone prerequisites**
- **Found during:** Task 1
- **Issue:** Listed as "Docker and Deployment" but actual directory is 017-docker-containers
- **Fix:** Changed to "Docker and Containers"
- **Files modified:** 025-capstone-project/README.md
- **Committed in:** a31b0a8

**3. [Rule 1 - Bug] Fixed Module 009 theory topic title**
- **Found during:** Task 1
- **Issue:** Theory topic 2 listed as "Password Hashing with bcrypt" but should reference Argon2
- **Fix:** Changed to "Password Hashing with Argon2"
- **Files modified:** 009-authentication-jwt/README.md
- **Committed in:** a31b0a8

---

**Total deviations:** 3 auto-fixed (3 bugs)
**Impact on plan:** All auto-fixes were additional instances of the same cross-reference/library errors the plan targeted. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All cross-reference errors identified in the Phase 10 research audit are now corrected
- Theory files in 025-capstone-project/theory/ have their own module mapping scheme (matching the shifted numbering) which was noted as correct per research -- not modified

---
*Phase: 10-verify-fix-crossrefs*
*Completed: 2026-03-11*
