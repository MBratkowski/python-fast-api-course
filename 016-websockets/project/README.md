# Project: Real-Time Notification System

## Overview

Build a real-time notification system using WebSockets. Users connect with authentication, receive targeted notifications, and can subscribe to topic channels. This project combines everything from Module 016 into a production-style application.

## Requirements

### Core Features

1. **Authenticated WebSocket endpoint** (`/ws?token=<jwt>`)
   - Accept WebSocket connections with JWT token in query parameter
   - Verify token and extract user_id
   - Reject unauthenticated connections with WS_1008_POLICY_VIOLATION
   - Track connected users by user_id

2. **ConnectionManager with user tracking**
   - Track connections by user_id (dict mapping)
   - Support `send_to_user(user_id, message)` for targeted notifications
   - Support `broadcast(message)` for system-wide announcements
   - Clean up on disconnect

3. **Notification broadcasting** (`POST /notify`)
   - REST endpoint that sends notifications to connected WebSocket clients
   - Support targeting: all users, specific user, or a topic
   - JSON notification format: `{"type": "notification", "title": "...", "body": "..."}`

4. **Topic subscriptions**
   - Users subscribe to topics via WebSocket message: `{"action": "subscribe", "topic": "..."}`
   - Users unsubscribe via: `{"action": "unsubscribe", "topic": "..."}`
   - Notifications can target a topic (only subscribers receive them)

5. **Online status** (`GET /users/online`)
   - REST endpoint returning list of currently connected users
   - Include connection count

### Technical Requirements

- Use FastAPI with WebSocket support
- Use PyJWT for token verification
- Use the ConnectionManager pattern from theory
- Handle WebSocketDisconnect gracefully
- Clean up topic subscriptions on disconnect

## Starter Template

```python
"""
Real-Time Notification System

WebSocket-based notifications with authentication, user tracking,
and topic subscriptions.
"""

import jwt
from typing import Annotated
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query, status
from fastapi.websockets import WebSocketException
from pydantic import BaseModel
from contextlib import asynccontextmanager

app = FastAPI(title="Real-Time Notification System")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


# TODO: Implement authenticated WebSocket dependency
# - Extract token from query parameter
# - Decode and verify JWT
# - Return user_id
# - Raise WebSocketException on failure


# TODO: Implement NotificationManager class
# - __init__: connections dict (user_id -> WebSocket), topics dict (topic -> set of user_ids)
# - connect(user_id, websocket): accept and track
# - disconnect(user_id): remove from connections and all topics
# - send_to_user(user_id, message): send to specific user
# - broadcast(message): send to all connected users
# - subscribe(user_id, topic): add user to topic
# - unsubscribe(user_id, topic): remove user from topic
# - notify_topic(topic, message): send to all subscribers of a topic
# - get_online_users(): return list of connected user_ids


manager = None  # TODO: Create NotificationManager instance


class Notification(BaseModel):
    title: str
    body: str
    target: str = "all"  # "all", "user:<id>", or "topic:<name>"


# TODO: Implement WebSocket endpoint at /ws
# - Authenticate via query parameter token
# - Connect to manager
# - Handle incoming messages:
#   - {"action": "subscribe", "topic": "..."} -> subscribe to topic
#   - {"action": "unsubscribe", "topic": "..."} -> unsubscribe
# - Handle disconnect: cleanup


# TODO: Implement POST /notify
# - Accept Notification body
# - Parse target:
#   - "all" -> manager.broadcast()
#   - "user:<id>" -> manager.send_to_user()
#   - "topic:<name>" -> manager.notify_topic()
# - Return {"status": "sent", "target": target}


# TODO: Implement GET /users/online
# - Return {"users": [...], "count": N}
```

## Running the Project

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart PyJWT

# Run the server
uvicorn project.main:app --reload --port 8000

# Generate a test token (Python)
import jwt
token = jwt.encode({"sub": "user1"}, "your-secret-key-change-in-production", algorithm="HS256")
print(token)

# Connect with wscat (install: npm install -g wscat)
wscat -c "ws://localhost:8000/ws?token=<your-token>"

# Subscribe to a topic (send as JSON message)
{"action": "subscribe", "topic": "news"}

# Send notification via REST
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{"title": "Alert", "body": "System maintenance at 3 PM", "target": "all"}'

# Send to specific user
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{"title": "Message", "body": "You have a new order", "target": "user:user1"}'

# Send to topic subscribers
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{"title": "News", "body": "Breaking news!", "target": "topic:news"}'

# Check online users
curl http://localhost:8000/users/online
```

## Success Criteria

- [ ] WebSocket connections require valid JWT token
- [ ] Unauthenticated connections are rejected with 1008 code
- [ ] Connected users are tracked by user_id
- [ ] Broadcasting reaches all connected clients
- [ ] Targeted notifications reach only the specified user
- [ ] Topic subscriptions work (subscribe, unsubscribe)
- [ ] Topic notifications reach only subscribed users
- [ ] Disconnects clean up connections and subscriptions
- [ ] Online users endpoint returns accurate data
- [ ] Tests pass: `pytest project/ -v`

## Stretch Goals

1. **Room-based notifications** -- Users join rooms (per-user channels like `user:{id}`) for private notifications
2. **Message history on reconnect** -- Store last N notifications per user in memory; send missed ones on reconnect
3. **Redis Pub/Sub** -- Use Redis for cross-server notification broadcasting (see theory/06)
4. **Heartbeat/ping-pong** -- Implement periodic ping to detect dead connections and clean up
5. **Notification persistence** -- Store notifications in a list (or database) with read/unread status
6. **Rate limiting** -- Limit how many messages a client can send per minute via WebSocket
