"""
Exercise 2: Connection Manager

Build the ConnectionManager class that tracks active WebSocket connections
and provides methods for sending messages to specific clients or broadcasting.

No external dependencies -- uses FastAPI's built-in WebSocket support.

Run: pytest 016-websockets/exercises/02_connection_manager.py -v
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

# ============= APP SETUP =============

app = FastAPI()


# ============= TODO: Exercise 2.1 - 2.4 =============
# Build a ConnectionManager class with the following methods:
#
# Exercise 2.1: connect(self, websocket: WebSocket)
#   - Accept the WebSocket connection (await websocket.accept())
#   - Add the websocket to self.active_connections list
#
# Exercise 2.2: disconnect(self, websocket: WebSocket)
#   - Remove the websocket from self.active_connections list
#
# Exercise 2.3: send_personal_message(self, message: str, websocket: WebSocket)
#   - Send a text message to a specific WebSocket connection
#
# Exercise 2.4: broadcast(self, message: str)
#   - Send a text message to ALL active connections
#
# The class should have:
#   - __init__ that creates self.active_connections as an empty list
#   - All methods above

class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection and track it."""
        # TODO: Implement - accept the connection and add to list
        pass

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket from tracking."""
        # TODO: Implement - remove from list
        pass

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific client."""
        # TODO: Implement - send text to the specific websocket
        pass

    async def broadcast(self, message: str):
        """Send a message to ALL connected clients."""
        # TODO: Implement - loop through active_connections and send to each
        pass


# Create a global manager instance
manager = ConnectionManager()


# ============= ENDPOINT (DO NOT MODIFY) =============
# This endpoint uses your ConnectionManager.
# It will work correctly once you implement the methods above.

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Chat endpoint using ConnectionManager."""
    await manager.connect(websocket)
    try:
        await manager.broadcast(f"{client_id} joined")
        while True:
            data = await websocket.receive_text()
            # Send personal acknowledgment
            await manager.send_personal_message(
                f"You said: {data}", websocket
            )
            # Broadcast to everyone
            await manager.broadcast(f"{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} left")


# ============= TESTS (DO NOT MODIFY) =============

client = TestClient(app)


class TestConnect:
    """Tests for Exercise 2.1: connect method."""

    def test_connect_adds_to_list(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/test") as ws:
            assert len(manager.active_connections) == 1
        manager.active_connections.clear()

    def test_connect_multiple(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/a") as ws1:
            with client.websocket_connect("/ws/b") as ws2:
                assert len(manager.active_connections) == 2
        manager.active_connections.clear()

    def test_connect_sends_join_broadcast(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/alice") as ws:
            msg = ws.receive_text()
            assert msg == "alice joined"
        manager.active_connections.clear()


class TestDisconnect:
    """Tests for Exercise 2.2: disconnect method."""

    def test_disconnect_removes_from_list(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/test") as ws:
            assert len(manager.active_connections) == 1
        # After disconnect, list should be empty
        assert len(manager.active_connections) == 0

    def test_disconnect_one_of_two(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/stay") as ws1:
            with client.websocket_connect("/ws/leave") as ws2:
                assert len(manager.active_connections) == 2
                # ws2 receives its own join broadcast
                ws2.receive_text()
            # ws2 disconnected, only ws1 remains
            assert len(manager.active_connections) == 1
        manager.active_connections.clear()


class TestPersonalMessage:
    """Tests for Exercise 2.3: send_personal_message method."""

    def test_personal_message_sent(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/user1") as ws:
            ws.receive_text()  # consume join broadcast
            ws.send_text("hello")
            # First response should be personal message
            personal = ws.receive_text()
            assert personal == "You said: hello"
        manager.active_connections.clear()


class TestBroadcast:
    """Tests for Exercise 2.4: broadcast method."""

    def test_broadcast_to_single_client(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/solo") as ws:
            ws.receive_text()  # consume join broadcast
            ws.send_text("hi")
            ws.receive_text()  # consume personal message
            broadcast_msg = ws.receive_text()
            assert broadcast_msg == "solo: hi"
        manager.active_connections.clear()

    def test_broadcast_join_message(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/first") as ws1:
            join1 = ws1.receive_text()
            assert join1 == "first joined"

            with client.websocket_connect("/ws/second") as ws2:
                # first should receive second's join broadcast
                join2_on_ws1 = ws1.receive_text()
                assert join2_on_ws1 == "second joined"

                # second also receives its own join broadcast
                join2_on_ws2 = ws2.receive_text()
                assert join2_on_ws2 == "second joined"
        manager.active_connections.clear()

    def test_broadcast_leave_message(self):
        manager.active_connections.clear()
        with client.websocket_connect("/ws/stayer") as ws1:
            ws1.receive_text()  # consume join

            with client.websocket_connect("/ws/leaver") as ws2:
                ws1.receive_text()  # consume leaver's join on ws1
                ws2.receive_text()  # consume leaver's join on ws2

            # leaver disconnected -- stayer should get leave message
            leave_msg = ws1.receive_text()
            assert leave_msg == "leaver left"
        manager.active_connections.clear()
