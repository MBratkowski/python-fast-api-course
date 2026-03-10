# Architecture Patterns

## Why This Matters

In iOS development, you debate MVVM vs MVC vs VIPER. In Android, you choose between MVVM with Repository pattern vs MVI. These architecture decisions determine how testable, maintainable, and scalable your app becomes. Backend architecture faces the same tradeoffs with different names.

The difference is stakes. A poorly architected mobile app affects one user at a time. A poorly architected backend affects every user simultaneously. When your service layer is tangled with your route handlers, one bug in business logic can take down authentication for everyone.

This file synthesizes the architecture patterns from Modules 008-010, 013, and 014 into a cohesive guide for structuring your capstone project.

## Quick Review

- **Service layer pattern** (Module 008): Business logic lives in service functions, not route handlers. Routes handle HTTP concerns (parsing requests, formatting responses). Services handle domain logic (validation rules, data transformations, authorization checks).
- **Dependency injection with Depends()** (Module 008): FastAPI's `Depends()` injects database sessions, current user, configuration, and any other shared resource. This makes route handlers thin and testable.
- **JWT authentication flow** (Module 009): Login returns access + refresh tokens. Access tokens are short-lived (15-30 min). Refresh tokens rotate on use. The `get_current_user` dependency extracts and validates the token on every protected request.
- **Role-Based Access Control** (Module 010): Roles (admin, user, moderator) gate access to endpoints. The pattern uses a dependency that checks `current_user.role` against allowed roles. Use 401 for "not authenticated" and 403 for "not authorized."
- **Background tasks** (Module 013): Celery workers handle slow operations (sending emails, processing images) outside the request/response cycle. The API enqueues a task and returns immediately.
- **Caching with Redis** (Module 014): Frequently-read, rarely-changed data (user profiles, product listings) is cached in Redis. Cache invalidation happens in the service layer when data changes.

## How They Compose

Each pattern solves one problem. Together, they form a layered architecture:

```
Request
  |
  v
[Route Handler]      -- HTTP concerns: parse request, format response
  |
  v
[Dependencies]       -- Cross-cutting: auth, DB session, rate limiting
  |
  v
[Service Layer]      -- Business logic: validation, authorization, orchestration
  |
  v
[Data Access]        -- Database queries, cache reads/writes
  |
  v
[Database / Redis]   -- Storage
```

### Layer Responsibilities

| Layer | Does | Does NOT |
|-------|------|----------|
| Route Handler | Parse HTTP request, call service, return HTTP response | Contain business logic, run SQL queries, check permissions |
| Dependencies | Provide database session, current user, config | Contain business logic |
| Service Layer | Validate business rules, orchestrate operations, check authorization | Know about HTTP status codes, parse request bodies |
| Data Access | Execute SQL queries, manage transactions, read/write cache | Know about business rules |

### The Dependency Graph

Understanding which layer depends on which prevents circular imports and makes testing straightforward:

```
Routes --> Services --> Repositories (Data Access)
  |           |
  v           v
Dependencies  Models / Schemas
```

Routes depend on services. Services depend on repositories and models. Nothing depends on routes. This means you can test services without HTTP, and test repositories without business logic.

### Auth Integration Pattern

Authentication and authorization weave through all layers:

```python
# Route layer: declares that auth is required
@router.get("/posts/{post_id}")
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),  # Auth dependency
    db: Session = Depends(get_db),                     # DB dependency
):
    # Service layer: checks authorization
    return post_service.get_post(db, post_id, current_user)

# Service layer: enforces business rules
def get_post(db: Session, post_id: int, current_user: User) -> Post:
    post = db.get(Post, post_id)
    if not post:
        raise PostNotFoundError(post_id)
    if post.is_private and post.author_id != current_user.id:
        raise NotAuthorizedError("Cannot view private post")
    return post
```

Notice: the route handler does not check permissions. The service does. This means the same permission logic applies whether the request comes from the API, a background task, or a test.

### When to Cache vs When to Use Background Tasks

| Situation | Use | Why |
|-----------|-----|-----|
| Same data requested repeatedly | Cache (Module 014) | Avoid redundant DB queries |
| Response takes > 500ms to compute | Background task (Module 013) | Do not block the client |
| Data changes rarely | Cache with TTL | Set-and-forget invalidation |
| Data changes on every write | Cache with explicit invalidation | Invalidate in service layer on update |
| Operation has side effects (email, webhook) | Background task | Decouple from request lifecycle |
| Read-heavy, write-light resource | Cache | Classic cache use case |

## Decision Framework

### "Where Does This Logic Belong?"

```
Is it about HTTP (status codes, headers, request parsing)?
  Yes --> Route handler

Is it about "who is making this request"?
  Yes --> Dependency (get_current_user, get_db)

Is it a business rule ("users can only edit their own posts")?
  Yes --> Service layer

Is it a database query?
  Yes --> Service layer or dedicated repository

Is it a slow side effect (email, file processing)?
  Yes --> Background task (Celery)

Is it data that's read 100x more than written?
  Yes --> Cache it (Redis)
```

### Structuring Your Project

```
src/
├── api/
│   ├── auth.py          # Auth routes: login, register, refresh
│   ├── users.py         # User routes: profile, settings
│   ├── posts.py         # Post routes: CRUD
│   └── deps.py          # Shared dependencies: get_db, get_current_user
├── services/
│   ├── auth_service.py  # Auth logic: hash password, verify token, create tokens
│   ├── user_service.py  # User logic: create, update, permissions
│   └── post_service.py  # Post logic: create, update, delete, feed
├── models/
│   ├── user.py          # SQLAlchemy User model
│   └── post.py          # SQLAlchemy Post model
├── schemas/
│   ├── user.py          # Pydantic UserCreate, UserResponse, UserUpdate
│   └── post.py          # Pydantic PostCreate, PostResponse, PostUpdate
├── core/
│   ├── config.py        # Settings from environment variables
│   ├── security.py      # JWT creation/verification, password hashing
│   └── exceptions.py    # Custom exception classes
├── db/
│   └── session.py       # Database engine, session factory
└── main.py              # FastAPI app, router registration
```

## Capstone Application

**Task Management API -- Architecture Design**

For the Task Management capstone option, here is how the layers map:

**Route layer** (`api/tasks.py`):
```python
@router.post("/tasks", status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return task_service.create_task(db, task_data, current_user)
```

**Service layer** (`services/task_service.py`):
```python
def create_task(db: Session, data: TaskCreate, user: User) -> Task:
    # Business rule: verify project belongs to user
    project = db.get(Project, data.project_id)
    if not project or project.owner_id != user.id:
        raise NotAuthorizedError("Cannot add tasks to this project")

    # Business rule: enforce task limit per project (free tier)
    task_count = db.scalar(
        select(func.count(Task.id)).where(Task.project_id == project.id)
    )
    if user.plan == "free" and task_count >= 50:
        raise TaskLimitExceededError("Free plan limited to 50 tasks per project")

    task = Task(**data.model_dump(), creator_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)

    # Side effect: notify project members (background task)
    notify_project_members.delay(project.id, f"New task: {task.title}")

    return task
```

**Key architecture decisions:**
- Route handler is 4 lines. All logic is in the service.
- Authorization check is in the service, not a dependency (because it needs the specific resource).
- Task limit is a business rule -- it lives in the service, not the database.
- Notification is a background task -- it does not slow down the response.
- Cache strategy: cache project task lists (read-heavy), invalidate on task create/update/delete.

## Checklist

Before writing your capstone code, verify your architecture:

- [ ] Route handlers contain zero business logic (only HTTP parsing and response formatting)
- [ ] Service layer handles all business rules and authorization checks
- [ ] `Depends()` used for database sessions, current user, and shared configuration
- [ ] Custom exception classes defined for domain errors (not raw HTTPException in services)
- [ ] Exception handler in main.py converts domain exceptions to HTTP responses
- [ ] Schemas separated: Create, Update, Response for each resource
- [ ] Models use SQLAlchemy 2.0 patterns (Mapped, mapped_column, DeclarativeBase)
- [ ] Background tasks identified for operations > 500ms or with side effects
- [ ] Cache strategy planned for read-heavy resources
- [ ] No circular imports between layers (routes -> services -> models, never backwards)

## Key Takeaways

1. **Layers exist to separate concerns.** When a route handler contains a SQL query, you have a layering violation. Fix it before it spreads.
2. **Depends() is FastAPI's superpower.** Use it for everything that is shared across routes: database sessions, auth, configuration, rate limiting.
3. **Services own business logic.** If you are writing an `if` statement about business rules in a route handler, move it to the service.
4. **Background tasks decouple side effects.** Sending email, processing images, sending webhooks -- none of these should block the API response.
5. **Cache at the service layer, not the route layer.** The service knows when data changes and can invalidate the cache. The route does not.
