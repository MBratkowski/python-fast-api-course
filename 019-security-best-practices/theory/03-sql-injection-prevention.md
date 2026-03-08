# SQL Injection Prevention

## Why This Matters

On mobile, you interact with local databases through safe abstractions -- Core Data on iOS, Room on Android. These ORMs generate parameterized queries automatically, so you rarely think about SQL injection. But on the server, a single mistake -- using Python string formatting in a SQL query -- can let an attacker read your entire database, modify data, or even delete tables.

SQL injection has been a top vulnerability for over 20 years. It is devastatingly simple: if user input is concatenated into a SQL string, the attacker can alter the query's meaning. The good news: SQLAlchemy prevents this by default when you use it correctly. The bad news: it is easy to bypass that protection with raw SQL and f-strings.

## How SQL Injection Works

SQL injection happens when user input is directly embedded in a SQL query string:

```python
# VULNERABLE: String formatting in SQL
def get_user_by_username(username: str, db: Session):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = db.execute(text(query))
    return result.fetchone()
```

### Normal Usage

Input: `alice`

Generated query:
```sql
SELECT * FROM users WHERE username = 'alice'
```

This works fine. But what if the attacker sends a crafted input?

### Attack: Reading All Users

Input: `' OR '1'='1`

Generated query:
```sql
SELECT * FROM users WHERE username = '' OR '1'='1'
```

The `OR '1'='1'` clause is always true, so this returns **every user in the table**.

### Attack: Dropping a Table

Input: `'; DROP TABLE users; --`

Generated query:
```sql
SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
```

This executes two statements: the SELECT (returning nothing) and `DROP TABLE users` (destroying your data). The `--` comments out the trailing quote.

### Attack: Extracting Data

Input: `' UNION SELECT password_hash, email FROM users --`

Generated query:
```sql
SELECT * FROM users WHERE username = '' UNION SELECT password_hash, email FROM users --'
```

The UNION combines results from both queries, leaking password hashes and emails.

## Why SQLAlchemy Is Safe by Default

When you use SQLAlchemy's ORM or expression language, queries are automatically parameterized:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

# SAFE: SQLAlchemy parameterizes this automatically
def get_user_by_username(username: str, db: Session):
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalar_one_or_none()
```

What SQLAlchemy actually sends to the database:

```sql
SELECT users.id, users.username, users.email
FROM users
WHERE users.username = $1
-- Parameter: ('alice',)
```

The user input is sent as a separate parameter, not embedded in the SQL string. The database treats it as a literal value, never as SQL code. Even if the input contains SQL syntax like `' OR '1'='1`, it is treated as the literal string `' OR '1'='1`.

## The Danger of Raw SQL

SQLAlchemy does allow raw SQL, but you must use parameters:

### VULNERABLE: f-strings in text()

```python
from sqlalchemy import text

# NEVER DO THIS
def search_users(search_term: str, db: Session):
    # f-string embeds user input directly in SQL
    query = text(f"SELECT * FROM users WHERE username LIKE '%{search_term}%'")
    return db.execute(query).fetchall()
```

### SAFE: Bound Parameters with text()

```python
from sqlalchemy import text

# ALWAYS DO THIS when using raw SQL
def search_users(search_term: str, db: Session):
    query = text("SELECT * FROM users WHERE username LIKE :pattern")
    return db.execute(
        query,
        {"pattern": f"%{search_term}%"},
    ).fetchall()
```

The `:pattern` syntax creates a named parameter. SQLAlchemy sends the value separately from the query, making injection impossible.

### SAFE: SQLAlchemy Expression Language

```python
from sqlalchemy import select

# Best approach: use the expression language
def search_users(search_term: str, db: Session):
    stmt = select(User).where(User.username.contains(search_term))
    return db.execute(stmt).scalars().all()
```

## Common Vulnerable Patterns

### Pattern 1: Dynamic Column Names

```python
# VULNERABLE: Column name from user input
def sort_users(sort_by: str, db: Session):
    query = text(f"SELECT * FROM users ORDER BY {sort_by}")
    return db.execute(query).fetchall()
    # Attack: sort_by = "1; DROP TABLE users; --"
```

```python
# SAFE: Whitelist allowed columns
ALLOWED_SORT_COLUMNS = {"username", "email", "created_at"}

def sort_users(sort_by: str, db: Session):
    if sort_by not in ALLOWED_SORT_COLUMNS:
        raise HTTPException(400, f"Cannot sort by '{sort_by}'")
    # Safe because sort_by is from a known whitelist
    stmt = select(User).order_by(getattr(User, sort_by))
    return db.execute(stmt).scalars().all()
```

### Pattern 2: Dynamic Table Names

```python
# VULNERABLE: Table name from user input
def get_records(table_name: str, db: Session):
    query = text(f"SELECT * FROM {table_name}")
    return db.execute(query).fetchall()
```

**You cannot parameterize table or column names** -- parameters only work for values. Use a whitelist:

```python
ALLOWED_TABLES = {"users", "posts", "comments"}

def get_records(table_name: str, db: Session):
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(400, "Invalid table")
    # Use SQLAlchemy's Table or model mapping instead
    ...
```

### Pattern 3: IN Clauses

```python
# VULNERABLE: Building IN clause with f-string
def get_users_by_ids(ids: list[int], db: Session):
    id_str = ",".join(str(i) for i in ids)
    query = text(f"SELECT * FROM users WHERE id IN ({id_str})")
    return db.execute(query).fetchall()
```

```python
# SAFE: Use SQLAlchemy's in_() method
def get_users_by_ids(ids: list[int], db: Session):
    stmt = select(User).where(User.id.in_(ids))
    return db.execute(stmt).scalars().all()
```

## The Golden Rules

1. **Never use f-strings, `.format()`, or `%` in SQL queries**
2. **Always use SQLAlchemy's ORM or expression language** for queries
3. **When raw SQL is necessary, always use bound parameters** (`:name` syntax with `text()`)
4. **Whitelist dynamic column/table names** -- they cannot be parameterized
5. **Use Pydantic validators as defense-in-depth** -- reject suspicious input before it reaches your queries

## Testing for SQL Injection

You can verify your endpoints are not vulnerable by sending SQL injection payloads in tests:

```python
def test_login_not_vulnerable_to_sql_injection(client: TestClient):
    """SQL injection in username should not bypass authentication."""
    response = client.post("/auth/login", data={
        "username": "' OR '1'='1",
        "password": "anything",
    })
    # Should fail authentication, not return all users
    assert response.status_code == 401
```

## Key Takeaways

1. **SQL injection works by embedding user input in SQL strings** -- the attacker adds SQL syntax that changes the query's meaning
2. **SQLAlchemy prevents injection by default** when you use `select()`, `where()`, `in_()`, etc.
3. **The vulnerability appears with raw SQL** -- f-strings, `.format()`, or `%` in `text()` queries
4. **Use `:parameter` syntax** with `text()` when raw SQL is necessary
5. **Column and table names cannot be parameterized** -- always whitelist them
6. **Defense-in-depth:** validate input with Pydantic AND use parameterized queries
