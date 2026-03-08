# Scaling WebSockets with Redis Pub/Sub

## Why This Matters

The ConnectionManager works perfectly on a single server. But what happens when you scale to multiple servers behind a load balancer? Client A connects to Server 1, Client B connects to Server 2. When Client A sends a message, Server 1's ConnectionManager broadcasts to its local connections -- but Client B on Server 2 never gets the message.

This is the same problem that push notification services solve. APNs (iOS) and FCM (Android) are centralized servers that fan out messages to all devices. Redis Pub/Sub gives you the same pattern for WebSocket servers: publish to a Redis channel, and every server subscribed to that channel receives and broadcasts locally.

## The Single-Server Limitation

```
Single Server (ConnectionManager works):

  Client A ---> Server 1 (manager has [A, B, C])
  Client B --->     |
  Client C --->     |

  A sends "hello" -> manager.broadcast() -> B and C receive "hello"


Multiple Servers (ConnectionManager breaks):

  Client A ---> Server 1 (manager has [A, B])
  Client B --->     |

  Client C ---> Server 2 (manager has [C, D])
  Client D --->     |

  A sends "hello" -> Server 1 broadcasts -> B receives
                     Server 2 knows nothing -> C, D never receive!
```

## Redis Pub/Sub: The Solution

Redis Pub/Sub is a messaging system where publishers send messages to channels and subscribers receive them. Each server subscribes to a Redis channel and publishes messages there. Redis fans out to all subscribers.

```
With Redis Pub/Sub:

  Client A ---> Server 1 --publish--> Redis Channel
  Client B --->     |                      |
                    |<---subscribe----------+

  Client C ---> Server 2 --publish--> Redis Channel
  Client D --->     |                      |
                    |<---subscribe----------+

  A sends "hello":
    1. Server 1 publishes "hello" to Redis
    2. Redis sends "hello" to all subscribers (Server 1 + Server 2)
    3. Server 1 broadcasts to local connections (A, B)
    4. Server 2 broadcasts to local connections (C, D)
    -> Everyone receives "hello"
```

## Redis Pub/Sub Basics

```python
import redis.asyncio as redis

# Publisher
async def publish_message(channel: str, message: str):
    """Publish a message to a Redis channel."""
    client = redis.from_url("redis://localhost:6379")
    await client.publish(channel, message)
    await client.close()


# Subscriber
async def subscribe_to_channel(channel: str):
    """Subscribe and listen for messages."""
    client = redis.from_url("redis://localhost:6379")
    pubsub = client.pubsub()
    await pubsub.subscribe(channel)

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"].decode("utf-8")
            print(f"Received: {data}")

    await pubsub.unsubscribe(channel)
    await client.close()
```

## ConnectionManager with Redis Pub/Sub

Extend the ConnectionManager to use Redis for cross-server broadcasting:

```python
import json
import asyncio
import redis.asyncio as redis
from fastapi import WebSocket
from contextlib import asynccontextmanager


class RedisConnectionManager:
    """ConnectionManager that uses Redis Pub/Sub for multi-server support."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.active_connections: list[WebSocket] = []
        self.redis_client: redis.Redis | None = None
        self.pubsub: redis.client.PubSub | None = None
        self.channel = "ws:broadcast"

    async def initialize(self):
        """Connect to Redis and start listening for messages."""
        self.redis_client = redis.from_url(
            self.redis_url, decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(self.channel)

        # Start background listener
        asyncio.create_task(self._listen_for_messages())

    async def shutdown(self):
        """Clean up Redis connections."""
        if self.pubsub:
            await self.pubsub.unsubscribe(self.channel)
        if self.redis_client:
            await self.redis_client.close()

    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Publish message to Redis (all servers will receive it)."""
        if self.redis_client:
            await self.redis_client.publish(self.channel, message)

    async def _broadcast_local(self, message: str):
        """Send to all LOCAL connections (called when Redis message received)."""
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.active_connections.remove(conn)

    async def _listen_for_messages(self):
        """Background task: listen for Redis Pub/Sub messages."""
        if not self.pubsub:
            return
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                await self._broadcast_local(message["data"])
```

### Using with FastAPI Lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

manager = RedisConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and clean up Redis connection."""
    await manager.initialize()
    yield
    await manager.shutdown()


app = FastAPI(lifespan=lifespan)


@app.websocket("/ws/{client_id}")
async def ws_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Publish to Redis -> all servers broadcast locally
            await manager.broadcast(f"{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} left")
```

## Room-Based Redis Pub/Sub

For room support, use separate Redis channels per room:

```python
class RedisRoomManager:
    """Room-based ConnectionManager with Redis Pub/Sub."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.rooms: dict[str, list[WebSocket]] = {}
        self.redis_client: redis.Redis | None = None
        self.pubsub: redis.client.PubSub | None = None

    async def initialize(self):
        self.redis_client = redis.from_url(
            self.redis_url, decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()

    async def join_room(self, websocket: WebSocket, room: str):
        """Add connection to a room and subscribe to Redis channel."""
        if room not in self.rooms:
            self.rooms[room] = []
            # Subscribe to Redis channel for this room
            await self.pubsub.subscribe(f"room:{room}")

        self.rooms[room].append(websocket)

    async def leave_room(self, websocket: WebSocket, room: str):
        """Remove connection from room."""
        if room in self.rooms:
            self.rooms[room].remove(websocket)
            if not self.rooms[room]:
                del self.rooms[room]
                # Unsubscribe when room is empty
                await self.pubsub.unsubscribe(f"room:{room}")

    async def broadcast_to_room(self, room: str, message: str):
        """Publish to room's Redis channel."""
        if self.redis_client:
            await self.redis_client.publish(f"room:{room}", message)

    async def _broadcast_room_local(self, room: str, message: str):
        """Send to local connections in a room."""
        if room in self.rooms:
            for ws in self.rooms[room]:
                try:
                    await ws.send_text(message)
                except Exception:
                    pass
```

## Architecture Overview

```
                    ┌──────────────┐
                    │    Redis     │
                    │  Pub/Sub     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼─────┐ ┌───▼─────┐
        │ Server 1  │ │ Server 2│ │ Server 3│
        │ Manager   │ │ Manager │ │ Manager │
        │ [A, B]    │ │ [C, D]  │ │ [E]     │
        └───────────┘ └─────────┘ └─────────┘
            ▲  ▲          ▲  ▲        ▲
            │  │          │  │        │
          A    B        C    D      E

  Flow:
  1. Client A sends message on Server 1
  2. Server 1 publishes to Redis
  3. Redis forwards to all subscribers (Servers 1, 2, 3)
  4. Each server broadcasts to its local connections
  5. All clients (A-E) receive the message
```

## When to Use Redis Pub/Sub

| Scenario | Single Server OK? | Need Redis Pub/Sub? |
|----------|-------------------|---------------------|
| Development/testing | Yes | No |
| Single server deployment | Yes | No |
| Multiple servers behind LB | No | Yes |
| Horizontal auto-scaling | No | Yes |
| Kubernetes/container clusters | No | Yes |

**Start simple:** Build with ConnectionManager first. Add Redis Pub/Sub when you deploy multiple servers.

## Message Serialization

For structured messages, serialize to JSON:

```python
import json

async def broadcast_event(self, event_type: str, data: dict):
    """Broadcast a structured event via Redis."""
    message = json.dumps({
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    })
    await self.redis_client.publish(self.channel, message)

# Usage
await manager.broadcast_event("chat_message", {
    "user": "alice",
    "text": "Hello everyone!",
    "room": "general",
})
```

## Production Considerations

### Connection Pooling

```python
# Use connection pool for Redis (not a new connection per operation)
redis_pool = redis.ConnectionPool.from_url("redis://localhost:6379")
redis_client = redis.Redis(connection_pool=redis_pool)
```

### Error Handling

```python
async def _listen_for_messages(self):
    """Listen with reconnection logic."""
    while True:
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    await self._broadcast_local(message["data"])
        except redis.ConnectionError:
            print("Redis connection lost, reconnecting...")
            await asyncio.sleep(1)
            await self.pubsub.subscribe(self.channel)
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """Check Redis and WebSocket manager health."""
    try:
        await manager.redis_client.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    return {
        "redis": "ok" if redis_ok else "error",
        "local_connections": len(manager.active_connections),
    }
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI + Redis) |
|---------|-------------|-------------------|--------------------------|
| Push fan-out | APNs (Apple servers) | FCM (Google servers) | Redis Pub/Sub (your servers) |
| Multi-device | APNs handles routing | FCM handles routing | Redis channel per room/user |
| Scaling | APNs scales automatically | FCM scales automatically | Add Redis, add servers |
| Offline handling | APNs queues messages | FCM queues messages | Not built-in (need message store) |
| Pub/Sub pattern | Combine `Publisher` | Kotlin `SharedFlow` | Redis channels + `listen()` |

## Key Takeaways

- **Single-server ConnectionManager** doesn't work across multiple servers behind a load balancer
- **Redis Pub/Sub** bridges servers: publish to a channel, all subscribers receive the message
- Each server **subscribes** to Redis and **broadcasts locally** when messages arrive
- Use **separate channels** for rooms (`room:general`, `room:private`)
- Initialize Redis in the **FastAPI lifespan** for proper setup/teardown
- Handle **dead connections** during local broadcast to prevent accumulation
- Add **reconnection logic** for Redis connection failures
- **Start simple** -- use plain ConnectionManager first, add Redis when scaling horizontally
- Redis Pub/Sub is **fire-and-forget** -- messages are not stored. If no subscriber is listening, the message is lost
