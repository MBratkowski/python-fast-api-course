# Module 016: WebSockets and Real-Time

## Why This Module?

As a mobile developer, you've consumed WebSocket connections -- connecting to chat servers, receiving live updates, handling push notifications. You've used `URLSessionWebSocketTask` (iOS) or OkHttp's `WebSocket` (Android) to maintain persistent connections. Now you'll build the server that those clients connect to.

The shift is significant: on mobile, you manage one connection. On the server, you manage thousands of concurrent connections, route messages between them, handle disconnects gracefully, and scale across multiple servers.

## What You'll Learn

- WebSocket vs HTTP: when persistent connections make sense
- FastAPI's WebSocket decorator and lifecycle (accept, receive, send)
- ConnectionManager pattern for tracking active connections
- Broadcasting and room-based messaging
- WebSocket authentication (tokens via query parameters)
- Scaling with Redis Pub/Sub for multi-server deployments

## Mobile Developer Context

You've connected to WebSocket servers from mobile apps. Now you build the server side.

**Real-Time Communication Across Platforms:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| WebSocket client | `URLSessionWebSocketTask` | OkHttp `WebSocketListener` | N/A (you build the server) |
| WebSocket server | N/A | N/A | `@app.websocket("/ws")` |
| Push notifications | APNs | FCM | Server-side WebSocket broadcast |
| Real-time streams | Combine `Publisher` | Kotlin `StateFlow` / `SharedFlow` | `websocket.send_text()` / `send_json()` |
| Connection tracking | Single connection | Single connection | ConnectionManager (thousands) |

**Key Differences from Mobile:**
- On mobile, you manage one WebSocket connection. On the server, you manage all of them
- On mobile, a disconnect means "retry." On the server, a disconnect means "clean up that client"
- On mobile, you receive messages. On the server, you route messages between clients
- On mobile, push notifications come from APNs/FCM. On the server, you are the notification source

## Quick Assessment

Before starting, you should be comfortable with:
- [ ] FastAPI route handlers and dependency injection (Module 003-004)
- [ ] async/await patterns (Module 012)
- [ ] JWT authentication concepts (Module 009)
- [ ] Python classes and data structures (dicts, lists)

## Topics

### Theory
1. WebSocket vs HTTP -- When to use persistent connections
2. FastAPI WebSocket -- Accept, receive, send lifecycle
3. Connection Manager -- Tracking and managing active connections
4. Broadcasting and Rooms -- Message routing patterns
5. WebSocket Authentication -- Securing WebSocket connections
6. Scaling with Redis Pub/Sub -- Multi-server real-time

### Exercises
1. Basic WebSocket Endpoints -- Echo, JSON, disconnect handling
2. Connection Manager -- Build the connection tracking class
3. Broadcasting -- Chat endpoint with room support

### Project
Real-time notification system with auth, user tracking, and broadcasting.

## Time Estimate

- Theory: ~90 minutes
- Exercises: ~60 minutes
- Project: ~90 minutes

## Example

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left")
```
