# ORM Concepts

## Why This Matters

In mobile development, you use **Core Data** (iOS), **Room** (Android), or other frameworks to work with databases through objects instead of SQL strings. SQLAlchemy is Python's equivalent - the industry-standard ORM that lets you map database tables to Python classes.

Instead of writing `"SELECT * FROM users WHERE id = ?"`, you work with Python objects: `session.get(User, user_id)`.

## What is an ORM?

**ORM = Object-Relational Mapping**

It's a layer that translates between two worlds:
- **Relational databases** (tables, rows, columns, SQL)
- **Object-oriented code** (classes, objects, attributes, Python)

The mapping works like this:

| Database Concept | Python Concept |
|------------------|----------------|
| Table            | Class          |
| Row              | Object instance |
| Column           | Attribute      |
| Foreign Key      | Reference/relationship |
| SQL query        | Method call    |

## How SQLAlchemy Works

```python
# Define a model (class)
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))

# Create a user (object)
user = User(username="alice", email="alice@example.com")
session.add(user)
await session.commit()

# Query users (Python code, not SQL)
result = await session.execute(
    select(User).where(User.username == "alice")
)
user = result.scalar_one_or_none()

# Access attributes (not SQL columns)
print(user.email)  # alice@example.com
```

Behind the scenes, SQLAlchemy generates and executes SQL:

```sql
INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com');
SELECT * FROM users WHERE username = 'alice';
```

## Benefits of Using an ORM

### 1. Type Safety
With type hints, your editor catches errors before runtime:

```python
# Editor knows user.email is a string
user.email = "new@example.com"  # ✅ Works

# Editor warns about type mismatch
user.email = 123  # ❌ Type error
```

### 2. No SQL Injection
Parameters are automatically escaped:

```python
# SAFE - SQLAlchemy handles escaping
username = user_input  # Could be "'; DROP TABLE users; --"
result = await session.execute(
    select(User).where(User.username == username)
)

# SQLAlchemy generates safe parameterized query:
# SELECT * FROM users WHERE username = $1
# With parameter: "'; DROP TABLE users; --"
```

### 3. Database-Agnostic Code
Switch databases without rewriting queries:

```python
# Same code works with PostgreSQL, MySQL, SQLite
user = await session.get(User, user_id)

# SQLAlchemy generates database-specific SQL automatically
```

### 4. Migration Support
SQLAlchemy tracks your models and can auto-generate schema changes:

```bash
# Change your model
class User(Base):
    # Add new field
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

# Alembic auto-generates migration
alembic revision --autogenerate -m "add user bio"

# Apply to database
alembic upgrade head
```

## Tradeoffs to Understand

### 1. Performance Overhead
ORMs add abstraction layers. Complex queries might be slower than hand-optimized SQL.

**When to optimize:**
- Most queries: Use ORM (developer time matters more)
- Critical hot paths: Use raw SQL if profiling shows issues
- Reports/analytics: Raw SQL is often clearer

### 2. Abstraction Leaks
You still need to understand SQL for:
- **N+1 query problems** (loading related data inefficiently)
- **Complex joins** (when to use `selectinload` vs `joinedload`)
- **Performance tuning** (indexes, query optimization)

The ORM doesn't hide SQL - it generates it. You need to know what SQL is being generated.

```python
# Enable SQL logging to see what's happening
engine = create_async_engine(DATABASE_URL, echo=True)

# Now you'll see all generated SQL queries
```

## Mobile Development Analogies

If you've used database frameworks in mobile development:

| Mobile Framework | SQLAlchemy Equivalent |
|------------------|----------------------|
| **Core Data** (iOS) |  |
| NSManagedObject | SQLAlchemy model class |
| NSManagedObjectContext | SQLAlchemy session |
| Core Data stack | SQLAlchemy engine |
| NSFetchRequest | SQLAlchemy select() |
| Core Data model editor | Python model definitions |
| **Room** (Android) |  |
| @Entity class | SQLAlchemy model |
| @Dao interface | SQLAlchemy session methods |
| RoomDatabase | SQLAlchemy engine |
| @Query methods | SQLAlchemy select() |
| **Realm** (Mobile) |  |
| RealmObject | SQLAlchemy model |
| Realm instance | SQLAlchemy session |

## When to Use an ORM

**Use SQLAlchemy when:**
- ✅ Building CRUD APIs (most backend work)
- ✅ You want type safety and IDE support
- ✅ You need migrations and schema versioning
- ✅ Your team knows Python better than SQL
- ✅ You're building a new application

**Consider raw SQL when:**
- ⚠️ Generating reports with complex aggregations
- ⚠️ Performance-critical queries that are slow in ORM
- ⚠️ You're working with a legacy database you can't change

For FastAPI applications, **SQLAlchemy is the standard choice**. It integrates seamlessly and handles 95% of database needs.

## Key Takeaways

1. **ORM maps database tables to Python classes** - work with objects, not SQL strings
2. **SQLAlchemy is Python's standard ORM** - equivalent to Core Data, Room, or Realm
3. **Benefits: type safety, SQL injection prevention, database portability, migrations**
4. **Tradeoff: abstraction overhead** - you still need to understand SQL and watch for N+1 queries
5. **Enable `echo=True` during development** - see what SQL is being generated
6. **For FastAPI apps, SQLAlchemy is the default choice**
