"""
Exercise 1: Basic WebSocket Endpoints

Learn to create WebSocket endpoints with FastAPI.
Implement echo, JSON processing, and disconnect handling.

No external dependencies -- uses FastAPI's built-in WebSocket support.

Run: pytest 016-websockets/exercises/01_basic_websocket.py -v
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

# ============= APP SETUP =============

app = FastAPI()

# Track disconnect events for testing
disconnect_log: list[str] = []


# ============= TODO: Exercise 1.1 =============
# Create a WebSocket endpoint at /ws/echo that:
# - Accepts the WebSocket connection
# - Enters a loop that receives text messages
# - Sends back each message prefixed with "Echo: "
#   e.g., receives "hello" -> sends "Echo: hello"
# - Handles WebSocketDisconnect to exit cleanly
#
# Hints:
# - Use await websocket.accept() to start
# - Use await websocket.receive_text() to get messages
# - Use await websocket.send_text() to respond
# - Wrap the loop in try/except WebSocketDisconnect

@app.websocket("/ws/echo")
async def echo_endpoint(websocket: WebSocket):
    """Echo server -- sends back whatever it receives, prefixed with 'Echo: '."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.2 =============
# Create a WebSocket endpoint at /ws/json that:
# - Accepts the WebSocket connection
# - Receives JSON messages (dicts)
# - Processes the message:
#   - If message has "action": "greet" and "name": "<name>",
#     respond with {"response": "Hello, <name>!", "status": "ok"}
#   - If message has "action": "add" and "a": <num> and "b": <num>,
#     respond with {"response": a + b, "status": "ok"}
#   - For any other action,
#     respond with {"response": "Unknown action", "status": "error"}
# - Handles WebSocketDisconnect to exit cleanly
#
# Hints:
# - Use await websocket.receive_json() to get parsed dict
# - Use await websocket.send_json() to send dict response

@app.websocket("/ws/json")
async def json_endpoint(websocket: WebSocket):
    """JSON processing endpoint."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.3 =============
# Create a WebSocket endpoint at /ws/tracked/{client_id} that:
# - Accepts the WebSocket connection
# - Sends a welcome message: "Welcome, {client_id}!"
# - Enters a message loop (receive text, echo back)
# - On disconnect, appends "{client_id} disconnected" to the
#   disconnect_log list (defined above)
#
# This exercises proper cleanup on disconnect.
#
# Hints:
# - Use the client_id path parameter
# - In the except WebSocketDisconnect block, append to disconnect_log

@app.websocket("/ws/tracked/{client_id}")
async def tracked_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket with disconnect tracking."""
    # TODO: Implement
    pass


# ============= TESTS (DO NOT MODIFY) =============

client = TestClient(app)


class TestEchoEndpoint:
    """Tests for Exercise 1.1: Echo WebSocket."""

    def test_echo_single_message(self):
        with client.websocket_connect("/ws/echo") as ws:
            ws.send_text("hello")
            response = ws.receive_text()
            assert response == "Echo: hello"

    def test_echo_multiple_messages(self):
        with client.websocket_connect("/ws/echo") as ws:
            for msg in ["first", "second", "third"]:
                ws.send_text(msg)
                response = ws.receive_text()
                assert response == f"Echo: {msg}"

    def test_echo_empty_string(self):
        with client.websocket_connect("/ws/echo") as ws:
            ws.send_text("")
            response = ws.receive_text()
            assert response == "Echo: "

    def test_echo_special_characters(self):
        with client.websocket_connect("/ws/echo") as ws:
            ws.send_text("hello! @#$%")
            response = ws.receive_text()
            assert response == "Echo: hello! @#$%"


class TestJsonEndpoint:
    """Tests for Exercise 1.2: JSON processing WebSocket."""

    def test_greet_action(self):
        with client.websocket_connect("/ws/json") as ws:
            ws.send_json({"action": "greet", "name": "Alice"})
            response = ws.receive_json()
            assert response["response"] == "Hello, Alice!"
            assert response["status"] == "ok"

    def test_add_action(self):
        with client.websocket_connect("/ws/json") as ws:
            ws.send_json({"action": "add", "a": 3, "b": 7})
            response = ws.receive_json()
            assert response["response"] == 10
            assert response["status"] == "ok"

    def test_add_action_negative_numbers(self):
        with client.websocket_connect("/ws/json") as ws:
            ws.send_json({"action": "add", "a": -5, "b": 3})
            response = ws.receive_json()
            assert response["response"] == -2

    def test_unknown_action(self):
        with client.websocket_connect("/ws/json") as ws:
            ws.send_json({"action": "unknown"})
            response = ws.receive_json()
            assert response["status"] == "error"
            assert response["response"] == "Unknown action"

    def test_multiple_actions(self):
        with client.websocket_connect("/ws/json") as ws:
            ws.send_json({"action": "greet", "name": "Bob"})
            r1 = ws.receive_json()
            assert r1["response"] == "Hello, Bob!"

            ws.send_json({"action": "add", "a": 1, "b": 2})
            r2 = ws.receive_json()
            assert r2["response"] == 3


class TestTrackedEndpoint:
    """Tests for Exercise 1.3: Disconnect tracking WebSocket."""

    def test_welcome_message(self):
        with client.websocket_connect("/ws/tracked/user42") as ws:
            welcome = ws.receive_text()
            assert welcome == "Welcome, user42!"

    def test_echo_after_welcome(self):
        with client.websocket_connect("/ws/tracked/alice") as ws:
            ws.receive_text()  # consume welcome
            ws.send_text("test message")
            response = ws.receive_text()
            assert "test message" in response

    def test_disconnect_logged(self):
        disconnect_log.clear()
        with client.websocket_connect("/ws/tracked/bob") as ws:
            ws.receive_text()  # consume welcome
        # After context manager exits, disconnect should be logged
        assert "bob disconnected" in disconnect_log

    def test_multiple_disconnects_tracked(self):
        disconnect_log.clear()
        for name in ["x", "y", "z"]:
            with client.websocket_connect(f"/ws/tracked/{name}") as ws:
                ws.receive_text()  # consume welcome
        assert len(disconnect_log) == 3
        assert "x disconnected" in disconnect_log
        assert "y disconnected" in disconnect_log
        assert "z disconnected" in disconnect_log
