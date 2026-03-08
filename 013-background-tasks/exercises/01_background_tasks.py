"""
Exercise 1: FastAPI BackgroundTasks

Learn to use FastAPI's built-in BackgroundTasks for post-response processing.
Practice adding tasks, passing arguments, and using BackgroundTasks in dependencies.

Run: pytest 013-background-tasks/exercises/01_background_tasks.py -v
"""

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.testclient import TestClient
import pytest

# ============= APP SETUP (PROVIDED) =============

app = FastAPI()

# Shared log that background tasks write to (for testing)
task_log: list[str] = []


def clear_log():
    """Clear the task log between tests."""
    task_log.clear()


# ============= TODO: Exercise 1.1 =============
# Create a background task function that logs a message.
# - Function name: log_message
# - Parameters: message (str)
# - Append the message to the task_log list
# - This is a sync function (not async)

def log_message(message: str):
    """Background task that logs a message."""
    # TODO: Implement - append message to task_log
    pass


# ============= TODO: Exercise 1.2 =============
# Create an endpoint that uses BackgroundTasks to schedule log_message.
# - Route: POST /send-notification/{email}
# - Accept email as path parameter
# - Schedule log_message with message: "Notification sent to {email}"
# - Return {"message": "Notification scheduled", "email": email}

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    """Schedule a notification in the background."""
    # TODO: Implement
    # - Use background_tasks.add_task() to schedule log_message
    # - Return the response dict
    pass


# ============= TODO: Exercise 1.3 =============
# Create an endpoint that schedules multiple background tasks.
# - Route: POST /process-order/{order_id}
# - Schedule THREE log_message tasks:
#   1. "Order {order_id} confirmed"
#   2. "Inventory updated for order {order_id}"
#   3. "Receipt sent for order {order_id}"
# - Return {"message": "Order processed", "order_id": order_id}

@app.post("/process-order/{order_id}")
async def process_order(order_id: int, background_tasks: BackgroundTasks):
    """Process an order with multiple background tasks."""
    # TODO: Implement
    # - Add three background tasks using add_task()
    # - Return the response dict
    pass


# ============= TODO: Exercise 1.4 =============
# Create a dependency that adds its own background task.
# - Function name: track_request
# - Accept BackgroundTasks and a query param action (str, default "unknown")
# - Schedule log_message with message: "Tracked action: {action}"
# - Return the action string
#
# Then create an endpoint that uses this dependency:
# - Route: POST /items/
# - Depends on track_request
# - Also schedules its own log_message: "Item created"
# - Return {"message": "Item created", "tracked_action": action}

def track_request(
    background_tasks: BackgroundTasks,
    action: str = "unknown"
):
    """Dependency that tracks the request action in background."""
    # TODO: Implement
    # - Schedule log_message via background_tasks
    # - Return the action string
    pass


@app.post("/items/")
async def create_item(
    background_tasks: BackgroundTasks,
    action: str = Depends(track_request)
):
    """Create item with dependency that also adds background tasks."""
    # TODO: Implement
    # - Schedule log_message("Item created")
    # - Return response with message and tracked_action
    pass


# ============= TODO: Exercise 1.5 =============
# Create a background task function with multiple parameters.
# - Function name: send_email_task
# - Parameters: to (str), subject (str), body (str, default "")
# - Append to task_log: "Email to {to}: {subject} - {body}"
#
# Create an endpoint that uses it:
# - Route: POST /send-email
# - Accept query params: to (str), subject (str), body (str, default "No body")
# - Schedule send_email_task with all three arguments
# - Return {"message": "Email queued", "to": to}

def send_email_task(to: str, subject: str, body: str = ""):
    """Background task that simulates sending an email."""
    # TODO: Implement - append formatted string to task_log
    pass


@app.post("/send-email")
async def send_email(
    to: str,
    subject: str,
    body: str = "No body",
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Queue an email to be sent in the background."""
    # TODO: Implement
    # - Schedule send_email_task with to, subject, body
    # - Return response dict
    pass


# ============= TESTS =============
# Run with: pytest 013-background-tasks/exercises/01_background_tasks.py -v

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_log():
    """Clear task log before each test."""
    clear_log()
    yield
    clear_log()


def test_log_message_function():
    """Test that log_message appends to task_log."""
    log_message("test message")
    assert len(task_log) == 1, "Should have 1 log entry"
    assert task_log[0] == "test message", "Should log exact message"


def test_send_notification_endpoint():
    """Test notification endpoint schedules background task."""
    response = client.post("/send-notification/user@example.com")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Notification scheduled"
    assert data["email"] == "user@example.com"

    # BackgroundTasks execute after response in TestClient
    assert len(task_log) == 1, "Should have 1 background task logged"
    assert "user@example.com" in task_log[0], "Should log the email"


def test_process_order_multiple_tasks():
    """Test order endpoint schedules three background tasks."""
    response = client.post("/process-order/42")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 42

    # Three background tasks should have executed
    assert len(task_log) == 3, f"Should have 3 log entries, got {len(task_log)}"
    assert "42" in task_log[0], "First task should reference order 42"
    assert "42" in task_log[1], "Second task should reference order 42"
    assert "42" in task_log[2], "Third task should reference order 42"


def test_dependency_adds_background_task():
    """Test that dependency and endpoint both add background tasks."""
    response = client.post("/items/?action=purchase")
    assert response.status_code == 200
    data = response.json()
    assert data["tracked_action"] == "purchase"

    # Both dependency and endpoint tasks should execute
    assert len(task_log) == 2, f"Should have 2 log entries, got {len(task_log)}"
    assert any("purchase" in entry for entry in task_log), "Should track the action"
    assert any("Item created" in entry for entry in task_log), "Should log item creation"


def test_send_email_with_all_params():
    """Test email endpoint passes all parameters to background task."""
    response = client.post("/send-email?to=dev@test.com&subject=Hello&body=Welcome!")
    assert response.status_code == 200
    data = response.json()
    assert data["to"] == "dev@test.com"

    assert len(task_log) == 1, "Should have 1 log entry"
    assert "dev@test.com" in task_log[0], "Should include recipient"
    assert "Hello" in task_log[0], "Should include subject"
    assert "Welcome!" in task_log[0], "Should include body"


def test_send_email_default_body():
    """Test email endpoint uses default body when not provided."""
    response = client.post("/send-email?to=dev@test.com&subject=Test")
    assert response.status_code == 200

    assert len(task_log) == 1, "Should have 1 log entry"
    assert "No body" in task_log[0], "Should use default body"
