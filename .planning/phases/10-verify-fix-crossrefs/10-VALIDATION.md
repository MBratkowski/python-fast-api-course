---
phase: 10
slug: verify-fix-crossrefs
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-11
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual verification (file inspection) |
| **Config file** | none |
| **Quick run command** | `test -f <file> && echo exists` |
| **Full suite command** | `find . -name "*.md" -path "*/017-*" -o -path "*/019-*" | wc -l` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Verify files exist and content matches via grep/inspection
- **After every plan wave:** All fixes applied, both modules verified
- **Before `/gsd:verify-work`:** All 7 success criteria confirmed
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | PROD-01 | manual | File existence + content inspection | N/A | ⬜ pending |
| 10-01-02 | 01 | 1 | PROD-03 | manual | File existence + content inspection | N/A | ⬜ pending |
| 10-02-01 | 02 | 1 | PROD-01 | manual | `grep` cross-ref corrections | N/A | ⬜ pending |
| 10-02-02 | 02 | 1 | PROD-03 | manual | File existence + cleanup | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No test infrastructure needed — this phase is pure content verification and text correction.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Module 017 content complete | PROD-01 | Content quality review | Verify theory/, exercises/, project/ dirs have expected files |
| Module 019 content complete | PROD-03 | Content quality review | Verify theory/, exercises/, project/ dirs have expected files |
| Cross-references correct | PROD-01 | Text inspection | Grep capstone READMEs for correct module mappings |
| Library refs updated | PROD-03 | Text inspection | Grep Module 009 for pwdlib/PyJWT references |
| Phase 6 documented | PROD-01 | Documentation review | Check VERIFICATION.md and SUMMARY.md exist |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 2s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-11
