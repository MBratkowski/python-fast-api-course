# Backend Development Mastery

A comprehensive, hands-on course for mobile developers transitioning to backend development. Learn to build production-grade REST APIs with Python and FastAPI.

## Who Is This For?

Mobile developers (iOS/Android/Flutter/React Native) who want to:
- Build their own backend services
- Understand what happens on the server side
- Become full-stack developers
- Build side projects end-to-end

## Prerequisites

- Programming experience (you already know a language)
- Basic understanding of HTTP (you've called APIs from mobile apps)
- Command line basics

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd python-fast-api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start learning!
# Open 001-python-backend-quickstart/README.md
```

## Course Structure

### Part 1: Foundations
| Module | Topic | What You'll Build |
|--------|-------|-------------------|
| 001 | Python for Backend | Quick Python refresher for developers |
| 002 | HTTP & REST | Understanding the protocol you've been using |
| 003 | FastAPI Basics | Your first API endpoint |
| 004 | Request & Response | Path params, query params, headers |
| 005 | Pydantic Validation | Request/response schemas |

### Part 2: Data Layer
| Module | Topic | What You'll Build |
|--------|-------|-------------------|
| 006 | SQL Databases | PostgreSQL fundamentals |
| 007 | SQLAlchemy ORM | Models and relationships |
| 008 | CRUD Operations | Full REST API for a resource |

### Part 3: Authentication & Security
| Module | Topic | What You'll Build |
|--------|-------|-------------------|
| 009 | Authentication (JWT) | Login, signup, tokens |
| 010 | Authorization | Roles, permissions, protected routes |
| 019 | Security Best Practices | OWASP, input validation, secrets |

### Part 4: Advanced Features
| Module | Topic | What You'll Build |
|--------|-------|-------------------|
| 011 | Testing APIs | pytest, test client, fixtures |
| 012 | Async Python | async/await, concurrent requests |
| 013 | Background Tasks | Celery, task queues |
| 014 | Caching (Redis) | Performance optimization |
| 015 | File Uploads | Handling files, S3 storage |
| 016 | WebSockets | Real-time communication |

### Part 5: Production
| Module | Topic | What You'll Build |
|--------|-------|-------------------|
| 017 | Docker | Containerizing your API |
| 018 | CI/CD | GitHub Actions, deployment |
| 020 | Performance | Profiling, optimization |
| 021 | Logging & Monitoring | Structured logs, metrics |
| 022 | API Versioning | Managing API evolution |
| 023 | Rate Limiting | Protecting your API |
| 024 | Microservices Basics | Service communication |

### Part 6: Capstone
| Module | Topic | What You'll Build |
|--------|-------|-------------------|
| 025 | Capstone Project | Full production API from scratch |

## How Each Module Works

1. **Theory** - Read the concept explanations (15-20 min)
2. **Exercises** - Hands-on coding tasks (30-45 min)
3. **Project** - Build something real (1-2 hours)

## Tech Stack You'll Learn

- **Python 3.12+** - The language
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM for database access
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Redis** - Caching layer
- **Docker** - Containerization
- **pytest** - Testing framework

## Why FastAPI?

As a mobile developer, you'll appreciate:
- **Type hints** - Like Swift/Kotlin type safety
- **Auto-generated docs** - Swagger UI out of the box
- **Async support** - Handle concurrent requests efficiently
- **Pydantic** - Schema validation like mobile data models
- **Modern Python** - Clean, readable code

## License

MIT
