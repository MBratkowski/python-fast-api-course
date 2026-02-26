# Module 002: HTTP & REST Fundamentals

## Why This Module?

You've been calling REST APIs from mobile apps. Now understand what's happening on the server side - HTTP methods, status codes, headers, and REST design principles.

## What You'll Learn

- HTTP request/response cycle
- HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Status codes (2xx, 4xx, 5xx)
- Headers (Content-Type, Authorization, etc.)
- REST architectural principles
- API design best practices

## Mobile Developer Context

You know: `URLSession`, `Retrofit`, `Dio`, `fetch()`
Now learn: What the server does when it receives your requests

## Topics

### Theory
1. HTTP Protocol Basics
2. Request Methods & When to Use Them
3. Status Codes Reference
4. Headers & Content Negotiation
5. REST Principles (Resources, Stateless, HATEOAS)
6. API Design Patterns

### Exercises
- Analyze real API requests/responses
- Design a REST API for a given use case
- Identify violations of REST principles

### Project
Design the API specification for a task management app (the same kind you'd build as a mobile app).

## Key Concepts

| HTTP Method | Purpose | Example |
|-------------|---------|---------|
| GET | Read data | GET /users/123 |
| POST | Create new | POST /users |
| PUT | Replace entire resource | PUT /users/123 |
| PATCH | Partial update | PATCH /users/123 |
| DELETE | Remove | DELETE /users/123 |

| Status Code | Meaning |
|-------------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |
