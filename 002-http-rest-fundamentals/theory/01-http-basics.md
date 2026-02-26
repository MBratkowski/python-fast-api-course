# HTTP Protocol Basics

## Why This Matters

In mobile development, you use URLSession (iOS), Retrofit (Android), or fetch (React Native) to make HTTP requests. These libraries hide the details, but when you build the backend, you need to understand what's inside those requests and responses.

## The Client-Server Model

HTTP follows a request-response pattern:

1. **Client** (your mobile app) sends a request
2. **Server** (your API) processes it
3. **Server** sends back a response

```
[Mobile App] --HTTP Request--> [API Server]
[Mobile App] <--HTTP Response-- [API Server]
```

## HTTP Request Structure

Every HTTP request has:

1. **Request Line**: Method, URL, HTTP version
2. **Headers**: Metadata about the request
3. **Body** (optional): Data being sent

Example:
```
GET /api/users/123 HTTP/1.1
Host: api.example.com
Authorization: Bearer token123
Accept: application/json

```

Another example with a body:
```
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 52

{"name": "Alice", "email": "alice@example.com"}
```

## HTTP Response Structure

Every HTTP response has:

1. **Status Line**: HTTP version, status code, status text
2. **Headers**: Metadata about the response
3. **Body**: Data being returned

Example:
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 78
Cache-Control: max-age=300

{"id": 123, "name": "Alice", "email": "alice@example.com"}
```

## Request Methods

The request method tells the server what action to perform:

- `GET` - Retrieve data (read-only)
- `POST` - Create new resource
- `PUT` - Replace entire resource
- `PATCH` - Update part of resource
- `DELETE` - Remove resource

Think of these like the different actions in your mobile app: viewing a screen (GET), submitting a form (POST), updating profile (PATCH), deleting an item (DELETE).

## Status Codes

The status code tells the client if the request succeeded:

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server crashed

You've handled these in your mobile error handling - now you'll be the one sending them back.

## Headers

Headers are key-value pairs that provide metadata:

**Common Request Headers:**
- `Content-Type: application/json` - Format of request body
- `Authorization: Bearer token` - Authentication credentials
- `Accept: application/json` - Formats client can handle

**Common Response Headers:**
- `Content-Type: application/json` - Format of response body
- `Cache-Control: max-age=300` - Cache for 5 minutes
- `Set-Cookie: session=abc123` - Store session info

## Key Takeaways

1. HTTP is a request-response protocol
2. Every request has: method, URL, headers, optional body
3. Every response has: status code, headers, body
4. You've been using HTTP from the client side - now you'll build the server side
5. Understanding these fundamentals helps you design better APIs
