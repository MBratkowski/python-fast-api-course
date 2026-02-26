# REST Principles

## Why This Matters

REST (Representational State Transfer) is the architectural style behind most web APIs. Your mobile apps already consume RESTful APIs - now you'll learn the principles behind them so you can design consistent, predictable APIs.

## What is REST?

REST is an architectural style for designing networked applications. It's not a protocol or standard - it's a set of constraints that make APIs scalable, maintainable, and easy to understand.

**Mobile analogy**: REST is like the design patterns you follow in mobile development (MVC, MVVM) - guidelines that lead to better architecture.

## The Six REST Constraints

### 1. Client-Server Separation

The client (mobile app) and server (API) are separate systems that communicate over HTTP. The client doesn't need to know how the server stores data, and the server doesn't need to know about the UI.

**Benefit**: Client and server can evolve independently

```
[Mobile App] ←→ [API Server] ←→ [Database]
    Client          Server
```

### 2. Stateless

Each request contains all information needed to process it. The server doesn't store session state between requests.

**Bad (Stateful)**:
```
1. POST /api/login → Server stores "user is logged in"
2. GET /api/profile → Server remembers user from step 1
```

**Good (Stateless)**:
```
1. POST /api/login → Returns JWT token
2. GET /api/profile
   Authorization: Bearer <token>
   → Token contains all needed info
```

**Mobile analogy**: Like passing all context with each function call instead of relying on global state

### 3. Cacheable

Responses must define whether they can be cached and for how long:

```
HTTP/1.1 200 OK
Cache-Control: max-age=300

{"data": "..."}
```

**Benefit**: Reduces load on server, faster responses for clients

**Mobile analogy**: Like your app's image cache or data layer caching

### 4. Uniform Interface

All resources follow the same patterns:
- Resources identified by URLs (`/users/123`)
- Resources manipulated through representations (JSON, XML)
- Self-descriptive messages (status codes, headers)
- Hypermedia (links to related resources)

**Example**:
```
GET /api/users/123
→ 200 OK
{
  "id": 123,
  "name": "Alice",
  "links": {
    "self": "/api/users/123",
    "posts": "/api/users/123/posts"
  }
}
```

**Mobile analogy**: Like following iOS Human Interface Guidelines - consistent patterns make APIs predictable

### 5. Layered System

Client doesn't know if it's talking directly to the server or through intermediaries (load balancers, caches, CDNs):

```
[Mobile App] → [CDN] → [Load Balancer] → [API Server]
```

**Benefit**: Can add caching layers without changing the API

**Mobile analogy**: Like using a networking abstraction layer - you don't know if it's hitting the network or cache

### 6. Code on Demand (Optional)

Server can send executable code to the client (JavaScript). This is optional and rarely used in mobile APIs.

## Resource-Based URLs

REST APIs use resources (nouns), not actions (verbs):

**Bad**:
```
POST /api/createUser
POST /api/deleteUser
GET /api/getUserById?id=123
```

**Good**:
```
POST /api/users
DELETE /api/users/123
GET /api/users/123
```

The HTTP method conveys the action, the URL identifies the resource.

## RESTful URL Examples

**Collection and Resource**:
```
GET    /users           # List all users
POST   /users           # Create new user
GET    /users/123       # Get specific user
PUT    /users/123       # Replace user
PATCH  /users/123       # Update user
DELETE /users/123       # Delete user
```

**Nested Resources**:
```
GET    /users/123/posts      # Get user's posts
POST   /users/123/posts      # Create post for user
GET    /users/123/posts/456  # Get specific post
```

**Filters and Pagination**:
```
GET /users?role=admin&limit=10
GET /posts?author=123&sort=date
```

**Mobile analogy**: Like your app's navigation structure - predictable hierarchy

## HATEOAS (Hypermedia as the Engine of Application State)

Responses include links to related resources:

```json
{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com",
  "_links": {
    "self": {"href": "/users/123"},
    "posts": {"href": "/users/123/posts"},
    "followers": {"href": "/users/123/followers"}
  }
}
```

**Benefit**: Clients can discover available actions without hardcoding URLs

**Note**: Many APIs skip this in practice - it's the most optional REST principle

## REST vs RPC vs GraphQL

**REST**: Resource-based URLs, standard methods
```
GET /api/users/123
PUT /api/users/123
```

**RPC** (Remote Procedure Call): Function-based URLs
```
POST /api/getUser {"id": 123}
POST /api/updateUser {"id": 123, "name": "Alice"}
```

**GraphQL**: Query language for APIs
```
POST /api/graphql
{
  user(id: 123) {
    name
    posts {
      title
    }
  }
}
```

Most web and mobile APIs use REST because it's simple and well-understood.

## Key Takeaways

1. REST is an architectural style with six constraints
2. Stateless means each request is self-contained
3. Resources are nouns (`/users`), actions are HTTP methods
4. Caching improves performance without changing the API
5. Consistent patterns make APIs predictable and easy to use
6. You've been consuming REST APIs - now you'll design them
7. Not all APIs follow REST perfectly, and that's okay
