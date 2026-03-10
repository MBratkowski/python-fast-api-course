---
phase: 9
slug: complete-missing-content
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-10
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (project standard) |
| **Config file** | None at project root — exercises self-contain tests |
| **Quick run command** | `pytest 0XX-module/exercises/ -v` |
| **Full suite command** | `pytest 018-ci-cd-deployment/ 020-performance-optimization/ -v --co` |
| **Estimated runtime** | ~5 seconds (collect-only) |

---

## Sampling Rate

- **After every task commit:** `ls` to verify file count; `pytest --co` to verify tests collect
- **After every plan wave:** Full file count and structure verification
- **Before `/gsd:verify-work`:** All 6+3+1 files exist per module; all exercises collect without import errors
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | PROD-02 | smoke | `ls 018-ci-cd-deployment/theory/*.md \| wc -l` (expect 6) | ❌ W0 | ⬜ pending |
| 09-01-02 | 01 | 1 | PROD-02 | unit | `pytest 018-ci-cd-deployment/exercises/ -v --co` | ❌ W0 | ⬜ pending |
| 09-02-01 | 02 | 1 | PROD-04 | smoke | `ls 020-performance-optimization/theory/*.md \| wc -l` (expect 6) | ❌ W0 | ⬜ pending |
| 09-02-02 | 02 | 1 | PROD-04 | unit | `pytest 020-performance-optimization/exercises/ -v --co` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Module 018: 3 theory files, 3 exercise files, 1 project README
- [ ] Module 020: 6 theory files, 3 exercise files, 1 project README, README rewrite

*All content is new — Wave 0 establishes the file structure.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Content quality matches established pattern | PROD-02, PROD-04 | Style/pedagogy review | Compare against completed modules (021, 022, 023) for tone, depth, structure |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
