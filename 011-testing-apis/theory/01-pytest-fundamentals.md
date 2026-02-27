# pytest Fundamentals

## Why This Matters

pytest is Python's most popular testing framework — like XCTest for iOS, JUnit for Android, or flutter_test for Dart. It's built into every professional Python project.

The core concept is universal: **arrange, act, assert**. You set up test data, execute the code, and verify the results. The syntax differs, but if you've written `XCTAssertEqual` or `assertEquals`, you already know how to think about tests.

**Key difference**: Python uses native `assert` statements. No special methods, no imports needed. Just `assert 2 + 2 == 4`.

## Test Discovery

pytest automatically finds and runs your tests. No decorators, no registration.

**Rules:**
- Test files must start with `test_` or end with `_test.py`
- Test functions must start with `test_`
- Test classes must start with `Test` (optional, rarely used)

```python
# test_calculator.py — pytest finds this automatically

def test_addition():
    """Test that addition works."""
    result = 2 + 2
    assert result == 4

def test_subtraction():
    """Test that subtraction works."""
    result = 10 - 3
    assert result == 7

# This won't run (doesn't start with test_)
def helper_function():
    return 42
```

**Comparison to Mobile:**

| Platform | Test Discovery |
|----------|---------------|
| **Swift (XCTest)** | Methods starting with `test` in `XCTestCase` subclasses |
| **Kotlin (JUnit)** | Methods with `@Test` annotation |
| **Dart (flutter_test)** | Calls to `test()` function |
| **Python (pytest)** | Functions starting with `test_` |

## Native Assertions

pytest uses Python's built-in `assert` statement. When an assertion fails, pytest shows detailed context.

```python
def test_user_creation():
    """Test creating a user object."""
    user = {"id": 1, "name": "Alice", "email": "alice@example.com"}

    assert user["id"] == 1
    assert user["name"] == "Alice"
    assert user["email"] == "alice@example.com"

def test_list_operations():
    """Test list contains expected items."""
    items = [1, 2, 3, 4, 5]

    assert 3 in items
    assert len(items) == 5
    assert items[0] == 1

def test_error_handling():
    """Test that function raises expected exception."""
    import pytest

    def divide(a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    # Verify exception is raised
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

**Assertion Comparison:**

| Check | Swift (XCTest) | Kotlin (JUnit) | Dart (flutter_test) | Python (pytest) |
|-------|----------------|----------------|---------------------|-----------------|
| Equality | `XCTAssertEqual(a, b)` | `assertEquals(a, b)` | `expect(a, b)` | `assert a == b` |
| Not equal | `XCTAssertNotEqual(a, b)` | `assertNotEquals(a, b)` | `expect(a, isNot(b))` | `assert a != b` |
| True | `XCTAssertTrue(x)` | `assertTrue(x)` | `expect(x, isTrue)` | `assert x` |
| Contains | `XCTAssert(list.contains(x))` | `assertTrue(list.contains(x))` | `expect(list, contains(x))` | `assert x in list` |
| Exception | `XCTAssertThrowsError` | `assertThrows` | `expect(..., throwsA)` | `with pytest.raises(...)` |

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py -v

# Run specific test function
pytest tests/test_api.py::test_create_user -v

# Run tests matching pattern
pytest -k "create" -v  # Runs all tests with "create" in name

# Run with output (print statements)
pytest -s

# Stop on first failure
pytest -x

# Show locals on failure
pytest -l
```

## Test Output

pytest provides clear, readable output:

```bash
$ pytest -v

tests/test_calculator.py::test_addition PASSED                [ 50%]
tests/test_calculator.py::test_subtraction PASSED             [100%]

======================== 2 passed in 0.01s =========================
```

When a test fails, pytest shows exactly what went wrong:

```bash
$ pytest -v

tests/test_calculator.py::test_addition FAILED                [ 50%]

=========================== FAILURES ===========================
________________________ test_addition _________________________

    def test_addition():
        result = 2 + 2
>       assert result == 5
E       assert 4 == 5

tests/test_calculator.py:4: AssertionError
```

## Organizing Tests

**Project structure:**

```
project/
├── src/
│   ├── api/
│   │   └── users.py
│   └── services/
│       └── user_service.py
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_api/
│   │   └── test_users.py    # Test API endpoints
│   └── test_services/
│       └── test_user_service.py  # Test business logic
└── pytest.ini               # pytest configuration
```

**Best practices:**
- Mirror your source structure in tests (`src/api/users.py` → `tests/test_api/test_users.py`)
- One test file per source file
- Group related tests in the same file
- Use descriptive test names: `test_create_user_success`, `test_create_user_duplicate_email`

## Example: Testing a Simple Function

```python
# src/utils/validator.py
def validate_email(email: str) -> bool:
    """Check if email is valid."""
    if not email or "@" not in email:
        return False
    local, domain = email.split("@", 1)
    return len(local) > 0 and len(domain) > 0 and "." in domain

# tests/test_utils/test_validator.py
from src.utils.validator import validate_email

def test_validate_email_valid():
    """Test valid email passes validation."""
    assert validate_email("alice@example.com") is True

def test_validate_email_no_at_sign():
    """Test email without @ is invalid."""
    assert validate_email("alice.example.com") is False

def test_validate_email_empty():
    """Test empty email is invalid."""
    assert validate_email("") is False

def test_validate_email_no_domain():
    """Test email without domain is invalid."""
    assert validate_email("alice@") is False

def test_validate_email_no_tld():
    """Test email without TLD is invalid."""
    assert validate_email("alice@example") is False
```

## Key Takeaways

1. **Test discovery**: Name files and functions with `test_` prefix
2. **Native assertions**: Use Python's `assert` statement (no special methods)
3. **Run tests**: Use `pytest -v` for verbose output
4. **Test structure**: Mirror source code structure in tests directory
5. **Test naming**: Use descriptive names that explain what's being tested
6. **Isolation**: Each test should be independent (no shared state)
7. **Arrange-Act-Assert**: Same pattern you use in mobile testing
