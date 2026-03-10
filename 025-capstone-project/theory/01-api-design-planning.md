# API Design Planning

## Why This Matters

As a mobile developer, you have consumed dozens of REST APIs -- from Firebase to Twitter to your own company's backend. You know what a good API feels like: predictable URLs, consistent response formats, clear error messages. You also know what a bad API feels like: endpoints that return different shapes depending on context, error codes that lie, pagination that breaks.

In iOS, you design your View hierarchy before writing any SwiftUI code. In Android, you plan your navigation graph before building Fragments. API design is the backend equivalent: it is the contract your clients depend on. Get it right, and everything downstream (database schema, service layer, tests, documentation) falls into place. Get it wrong, and you spend months patching mismatches between what the API promises and what it delivers.

This file synthesizes everything from Modules 002-005 into a single planning workflow you can use before writing any code.

## Quick Review

- **HTTP methods and status codes** (Module 002): GET reads, POST creates, PUT/PATCH updates, DELETE removes. Status codes communicate outcome (200 OK, 201 Created, 404 Not Found, 422 Validation Error).
- **FastAPI route declarations** (Module 003): Path operations map HTTP methods to Python functions. Path parameters, query parameters, and request bodies each have specific use cases.
- **Request/response modeling** (Module 004): Path parameters identify resources (`/users/{id}`), query parameters filter collections (`?status=active`), headers carry metadata (`Authorization`, `Content-Type`).
- **Pydantic validation** (Module 005): Schemas enforce contracts at the boundary. Separate Create, Update, and Response schemas prevent data leakage and allow independent evolution.
- **Error response format** (Module 003): FastAPI uses `{"detail": "..."}` by default. Custom exception handlers let you standardize error shapes across the entire API.

## How They Compose

Individually, each concept solves a narrow problem. Together, they form a design pipeline:

**Requirements --> Resources --> Endpoints --> Schemas --> Error Handling**

1. **Requirements to resources.** Read the feature list. Identify the nouns -- these are your resources (users, posts, comments). Each resource gets its own URL namespace (`/users`, `/posts`).

2. **Resources to endpoints.** For each resource, decide which operations it supports. Not every resource needs all five CRUD operations. A "login" resource only needs POST. A "feed" resource only needs GET.

3. **Endpoints to schemas.** For each endpoint, define request and response schemas. The Create schema accepts what the client sends. The Response schema controls what the client sees. They are rarely identical -- the response includes `id`, `created_at`, computed fields; the request does not.

4. **Schemas to error handling.** Every schema boundary is a place where validation can fail. Plan your error responses: what does the client get when they send an invalid email? When they reference a nonexistent user? When they lack permission?

The key insight is that these are not independent decisions. Your endpoint design constrains your schema design, which constrains your error handling. Plan them together, not sequentially.

### The Consistency Principle

Mobile developers know this intuitively: if `GET /users/{id}` returns `{"data": {"id": 1, "name": "Alice"}}`, then `GET /posts/{id}` should return `{"data": {"id": 1, "title": "..."}}` -- same wrapper, same shape. Consistency across resources reduces the cognitive load for every client developer (including yourself, when you build the mobile frontend).

## Decision Framework

Use this flowchart when designing an endpoint:

```
1. What resource does this operate on?
   --> /resource-name (plural: /users, /posts, /comments)

2. What operation?
   - Read one    --> GET /resources/{id}          --> 200
   - Read many   --> GET /resources?filters        --> 200
   - Create      --> POST /resources               --> 201
   - Full update --> PUT /resources/{id}           --> 200
   - Partial update --> PATCH /resources/{id}      --> 200
   - Delete      --> DELETE /resources/{id}        --> 204

3. Does it require authentication?
   - Public (register, login, public feed) --> No auth
   - User-specific data --> Bearer token required
   - Admin operations --> Bearer token + role check

4. What can go wrong?
   - Resource not found         --> 404
   - Validation error           --> 422 (FastAPI default)
   - Not authenticated          --> 401
   - Not authorized             --> 403
   - Conflict (duplicate email) --> 409
   - Rate limited               --> 429

5. Nested resources?
   - Comments on a post --> GET /posts/{post_id}/comments
   - Keep nesting to max 2 levels
```

### When to Use Nested vs Flat Routes

| Pattern | Use When | Example |
|---------|----------|---------|
| Nested: `/posts/{id}/comments` | Child only exists in context of parent | Comments belong to a post |
| Flat: `/comments?post_id=X` | Child can be queried independently | Search all comments by a user |
| Both | Common resource with multiple access patterns | Provide both for flexibility |

## Capstone Application

**Social Media API -- Endpoint Design**

Here is how you would apply the framework to the Social Media capstone option:

**Resources identified:** Users, Posts, Comments, Likes, Followers

**Endpoint plan:**

| Method | Path | Auth | Description | Status Codes |
|--------|------|------|-------------|-------------|
| POST | `/auth/register` | No | Create account | 201, 409, 422 |
| POST | `/auth/login` | No | Get tokens | 200, 401 |
| POST | `/auth/refresh` | Yes | Refresh access token | 200, 401 |
| GET | `/users/me` | Yes | Current user profile | 200, 401 |
| GET | `/users/{id}` | Yes | Any user profile | 200, 404 |
| PATCH | `/users/me` | Yes | Update own profile | 200, 422 |
| POST | `/posts` | Yes | Create post | 201, 422 |
| GET | `/posts` | Yes | Feed (paginated) | 200 |
| GET | `/posts/{id}` | Yes | Single post | 200, 404 |
| PUT | `/posts/{id}` | Yes | Update own post | 200, 403, 404 |
| DELETE | `/posts/{id}` | Yes | Delete own post | 204, 403, 404 |
| POST | `/posts/{id}/comments` | Yes | Add comment | 201, 404, 422 |
| GET | `/posts/{id}/comments` | Yes | List comments | 200, 404 |
| POST | `/posts/{id}/like` | Yes | Like a post | 201, 409 |
| DELETE | `/posts/{id}/like` | Yes | Unlike a post | 204, 404 |
| POST | `/users/{id}/follow` | Yes | Follow user | 201, 409 |
| DELETE | `/users/{id}/follow` | Yes | Unfollow user | 204, 404 |

**Schema plan (for the Posts resource):**

```python
# Create -- what the client sends
class PostCreate(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(max_length=5000)
    tags: list[str] = []

# Response -- what the client receives
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    author_id: int
    author_name: str
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime

# Update -- partial, all fields optional
class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
```

Notice how the three schemas serve different purposes: Create has validation constraints, Response includes computed fields (like_count, author_name), and Update makes everything optional.

## Checklist

Before writing any endpoint code, verify:

- [ ] All resources identified from requirements (nouns in the feature list)
- [ ] Each resource has appropriate CRUD endpoints (not more, not fewer)
- [ ] HTTP methods match operations (POST for create, not GET)
- [ ] URL paths use plural nouns and kebab-case (`/user-profiles`, not `/getUserProfile`)
- [ ] Nested routes limited to 2 levels maximum
- [ ] Auth requirements marked for every endpoint
- [ ] Separate Pydantic schemas planned for Create, Update, and Response
- [ ] Error responses planned for each endpoint (at minimum: 404, 422, 401/403)
- [ ] Status codes match operations (201 for POST, 204 for DELETE)
- [ ] Pagination planned for all list endpoints (page/size or cursor-based)

## Key Takeaways

1. **Design the API before writing code.** The endpoint list is your blueprint. Every downstream decision (schema, database, tests) flows from it.
2. **Consistency beats cleverness.** Same response wrapper, same error format, same auth pattern across all endpoints. Your future self (and your mobile team) will thank you.
3. **Separate schemas are not overhead -- they are protection.** Create, Update, and Response schemas evolve independently. Coupling them creates breaking changes.
4. **Plan your errors as carefully as your successes.** Clients spend more time handling errors than happy paths. Give them clear, consistent error responses.
5. **Use the Decision Framework under pressure.** When a PM asks for a new endpoint, walk through the five questions. It takes 2 minutes and prevents weeks of rework.
