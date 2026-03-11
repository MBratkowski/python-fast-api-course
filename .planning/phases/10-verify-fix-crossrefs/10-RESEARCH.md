# Phase 10: Verify Existing Content & Fix Cross-References - Research

**Researched:** 2026-03-11
**Domain:** Content verification, cross-reference correction, tech debt cleanup
**Confidence:** HIGH

## Summary

Phase 10 is a verification and cleanup phase, not a content creation phase. The work involves three categories: (1) formally verifying that Modules 017 (Docker) and 019 (Security) are complete (content already exists in the repo but was never verified through the GSD process since Phase 6 was skipped), (2) correcting 7 specific cross-reference errors in the capstone module where module numbers are mapped to wrong topic names, and (3) cleaning up tech debt items identified in the v1.0 Milestone Audit.

All issues are precisely identified with file paths and line numbers from the audit report. No research into external libraries or frameworks is needed -- this is entirely an internal content correction phase.

**Primary recommendation:** Structure as a single plan with 3-4 tasks: one for Module 017/019 verification, one for cross-reference fixes, one for tech debt cleanup (009 README, duplicate directory, Phase 6 docs).

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROD-01 | Module 017 -- Docker & Containers: 6 theory files, 3 exercises, 1 project | Content exists (committed at 1a992ec). Needs formal verification with VERIFICATION.md evidence. All 10 files confirmed present in 017-docker-containers/. |
| PROD-03 | Module 019 -- Security Best Practices: 7 theory files, 3 exercises, 1 project | Content exists (committed at afc7137). Needs formal verification with VERIFICATION.md evidence. All 11 files confirmed present in 019-security-best-practices/. |
</phase_requirements>

## Inventory of Issues

### Issue 1: Module 017 (Docker) -- Needs Formal Verification

**Status:** Content EXISTS but was never formally verified
**Location:** `017-docker-containers/`
**Content found:**
- `theory/`: 01-container-concepts.md, 02-dockerfile-basics.md, 03-multi-stage-builds.md, 04-docker-compose.md, 05-networking-volumes.md, 06-production-optimizations.md (6 files)
- `exercises/`: 01_dockerfile.py, 02_docker_compose.py, 03_multi_stage_build.py (3 files)
- `project/README.md` (1 file)
- `README.md` (module overview)

**What to do:** Create VERIFICATION.md evidence that these files meet PROD-01 requirements (check for "Why This Matters" sections, "Key Takeaways", TODO stubs in exercises, embedded pytest tests, project starter template).

### Issue 2: Module 019 (Security) -- Needs Formal Verification

**Status:** Content EXISTS but was never formally verified
**Location:** `019-security-best-practices/`
**Content found:**
- `theory/`: 01-owasp-top-10.md through 07-security-headers.md (7 files -- note: this module has 7 theory files, not 6)
- `exercises/`: 01_identify_vulnerabilities.py, 02_cors_configuration.py, 03_input_sanitization.py (3 files)
- `project/README.md` (1 file)
- `README.md` (module overview)

**What to do:** Create VERIFICATION.md evidence that these files meet PROD-03 requirements.

### Issue 3: Capstone Cross-Reference Errors (7 total)

**Confidence:** HIGH -- verified by direct file inspection

#### In `025-capstone-project/README.md` (Prerequisites section, lines 52-57):

| Line | Current (WRONG) | Correct |
|------|-----------------|---------|
| 54 | Module 019: Logging and Monitoring | Module 019: Security Best Practices |
| 55 | Module 020: Health Checks | Module 020: Performance Optimization |
| 56 | Module 021: API Versioning | Module 021: Logging and Monitoring |
| 57 | Module 022: API Documentation | Module 022: API Versioning |

**Root cause:** Modules 019-022 were shifted by one position. The original mapping skipped "Security Best Practices" and inserted a phantom "API Documentation" module. Module 017 label ("Docker and Deployment") is slightly off but not critically wrong (actual: "Docker and Containers").

#### In `025-capstone-project/project/README.md` (Resources section, lines 431-432):

| Line | Current (WRONG) | Correct |
|------|-----------------|---------|
| 431 | Module 019 (Logging) | Module 019 (Security Best Practices) |
| 431 | Module 020 (Health Checks) | Module 020 (Performance Optimization) |
| 432 | Module 021 (Versioning) | Module 021 (Logging and Monitoring) |

**Note:** The grouping in project/README.md also needs adjustment since Module 019 (Security) should not be under "Production" alongside "Health Checks" -- it belongs with Auth or gets its own Security grouping. Module 022 (API Versioning) is correctly labeled on line 432.

### Issue 4: Module 009 README Library References

**Location:** `009-authentication-jwt/README.md`
**Current:** References "bcrypt" for password hashing and uses `from jose import jwt` in code example
**Should be:** "pwdlib with Argon2" for password hashing and `import jwt` (PyJWT) for JWT operations
**Decision source:** Phase 3 decisions -- [03-01]: Use PyJWT (not python-jose which is abandoned), Use pwdlib with Argon2 (not passlib which is deprecated)

**Specific lines to fix:**
- Line 9: `- Password hashing (bcrypt)` should be `- Password hashing (pwdlib + Argon2)`
- Line 38: `from jose import jwt, JWTError` should be `import jwt` (PyJWT uses `jwt.decode()` and `jwt.exceptions.InvalidTokenError`)
- Line 46: `except JWTError:` should be `except jwt.InvalidTokenError:`

### Issue 5: Duplicate Empty Directory

**Location:** `012-async-python/` -- contains only a README.md
**Actual module:** `012-advanced-async-python/` -- contains all theory, exercises, project content
**Action:** Remove `012-async-python/` directory entirely

### Issue 6: Phase 6 Missing VERIFICATION.md and SUMMARY.md

**Location:** `.planning/phases/06-production-part-a/`
**Current contents:** 06-01-PLAN.md, 06-02-PLAN.md, 06-RESEARCH.md (plans exist but were never executed)
**Context:** Phase 6 was originally planned for Modules 017-020 but was never formally executed. Modules 017 and 019 content was committed directly. Modules 018 and 020 were completed in Phase 9. Phase 7 skipped Phase 6's dependency.

**What to create:**
- `06-VERIFICATION.md`: Document that Phase 6 plans were superseded -- PROD-01/03 verified in Phase 10, PROD-02/04 completed in Phase 9
- Phase 6 does NOT need SUMMARY.md files since no plans were executed -- it needs a phase-level note explaining the supersession

### Issue 7: Module 020 Phantom References in Capstone (NOW RESOLVED)

The audit flagged that capstone theory/06-deployment-checklist.md references Module 020 content (N+1 queries, connection pooling) that "does not exist." However, Phase 9 has since completed Module 020 content. These references are now VALID. No action needed.

**Verification:** Module 020 now has theory/03-n-plus-one-queries.md and theory/04-connection-pooling.md (confirmed in Phase 9 verification).

## Architecture Patterns

### Verification Pattern (from Phase 9 VERIFICATION.md)

The established verification format checks:

1. **Observable Truths table** -- each success criterion mapped to VERIFIED/FAILED with evidence
2. **Required Artifacts table** -- each file listed with expected content, status, and details (line counts, key sections)
3. **Key Link Verification** -- cross-references between files verified as WIRED/BROKEN
4. **Requirements Coverage** -- requirement IDs mapped to plans with SATISFIED/UNSATISFIED status
5. **Anti-Patterns Found** -- any issues with severity ratings
6. **Gaps Summary** -- remaining issues

### Verification Checklist for Modules 017 and 019

For each module, verify:
- [ ] Theory files have "Why This Matters" mobile-dev framing
- [ ] Theory files have "Key Takeaways" sections
- [ ] Exercise files have TODO stubs
- [ ] Exercise files have embedded pytest tests that would fail until stubs are filled
- [ ] Project README has requirements, starter template, and success criteria
- [ ] Module README follows established pattern

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Module-to-topic mapping | Manual lookup | Actual module README first lines | Each README line 1 has canonical title |
| Verification format | New format | Copy Phase 9's 09-VERIFICATION.md structure | Consistency with existing verifications |

## Common Pitfalls

### Pitfall 1: Incomplete Cross-Reference Fix
**What goes wrong:** Fixing the 7 identified errors but missing other references in theory files
**Why it happens:** The audit identified 7 in README/project, but theory files also reference module numbers
**How to avoid:** Grep ALL of `025-capstone-project/` for "Module 019", "Module 020", "Module 021", "Module 022" and verify each reference. Theory files (especially 06-deployment-checklist.md) have extensive module references that appear CORRECT (they reference Module 019 as security, Module 020 as performance, etc.)
**Note:** After inspection, the theory files use CORRECT module-to-topic mappings. Only the README.md prerequisites and project/README.md resources sections have errors.

### Pitfall 2: Over-Scoping Phase 6 Documentation
**What goes wrong:** Trying to retroactively create full SUMMARY.md files for plans that were never executed
**Why it happens:** Phase 6 has plans but they were superseded by Phase 9 and 10
**How to avoid:** Create a minimal VERIFICATION.md noting supersession, not fabricated summaries

### Pitfall 3: Forgetting CLAUDE.md Library Reference
**What goes wrong:** Fixing Module 009 README but leaving CLAUDE.md referencing python-jose
**Note from audit:** "CLAUDE.md says 'python-jose' but course uses PyJWT"
**Location:** CLAUDE.md line `- **Auth**: JWT (python-jose)` should be `- **Auth**: JWT (PyJWT)`

## Complete Fix Inventory

| # | File | Change | Category |
|---|------|--------|----------|
| 1 | `025-capstone-project/README.md:54` | "Logging and Monitoring" -> "Security Best Practices" | Cross-ref |
| 2 | `025-capstone-project/README.md:55` | "Health Checks" -> "Performance Optimization" | Cross-ref |
| 3 | `025-capstone-project/README.md:56` | "API Versioning" -> "Logging and Monitoring" | Cross-ref |
| 4 | `025-capstone-project/README.md:57` | "API Documentation" -> "API Versioning" | Cross-ref |
| 5 | `025-capstone-project/project/README.md:431` | "Module 019 (Logging)" -> "Module 019 (Security)" | Cross-ref |
| 6 | `025-capstone-project/project/README.md:431` | "Module 020 (Health Checks)" -> "Module 020 (Performance)" | Cross-ref |
| 7 | `025-capstone-project/project/README.md:431-432` | Regroup: 019=Security, 020=Performance, 021=Logging, 022=Versioning | Cross-ref |
| 8 | `009-authentication-jwt/README.md:9` | "bcrypt" -> "pwdlib + Argon2" | Library ref |
| 9 | `009-authentication-jwt/README.md:38` | `from jose import jwt, JWTError` -> `import jwt` | Library ref |
| 10 | `009-authentication-jwt/README.md:46` | `except JWTError:` -> `except jwt.InvalidTokenError:` | Library ref |
| 11 | `CLAUDE.md` | `python-jose` -> `PyJWT` | Library ref |
| 12 | `012-async-python/` | Remove entire directory | Cleanup |
| 13 | `.planning/phases/06-production-part-a/06-VERIFICATION.md` | Create supersession doc | Phase docs |

## Validation Architecture

> nyquist_validation not explicitly set in config.json -- treating as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | None (standard pytest discovery) |
| Quick run command | `pytest -x` |
| Full suite command | `pytest -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROD-01 | Module 017 content complete | manual-only | File existence + content inspection | N/A -- verification phase |
| PROD-03 | Module 019 content complete | manual-only | File existence + content inspection | N/A -- verification phase |

**Justification for manual-only:** This phase verifies content completeness (markdown files, exercise structure, cross-references). There are no code changes that produce runnable behavior. Verification is done by file inspection, not test execution.

### Sampling Rate
- **Per task commit:** Verify files exist and content matches expectations via grep/inspection
- **Per wave merge:** N/A -- single wave
- **Phase gate:** All 13 fixes applied, both modules verified, Phase 6 documented

### Wave 0 Gaps
None -- no test infrastructure needed. This phase is pure content verification and text correction.

## Open Questions

1. **Module 017 content quality**
   - What we know: Files exist with correct names and counts
   - What's unclear: Whether theory files follow the exact same quality pattern as later phases (mobile-dev analogies, etc.) since they were created outside the GSD process
   - Recommendation: During verification, check for standard sections but do not rewrite content -- just document findings

2. **Phase 6 SUMMARY.md scope**
   - What we know: Roadmap success criterion says "Phase 6 has VERIFICATION.md and SUMMARY.md"
   - What's unclear: Whether SUMMARY.md means per-plan summaries (which would be fabricated) or a phase-level summary
   - Recommendation: Create a phase-level SUMMARY.md explaining supersession status, not per-plan summaries for plans that were never executed

## Sources

### Primary (HIGH confidence)
- Direct file inspection of all referenced modules and directories
- `.planning/v1.0-MILESTONE-AUDIT.md` -- source of all identified gaps
- `.planning/phases/09-complete-missing-content/09-VERIFICATION.md` -- verification format reference
- `.planning/STATE.md` -- project decisions on library choices (PyJWT, pwdlib)

### Secondary (MEDIUM confidence)
- None needed -- all research is internal to the project

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Issue inventory: HIGH -- all issues verified by direct file inspection against audit report
- Fix specifics: HIGH -- line numbers and exact text changes identified
- Verification format: HIGH -- follows established pattern from Phase 9

**Research date:** 2026-03-11
**Valid until:** 2026-04-11 (stable -- internal project content)
