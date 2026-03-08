# Connection Manager Pattern

## Why This Matters

In the previous section, each WebSocket endpoint handled one connection in isolation. But real-time features need coordination: a chat message from one client should reach all other clients. A notification should go to a specific user. A status update should broadcast to everyone.

The ConnectionManager pattern solves this. It tracks all active connections and provides methods to send messages to individual clients or broadcast to everyone. This is the same pattern you'd see in a mobile app's notification center, but server-side and handling all clients at once.

## Why a Manager?

Without a manager, you have no way to coordinate between connections:

```python
# WITHOUT ConnectionManager -- each handler is isolated
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Can only respond to THIS client
        # No way to reach other connected clients
        await websocket.send_text(f"Echo: {data}")
```

With a manager, you can route messages:

```python
# WITH ConnectionManager -- handlers share state
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Send to ALL connected clients
            await manager.broadcast(f"Someone says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## The ConnectionManager Class

This is the standard pattern from the FastAPI documentation:

```python
from fastapi import WebSocket

class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and track it."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket from tracking."""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific client."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Send a message to ALL connected clients."""
        for connection in self.active_connections:
            await connection.send_text(message)
```

### Using the ConnectionManager

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    # Connect and track
    await manager.connect(websocket)

    try:
        # Announce arrival
        await manager.broadcast(f"Client #{client_id} joined the chat")

        while True:
            # Receive and broadcast
            data = await websocket.receive_text()
            # Personal acknowledgment
            await manager.send_personal_message(f"You said: {data}", websocket)
            # Broadcast to everyone
            await manager.broadcast(f"Client #{client_id}: {data}")

    except WebSocketDisconnect:
        # Clean up and announce departure
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

## Enhanced ConnectionManager with User Tracking

For real applications, you want to track who is connected:

```python
from fastapi import WebSocket

class ConnectionManager:
    """Enhanced manager with user-based tracking."""

    def __init__(self):
        # Map user_id -> WebSocket for targeted messaging
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept connection and track by user ID."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        """Remove user's connection."""
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, message: str):
        """Send a message to a specific user."""
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str, exclude: str | None = None):
        """Send to all connected users, optionally excluding one."""
        for uid, websocket in self.active_connections.items():
            if uid != exclude:
                await websocket.send_text(message)

    def get_online_users(self) -> list[str]:
        """Get list of currently connected user IDs."""
        return list(self.active_connections.keys())

    @property
    def connection_count(self) -> int:
        """Number of active connections."""
        return len(self.active_connections)
```

### Usage with User Tracking

```python
app = FastAPI()
manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def ws(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    await manager.broadcast(f"{user_id} is online", exclude=user_id)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"{user_id} went offline")

@app.get("/online-users")
async def get_online_users():
    """REST endpoint to check who's online."""
    return {
        "users": manager.get_online_users(),
        "count": manager.connection_count,
    }
```

## Connection Lifecycle

```
Client A connects:
  manager.active_connections = [A]

Client B connects:
  manager.active_connections = [A, B]

Client A sends "hello":
  manager.broadcast("hello")
  -> sends to A and B

Client B disconnects:
  manager.disconnect(B)
  manager.active_connections = [A]

Client C connects:
  manager.active_connections = [A, C]
```

## Handling Dead Connections

Sometimes connections die without sending a close frame (network drop, app crash). The manager won't know until you try to send to them:

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def broadcast(self, message: str):
        """Broadcast with dead connection cleanup."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for dead in dead_connections:
            self.active_connections.remove(dead)
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Connection tracking | N/A (client manages one) | N/A (client manages one) | `ConnectionManager` class |
| Send to one | N/A | N/A | `send_personal_message()` |
| Send to all | N/A (server's job) | N/A (server's job) | `broadcast()` |
| Online status | Check connection state | Check connection state | `get_online_users()` |
| Cleanup | `onComplete` delegate | `onClosed()` callback | `disconnect()` + dead conn cleanup |

## Key Takeaways

- **ConnectionManager** tracks all active WebSocket connections in a shared data structure
- Use a **list** for simple tracking, a **dict** (user_id -> WebSocket) for targeted messaging
- The **connect** method accepts the WebSocket and adds it to tracking
- The **disconnect** method removes it from tracking (call in `except WebSocketDisconnect`)
- **broadcast** sends a message to all connected clients
- **send_personal_message** sends to one specific client
- Handle **dead connections** by catching exceptions during broadcast and cleaning up
- The manager is a **module-level singleton** -- all WebSocket handlers share the same instance
