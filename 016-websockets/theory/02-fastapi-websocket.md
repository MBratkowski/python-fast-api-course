# FastAPI WebSocket Endpoints

## Why This Matters

On mobile, you connect to a WebSocket server using `URLSessionWebSocketTask` (iOS) or OkHttp (Android), then listen for messages in a callback or delegate. On the server, you handle the other side: accepting connections, receiving messages, sending responses, and handling disconnects.

FastAPI makes this straightforward with the `@app.websocket` decorator and the `WebSocket` object. The lifecycle is: accept, loop (receive/send), handle disconnect.

## The WebSocket Lifecycle

```
1. Client connects -> Server accepts
2. Loop: receive messages, send responses
3. Client disconnects (or server closes) -> Cleanup
```

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Step 1: Accept the connection
    await websocket.accept()

    try:
        # Step 2: Message loop
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You said: {data}")
    except WebSocketDisconnect:
        # Step 3: Handle disconnect
        print("Client disconnected")
```

## accept() -- Starting the Connection

Before any communication, the server must accept the WebSocket handshake:

```python
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    # Must call accept() first -- completes the HTTP upgrade
    await websocket.accept()

    # Now you can send and receive
    await websocket.send_text("Welcome!")
```

If you don't call `accept()`, the client's connection attempt will hang or fail.

## receive_text() and send_text()

For plain text messages:

```python
@app.websocket("/ws")
async def echo_server(websocket: WebSocket):
    """Simple echo server -- sends back whatever it receives."""
    await websocket.accept()
    try:
        while True:
            # Wait for a text message from the client
            message = await websocket.receive_text()

            # Send a text message back
            await websocket.send_text(f"Echo: {message}")
    except WebSocketDisconnect:
        pass
```

## receive_json() and send_json()

For structured data (parsed as Python dicts):

```python
@app.websocket("/ws")
async def json_endpoint(websocket: WebSocket):
    """Receive JSON, process it, send JSON back."""
    await websocket.accept()
    try:
        while True:
            # Receive and parse JSON
            data = await websocket.receive_json()
            # data is a dict, e.g. {"action": "ping", "timestamp": 123}

            # Process and respond with JSON
            response = {
                "action": "pong",
                "received": data,
                "status": "ok",
            }
            await websocket.send_json(response)
    except WebSocketDisconnect:
        pass
```

## WebSocketDisconnect Exception

When a client disconnects (closes the browser, loses network, etc.), the `receive_*` methods raise `WebSocketDisconnect`. You must handle this or your server will crash.

```python
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Got: {data}")
    except WebSocketDisconnect as e:
        # e.code contains the close code (e.g., 1000 for normal close)
        print(f"Client disconnected with code: {e.code}")
```

### Common Close Codes

| Code | Meaning |
|------|---------|
| 1000 | Normal closure |
| 1001 | Going away (page navigation, server shutdown) |
| 1006 | Abnormal closure (no close frame) |
| 1008 | Policy violation |
| 1011 | Server error |

## Path Parameters with WebSocket

WebSocket endpoints support path parameters, just like HTTP endpoints:

```python
@app.websocket("/ws/{client_id}")
async def ws_with_id(websocket: WebSocket, client_id: int):
    """WebSocket endpoint with client identification."""
    await websocket.accept()
    await websocket.send_text(f"Welcome, client #{client_id}!")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Client #{client_id} said: {data}")
    except WebSocketDisconnect:
        print(f"Client #{client_id} disconnected")
```

## Query Parameters

```python
from typing import Annotated
from fastapi import WebSocket, Query

@app.websocket("/ws")
async def ws_with_query(
    websocket: WebSocket,
    room: Annotated[str, Query()] = "general",
):
    """WebSocket with query parameter: /ws?room=lobby"""
    await websocket.accept()
    await websocket.send_text(f"Joined room: {room}")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"[{room}] {data}")
    except WebSocketDisconnect:
        pass
```

## The try/except Pattern

Every WebSocket endpoint should follow this pattern:

```python
@app.websocket("/ws")
async def robust_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Main message handling loop
            data = await websocket.receive_text()
            # Process data...
            await websocket.send_text("response")
    except WebSocketDisconnect:
        # Client disconnected -- clean up resources
        pass
    except Exception as e:
        # Unexpected error -- log and close gracefully
        print(f"Error: {e}")
        await websocket.close(code=1011)  # Server error
```

**Never skip the try/except.** Without it:
- A disconnecting client crashes your handler
- Resources (memory, connection tracking) leak
- The event loop may report unhandled exceptions

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Connect | `.resume()` on task | `newWebSocket()` | `await websocket.accept()` |
| Receive text | `.receive()` callback | `onMessage()` | `await websocket.receive_text()` |
| Send text | `.send(.string(...))` | `ws.send(text)` | `await websocket.send_text()` |
| Receive JSON | Parse received string | Parse received string | `await websocket.receive_json()` |
| Disconnect | `onComplete` handler | `onClosed()` / `onFailure()` | `except WebSocketDisconnect` |
| Close | `.cancel(closeCode:)` | `ws.close(code, reason)` | `await websocket.close(code=)` |

## Key Takeaways

- Use `@app.websocket("/ws")` to create WebSocket endpoints in FastAPI
- Always call `await websocket.accept()` first to complete the handshake
- Use `receive_text()`/`send_text()` for strings, `receive_json()`/`send_json()` for structured data
- **Always** wrap the message loop in `try/except WebSocketDisconnect`
- WebSocket endpoints support **path parameters** and **query parameters** like HTTP endpoints
- The handler function runs for the **entire connection lifetime** -- it's a long-running coroutine
- Handle `WebSocketDisconnect` to clean up resources when clients leave
