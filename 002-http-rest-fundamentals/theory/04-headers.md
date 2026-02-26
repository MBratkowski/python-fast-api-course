# HTTP Headers

## Why This Matters

In mobile development, you set headers in URLRequest (Content-Type, Authorization) and read headers in responses (Cache-Control, ETag). Headers are the metadata that tells both sides how to handle the request and response.

## What Are Headers?

Headers are key-value pairs that provide information about the request or response:

```
GET /api/users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer token123
Accept: application/json
User-Agent: MyApp/1.0
```

## Common Request Headers

### Content-Type

Tells the server what format the request body is in:

```
POST /api/users HTTP/1.1
Content-Type: application/json

{"name": "Alice"}
```

Common values:
- `application/json` - JSON data
- `application/x-www-form-urlencoded` - Form data
- `multipart/form-data` - File uploads
- `text/plain` - Plain text

**Mobile analogy**: Like setting the body format in your HTTP client

### Authorization

Provides authentication credentials:

```
GET /api/protected HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Common schemes:
- `Bearer <token>` - JWT or OAuth token
- `Basic <credentials>` - Username:password (base64)
- `API-Key <key>` - API key

**Mobile analogy**: Like passing your auth token with every request

### Accept

Tells the server what response formats the client can handle:

```
GET /api/users HTTP/1.1
Accept: application/json
```

Or multiple formats with preferences:
```
Accept: application/json, application/xml;q=0.9, */*;q=0.8
```

**Mobile analogy**: Like specifying you want JSON, not XML or HTML

### User-Agent

Identifies the client making the request:

```
GET /api/data HTTP/1.1
User-Agent: MyApp/1.0 (iOS 17.0)
```

**Mobile analogy**: Your app's name and version in network requests

## Common Response Headers

### Content-Type

Tells the client what format the response body is in:

```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice"}
```

**Mobile analogy**: Tells your JSON decoder how to parse the response

### Cache-Control

Tells the client how to cache the response:

```
HTTP/1.1 200 OK
Cache-Control: max-age=300

{"data": "..."}
```

Common values:
- `max-age=300` - Cache for 5 minutes
- `no-cache` - Revalidate before using cache
- `no-store` - Don't cache at all
- `private` - Only cache in browser, not CDN

**Mobile analogy**: Like your app's cache expiration logic

### Set-Cookie

Stores data in the client for future requests:

```
HTTP/1.1 200 OK
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict
```

**Mobile analogy**: Like storing a token in Keychain/SharedPreferences

### Location

Tells the client where a resource was created or moved:

```
HTTP/1.1 201 Created
Location: /api/users/456

{"id": 456, "name": "Bob"}
```

**Mobile analogy**: The URL where you can fetch the newly created resource

## Content Negotiation

Clients and servers negotiate the format using `Accept` and `Content-Type`:

**Client wants JSON:**
```
GET /api/users/123 HTTP/1.1
Accept: application/json
```

**Server responds with JSON:**
```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice"}
```

**Client sends JSON:**
```
POST /api/users HTTP/1.1
Content-Type: application/json

{"name": "Bob"}
```

**Server confirms:**
```
HTTP/1.1 201 Created
Content-Type: application/json

{"id": 456, "name": "Bob"}
```

## CORS Headers

CORS (Cross-Origin Resource Sharing) headers allow browsers to make requests from different domains:

**Preflight request (browser sends):**
```
OPTIONS /api/users HTTP/1.1
Origin: https://myapp.com
```

**Server response:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://myapp.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Mobile analogy**: Mobile apps don't need CORS, but web frontends do

## Custom Headers

You can define custom headers (prefix with `X-` by convention):

```
GET /api/data HTTP/1.1
X-Request-ID: abc-123-def
X-API-Version: 2.0
```

```
HTTP/1.1 200 OK
X-Request-ID: abc-123-def
X-Rate-Limit-Remaining: 998
```

## Key Takeaways

1. Headers carry metadata about requests and responses
2. `Content-Type` specifies body format (JSON, XML, form data)
3. `Authorization` carries authentication credentials (Bearer tokens)
4. `Accept` tells server what formats client can handle
5. `Cache-Control` determines caching behavior
6. CORS headers allow cross-origin requests from browsers
7. You've been using headers in mobile - now you'll send them back
