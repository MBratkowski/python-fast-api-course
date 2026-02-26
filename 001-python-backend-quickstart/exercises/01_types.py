"""
Exercise 1: Type Hints Practice

Complete the functions below with proper type hints.
Run: pytest 001-python-backend-quickstart/exercises/01_types.py -v
"""


# Exercise 1.1: Basic types
# Add type hints to this function
def greet(name, greeting="Hello"):
    """Return a greeting message."""
    return f"{greeting}, {name}!"


# Exercise 1.2: Optional types
# This function might return None - add proper type hints
def find_by_id(items, item_id):
    """Find item by ID, return None if not found."""
    for item in items:
        if item.get("id") == item_id:
            return item
    return None


# Exercise 1.3: List and Dict types
# Add type hints for collections
def get_user_emails(users):
    """Extract emails from list of user dicts."""
    return [user["email"] for user in users if "email" in user]


# Exercise 1.4: Complex return type
# This returns either a user dict or an error dict
def validate_user(name, email):
    """Validate user data, return user or error."""
    if not name:
        return {"error": "Name is required"}
    if "@" not in email:
        return {"error": "Invalid email"}
    return {"name": name, "email": email}


# Exercise 1.5: Callable type
# Add type hint for a function parameter
def apply_to_all(items, transform):
    """Apply transform function to all items."""
    return [transform(item) for item in items]


# ============= TESTS =============
# Run with: pytest 001-python-backend-quickstart/exercises/01_types.py -v

def test_greet():
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob", "Hi") == "Hi, Bob!"


def test_find_by_id():
    items = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    assert find_by_id(items, 1) == {"id": 1, "name": "A"}
    assert find_by_id(items, 99) is None


def test_get_user_emails():
    users = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob"},
        {"name": "Charlie", "email": "charlie@example.com"},
    ]
    assert get_user_emails(users) == ["alice@example.com", "charlie@example.com"]


def test_validate_user():
    assert validate_user("Alice", "alice@example.com") == {
        "name": "Alice",
        "email": "alice@example.com"
    }
    assert "error" in validate_user("", "alice@example.com")
    assert "error" in validate_user("Alice", "invalid")


def test_apply_to_all():
    result = apply_to_all([1, 2, 3], lambda x: x * 2)
    assert result == [2, 4, 6]
