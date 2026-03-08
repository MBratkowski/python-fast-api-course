"""
Exercise 3: Broadcasting and Rooms

Build a WebSocket chat endpoint with room support.
Implement room-based join/leave logic and broadcast_to_room.

No external dependencies -- uses FastAPI's built-in WebSocket support.

Run: pytest 016-websockets/exercises/03_broadcasting.py -v
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

# ============= APP SETUP =============

app = FastAPI()


# ============= TODO: Exercise 3.1 - 3.3 =============
# Build a RoomManager class that extends ConnectionManager with room support.
#
# Exercise 3.1: join_room(self, websocket: WebSocket, room: str)
#   - Add the websocket to the room's connection list
#   - If the room doesn't exist yet, create it (empty list in self.rooms dict)
#   - Also track which rooms each websocket belongs to (self.connection_rooms)
#
# Exercise 3.2: leave_room(self, websocket: WebSocket, room: str)
#   - Remove the websocket from the room's connection list
#   - Remove the room from the websocket's room set (self.connection_rooms)
#   - If the room is now empty, delete it from self.rooms
#
# Exercise 3.3: broadcast_to_room(self, room: str, message: str)
#   - Send a text message to ALL connections in the specified room
#   - If the room doesn't exist, do nothing (no error)
#
# The class already has connect() and disconnect() implemented.
# disconnect() should remove the websocket from ALL rooms it belongs to.

class RoomManager:
    """ConnectionManager with room-based broadcasting."""

    def __init__(self):
        # room_name -> list of WebSocket connections
        self.rooms: dict[str, list[WebSocket]] = {}
        # websocket -> set of room names it belongs to
        self.connection_rooms: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept connection (not in any room yet)."""
        await websocket.accept()
        self.connection_rooms[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        """Remove connection from all rooms and tracking."""
        rooms = self.connection_rooms.pop(websocket, set())
        for room in rooms:
            if room in self.rooms:
                if websocket in self.rooms[room]:
                    self.rooms[room].remove(websocket)
                if not self.rooms[room]:
                    del self.rooms[room]

    def join_room(self, websocket: WebSocket, room: str):
        """Add a connection to a room."""
        # TODO: Implement
        # - Create the room in self.rooms if it doesn't exist
        # - Add websocket to the room's list (avoid duplicates)
        # - Add room name to self.connection_rooms[websocket]
        pass

    def leave_room(self, websocket: WebSocket, room: str):
        """Remove a connection from a room."""
        # TODO: Implement
        # - Remove websocket from the room's list in self.rooms
        # - Remove room from self.connection_rooms[websocket]
        # - If room is empty, delete it from self.rooms
        pass

    async def broadcast_to_room(self, room: str, message: str):
        """Send a message to all connections in a specific room."""
        # TODO: Implement
        # - Get the list of connections for the room
        # - Send the message to each connection
        # - If room doesn't exist, do nothing
        pass


# Create global manager
room_manager = RoomManager()


# ============= ENDPOINT (DO NOT MODIFY) =============
# Chat endpoint that uses your RoomManager.
# Accepts JSON commands: join, leave, message.

@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    """Chat endpoint with room support."""
    await room_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "join":
                room = data["room"]
                room_manager.join_room(websocket, room)
                await room_manager.broadcast_to_room(
                    room, f"Someone joined {room}"
                )

            elif action == "leave":
                room = data["room"]
                await room_manager.broadcast_to_room(
                    room, f"Someone left {room}"
                )
                room_manager.leave_room(websocket, room)

            elif action == "message":
                room = data["room"]
                text = data["text"]
                await room_manager.broadcast_to_room(room, text)

    except WebSocketDisconnect:
        room_manager.disconnect(websocket)


# ============= TESTS (DO NOT MODIFY) =============

client = TestClient(app)


class TestJoinRoom:
    """Tests for Exercise 3.1: join_room method."""

    def test_join_creates_room(self):
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json({"action": "join", "room": "general"})
            ws.receive_text()  # consume join broadcast
            assert "general" in room_manager.rooms
            assert len(room_manager.rooms["general"]) == 1
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()

    def test_join_multiple_rooms(self):
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json({"action": "join", "room": "room-a"})
            ws.receive_text()
            ws.send_json({"action": "join", "room": "room-b"})
            ws.receive_text()
            assert "room-a" in room_manager.rooms
            assert "room-b" in room_manager.rooms
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()

    def test_join_broadcast_received(self):
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json({"action": "join", "room": "lobby"})
            msg = ws.receive_text()
            assert msg == "Someone joined lobby"
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()


class TestLeaveRoom:
    """Tests for Exercise 3.2: leave_room method."""

    def test_leave_removes_from_room(self):
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json({"action": "join", "room": "temp"})
            ws.receive_text()  # join broadcast
            assert len(room_manager.rooms.get("temp", [])) == 1

            ws.send_json({"action": "leave", "room": "temp"})
            ws.receive_text()  # leave broadcast
            # Room should be deleted when empty
            assert "temp" not in room_manager.rooms
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()

    def test_leave_one_room_stay_in_another(self):
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json({"action": "join", "room": "stay"})
            ws.receive_text()
            ws.send_json({"action": "join", "room": "go"})
            ws.receive_text()

            ws.send_json({"action": "leave", "room": "go"})
            ws.receive_text()  # leave broadcast

            assert "stay" in room_manager.rooms
            assert "go" not in room_manager.rooms
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()


class TestBroadcastToRoom:
    """Tests for Exercise 3.3: broadcast_to_room method."""

    def test_message_sent_to_room_members(self):
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json({"action": "join", "room": "chat"})
            ws.receive_text()  # join broadcast

            ws.send_json({"action": "message", "room": "chat", "text": "hello"})
            msg = ws.receive_text()
            assert msg == "hello"
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()

    def test_room_isolation(self):
        """Messages in one room should not reach members of another room."""
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws1:
            with client.websocket_connect("/ws/chat") as ws2:
                # ws1 joins room-a, ws2 joins room-b
                ws1.send_json({"action": "join", "room": "room-a"})
                ws1.receive_text()  # join broadcast for room-a

                ws2.send_json({"action": "join", "room": "room-b"})
                ws2.receive_text()  # join broadcast for room-b

                # Send message to room-a
                ws1.send_json({
                    "action": "message",
                    "room": "room-a",
                    "text": "only for room-a",
                })
                msg = ws1.receive_text()
                assert msg == "only for room-a"

                # ws2 should NOT have received anything
                # (we can verify by sending to room-b and checking ws2 gets it)
                ws2.send_json({
                    "action": "message",
                    "room": "room-b",
                    "text": "only for room-b",
                })
                msg_b = ws2.receive_text()
                assert msg_b == "only for room-b"
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()

    def test_broadcast_to_multiple_members(self):
        """Both members of a room should receive the broadcast."""
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws1:
            with client.websocket_connect("/ws/chat") as ws2:
                # Both join the same room
                ws1.send_json({"action": "join", "room": "shared"})
                ws1.receive_text()  # ws1 gets join broadcast

                ws2.send_json({"action": "join", "room": "shared"})
                # ws1 receives ws2's join broadcast
                ws1.receive_text()
                # ws2 receives its own join broadcast
                ws2.receive_text()

                # Send message from ws1
                ws1.send_json({
                    "action": "message",
                    "room": "shared",
                    "text": "hello everyone",
                })

                # Both should receive it
                msg1 = ws1.receive_text()
                msg2 = ws2.receive_text()
                assert msg1 == "hello everyone"
                assert msg2 == "hello everyone"
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()

    def test_disconnect_removes_from_rooms(self):
        """Disconnecting should clean up all room memberships."""
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json({"action": "join", "room": "cleanup-test"})
            ws.receive_text()
            assert "cleanup-test" in room_manager.rooms

        # After disconnect, empty room should be cleaned up
        assert "cleanup-test" not in room_manager.rooms
        room_manager.rooms.clear()
        room_manager.connection_rooms.clear()
