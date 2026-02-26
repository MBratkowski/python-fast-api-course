# Module 016: WebSockets & Real-Time

## Why This Module?

Build real-time features: chat, notifications, live updates. WebSockets maintain persistent connections.

## Mobile Developer Context

You know push notifications. WebSockets give you bidirectional real-time communication within the app.

## What You'll Learn

- WebSocket fundamentals
- FastAPI WebSocket support
- Connection management
- Broadcasting messages
- Authentication for WebSockets
- Scaling WebSockets

## Topics

### Theory
1. WebSocket vs HTTP
2. FastAPI WebSocket Endpoints
3. Connection Manager Pattern
4. Broadcasting & Rooms
5. WebSocket Authentication
6. Scaling with Redis Pub/Sub

### Project
Build a real-time notification system.

## Example

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        self.connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: dict):
        if websocket := self.connections.get(user_id):
            await websocket.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming message
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
```
