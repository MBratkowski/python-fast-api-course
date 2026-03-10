# Phase 08: Capstone - Research

**Researched:** 2026-03-10
**Domain:** Capstone project synthesis -- API design planning, schema design, architecture review, deployment checklists, enhanced project guidance
**Confidence:** HIGH

## Summary

This research covers Module 025, the capstone module that synthesizes all 24 prior modules into a comprehensive final project. Unlike previous phases that introduced new technologies, this phase is purely about synthesis, review, and guided project planning. The module needs 6 theory files, 3 exercises, and an enhanced version of the existing project README.

The capstone module already has a README with project options (Social Media, E-Commerce, Task Management), requirements checklists, project structure, evaluation criteria, and a timeline. The phase goal is to (1) create theory files that review and connect concepts from all prior modules, (2) create exercises that guide learners through design review, schema modeling, and test planning, and (3) enhance the existing README with detailed starter templates, grading rubrics, and phased implementation guidance.

The key challenge is pedagogical, not technical: theory files must synthesize concepts across modules without just repeating them, exercises must be practical planning activities (not coding exercises in the traditional sense), and the enhanced README must give learners enough structure to succeed on their own without being so prescriptive that it eliminates the learning challenge.

**Primary recommendation:** Theory files should be structured as review-and-connect documents, each taking a major domain (API design, database schema, architecture, project setup, testing strategy, deployment) and showing how prior module concepts compose together. Exercises should produce concrete artifacts (API spec document, schema diagram/SQL, test plan) rather than runnable code. The enhanced README should add grading rubrics with point values, phased implementation checklists with time estimates, and starter code templates for each project option.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CAPS-01 | Module 025 -- Capstone Project: 6 theory files (API design planning, database schema design, architecture patterns review, project setup, testing strategy, deployment checklist), 3 exercises (design review, schema modeling, test planning), enhanced project (update existing README with detailed starter templates) | Theory files synthesize Modules 002-024 concepts; exercises produce planning artifacts; existing README at 025-capstone-project/README.md needs enhancement with templates, rubrics, phased guidance |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| N/A -- no new libraries | -- | This phase creates educational content only | Capstone references all prior module libraries but introduces no new ones |

### Referenced Libraries (from prior modules)

The capstone theory and project reference these established libraries. No new installation needed:

| Library | Module Introduced | Capstone Relevance |
|---------|-------------------|-------------------|
| FastAPI | 003 | Core framework for capstone project |
| Pydantic v2 | 005 | Request/response validation |
| SQLAlchemy 2.0 | 007 | ORM and database models |
| Alembic | 007 | Database migrations |
| PyJWT | 009 | JWT authentication |
| pwdlib (Argon2) | 009 | Password hashing |
| pytest + httpx | 011 | Testing framework |
| Redis (redis-py) | 014 | Caching layer |
| structlog | 021 | Structured logging |
| Docker | 017 | Containerization |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Design-focused exercises | More coding exercises | Capstone is about planning + synthesis, not new skill introduction; coding is the project itself |
| Three project options | Single prescribed project | Options let learners choose their interest area; adds engagement at cost of more template work |
| Grading rubrics | Simple pass/fail checklists | Rubrics give clearer feedback; worth the extra content effort |

**Installation:**
```bash
# No new packages -- capstone uses everything from Modules 002-024
# Learner's project will install from their own requirements.txt
```

## Architecture Patterns

### Module 025 Structure

```
025-capstone-project/
├── theory/
│   ├── 01-api-design-planning.md       # REST API design synthesis (Modules 002-004)
│   ├── 02-database-schema-design.md    # Schema design synthesis (Modules 006-008)
│   ├── 03-architecture-patterns.md     # Architecture review (service layer, DI, RBAC)
│   ├── 04-project-setup.md             # Project scaffolding (Docker, config, structure)
│   ├── 05-testing-strategy.md          # Test planning synthesis (Module 011 + integration)
│   └── 06-deployment-checklist.md      # Production readiness (Modules 017-024)
├── exercises/
│   ├── 01_design_review.py             # API design review exercise
│   ├── 02_schema_modeling.py           # Database schema modeling exercise
│   └── 03_test_planning.py             # Test plan creation exercise
├── project/
│   └── README.md                       # (existing -- enhanced with templates, rubrics, phases)
└── README.md                           # (existing -- enhanced with synthesis framing)
```

### Pattern 1: Theory as Synthesis, Not Repetition

**What:** Each theory file takes a domain, briefly recalls key concepts from prior modules, then shows how they compose for a real project
**When to use:** Every theory file in Module 025
**Structure:**

```markdown
# Topic Title

## Quick Review
- Key concept 1 (from Module X): one-sentence reminder
- Key concept 2 (from Module Y): one-sentence reminder

## How They Compose
[New insight: how these concepts work together at project scale]

## Decision Framework
[Flowchart or decision table for making design choices]

## Capstone Application
[Concrete example applying this to one of the three project options]

## Checklist
- [ ] Item 1
- [ ] Item 2
```

### Pattern 2: Exercises as Planning Artifacts

**What:** Exercises produce design documents and plans rather than runnable API code
**When to use:** All three exercises -- they are preparation for the project, not the project itself
**Key difference from other modules:** Exercises in Modules 002-024 produce runnable Python with embedded tests. Module 025 exercises should still be Python files with embedded tests, but the "code" validates planning artifacts (data structures representing API specs, schema designs, test plans).

**Example approach:**
```python
"""
Exercise 1: API Design Review

Review and validate an API design specification.
You'll create a structured API spec and verify it follows
REST best practices from Modules 002-005.

Run: pytest 025-capstone-project/exercises/01_design_review.py -v
"""

from pydantic import BaseModel
from typing import Optional


# ============= API SPECIFICATION MODEL (PROVIDED) =============

class EndpointSpec(BaseModel):
    method: str        # GET, POST, PUT, DELETE
    path: str          # /users/{id}
    description: str
    auth_required: bool
    request_body: Optional[str]   # Pydantic schema name
    response_model: str           # Pydantic schema name
    status_codes: list[int]       # Expected status codes


class APIDesign(BaseModel):
    title: str
    version: str
    base_url: str
    endpoints: list[EndpointSpec]


# ============= YOUR API DESIGN (IMPLEMENT) =============

# TODO: Create an API design for your chosen capstone project
# Requirements:
# - At least 10 endpoints covering CRUD for 2+ resources
# - Auth endpoints (register, login, refresh)
# - Proper HTTP methods for each operation
# - All endpoints have descriptive names
# - Protected endpoints marked with auth_required=True

def create_api_design() -> APIDesign:
    """Design your capstone API specification."""
    pass  # TODO: Implement


# ============= TESTS =============

def test_minimum_endpoints():
    design = create_api_design()
    assert len(design.endpoints) >= 10

def test_has_auth_endpoints():
    design = create_api_design()
    paths = [e.path for e in design.endpoints]
    assert any("register" in p or "signup" in p for p in paths)
    assert any("login" in p or "token" in p for p in paths)

def test_crud_coverage():
    design = create_api_design()
    methods = {e.method for e in design.endpoints}
    assert methods >= {"GET", "POST", "PUT", "DELETE"}

def test_protected_endpoints():
    design = create_api_design()
    protected = [e for e in design.endpoints if e.auth_required]
    assert len(protected) >= 5
```

### Pattern 3: Enhanced Project README Structure

**What:** The existing README gets enhanced with detailed starter templates, grading rubrics, and phased guidance
**Current state:** The README at `025-capstone-project/README.md` has project options, requirements checklists, project structure, evaluation criteria, and timeline
**Enhancement areas:**

1. **Grading rubrics** -- Point-based scoring for each category (functionality, code quality, testing, documentation, production readiness)
2. **Phased implementation guide** -- Break the timeline into weekly phases with specific deliverables and checkpoints
3. **Starter templates** -- For each project option, provide: database schema SQL, Pydantic model stubs, initial API route stubs, Docker Compose template, CI/CD workflow template
4. **Common mistakes** -- What past learners (hypothetically) get wrong at each phase
5. **Self-assessment checklists** -- Per-phase checklists learners can use to verify their own progress

### Anti-Patterns to Avoid

- **Just repeating module content in theory files:** Theory must add value through synthesis and composition, not recap
- **Making exercises too open-ended:** Without testable structure, exercises become "write an essay" which is hard to self-assess
- **Providing too much starter code in the project:** The capstone should challenge learners to build from scratch; templates should scaffold structure, not implement features
- **Ignoring the mobile developer audience:** Theory files should continue the mobile-developer analogy pattern established in all prior modules
- **Skipping the "Why This Matters" mobile context framing:** Every module README and theory file starts with mobile developer context; Module 025 must maintain this

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API design validation | Manual review instructions | Pydantic models representing API specs | Testable, structured, consistent |
| Schema validation | Free-form SQL writing | Pydantic models representing table/column specs | Tests can verify relationships, constraints, naming |
| Test plan structure | Unstructured text document | Python data structures with validation tests | Learners can verify their plan is complete |
| Project templates | Everything from scratch | Provide docker-compose.yml, .github/workflows/ci.yml, pyproject.toml templates | These are boilerplate, not learning objectives |

**Key insight:** The capstone module's exercises should use Pydantic models to represent planning artifacts (API specs, schemas, test plans) so that pytest can validate them. This maintains the established pattern of "exercises with embedded tests" while adapting to planning-focused content.

## Common Pitfalls

### Pitfall 1: Theory Files That Are Just Module Summaries

**What goes wrong:** Theory files become "Module 002 covered X, Module 003 covered Y" without adding synthesis value
**Why it happens:** Natural tendency to recap rather than compose
**How to avoid:** Each theory file should answer "How do these concepts work TOGETHER at project scale?" not "What did we learn?"
**Warning signs:** Theory file reads like a table of contents for prior modules

### Pitfall 2: Exercises Too Abstract for Self-Assessment

**What goes wrong:** Exercises say "design an API" without testable criteria, making it impossible for learners to know if they succeeded
**Why it happens:** Planning exercises are inherently less structured than coding exercises
**How to avoid:** Use Pydantic models to represent planning artifacts; write tests that validate completeness and structure
**Warning signs:** Exercise has no embedded tests or only trivial tests

### Pitfall 3: Project README Overwhelms Learners

**What goes wrong:** Enhanced README with rubrics, templates, and phases becomes so long that learners don't know where to start
**Why it happens:** Trying to be comprehensive
**How to avoid:** Use clear section headers with "start here" callouts; keep each phase's guidance to one screen of text; put detailed templates in expandable sections or separate files
**Warning signs:** README exceeds 300 lines; no clear "start here" marker

### Pitfall 4: Starter Templates Do Too Much

**What goes wrong:** Templates provide so much code that learners just fill in blanks instead of building
**Why it happens:** Wanting to help learners succeed
**How to avoid:** Templates should provide structure (file layout, Docker config, CI workflow) but NOT business logic. Schema templates show table structure but not all columns. Route templates show the router setup but not endpoint implementations.
**Warning signs:** Learner can pass 50%+ of requirements just by using templates without writing any logic

### Pitfall 5: Missing Cross-Module References

**What goes wrong:** Theory files don't explicitly link back to which module covered each concept
**Why it happens:** Assuming learners remember where things were taught
**How to avoid:** Every concept reference should include "(Module XXX)" so learners can go back and review
**Warning signs:** Theory file mentions "dependency injection" without referencing Module 005/008

### Pitfall 6: Inconsistent Difficulty Across Project Options

**What goes wrong:** One project option (e.g., E-Commerce with payment integration) is significantly harder than others
**Why it happens:** Different domains have different inherent complexity
**How to avoid:** Ensure all three options have comparable scope: 3-4 main resources, similar relationship complexity, equivalent auth needs. Payment integration should be optional/bonus.
**Warning signs:** One option requires external service integration while others don't

## Code Examples

### Exercise Pattern: Schema Modeling with Testable Artifacts

```python
"""
Exercise 2: Database Schema Modeling

Model your capstone database schema as Python data structures
and validate it meets relational design requirements.

Run: pytest 025-capstone-project/exercises/02_schema_modeling.py -v
"""

from pydantic import BaseModel


class Column(BaseModel):
    name: str
    type: str          # "integer", "varchar", "text", "timestamp", "boolean"
    primary_key: bool = False
    nullable: bool = True
    foreign_key: str | None = None  # "table.column" format


class Table(BaseModel):
    name: str
    columns: list[Column]


class DatabaseSchema(BaseModel):
    tables: list[Table]


# TODO: Create your capstone database schema
def create_schema() -> DatabaseSchema:
    """Design the database schema for your capstone project."""
    pass  # Implement


# Tests validate schema completeness
def test_minimum_tables():
    schema = create_schema()
    assert len(schema.tables) >= 4, "Need at least 4 tables"

def test_all_tables_have_primary_key():
    schema = create_schema()
    for table in schema.tables:
        pks = [c for c in table.columns if c.primary_key]
        assert len(pks) >= 1, f"Table {table.name} needs a primary key"

def test_has_foreign_keys():
    schema = create_schema()
    fks = [
        c for t in schema.tables
        for c in t.columns if c.foreign_key
    ]
    assert len(fks) >= 3, "Need at least 3 foreign key relationships"

def test_has_user_table():
    schema = create_schema()
    table_names = [t.name.lower() for t in schema.tables]
    assert "users" in table_names or "user" in table_names

def test_has_timestamps():
    schema = create_schema()
    for table in schema.tables:
        col_names = [c.name for c in table.columns]
        assert "created_at" in col_names, f"Table {table.name} needs created_at"
```

### Exercise Pattern: Test Plan with Validation

```python
"""
Exercise 3: Test Planning

Create a test plan for your capstone project.
Define test cases that cover critical paths.

Run: pytest 025-capstone-project/exercises/03_test_planning.py -v
"""

from pydantic import BaseModel


class TestCase(BaseModel):
    name: str                    # test_user_registration_success
    category: str                # "unit", "integration", "e2e"
    endpoint: str                # POST /auth/register
    description: str             # What this test verifies
    priority: str                # "critical", "high", "medium", "low"


class TestPlan(BaseModel):
    test_cases: list[TestCase]


def create_test_plan() -> TestPlan:
    """Create a comprehensive test plan for your capstone."""
    pass  # Implement


def test_minimum_test_cases():
    plan = create_test_plan()
    assert len(plan.test_cases) >= 15

def test_has_critical_tests():
    plan = create_test_plan()
    critical = [t for t in plan.test_cases if t.priority == "critical"]
    assert len(critical) >= 5

def test_covers_auth():
    plan = create_test_plan()
    auth_tests = [t for t in plan.test_cases if "auth" in t.endpoint.lower()]
    assert len(auth_tests) >= 3

def test_has_all_categories():
    plan = create_test_plan()
    categories = {t.category for t in plan.test_cases}
    assert "unit" in categories
    assert "integration" in categories
```

### Theory File Structure: Deployment Checklist Example

```markdown
# Deployment Checklist

## Quick Review
- Docker multi-stage builds (Module 017): Separate build and runtime stages
- GitHub Actions CI/CD (Module 018): Automated test + deploy pipeline
- Security headers and CORS (Module 019): Production hardening
- Performance profiling (Module 020): N+1 queries, connection pooling
- Structured logging (Module 021): JSON logs with request tracing
- API versioning (Module 022): URL prefix versioning with deprecation
- Rate limiting (Module 023): Token bucket with Redis
- Service architecture (Module 024): When to split vs keep monolith

## Pre-Deployment Checklist

### Security (Module 019)
- [ ] All inputs validated with Pydantic models
- [ ] SQL injection prevented (SQLAlchemy parameterized queries)
- [ ] CORS configured for specific origins
- [ ] Security headers set (X-Content-Type-Options, etc.)
- [ ] Secrets in environment variables, not code
- [ ] Rate limiting enabled on auth endpoints

### Performance (Module 020)
- [ ] No N+1 queries (use joinedload/selectinload)
- [ ] Database indexes on frequently queried columns
- [ ] Redis caching for expensive queries
- [ ] Connection pooling configured

[... continues for each domain ...]
```

### Enhanced README: Grading Rubric Pattern

```markdown
## Grading Rubric

### Functionality (30 points)
| Criteria | Points | Description |
|----------|--------|-------------|
| Auth system works | 8 | Register, login, token refresh, protected routes |
| CRUD operations | 8 | Create, read, update, delete for all main resources |
| Input validation | 6 | Pydantic schemas reject invalid data with clear errors |
| Error handling | 4 | Consistent error format, appropriate status codes |
| Relationships | 4 | Related data correctly linked and queryable |

### Code Quality (20 points)
| Criteria | Points | Description |
|----------|--------|-------------|
| Project structure | 5 | Follows src/ layout with clear separation |
| Service layer | 5 | Business logic in services, not routes |
| Type hints | 5 | Functions and models fully typed |
| Clean code | 5 | No dead code, clear naming, DRY |

### Testing (20 points)
| Criteria | Points | Description |
|----------|--------|-------------|
| Test coverage | 8 | 80%+ line coverage |
| Auth tests | 4 | Registration, login, protected endpoints |
| CRUD tests | 4 | Happy path + error cases for each resource |
| Fixtures | 4 | Proper test isolation with fixtures |

### Documentation (15 points)
| Criteria | Points | Description |
|----------|--------|-------------|
| README | 5 | Setup instructions, API overview |
| API docs | 5 | OpenAPI/Swagger with descriptions |
| Code comments | 5 | Complex logic explained |

### Production Readiness (15 points)
| Criteria | Points | Description |
|----------|--------|-------------|
| Docker setup | 5 | Dockerfile + docker-compose with all services |
| CI pipeline | 5 | GitHub Actions runs tests on push |
| Logging | 3 | Structured logging configured |
| Health check | 2 | /health endpoint responds |
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Capstone as "just build something" | Guided capstone with rubrics and phases | Modern bootcamp pedagogy | Better completion rates, clearer expectations |
| Free-form design exercises | Structured planning with testable artifacts | Test-driven curriculum design | Learners can self-assess progress |
| Single capstone option | Multiple project options | Learner-choice pedagogy | Higher engagement, same skill coverage |
| Final project only | Theory + exercises + enhanced project | Scaffolded learning design | Planning skills taught explicitly, not assumed |

## Open Questions

1. **Exercise file format: pure planning or still runnable Python?**
   - What we know: All prior modules use .py files with embedded pytest tests. Requirement says "exercises guide learners through design review, schema modeling, and test planning."
   - What's unclear: Whether exercises should be runnable code or markdown planning documents
   - Recommendation: Keep as .py files with Pydantic models representing planning artifacts and pytest tests validating completeness. This maintains the established pattern while adapting to planning content. Confidence: HIGH -- this approach works and is consistent.

2. **How much to change the existing README vs create new project/README.md**
   - What we know: The top-level 025-capstone-project/README.md exists with basic project info. The requirement says "enhanced project (update existing README with detailed starter templates)."
   - What's unclear: Whether to update the top-level README or create/update a project/README.md (as other modules do)
   - Recommendation: Update the top-level README.md with module framing (Why This Module?, What You'll Learn, Mobile Developer Context, Topics). Create project/README.md with the detailed capstone guidance (rubrics, phases, templates). This follows the dual-README pattern of other modules.

3. **Starter template depth for three project options**
   - What we know: Three options (Social Media, E-Commerce, Task Management) each need enough scaffolding to start
   - What's unclear: How detailed each option's template should be
   - Recommendation: Provide a common template (Docker, CI/CD, project structure) shared across all options, plus per-option schema outlines (table names and key columns only) and endpoint lists. Keep templates structural, not implementational.

## Sources

### Primary (HIGH confidence)
- Existing module patterns from Modules 002-024 in this repository -- established content structure, exercise format, README format
- Existing 025-capstone-project/README.md -- current state to enhance
- Phase 7 research and completed plans -- most recent content creation patterns

### Secondary (MEDIUM confidence)
- FastAPI project structure best practices (from FastAPI docs and course architecture in CLAUDE.md)
- Capstone project pedagogy patterns from software engineering bootcamps

### Tertiary (LOW confidence)
- None -- this phase relies entirely on established project patterns and pedagogical decisions

## Metadata

**Confidence breakdown:**
- Content structure: HIGH - follows established pattern from 24 prior modules; no new technology to research
- Theory file topics: HIGH - directly specified in CAPS-01 requirement (API design, schema design, architecture review, project setup, testing strategy, deployment checklist)
- Exercise approach: HIGH - Pydantic-based planning artifacts maintain consistency with prior exercise patterns
- Enhanced README: HIGH - existing README provides clear base; enhancements (rubrics, phases, templates) are well-understood pedagogical tools

**Research date:** 2026-03-10
**Valid until:** ~2026-06-10 (90 days -- no external dependencies; content structure is stable)
