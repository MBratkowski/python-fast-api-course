# Phase 9: Complete Missing Module Content - Research

**Researched:** 2026-03-10
**Domain:** Course content creation (CI/CD and Performance Optimization modules)
**Confidence:** HIGH

## Summary

Phase 9 closes the two "unsatisfied" requirement gaps identified in the v1.0 milestone audit: PROD-02 (Module 018 -- CI/CD) and PROD-04 (Module 020 -- Performance Optimization). Module 018 already has 3 of 6 theory files and a comprehensive README; it needs 3 more theory files, 3 exercises, and 1 project. Module 020 has only a README stub and needs all content from scratch: 6 theory files, 3 exercises, and 1 project.

The content pattern is well-established across 20+ completed modules. Each theory file follows a "Why This Matters" opening with mobile developer analogies, code examples with explanations, comparison tables, and "Key Takeaways" closing. Each exercise is a single Python file with docstring instructions, TODO stubs, and embedded pytest tests. Each project is a README.md with requirements checklist, starter template, and success criteria.

**Primary recommendation:** Split into two plans -- one per module. Follow the established content patterns exactly. No new tooling or libraries needed; this is purely content authoring work.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROD-02 | Module 018 -- CI/CD & Deployment: 6 theory files, 3 exercises, 1 project | 3 theory files exist; need theory 04-06, 3 exercises, 1 project. Content topics defined in README and REQUIREMENTS.md |
| PROD-04 | Module 020 -- Performance Optimization: 6 theory files, 3 exercises, 1 project | Only README stub exists; all content needed. Topics defined in REQUIREMENTS.md |
</phase_requirements>

## Standard Stack

This phase is content authoring, not software development. The "stack" is the established content patterns from completed modules.

### Content Patterns (from completed modules)

| Pattern | Where Used | Description |
|---------|-----------|-------------|
| Theory file format | All 20+ modules | `# Title`, `## Why This Matters` (mobile analogy), concept sections with code, comparison tables, `## Key Takeaways` |
| Exercise file format | All 20+ modules | Single `.py` file with docstring instructions, `# TODO` stubs with hints, embedded pytest tests, `pass` placeholder |
| Project README format | All 20+ modules | `## Overview`, `## Requirements` (checkbox lists), `## Starter Template` (code), `## Success Criteria`, `## Stretch Goals` |
| Naming convention | All modules | Theory: `01-topic-name.md` through `06-topic-name.md`; Exercises: `01_exercise_name.py` through `03_exercise_name.py`; Project: `project/README.md` |
| Mobile analogies | All theory files | Every "Why This Matters" section includes iOS/Android parallels |

### Module 018 Topics (from README)

| # | Topic | Status | File Name |
|---|-------|--------|-----------|
| 1 | CI/CD Concepts | EXISTS | `01-cicd-concepts.md` |
| 2 | GitHub Actions Basics | EXISTS | `02-github-actions-basics.md` |
| 3 | CI Testing Pipeline | EXISTS | `03-ci-testing-pipeline.md` |
| 4 | Docker Image Building | MISSING | `04-docker-image-building.md` |
| 5 | Cloud Deployment | MISSING | `05-cloud-deployment.md` |
| 6 | Environment Variables and Secrets | MISSING | `06-environment-variables-secrets.md` |

Exercises (all MISSING):
1. `01_workflow_file.py` -- Write a basic GitHub Actions workflow for Python
2. `02_ci_test_pipeline.py` -- Pipeline with PostgreSQL service container
3. `03_deployment_config.py` -- Docker image build and tag workflow

Project (MISSING): `project/README.md` -- Full CI/CD pipeline

### Module 020 Topics (from REQUIREMENTS.md)

| # | Topic | File Name |
|---|-------|-----------|
| 1 | Profiling | `01-profiling.md` |
| 2 | Database Query Analysis | `02-query-analysis.md` |
| 3 | N+1 Queries | `03-n-plus-one-queries.md` |
| 4 | Connection Pooling | `04-connection-pooling.md` |
| 5 | Async Best Practices | `05-async-best-practices.md` |
| 6 | Load Testing | `06-load-testing.md` |

Exercises (all MISSING):
1. `01_profile_code.py` -- Profile Python code
2. `02_fix_n_plus_one.py` -- Fix N+1 query problems
3. `03_load_test.py` -- Load testing

Project (MISSING): `project/README.md` -- Profile and optimize slow endpoint

## Architecture Patterns

### Module File Structure (established pattern)
```
0XX-module-name/
├── README.md              # Module overview, mobile context, prerequisites, topics
├── theory/
│   ├── 01-topic.md        # ~100-200 lines each
│   ├── 02-topic.md
│   ├── 03-topic.md
│   ├── 04-topic.md
│   ├── 05-topic.md
│   └── 06-topic.md
├── exercises/
│   ├── 01_exercise.py     # ~100-200 lines each (docstring + stubs + tests)
│   ├── 02_exercise.py
│   └── 03_exercise.py
└── project/
    └── README.md           # ~80-150 lines (requirements + starter + criteria)
```

### Theory File Pattern
```markdown
# Topic Title

## Why This Matters
[1-2 paragraphs with mobile developer analogy -- iOS/Android parallel]

## [Core Concept Sections]
[Explanation with code examples, tables, diagrams using ASCII]

## [Practical Examples]
[Real-world code snippets with comments]

## Key Takeaways
- [5-8 bullet points summarizing the key lessons]
```

### Exercise File Pattern
```python
"""
Exercise N: Title

Description of the task.
Your tasks:
1. Implement X
2. Implement Y

Mobile analogy: [iOS/Android parallel]

Run: pytest 0XX-module-name/exercises/0N_exercise.py -v
"""

import ...

# ============= TODO: Implement ... =============
# Detailed instructions with hints

def function_to_implement():
    """Docstring with args and returns."""
    # TODO: Implement this function
    pass

# ============= TESTS (do not modify below) =============

class TestExercise:
    """Tests that validate the implementation."""

    def test_basic_case(self):
        ...

    def test_edge_case(self):
        ...
```

### Project README Pattern
```markdown
# Project: Title

## Overview
[2-3 paragraphs describing what the student builds]

## Requirements
### 1. Feature Area
- [ ] Specific requirement
- [ ] Specific requirement

### 2. Another Feature Area
- [ ] Specific requirement

## Starter Template
[File structure + code scaffolding]

## Success Criteria
[Numbered list of verifiable outcomes]

## Stretch Goals
[Optional extensions for advanced learners]
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Content format | New content structures | Existing module patterns from phases 1-8 | Consistency across all 24 modules is critical for learner experience |
| Exercise testing | Complex test infrastructure | Single-file embedded pytest pattern | Established in all completed exercises; self-contained and runnable |
| Mobile analogies | Generic comparisons | Specific iOS (Xcode Cloud, XCTest) and Android (Bitrise, JUnit) parallels | Every completed theory file uses this pattern |

## Common Pitfalls

### Pitfall 1: CI/CD Exercises Cannot Run in CI
**What goes wrong:** CI/CD exercises are inherently about YAML configuration files, not executable Python code. Writing pytest-testable exercises for YAML workflow files is awkward.
**Why it happens:** The subject matter (GitHub Actions YAML) is not Python.
**How to avoid:** Follow the pattern from other non-executable modules. Module 006 (SQL Fundamentals) exercises were "pure Python (no database connection)" to build concepts. CI/CD exercises should validate YAML structure, test workflow logic using Python dictionaries/validation, or focus on the Python side (e.g., writing a conftest.py for CI, building a Docker tag string generator). The README already defines exercises as: (1) write a workflow file, (2) test pipeline config, (3) deployment config -- these can be YAML validation or Python helper exercises.
**Warning signs:** Exercises that require actual GitHub Actions runner to validate.

### Pitfall 2: Performance Exercises Needing Real Database
**What goes wrong:** Exercises about N+1 queries and connection pooling need SQLAlchemy models but the exercise pattern is single-file with embedded tests.
**Why it happens:** Performance optimization is inherently about real database behavior.
**How to avoid:** Follow Module 007 pattern: use sync SQLAlchemy with SQLite in-memory for exercises. Module 008 exercises use TestClient with sync SQLAlchemy. For N+1 query exercises, provide a pre-built SQLAlchemy model and demonstrate the problem/solution pattern. For profiling, use cProfile on pure Python functions. For load testing, theory-only with code examples (like Sentry/Prometheus in Module 021).
**Warning signs:** Exercises requiring PostgreSQL, Docker, or external services.

### Pitfall 3: Inconsistent Style with Existing Theory Files
**What goes wrong:** Module 018 already has 3 theory files written in a specific style. The remaining 3 must match.
**Why it happens:** Different writing sessions produce different tones.
**How to avoid:** Read the existing 3 theory files for Module 018 before writing 04-06. Match the level of detail, code example density, mobile analogy style, and section structure exactly.
**Warning signs:** New theory files feeling noticeably different in tone or depth.

### Pitfall 4: Module 020 README Needs Rewrite
**What goes wrong:** Module 020 has a minimal README stub (63 lines) vs the comprehensive README pattern (100+ lines with mobile context table, prerequisites, time estimates).
**Why it happens:** It was a placeholder from initial project setup.
**How to avoid:** Rewrite the README to match the Module 018 README pattern (which is comprehensive -- 110 lines with mobile context table, prerequisites, time estimates, example code).
**Warning signs:** Skipping the README rewrite and only adding content files.

## Code Examples

### CI/CD Exercise Pattern -- YAML Validation via Python

Since CI/CD exercises deal with YAML configuration, exercises can validate workflow structure using Python:

```python
"""
Exercise 1: Write a GitHub Actions Workflow File

Your task: Define a CI workflow as a Python dictionary that represents
valid GitHub Actions YAML structure, then validate it.

Run: pytest 018-ci-cd-deployment/exercises/01_workflow_file.py -v
"""

import yaml

# ============= TODO: Define your workflow =============
# Create a dictionary representing a GitHub Actions workflow with:
# - name: "CI"
# - on: push to main, pull_request to main
# - jobs: one job called "test" that runs on ubuntu-latest
# - steps: checkout, setup-python 3.12, install deps, run pytest

def create_ci_workflow() -> dict:
    """Return a dict representing a valid GitHub Actions CI workflow."""
    # TODO: Implement
    pass

# ============= TESTS =============
class TestWorkflow:
    def test_has_name(self):
        wf = create_ci_workflow()
        assert "name" in wf

    def test_triggers_on_push(self):
        wf = create_ci_workflow()
        assert "push" in wf["on"]
```

### Performance Exercise Pattern -- N+1 with SQLAlchemy + SQLite

```python
"""
Exercise 2: Fix N+1 Queries

Given a pre-built SQLAlchemy model, fix the N+1 query problem
using eager loading.

Run: pytest 020-performance-optimization/exercises/02_fix_n_plus_one.py -v
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, relationship, selectinload

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")

# TODO: Fix the N+1 query
def get_authors_with_books(session: Session) -> list[dict]:
    """Fetch all authors with their books using eager loading."""
    pass
```

### Profiling Exercise Pattern -- cProfile on Pure Python

```python
"""
Exercise 1: Profile Python Code

Use cProfile to identify the bottleneck in a slow function.

Run: pytest 020-performance-optimization/exercises/01_profile_code.py -v
"""

import cProfile
import pstats
import io

def slow_function():
    """A function with an intentional bottleneck."""
    result = []
    for i in range(1000):
        result.append(sum(range(i)))  # O(n^2) bottleneck
    return result

# TODO: Profile slow_function and return the name of the slowest function
def find_bottleneck() -> str:
    """Use cProfile to find which function takes the most time."""
    pass
```

## State of the Art

Not applicable -- this phase is content creation, not technology adoption. The content topics themselves cover current (2025-2026) versions:

| Topic | Current Best Practice | Version/Tool |
|-------|----------------------|-------------|
| CI/CD | GitHub Actions | actions/checkout@v4, actions/setup-python@v5 |
| Docker in CI | docker/build-push-action | @v5 |
| Cloud deployment | Railway, Fly.io, or AWS ECS | Current platforms |
| Python profiling | cProfile + snakeviz | stdlib + snakeviz for visualization |
| Load testing | Locust | locust >= 2.0 |
| N+1 fix | SQLAlchemy selectinload/joinedload | SQLAlchemy 2.0+ |
| Connection pooling | SQLAlchemy engine pool config | pool_size, max_overflow, pool_timeout |
| Async patterns | asyncio.gather, asyncio.TaskGroup | Python 3.12+ |

## Open Questions

1. **CI/CD exercise format for YAML content**
   - What we know: All other exercises are pure Python files with embedded pytest. CI/CD is inherently YAML-based.
   - What's unclear: Exact approach for making YAML exercises testable.
   - Recommendation: Use Python dict-to-YAML approach (define workflow as dict, validate structure with pytest). This maintains the single-file pattern while teaching YAML structure. Alternative: exercises focus on Python-side CI concerns (conftest.py for CI, Dockerfile optimization, deployment scripts).

2. **Load testing exercise feasibility**
   - What we know: Locust requires a running server to test against. Single-file exercise pattern does not support running servers.
   - What's unclear: Whether to make load testing theory-only (like Sentry/Prometheus in Module 021).
   - Recommendation: Make load testing theory-only for the Locust part. The exercise can focus on writing a locustfile (define tasks, validate structure) without requiring a running target. Or use a simpler approach -- benchmark with `time` module or `timeit`.

## Validation Architecture

> Nyquist validation is not explicitly set to false in config.json, so including this section.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (project standard) |
| Config file | None at project root -- exercises self-contain tests |
| Quick run command | `pytest 0XX-module/exercises/ -v` |
| Full suite command | `pytest 018-ci-cd-deployment/ 020-performance-optimization/ -v --co` (collect-only to verify structure) |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROD-02 | Module 018 has 6 theory, 3 exercises, 1 project | smoke | `ls 018-ci-cd-deployment/theory/*.md \| wc -l` (expect 6) | No -- Wave 0 |
| PROD-02 | Module 018 exercises have embedded tests | unit | `pytest 018-ci-cd-deployment/exercises/ -v --co` | No -- Wave 0 |
| PROD-04 | Module 020 has 6 theory, 3 exercises, 1 project | smoke | `ls 020-performance-optimization/theory/*.md \| wc -l` (expect 6) | No -- Wave 0 |
| PROD-04 | Module 020 exercises have embedded tests | unit | `pytest 020-performance-optimization/exercises/ -v --co` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `ls` to verify file count; `pytest --co` to verify tests collect
- **Per wave merge:** Full file count and structure verification
- **Phase gate:** All 6+3+1 files exist per module; all exercises collect without import errors

### Wave 0 Gaps
- [ ] Module 018: 3 theory files, 3 exercise files, 1 project README
- [ ] Module 020: 6 theory files, 3 exercise files, 1 project README, README rewrite

## Sources

### Primary (HIGH confidence)
- Existing module files in repository (021-logging-monitoring, 022-api-versioning, 023-rate-limiting) -- established content patterns
- Module 018 existing theory files (01, 02, 03) -- style reference for remaining files
- Module 018 README.md -- comprehensive topic list and exercise definitions
- REQUIREMENTS.md -- exact content specifications for PROD-02 and PROD-04
- v1.0-MILESTONE-AUDIT.md -- gap identification and evidence

### Secondary (MEDIUM confidence)
- Module 020 README.md -- topic list (but minimal; needs expansion)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new tech; pure content authoring following established patterns
- Architecture: HIGH -- 20+ completed modules provide clear structural template
- Pitfalls: HIGH -- based on direct analysis of existing content and subject matter constraints

**Research date:** 2026-03-10
**Valid until:** 2026-04-10 (stable -- content patterns are locked)
