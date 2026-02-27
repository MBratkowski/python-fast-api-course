# Module 011: Testing APIs

## Why This Module?

Test your API like you test mobile apps. Learn pytest, FastAPI's TestClient, and async testing patterns to write reliable, maintainable tests for your REST APIs.

## What You'll Learn

- pytest fundamentals (test discovery, assertions, running tests)
- TestClient for testing FastAPI endpoints
- Async testing with pytest-asyncio
- Fixtures and conftest patterns
- Mocking external dependencies
- Test coverage with pytest-cov
- Testing CRUD operations systematically

## Mobile Developer Context

You've written unit tests in Xcode (XCTest), Android Studio (JUnit), or Flutter (flutter_test). The concepts are identical — arrange, act, assert. The syntax changes, but the patterns stay the same.

**Testing Across Platforms:**

| Concept | Swift (XCTest) | Kotlin (JUnit) | Dart (flutter_test) | Python (pytest) |
|---------|----------------|----------------|---------------------|-----------------|
| Test file | `*Tests.swift` | `*Test.kt` | `*_test.dart` | `test_*.py` |
| Test function | `func testSomething()` | `@Test fun testSomething()` | `test('something', ...)` | `def test_something():` |
| Assertion | `XCTAssertEqual(a, b)` | `assertEquals(a, b)` | `expect(a, b)` | `assert a == b` |
| Setup/Teardown | `setUp()` / `tearDown()` | `@BeforeEach` / `@AfterEach` | `setUp()` / `tearDown()` | `@pytest.fixture` |
| Mock | OCMock / swift-mock | Mockito / MockK | mocktail | unittest.mock |
| Run tests | Cmd+U | Gradle test | `flutter test` | `pytest -v` |

**Key Differences:**
- Python uses native `assert` statements (no special assertion methods)
- pytest discovers tests automatically (`test_` prefix, no decorators needed)
- FastAPI provides `TestClient` for testing endpoints without running a server
- Fixtures replace setUp/tearDown with more powerful dependency injection

## Topics

### Theory
1. pytest Fundamentals
2. TestClient Basics
3. Async Testing with pytest-asyncio
4. Fixtures and conftest.py
5. Mocking Strategies
6. Test Coverage

### Exercises
1. Basic API Tests with TestClient
2. Fixtures and Database Testing
3. Mocking External APIs

### Project
Comprehensive test suite for a CRUD API with fixtures, mocking, and async tests.

## Example

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

# Create test client
client = TestClient(app)

def test_read_item():
    """Test reading an item."""
    # Act
    response = client.get("/items/42")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "name": "Item 42"}

def test_item_not_found():
    """Test 404 for non-existent item."""
    response = client.get("/items/999")
    assert response.status_code == 404
```

## Quick Assessment

Before starting this module, ask yourself:
- Have you written unit tests in Swift, Kotlin, or Dart?
- Do you understand the arrange-act-assert pattern?
- Have you used mock objects to isolate tests?

If yes, you're ready. The syntax is new, but the concepts are familiar.

## Time Estimate

6-8 hours total:
- Theory: 2-3 hours
- Exercises: 2-3 hours
- Project: 2-3 hours

## Key Differences from Mobile Testing

1. **No UI testing**: You're testing HTTP endpoints, not UI components
2. **TestClient doesn't require a server**: Tests run in-process (like iOS unit tests)
3. **Database isolation**: Use fixtures to create/rollback test databases
4. **Async patterns**: FastAPI is async, so you'll test async code
5. **Native assertions**: Use Python's `assert` instead of XCTAssert/assertEquals/expect
