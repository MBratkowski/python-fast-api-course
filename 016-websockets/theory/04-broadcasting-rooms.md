# Broadcasting and Rooms

## Why This Matters

Not every message should go to everyone. In a chat app, messages stay within channels. In a game, updates go to players in the same lobby. In a notification system, alerts go to specific teams or topics.

Room-based messaging solves this: clients join rooms, and broadcasts go only to members of that room. On mobile, you've seen this with Firebase Realtime Database paths, Combine Publisher subjects, or Kotlin SharedFlow collectors. On the server, you implement the routing.

## Room-Based ConnectionManager

Extend the ConnectionManager to support rooms:

```python
from fastapi import WebSocket

class RoomConnectionManager:
    """ConnectionManager with room support."""

    def __init__(self):
        # room_name -> list of WebSocket connections
        self.rooms: dict[str, list[WebSocket]] = {}
        # Track which rooms each websocket is in
        self.connection_rooms: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept connection (not in any room yet)."""
        await websocket.accept()
        self.connection_rooms[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        """Remove connection from all rooms."""
        rooms = self.connection_rooms.pop(websocket, set())
        for room in rooms:
            if room in self.rooms:
                self.rooms[room].remove(websocket)
                if not self.rooms[room]:
                    del self.rooms[room]  # Clean up empty rooms

    def join_room(self, websocket: WebSocket, room: str):
        """Add a connection to a room."""
        if room not in self.rooms:
            self.rooms[room] = []
        if websocket not in self.rooms[room]:
            self.rooms[room].append(websocket)
            self.connection_rooms[websocket].add(room)

    def leave_room(self, websocket: WebSocket, room: str):
        """Remove a connection from a room."""
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
            self.connection_rooms[websocket].discard(room)
            if not self.rooms[room]:
                del self.rooms[room]

    async def broadcast_to_room(self, room: str, message: str):
        """Send a message to all connections in a specific room."""
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_text(message)

    async def broadcast_all(self, message: str):
        """Send a message to ALL connected clients across all rooms."""
        sent_to = set()
        for room_connections in self.rooms.values():
            for connection in room_connections:
                if id(connection) not in sent_to:
                    await connection.send_text(message)
                    sent_to.add(id(connection))

    def get_room_members(self, room: str) -> int:
        """Get number of connections in a room."""
        return len(self.rooms.get(room, []))

    def get_rooms(self) -> list[str]:
        """Get list of active rooms."""
        return list(self.rooms.keys())
```

### Using the Room Manager

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
manager = RoomConnectionManager()

@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    """Chat endpoint with room support."""
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "join":
                room = data["room"]
                manager.join_room(websocket, room)
                await manager.broadcast_to_room(
                    room, f"Someone joined {room}"
                )

            elif action == "leave":
                room = data["room"]
                manager.leave_room(websocket, room)
                await manager.broadcast_to_room(
                    room, f"Someone left {room}"
                )

            elif action == "message":
                room = data["room"]
                message = data["text"]
                await manager.broadcast_to_room(room, message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## Use Cases for Rooms

### Chat Application

```python
# Users join channel rooms
manager.join_room(websocket, "general")
manager.join_room(websocket, "random")
manager.join_room(websocket, "dev-team")

# Message goes to all members of that channel
await manager.broadcast_to_room("general", "Hello everyone!")
```

### Game Lobbies

```python
# Players join a game room
manager.join_room(player_ws, f"game:{game_id}")

# Game updates go to all players in that game
await manager.broadcast_to_room(
    f"game:{game_id}",
    '{"type": "move", "player": "X", "position": 4}'
)
```

### Topic Subscriptions

```python
# Users subscribe to topics they care about
manager.join_room(websocket, "topic:sports")
manager.join_room(websocket, "topic:tech")

# News updates go to relevant subscribers
await manager.broadcast_to_room("topic:sports", "Goal scored!")
await manager.broadcast_to_room("topic:tech", "New Python release!")
```

### Per-User Notifications

```python
# Each user gets their own "room" for private notifications
manager.join_room(websocket, f"user:{user_id}")

# Send targeted notification
await manager.broadcast_to_room(
    f"user:{user_id}",
    '{"type": "notification", "text": "Your order shipped!"}'
)
```

## Room Isolation

A key property: rooms are isolated. Broadcasting to "room-A" does not affect "room-B":

```
Room "general":  [Client 1, Client 2, Client 3]
Room "private":  [Client 2, Client 4]

broadcast_to_room("general", "hello")
  -> Client 1 receives "hello"
  -> Client 2 receives "hello"
  -> Client 3 receives "hello"
  -> Client 4 does NOT receive (not in "general")

broadcast_to_room("private", "secret")
  -> Client 2 receives "secret"
  -> Client 4 receives "secret"
  -> Client 1, 3 do NOT receive (not in "private")
```

## REST API for Room Information

Expose room state through regular HTTP endpoints:

```python
@app.get("/rooms")
async def list_rooms():
    """List all active rooms and their member counts."""
    return {
        "rooms": [
            {"name": room, "members": manager.get_room_members(room)}
            for room in manager.get_rooms()
        ]
    }

@app.get("/rooms/{room_name}")
async def room_info(room_name: str):
    """Get info about a specific room."""
    return {
        "room": room_name,
        "members": manager.get_room_members(room_name),
        "exists": room_name in manager.rooms,
    }
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Rooms/Channels | Firebase DB paths | Firebase DB paths | `dict[str, list[WebSocket]]` |
| Join room | Subscribe to path | `addValueEventListener` | `manager.join_room(ws, room)` |
| Leave room | Unsubscribe | `removeEventListener` | `manager.leave_room(ws, room)` |
| Room broadcast | N/A (server handles) | N/A (server handles) | `manager.broadcast_to_room()` |
| Subscriptions | Combine `Publisher` | Kotlin `SharedFlow` | Room membership in manager |

## Key Takeaways

- **Rooms** group WebSocket connections for targeted broadcasting
- Use `dict[str, list[WebSocket]]` to map room names to their member connections
- **join_room** and **leave_room** manage membership; **disconnect** removes from all rooms
- **broadcast_to_room** sends only to members of that specific room (isolation)
- Clean up **empty rooms** when the last member leaves to prevent memory leaks
- Common patterns: chat channels, game lobbies, topic subscriptions, per-user notification channels
- Expose room state through **REST endpoints** for dashboards and monitoring
- Track **which rooms each connection belongs to** for efficient cleanup on disconnect
