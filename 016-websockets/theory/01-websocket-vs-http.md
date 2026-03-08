# WebSocket vs HTTP

## Why This Matters

On mobile, you've used both HTTP requests and WebSocket connections. You know that REST APIs use request-response: send a request, get a response, connection closes. WebSockets keep the connection open for real-time, bidirectional communication -- like chat, live scores, or collaborative editing.

On the server side, the distinction matters even more. HTTP handlers process one request and return. WebSocket handlers stay alive for the entire connection, which could be minutes, hours, or days. This fundamentally changes how you think about server resources.

## HTTP: Request-Response

```
HTTP Request-Response:

Client                    Server
  |                         |
  |------- GET /users ----->|
  |<------ 200 OK ---------|
  |                         |
  |------- POST /items ---->|
  |<------ 201 Created ----|
  |                         |
  (connection closes)
```

Each HTTP request is independent. The client sends, the server responds, done. If the client needs new data, it sends another request.

## WebSocket: Persistent Bidirectional

```
WebSocket Connection:

Client                    Server
  |                         |
  |--- HTTP Upgrade ------->|
  |<-- 101 Switching -------|
  |                         |
  |=== WebSocket Open ======|
  |                         |
  |------- "hello" -------->|
  |<------ "hi back" -------|
  |                         |
  |<--- "new message" ------|  (server pushes without request)
  |                         |
  |------- "typing..." ---->|
  |<--- "user is typing" ---|
  |                         |
  |=== Connection Close ====|
```

The connection stays open. Either side can send messages at any time. The server can push data to the client without the client asking.

## WebSocket Handshake

WebSocket connections start as an HTTP request that "upgrades" to a WebSocket:

```
Client -> Server:
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

Server -> Client:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After this handshake, both sides communicate using WebSocket frames (not HTTP).

## When to Use What: Decision Tree

```
Do you need real-time updates?
  |
  No -> Use HTTP (REST API)
  |
  Yes -> How frequent are updates?
           |
           Rare (every few minutes) -> HTTP Polling
           |                           (client polls periodically)
           |
           Moderate (every few seconds) -> Server-Sent Events (SSE)
           |                               (server pushes, one-way)
           |
           Frequent + Bidirectional -> WebSocket
                                       (both sides send freely)
```

### Comparison Table

| Feature | HTTP (REST) | HTTP Polling | SSE | WebSocket |
|---------|-------------|-------------|-----|-----------|
| Direction | Client -> Server | Client -> Server | Server -> Client | Bidirectional |
| Connection | Short-lived | Short-lived | Long-lived | Long-lived |
| Overhead | Low per request | High (repeated requests) | Low | Very low |
| Real-time | No | ~seconds delay | Yes | Yes |
| Complexity | Simple | Simple | Moderate | Most complex |
| Use cases | CRUD APIs | Dashboards | News feeds | Chat, games, collab |

### Use Cases by Pattern

**HTTP REST API:**
- User registration, login
- CRUD operations (create, read, update, delete)
- File uploads
- Any request-response interaction

**HTTP Polling:**
- Dashboard that refreshes every 30 seconds
- Order status checking
- Simple notification checks

**Server-Sent Events (SSE):**
- Live news feed
- Stock price updates
- Build/deployment status
- Any one-way server-to-client stream

**WebSocket:**
- Chat applications
- Multiplayer games
- Collaborative document editing
- Live location sharing
- Trading platforms

## Resource Implications

HTTP handlers are stateless -- they process a request and free resources:

```python
# HTTP: handler runs once, returns, done
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.get_user(user_id)
    return user  # Handler is done, resources freed
```

WebSocket handlers hold resources for the connection lifetime:

```python
# WebSocket: handler runs for the ENTIRE connection
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    # This loop runs for minutes, hours, or days
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass  # Finally clean up
```

**This means:**
- 1000 HTTP requests/second might use 10 connections
- 1000 WebSocket clients means 1000 persistent connections
- Each WebSocket connection holds memory, file descriptors, and an event loop task

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| HTTP client | `URLSession` | OkHttp / Retrofit | N/A (you build the server) |
| WebSocket client | `URLSessionWebSocketTask` | OkHttp `WebSocket` | N/A (you build the server) |
| HTTP server | N/A | N/A | `@app.get()`, `@app.post()` |
| WebSocket server | N/A | N/A | `@app.websocket()` |
| Push from server | APNs (one-way) | FCM (one-way) | WebSocket (bidirectional) |

## Key Takeaways

- **HTTP** is request-response: client asks, server answers, connection closes
- **WebSocket** is persistent and bidirectional: both sides can send at any time
- WebSocket starts with an **HTTP upgrade handshake**, then switches to the WebSocket protocol
- Use HTTP for **CRUD operations**, WebSocket for **real-time bidirectional** communication
- On the server, WebSocket connections **hold resources** for their entire lifetime -- plan capacity accordingly
- Consider **SSE (Server-Sent Events)** when you only need server-to-client push (simpler than WebSocket)
- On mobile, you consume WebSocket connections. On the server, you manage thousands of them
