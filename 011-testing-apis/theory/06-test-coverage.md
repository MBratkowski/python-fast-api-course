# Test Coverage

## Why This Matters

Test coverage tells you which lines of code are executed during tests. It's like Xcode's code coverage (iOS), JaCoCo (Android), or lcov (Dart) — a tool to find untested code paths.

**Important:** 100% coverage doesn't mean perfect tests. But 40% coverage definitely means you have gaps.

## Installing pytest-cov

```bash
pip install pytest-cov
```

## Running with Coverage

```bash
# Basic coverage report
pytest --cov=src

# With missing lines
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html

# Both terminal and HTML
pytest --cov=src --cov-report=term-missing --cov-report=html
```

**Output:**

```bash
$ pytest --cov=src --cov-report=term-missing

---------- coverage: platform darwin, python 3.12 ----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/api/users.py           45      8    82%   34-38, 52
src/services/user.py       67     12    82%   89-95, 103-106
src/models/user.py         23      0   100%
-----------------------------------------------------
TOTAL                     135     20    85%
```

**Mobile Parallel:**

| Platform | Coverage Tool |
|----------|--------------|
| **iOS** | Xcode code coverage (Cmd+9 → Coverage) |
| **Android** | JaCoCo (Gradle task: `./gradlew jacocoTestReport`) |
| **Flutter** | lcov (`flutter test --coverage`) |
| **Python** | pytest-cov (`pytest --cov`) |

## HTML Coverage Report

The HTML report is interactive and shows exactly which lines are missing:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

**Features:**
- Color-coded lines (green = covered, red = missed)
- Click files to see line-by-line coverage
- Branch coverage for if/else statements
- Sort by coverage percentage

## Configuration

Add coverage settings to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/conftest.py",
    "*/__init__.py",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

Now just run `pytest` and get coverage automatically.

## What to Measure

**Include:**
- API endpoints
- Business logic (services)
- Data models with methods
- Utility functions
- Validation logic

**Exclude:**
- Test files (`tests/*`)
- Configuration files
- Database migrations
- `__init__.py` files
- Development scripts

## Aiming for Meaningful Coverage

**Don't chase 100%:**
```python
# This isn't worth testing
def __repr__(self):
    return f"<User {self.id}: {self.name}>"

# Mark as no cover
def __repr__(self):  # pragma: no cover
    return f"<User {self.id}: {self.name}>"
```

**Do test critical paths:**
```python
# ✅ Test this: authentication logic
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# ✅ Test this: authorization logic
def can_edit_post(user: User, post: Post) -> bool:
    return user.id == post.author_id or user.is_admin

# ✅ Test this: business logic
def calculate_discount(total: float, user_tier: str) -> float:
    if user_tier == "premium":
        return total * 0.15
    elif user_tier == "plus":
        return total * 0.10
    return 0
```

**Target: 80-90% coverage** for critical code.

## Testing CRUD Operations Systematically

For each endpoint, test these cases:

**CREATE (POST):**
- ✅ Happy path: valid data → 201
- ✅ Invalid data → 422
- ✅ Duplicate → 409
- ✅ Unauthorized → 401

**READ (GET):**
- ✅ Found → 200
- ✅ Not found → 404
- ✅ Unauthorized → 401
- ✅ List with pagination

**UPDATE (PUT/PATCH):**
- ✅ Happy path → 200
- ✅ Not found → 404
- ✅ Invalid data → 422
- ✅ Unauthorized → 401
- ✅ Forbidden (not owner) → 403

**DELETE:**
- ✅ Happy path → 204
- ✅ Not found → 404
- ✅ Unauthorized → 401
- ✅ Forbidden (not owner) → 403

Example:

```python
# tests/test_api/test_posts.py

def test_create_post_success(auth_client):
    """Test creating post with valid data."""
    response = auth_client.post("/posts", json={
        "title": "My Post",
        "content": "Content here"
    })
    assert response.status_code == 201

def test_create_post_invalid_data(auth_client):
    """Test creating post with missing title."""
    response = auth_client.post("/posts", json={
        "content": "Content without title"
    })
    assert response.status_code == 422

def test_get_post_success(auth_client, sample_post):
    """Test getting existing post."""
    response = auth_client.get(f"/posts/{sample_post.id}")
    assert response.status_code == 200
    assert response.json()["title"] == sample_post.title

def test_get_post_not_found(auth_client):
    """Test getting non-existent post."""
    response = auth_client.get("/posts/999999")
    assert response.status_code == 404

def test_update_post_success(auth_client, sample_post):
    """Test updating own post."""
    response = auth_client.put(f"/posts/{sample_post.id}", json={
        "title": "Updated Title",
        "content": "Updated content"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_update_post_not_owner(auth_client, other_user_post):
    """Test updating someone else's post."""
    response = auth_client.put(f"/posts/{other_user_post.id}", json={
        "title": "Hacked",
        "content": "Hacked"
    })
    assert response.status_code == 403

def test_delete_post_success(auth_client, sample_post):
    """Test deleting own post."""
    response = auth_client.delete(f"/posts/{sample_post.id}")
    assert response.status_code == 204

def test_delete_post_not_owner(auth_client, other_user_post):
    """Test deleting someone else's post."""
    response = auth_client.delete(f"/posts/{other_user_post.id}")
    assert response.status_code == 403
```

This systematic approach catches authorization bugs, validation issues, and edge cases.

## Branch Coverage

Coverage tools track if both branches of if/else are tested:

```python
def calculate_price(quantity: int, is_premium: bool) -> float:
    """Calculate price with premium discount."""
    base_price = quantity * 10.0

    if is_premium:
        return base_price * 0.9  # 10% discount
    else:
        return base_price

# ============= Tests =============

def test_calculate_price_premium():
    """Test premium pricing."""
    price = calculate_price(5, is_premium=True)
    assert price == 45.0  # Covers if branch

def test_calculate_price_regular():
    """Test regular pricing."""
    price = calculate_price(5, is_premium=False)
    assert price == 50.0  # Covers else branch
```

Without both tests, branch coverage would be 50%.

## Finding Gaps with Coverage

Run coverage and look for patterns:

```bash
$ pytest --cov=src --cov-report=term-missing

Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/api/posts.py           45      8    82%   67-72, 89
```

**Missing lines 67-72:** Error handling for database errors.
**Missing line 89:** Admin-only endpoint.

Write tests for those cases:

```python
def test_create_post_database_error(auth_client, monkeypatch):
    """Test handling database errors."""
    def mock_add(*args):
        raise SQLAlchemyError("Database connection failed")

    monkeypatch.setattr("services.post_service.create_post", mock_add)

    response = auth_client.post("/posts", json={"title": "Test"})
    assert response.status_code == 500

def test_delete_all_posts_admin_only(auth_client, admin_client):
    """Test admin-only endpoint."""
    # Regular user
    response = auth_client.delete("/posts/all")
    assert response.status_code == 403

    # Admin user
    response = admin_client.delete("/posts/all")
    assert response.status_code == 204
```

## Continuous Integration

Add coverage checks to CI:

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Fails if coverage drops below 80%
```

## Key Takeaways

1. **pytest-cov** measures code coverage
2. **Run with**: `pytest --cov=src --cov-report=term-missing --cov-report=html`
3. **HTML report** shows line-by-line coverage (interactive)
4. **Configure in pyproject.toml** for automatic coverage
5. **Exclude** test files, migrations, config from coverage
6. **Target 80-90%** coverage for critical code
7. **Test CRUD systematically**: happy path, errors, auth, validation
8. **Branch coverage** ensures both if/else paths are tested
9. **Don't chase 100%** — focus on meaningful tests
10. **CI checks** enforce minimum coverage threshold
