# API Design Best Practices

## Why This Matters

Designing an API is like defining your app's navigation routes - clear, consistent, and predictable patterns make it easy to use. These best practices come from years of mobile developers saying "I wish this API did X" or "Why does this API work this way?"

## Resource Naming Conventions

### Use Plural Nouns

**Good**:
```
GET /api/users
GET /api/posts
GET /api/comments
```

**Bad**:
```
GET /api/user        # Inconsistent
GET /api/get-posts   # Verbs in URL
```

**Why**: Consistent pattern for collections and individual resources
```
GET /api/users       # Collection
GET /api/users/123   # Individual resource
```

### Use Kebab-Case for URLs

**Good**:
```
GET /api/user-profiles
GET /api/blog-posts
```

**Bad**:
```
GET /api/UserProfiles    # PascalCase
GET /api/user_profiles   # snake_case
```

**Why**: URLs are case-insensitive in many systems, kebab-case is the web standard

### Hierarchy with Nested Resources

**Good**:
```
GET /api/users/123/posts          # User's posts
GET /api/users/123/posts/456      # Specific post by user
GET /api/posts/456/comments       # Comments on post
```

**Bad**:
```
GET /api/posts?userId=123         # Less clear hierarchy
GET /api/getUserPosts/123         # Verb in URL
```

**Rule**: Max 2-3 levels deep. Beyond that, use query parameters.

## URL Patterns

### List Resources

```
GET /api/users
Response: 200 OK
{
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ]
}
```

### Get Single Resource

```
GET /api/users/123
Response: 200 OK
{"id": 123, "name": "Alice"}
```

### Create Resource

```
POST /api/users
Body: {"name": "Charlie", "email": "charlie@example.com"}
Response: 201 Created
Location: /api/users/456
{"id": 456, "name": "Charlie", "email": "charlie@example.com"}
```

### Update Resource

```
PATCH /api/users/123
Body: {"name": "Alice Smith"}
Response: 200 OK
{"id": 123, "name": "Alice Smith", "email": "alice@example.com"}
```

### Delete Resource

```
DELETE /api/users/123
Response: 204 No Content
```

## Pagination

Always paginate list endpoints:

**Good**:
```
GET /api/users?page=1&limit=20
Response:
{
  "users": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

**Alternative (cursor-based)**:
```
GET /api/users?cursor=abc123&limit=20
Response:
{
  "users": [...],
  "next_cursor": "def456"
}
```

**Why**: Prevents loading thousands of records in one request

## Filtering and Sorting

Use query parameters for filters:

```
GET /api/users?role=admin&status=active&sort=-created_at
```

Common patterns:
- `field=value` - Filter by exact match
- `sort=field` - Sort ascending
- `sort=-field` - Sort descending (minus = desc)
- `search=query` - Full-text search

**Mobile analogy**: Like the filters and sorts in your list views

## Versioning

Version your API to allow changes without breaking existing clients:

**URL versioning** (common):
```
GET /api/v1/users
GET /api/v2/users
```

**Header versioning** (cleaner but less visible):
```
GET /api/users
Accept: application/vnd.myapi.v2+json
```

**When to version**: When making breaking changes (removing fields, changing types)

## Error Response Format

Use consistent error format:

**Good**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "error": "Must be valid email"
      }
    ]
  }
}
```

**Bad**:
```json
"Error: Invalid email"  # Just a string
```

**Mobile analogy**: Like your error models with code, message, and details

## Response Envelopes

Envelope collections but not single resources:

**Good for collections**:
```json
{
  "users": [...],
  "pagination": {...}
}
```

**Good for single resource**:
```json
{
  "id": 123,
  "name": "Alice"
}
```

**Bad**:
```json
{
  "data": {
    "id": 123,
    "name": "Alice"
  }
}
```
(Unnecessary wrapper for single resource)

**Why**: Collections need metadata (pagination), single resources don't

## Consistency is Key

Be consistent across your API:

**Naming**:
- `created_at` everywhere, not mix of `createdAt`, `created_at`, `creation_time`

**Formats**:
- ISO 8601 for dates: `2024-03-15T10:30:00Z`
- Same JSON structure for all resources

**Responses**:
- Always return the created/updated resource
- Always use same error format
- Always use envelope for collections

## Common Mistakes to Avoid

**Verbs in URLs**:
```
POST /api/createUser        ❌
GET /api/getUserById/123    ❌
```
Use:
```
POST /api/users             ✅
GET /api/users/123          ✅
```

**Mixing singular and plural**:
```
GET /api/user               ❌
GET /api/posts              ✅
```
Use:
```
GET /api/users              ✅
GET /api/posts              ✅
```

**Not using status codes correctly**:
```
POST /api/users
200 OK {"error": "Email exists"}    ❌
```
Use:
```
POST /api/users
409 Conflict {"error": "Email exists"}    ✅
```

**Returning bare arrays**:
```
GET /api/users
[{...}, {...}]              ❌
```
Use:
```
GET /api/users
{"users": [{...}, {...}]}   ✅
```

## Key Takeaways

1. Use plural nouns for resources (`/users`, not `/user`)
2. Use HTTP methods for actions, not verbs in URLs
3. Keep URLs hierarchical but not too deep (max 2-3 levels)
4. Always paginate collections
5. Use query parameters for filtering and sorting
6. Version your API when making breaking changes
7. Use consistent error response format
8. Follow the principle of least surprise - do what mobile devs expect
