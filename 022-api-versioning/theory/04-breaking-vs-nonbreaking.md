# Breaking vs Non-Breaking Changes

## Why This Matters

On iOS, when Apple deprecates a framework API, they mark it with `@available(*, deprecated)` but it keeps working for several OS versions. When they finally remove it (a breaking change), they do it in a major OS release with years of warning. Android follows the same pattern with `@Deprecated` annotations.

As a backend developer, you need to make the same distinction. Every time you modify your API, you need to decide: "Will this break existing clients, or is it safe to deploy without a new version?" Getting this wrong either breaks production apps (if you ship a breaking change without versioning) or creates unnecessary complexity (if you version for every minor change).

## The Decision Framework

Ask one question: **"Will existing client code continue to work unchanged after this deployment?"**

- **YES** --> Non-breaking change. Deploy without versioning.
- **NO** --> Breaking change. Needs a new API version.

## Breaking Changes (Require New Version)

### 1. Removing a Response Field

```python
# Before (v1)
{"id": 1, "name": "Alice", "email": "alice@example.com"}

# After -- "email" removed
{"id": 1, "name": "Alice"}
```

**Why it breaks:** Mobile app accessing `response["email"]` gets `nil`/`null`, potentially crashing.

### 2. Renaming a Response Field

```python
# Before (v1)
{"id": 1, "name": "Alice"}

# After -- "name" renamed to "full_name"
{"id": 1, "full_name": "Alice Smith"}
```

**Why it breaks:** Same as removing -- `response["name"]` is now `nil`.

### 3. Changing a Field's Type

```python
# Before (v1) -- id is an integer
{"id": 1, "name": "Alice"}

# After -- id is now a string (UUID)
{"id": "550e8400-e29b-41d4-a716-446655440000", "name": "Alice"}
```

**Why it breaks:** Client code that expects `Int` gets a `String`. Type mismatch causes crashes or data corruption.

### 4. Removing an Endpoint

```python
# Before: GET /users/{id}/avatar exists
# After: endpoint removed, returns 404
```

**Why it breaks:** Client gets 404 instead of the expected response.

### 5. Changing Required Parameters

```python
# Before: POST /users requires {"name": "Alice"}
# After: POST /users requires {"name": "Alice", "email": "alice@example.com"}
```

**Why it breaks:** Existing client requests missing the new required field get 422 validation errors.

### 6. Changing Response Structure

```python
# Before (v1) -- flat response
{"id": 1, "name": "Alice"}

# After -- wrapped response
{"data": {"id": 1, "name": "Alice"}, "meta": {"version": "2.0"}}
```

**Why it breaks:** Client accessing `response["id"]` gets `nil` (it's now inside `response["data"]["id"]`).

### 7. Changing Status Codes for Same Behavior

```python
# Before: successful creation returns 200
# After: successful creation returns 201
```

**Why it breaks:** Client code that checks `response.status_code == 200` now fails.

## Non-Breaking Changes (No New Version Needed)

### 1. Adding an Optional Response Field

```python
# Before
{"id": 1, "name": "Alice"}

# After -- "avatar_url" added
{"id": 1, "name": "Alice", "avatar_url": "https://cdn.example.com/alice.jpg"}
```

**Why it's safe:** Clients that don't know about `avatar_url` simply ignore it. JSON parsers skip unknown fields by default.

**Mobile parallel:** When Apple adds a new property to `UIView`, existing code using `UIView` continues to work. The new property is just there if you need it.

### 2. Adding a New Endpoint

```python
# New: GET /users/{id}/preferences
# Existing endpoints unchanged
```

**Why it's safe:** No existing client calls this endpoint.

### 3. Adding an Optional Query Parameter

```python
# Before: GET /users?page=1
# After: GET /users?page=1&sort=name  (sort is optional, defaults to "id")
```

**Why it's safe:** Existing requests without `sort` still work with the default behavior.

### 4. Adding an Optional Request Body Field

```python
# Before: POST /users requires {"name": "Alice"}
# After: POST /users accepts {"name": "Alice", "bio": "Developer"}  (bio is optional)
```

**Why it's safe:** Existing requests without `bio` still succeed.

### 5. Improving Performance

Same request, same response, faster execution. Never breaking.

### 6. Fixing a Bug (Usually)

```python
# Before: GET /users?search=alice returned ALL users (bug)
# After: GET /users?search=alice returns only users matching "alice" (fixed)
```

**Usually safe**, but be careful -- if clients depend on the buggy behavior, fixing it is technically breaking.

### 7. Adding New Response Headers

```python
# Adding X-Request-ID, X-RateLimit-Remaining headers
# Existing clients ignore unknown headers
```

## The Gray Area

Some changes are ambiguous:

| Change | Breaking? | Depends On |
|--------|-----------|------------|
| Fixing a bug | Maybe | Whether clients rely on buggy behavior |
| Changing error messages | Usually not | Whether clients parse error text (they shouldn't) |
| Adding pagination to a list endpoint | Maybe | If the response was previously unbounded |
| Changing default sort order | Maybe | If clients assume a specific order |
| Tightening validation | Maybe | If previously accepted inputs are now rejected |

**When in doubt, treat it as breaking.** It's safer to version and not need it than to skip versioning and break production.

## Practical Decision Checklist

Before deploying an API change, run through this checklist:

```
[ ] Does any response field get removed or renamed?
    YES --> Breaking. New version needed.

[ ] Does any response field change type?
    YES --> Breaking. New version needed.

[ ] Does the response structure change (flat to nested, etc.)?
    YES --> Breaking. New version needed.

[ ] Does any required parameter get added?
    YES --> Breaking. New version needed.

[ ] Does any endpoint get removed?
    YES --> Breaking. New version needed.

[ ] Are you ONLY adding optional fields/endpoints/parameters?
    YES --> Non-breaking. Deploy without versioning.
```

## Key Takeaways

1. **Breaking = existing client code fails.** If a mobile app in the App Store would crash or malfunction, it's breaking.
2. **Adding optional things is always safe.** New optional fields, new endpoints, new optional parameters -- all non-breaking.
3. **Removing or renaming anything is always breaking.** If a client uses it, they'll break when it's gone.
4. **Changing types is always breaking.** Even `int` to `string` for the same conceptual value.
5. **When in doubt, version it.** The cost of an unnecessary version is complexity. The cost of an unversioned breaking change is a production outage.
6. **Document your changes.** Maintain a changelog so API consumers know what changed and whether it affects them.
