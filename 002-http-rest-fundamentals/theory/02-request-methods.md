# HTTP Request Methods

## Why This Matters

In mobile development, you call different endpoints with different methods. GET for loading a list view, POST for submitting a form, DELETE for removing an item. Now you'll understand why each method exists and when to use it correctly.

## The HTTP Methods

| Method | Purpose | Has Body? | Idempotent? | Safe? |
|--------|---------|-----------|-------------|-------|
| GET | Read data | No | Yes | Yes |
| POST | Create new | Yes | No | No |
| PUT | Replace entire | Yes | Yes | No |
| PATCH | Partial update | Yes | No | No |
| DELETE | Remove | No | Yes | No |

**Idempotent**: Calling it multiple times has the same effect as calling it once
**Safe**: Doesn't modify server state (read-only)

## GET - Reading Data

**Purpose**: Retrieve data without modifying anything

```
GET /api/users/123 HTTP/1.1
Host: api.example.com
```

Response:
```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice"}
```

**Mobile analogy**: Like fetching data when a screen loads in your app

**Rules**:
- No request body
- Should not modify server state
- Results should be cacheable
- Safe to retry automatically

## POST - Creating Resources

**Purpose**: Create a new resource

```
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "Bob", "email": "bob@example.com"}
```

Response:
```
HTTP/1.1 201 Created
Location: /api/users/456
Content-Type: application/json

{"id": 456, "name": "Bob", "email": "bob@example.com"}
```

**Mobile analogy**: Like submitting a form to create a new item

**Rules**:
- Has a request body
- Not idempotent (creates new resource each time)
- Returns 201 Created with Location header

## PUT - Replacing Entire Resource

**Purpose**: Replace the entire resource with new data

```
PUT /api/users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "Alice Smith", "email": "alice@example.com", "bio": "Engineer"}
```

Response:
```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice Smith", "email": "alice@example.com", "bio": "Engineer"}
```

**Mobile analogy**: Like overwriting an entire cached object

**Rules**:
- Replaces all fields (missing fields get removed/reset)
- Idempotent (same request = same result)
- If resource doesn't exist, can create it

## PATCH - Partial Update

**Purpose**: Update only specific fields

```
PATCH /api/users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"bio": "Software Engineer"}
```

Response:
```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice", "email": "alice@example.com", "bio": "Software Engineer"}
```

**Mobile analogy**: Like updating one field in your model without replacing the whole thing

**Rules**:
- Only updates provided fields
- Other fields remain unchanged
- Use this for partial updates, not PUT

## DELETE - Removing Resources

**Purpose**: Delete a resource

```
DELETE /api/users/123 HTTP/1.1
Host: api.example.com
```

Response:
```
HTTP/1.1 204 No Content
```

**Mobile analogy**: Like deleting an item from a list view

**Rules**:
- No request body needed
- Returns 204 No Content (empty response) or 200 OK
- Idempotent (deleting same resource multiple times is fine)

## Common Mistakes

**Wrong: Using GET to modify data**
```
GET /api/users/delete/123  ❌
```
GET should never modify state. Use DELETE instead.

**Wrong: Using POST for updates**
```
POST /api/users/123/update  ❌
```
Use PATCH or PUT for updates.

**Wrong: Using PUT for partial updates**
```
PUT /api/users/123
{"bio": "Engineer"}
```
This might erase other fields. Use PATCH instead.

**Right: Using correct methods**
```
GET /api/users/123        ✅ Read
POST /api/users           ✅ Create
PATCH /api/users/123      ✅ Partial update
PUT /api/users/123        ✅ Full replacement
DELETE /api/users/123     ✅ Remove
```

## Key Takeaways

1. Each HTTP method has a specific purpose
2. GET is safe and idempotent (read-only)
3. POST creates new resources (not idempotent)
4. PUT replaces entire resource (idempotent)
5. PATCH updates specific fields
6. DELETE removes resources (idempotent)
7. Choosing the right method makes your API predictable and correct
