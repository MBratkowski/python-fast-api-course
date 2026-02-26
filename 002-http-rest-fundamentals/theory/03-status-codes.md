# HTTP Status Codes

## Why This Matters

In mobile development, you handle status codes in error callbacks: 401 means show login, 404 means show "not found", 500 means show error. Now you'll be the one choosing which status code to return and when.

## Status Code Families

Status codes are grouped by first digit:

| Family | Meaning | Examples |
|--------|---------|----------|
| 1xx | Informational | 101 Switching Protocols |
| 2xx | Success | 200 OK, 201 Created |
| 3xx | Redirection | 301 Moved Permanently |
| 4xx | Client Error | 400 Bad Request, 404 Not Found |
| 5xx | Server Error | 500 Internal Server Error |

## 2xx Success Codes

**200 OK** - Standard success response
```
GET /api/users/123
→ 200 OK
{"id": 123, "name": "Alice"}
```

**201 Created** - Resource created successfully
```
POST /api/users
{"name": "Bob"}
→ 201 Created
Location: /api/users/456
{"id": 456, "name": "Bob"}
```

**204 No Content** - Success but no response body
```
DELETE /api/users/123
→ 204 No Content
(no body)
```

**Mobile analogy**: Like your completion handlers with data or nil

## 3xx Redirection Codes

**301 Moved Permanently** - Resource moved to new URL
```
GET /api/v1/users
→ 301 Moved Permanently
Location: /api/v2/users
```

**304 Not Modified** - Cached version is still valid
```
GET /api/users/123
If-None-Match: "abc123"
→ 304 Not Modified
(no body)
```

**Mobile analogy**: Like your app's cache validation logic

## 4xx Client Error Codes

**400 Bad Request** - Invalid request format
```
POST /api/users
{"name": ""}
→ 400 Bad Request
{"detail": "Name cannot be empty"}
```

**401 Unauthorized** - Authentication required
```
GET /api/protected
→ 401 Unauthorized
{"detail": "Authentication credentials missing"}
```

**403 Forbidden** - Authenticated but not authorized
```
DELETE /api/users/999
→ 403 Forbidden
{"detail": "You don't have permission to delete this user"}
```

**404 Not Found** - Resource doesn't exist
```
GET /api/users/999999
→ 404 Not Found
{"detail": "User not found"}
```

**409 Conflict** - Request conflicts with current state
```
POST /api/users
{"email": "existing@example.com"}
→ 409 Conflict
{"detail": "Email already registered"}
```

**422 Unprocessable Entity** - Validation failed
```
POST /api/users
{"email": "not-an-email"}
→ 422 Unprocessable Entity
{
  "detail": [
    {"field": "email", "error": "Invalid email format"}
  ]
}
```

**429 Too Many Requests** - Rate limit exceeded
```
GET /api/data
→ 429 Too Many Requests
Retry-After: 60
{"detail": "Rate limit exceeded. Try again in 60 seconds"}
```

**Mobile analogy**: These are the errors you handle in your error callbacks

## 5xx Server Error Codes

**500 Internal Server Error** - Unexpected server failure
```
GET /api/users
→ 500 Internal Server Error
{"detail": "An unexpected error occurred"}
```

**502 Bad Gateway** - Upstream service failed
```
GET /api/users
→ 502 Bad Gateway
{"detail": "Database connection failed"}
```

**503 Service Unavailable** - Server overloaded or maintenance
```
GET /api/users
→ 503 Service Unavailable
Retry-After: 300
{"detail": "Server is under maintenance"}
```

**Mobile analogy**: Show generic error message and retry option

## Decision Table: What Status Code to Return?

| Scenario | Status Code |
|----------|-------------|
| Retrieved resource successfully | 200 OK |
| Created new resource | 201 Created |
| Updated resource successfully | 200 OK |
| Deleted resource | 204 No Content |
| Request body invalid (wrong format) | 400 Bad Request |
| Validation failed (email format wrong) | 422 Unprocessable Entity |
| No auth token provided | 401 Unauthorized |
| Token valid but insufficient permissions | 403 Forbidden |
| Resource doesn't exist | 404 Not Found |
| Duplicate resource (email exists) | 409 Conflict |
| Server code crashed | 500 Internal Server Error |
| External service failed | 502 Bad Gateway |
| Too many requests | 429 Too Many Requests |

## Common Mistakes

**Wrong: Using 200 for everything**
```
POST /api/users
→ 200 OK  ❌
```
Should be 201 Created

**Wrong: Using 404 for validation errors**
```
POST /api/users
{"email": "invalid"}
→ 404 Not Found  ❌
```
Should be 422 Unprocessable Entity

**Wrong: Using 500 for client errors**
```
GET /api/users/abc
→ 500 Internal Server Error  ❌
```
Should be 400 Bad Request (invalid ID format)

**Right: Using specific codes**
```
POST /api/users       → 201 Created         ✅
GET /api/users/999    → 404 Not Found       ✅
GET /api/protected    → 401 Unauthorized    ✅
POST invalid data     → 422 Validation Error ✅
Server crash          → 500 Server Error    ✅
```

## Key Takeaways

1. Status codes communicate what happened without reading the body
2. 2xx = success, 4xx = client mistake, 5xx = server problem
3. Use specific codes (404, 401, 422) rather than generic 400
4. Mobile apps rely on correct status codes for proper error handling
5. 500 errors are bugs - clients can't fix them
6. Choose the most specific code that fits the situation
