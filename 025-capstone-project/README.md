# Module 025: Capstone Project

## Why This Module?

As a mobile developer, you have built complete apps from idea to App Store or Play Store. You know the full lifecycle: planning the architecture, implementing features, writing tests, configuring CI/CD, and shipping to production. Building a backend API from scratch requires the same end-to-end thinking -- planning your data model, designing endpoints, implementing business logic, testing edge cases, and deploying to a server.

This module brings together everything from Modules 002-024 into a single project. Instead of following guided exercises, you will make architectural decisions, solve integration problems, and build something production-ready on your own.

## What You'll Learn

- How to plan an API design from requirements (synthesizing Modules 002-005)
- How to design a database schema for a real application (synthesizing Modules 006-008)
- How to make architecture decisions (service layer, auth, caching from Modules 008-014)
- How to set up a project from scratch (Docker, config from Modules 017-018)
- How to create a testing strategy (from Module 011)
- How to prepare for production deployment (from Modules 017-024)

## Mobile Developer Context

**Full Project Lifecycle Across Platforms:**

| Phase | iOS (Swift) | Android (Kotlin) | Backend (Python/FastAPI) |
|-------|-------------|-------------------|--------------------------|
| Planning | Wireframes + specs | Material Design + specs | API design document |
| Architecture | MVVM + Coordinator | MVVM + Clean Architecture | Layered architecture + DI |
| Data Layer | Core Data / SwiftData | Room / SQLDelight | SQLAlchemy + Alembic |
| Auth | Keychain + App Attest | Keystore + SafetyNet | JWT + bcrypt/argon2 |
| Testing | XCTest + UI Testing | JUnit + Espresso | pytest + TestClient |
| Deployment | App Store Connect | Play Console | Docker + CI/CD |
| Monitoring | Crashlytics / MetricKit | Firebase Crashlytics | structlog + health checks |

**Key Insight:** The project lifecycle is remarkably similar across platforms. The main difference is that backend projects need to handle concurrent users, persistent state, and always-on availability -- concerns that mobile platforms handle for you through the OS.

## Prerequisites

Before starting, you should have completed:
- [ ] Module 002: HTTP and REST Fundamentals
- [ ] Module 003: FastAPI Basics
- [ ] Module 004: Request Handling
- [ ] Module 005: Response Handling and Error Management
- [ ] Module 006: SQL Fundamentals
- [ ] Module 007: SQLAlchemy ORM
- [ ] Module 008: Database Integration with FastAPI
- [ ] Module 009: Authentication with JWT
- [ ] Module 010: Authorization and Security
- [ ] Module 011: Testing FastAPI Applications
- [ ] Module 012: Async Python
- [ ] Module 013: Background Tasks
- [ ] Module 014: Caching with Redis
- [ ] Module 015: File Handling
- [ ] Module 016: WebSockets
- [ ] Module 017: Docker and Containers
- [ ] Module 018: CI/CD Pipelines
- [ ] Module 019: Security Best Practices
- [ ] Module 020: Performance Optimization
- [ ] Module 021: Logging and Monitoring
- [ ] Module 022: API Versioning
- [ ] Module 023: Rate Limiting
- [ ] Module 024: Microservices Basics

## Topics

### Theory
1. API Design Planning -- REST API design synthesis (Modules 002-005)
2. Database Schema Design -- Schema design synthesis (Modules 006-008)
3. Architecture Patterns Review -- Architecture synthesis (Modules 008-014)
4. Project Setup Guide -- Project scaffolding (Modules 003, 017)
5. Testing Strategy -- Test planning synthesis (Module 011)
6. Deployment Checklist -- Production readiness (Modules 017-024)

### Exercises
1. Design Review -- Create and validate an API specification
2. Schema Modeling -- Model a database schema as testable artifacts
3. Test Planning -- Build a comprehensive test plan

### Project
Comprehensive capstone project: build a complete, production-ready REST API. See `project/README.md` for full details including grading rubrics, phased implementation guide, and starter templates.

## Time Estimate

- Theory: ~120 minutes
- Exercises: ~60 minutes
- Project: ~40+ hours (self-paced over 2-6 weeks)

## Note

This module is different from Modules 002-024 in several important ways. The theory files are synthesis and review -- they help you connect concepts across modules rather than introducing new material. The exercises produce planning artifacts (API specs, schema diagrams, test plans) rather than runnable APIs. They use Pydantic models with pytest to validate the completeness of your designs. The project itself is a major independent undertaking that will take weeks, not hours. Treat it like a real-world project: plan before you code, commit often, and iterate.
