# WebSocket Authentication

## Why This Matters

On mobile, you attach an `Authorization: Bearer <token>` header to every HTTP request. But WebSocket connections don't support custom HTTP headers during the handshake. The browser's WebSocket API has no way to set headers. This means the standard Bearer token pattern you've used everywhere doesn't work for WebSocket connections.

This is a real security gap. Without authentication, anyone can connect to your WebSocket endpoint and receive real-time data meant for authenticated users. You need alternative approaches, and the most common one is passing the token as a query parameter.

## The Challenge: No HTTP Headers

```
HTTP Request (headers work):
  GET /api/users
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
  -> Server reads header, authenticates user

WebSocket Handshake (no custom headers):
  GET /ws
  Upgrade: websocket
  Connection: Upgrade
  (No Authorization header from browser WebSocket API!)
  -> Server has no token to verify
```

**Why this happens:** The browser's `WebSocket` constructor only accepts a URL and optional subprotocols. There's no parameter for custom headers. Native mobile clients (URLSessionWebSocketTask, OkHttp) can add headers, but the server must also support browser clients.

## Solution 1: Query Parameter Token (Recommended)

Pass the JWT token as a URL query parameter:

```python
# Client connects to: ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiJ9...

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status
from fastapi.websockets import WebSocketException
from typing import Annotated
import jwt  # PyJWT

app = FastAPI()
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


async def get_ws_user(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None,
) -> str:
    """Verify JWT token from query parameter. Returns user_id."""
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        return user_id
    except jwt.InvalidTokenError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
```

### Using with Depends()

FastAPI's dependency injection works with WebSocket endpoints:

```python
from fastapi import Depends

@app.websocket("/ws")
async def authenticated_ws(
    websocket: WebSocket,
    user_id: str = Depends(get_ws_user),
):
    """WebSocket endpoint that requires authentication."""
    await websocket.accept()
    await websocket.send_text(f"Welcome, {user_id}!")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"{user_id}: {data}")
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
```

### Client-Side Usage

```javascript
// JavaScript (browser)
const token = localStorage.getItem("access_token");
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
```

```swift
// iOS (Swift)
var request = URLRequest(url: URL(string: "ws://localhost:8000/ws?token=\(token)")!)
let task = URLSession.shared.webSocketTask(with: request)
task.resume()
```

```kotlin
// Android (Kotlin)
val request = Request.Builder()
    .url("ws://localhost:8000/ws?token=$token")
    .build()
val ws = OkHttpClient().newWebSocket(request, listener)
```

## Solution 2: Cookie-Based Authentication

If your app uses HTTP-only cookies for auth (common in web apps):

```python
from fastapi import WebSocket, Cookie, status
from fastapi.websockets import WebSocketException

async def get_ws_user_from_cookie(
    websocket: WebSocket,
    session_token: str | None = Cookie(default=None),
) -> str:
    """Authenticate WebSocket via session cookie."""
    if session_token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user_id = await verify_session(session_token)
    if user_id is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return user_id


@app.websocket("/ws")
async def ws_with_cookie_auth(
    websocket: WebSocket,
    user_id: str = Depends(get_ws_user_from_cookie),
):
    await websocket.accept()
    # ... authenticated connection
```

**Cookie auth advantage:** The browser sends cookies automatically -- no need to add query parameters. But this only works for same-origin connections (CORS applies).

## Solution 3: First-Message Authentication

Accept the connection first, then require the first message to be a token:

```python
@app.websocket("/ws")
async def ws_first_message_auth(websocket: WebSocket):
    """Authenticate via the first message after connection."""
    await websocket.accept()

    try:
        # Wait for auth message (with timeout)
        auth_message = await websocket.receive_json()

        if auth_message.get("type") != "auth":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        token = auth_message.get("token")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload["sub"]
        except (jwt.InvalidTokenError, KeyError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Auth successful -- send confirmation
        await websocket.send_json({"type": "auth_ok", "user_id": user_id})

        # Now handle messages normally
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"{user_id}: {data}")

    except WebSocketDisconnect:
        pass
```

**Trade-off:** The connection is accepted before authentication. This means unauthenticated clients can briefly connect (consuming resources) before being kicked. Query parameter auth rejects them during the handshake.

## WebSocketException

FastAPI provides `WebSocketException` for rejecting connections during the handshake:

```python
from fastapi.websockets import WebSocketException
from starlette.status import WS_1008_POLICY_VIOLATION

# Reject during dependency resolution (before accept)
raise WebSocketException(code=WS_1008_POLICY_VIOLATION)
```

### Common WebSocket Close Codes for Auth

| Code | Name | When to Use |
|------|------|-------------|
| 1008 | Policy Violation | Missing or invalid token (recommended) |
| 1003 | Unsupported Data | Client sent unexpected format |
| 1000 | Normal Closure | Clean disconnect |

## Comparing Authentication Approaches

| Approach | Security | Complexity | Browser Support | Mobile Support |
|----------|----------|------------|----------------|----------------|
| Query parameter | Good (token in URL) | Simple | Yes | Yes |
| Cookie | Better (HTTP-only) | Medium | Yes (same-origin) | Requires cookie jar |
| First-message | Good | More complex | Yes | Yes |

**Recommendation:** Use query parameter tokens for most cases. It works across all clients (browser, iOS, Android) and integrates cleanly with FastAPI's dependency injection.

**Security note on query parameters:** Tokens in URLs may appear in server logs and browser history. Mitigate by:
- Using short-lived tokens (5-15 minutes)
- Generating a separate WebSocket-specific token from the main access token
- Ensuring logs don't capture query parameters in production

## Authenticated ConnectionManager

Combine authentication with the ConnectionManager pattern:

```python
from fastapi import WebSocket, Depends

class AuthenticatedConnectionManager:
    """ConnectionManager that tracks authenticated users."""

    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, message: str):
        ws = self.connections.get(user_id)
        if ws:
            await ws.send_text(message)

    async def broadcast(self, message: str):
        for ws in self.connections.values():
            await ws.send_text(message)


manager = AuthenticatedConnectionManager()


@app.websocket("/ws")
async def ws(
    websocket: WebSocket,
    user_id: str = Depends(get_ws_user),
):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"{user_id} left")
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| HTTP auth | `Authorization` header | OkHttp `Interceptor` | `Depends()` with `OAuth2PasswordBearer` |
| WS auth | URLRequest headers (native) | OkHttp headers (native) | Query param or cookie |
| Token storage | Keychain | EncryptedSharedPreferences | N/A (server verifies) |
| Token refresh | Background refresh | Authenticator | Client must reconnect |
| Reject connection | N/A (client side) | N/A (client side) | `WebSocketException(code=1008)` |

## Key Takeaways

- WebSocket connections **cannot use standard HTTP Authorization headers** from browser clients
- The **query parameter token** approach is the most compatible across browsers and mobile clients
- Use `WebSocketException` with `WS_1008_POLICY_VIOLATION` to reject unauthenticated connections
- FastAPI's **Depends()** works with WebSocket endpoints for clean dependency injection
- Use **PyJWT** (not python-jose) for JWT decoding -- consistent with the auth patterns from Module 009
- Consider **short-lived tokens** for WebSocket connections to minimize URL-based token exposure
- Combine auth with **ConnectionManager** to track authenticated users by user ID
- Cookie-based auth is simpler for same-origin web apps but doesn't work for cross-origin or mobile clients
