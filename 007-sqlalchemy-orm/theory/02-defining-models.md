# Defining SQLAlchemy Models

## Why This Matters

Defining a SQLAlchemy model is like creating a Room `@Entity` in Android or a Core Data entity in iOS - but in pure Python code with type hints. The model defines your database schema AND gives you a Python class to work with.

## SQLAlchemy 2.0 Pattern

SQLAlchemy 2.0 introduced a modern, type-safe way to define models using **`Mapped`** and **`mapped_column`**.

### Basic Model Structure

```python
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Base class for all models
class Base(DeclarativeBase):
    pass

# Define a model
class User(Base):
    __tablename__ = "users"  # Database table name

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # String fields with constraints
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    # Boolean with default
    is_active: Mapped[bool] = mapped_column(default=True)
```

This creates a `users` table:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL
);
```

## Breaking Down the Syntax

### 1. The Base Class

```python
class Base(DeclarativeBase):
    pass
```

**DeclarativeBase** is the foundation. All your models inherit from this base class.

In mobile terms:
- Core Data: This is like your managed object model
- Room: This is like the database abstract class

### 2. Table Name

```python
__tablename__ = "users"
```

**Required** - tells SQLAlchemy what the database table is called. By convention:
- Use lowercase
- Use plural nouns (`users`, not `user`)
- Use underscores for multi-word names (`blog_posts`, not `BlogPosts`)

### 3. Field Definition with `Mapped`

```python
username: Mapped[str] = mapped_column(String(50))
```

**`Mapped[type]`** tells Python (and your IDE) the field's type.

**`mapped_column(...)`** tells SQLAlchemy the database column properties.

This combines:
- **Python type hints** (for IDE autocomplete and mypy)
- **Database constraints** (for schema generation)

## Field Types

### Common Types

```python
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, Date
from datetime import datetime, date

class Article(Base):
    __tablename__ = "articles"

    # Integer (serial/autoincrement for primary keys)
    id: Mapped[int] = mapped_column(primary_key=True)

    # String with length limit
    title: Mapped[str] = mapped_column(String(200))

    # Text (no length limit)
    content: Mapped[str] = mapped_column(Text)

    # Boolean
    is_published: Mapped[bool] = mapped_column(default=False)

    # DateTime with default
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Date
    publish_date: Mapped[date] = mapped_column(Date, nullable=True)

    # Float
    rating: Mapped[float] = mapped_column(Float, default=0.0)
```

### String vs Text

```python
# String(N) - Use for fields with known max length
username: Mapped[str] = mapped_column(String(50))  # Max 50 chars
email: Mapped[str] = mapped_column(String(255))    # Max 255 chars

# Text - Use for long content (no length limit)
bio: Mapped[str] = mapped_column(Text)
article_body: Mapped[str] = mapped_column(Text)
```

In PostgreSQL:
- `String(N)` → `VARCHAR(N)`
- `Text` → `TEXT`

## Nullable Fields

By default, fields are **NOT NULL**. To allow NULL values:

```python
# Required field (NOT NULL)
username: Mapped[str] = mapped_column(String(50))

# Optional field (nullable)
bio: Mapped[str | None] = mapped_column(Text, nullable=True)
middle_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
```

The `str | None` type hint tells Python the field can be None.

The `nullable=True` tells SQLAlchemy to allow NULL in the database.

## Default Values

```python
# Default in Python
is_active: Mapped[bool] = mapped_column(default=True)

# Default using function (called each time)
created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# Server-side default (in SQL)
from sqlalchemy import func
updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

**`default`** vs **`server_default`**:
- **`default`**: Python function, runs in your app
- **`server_default`**: SQL expression, runs in database

For timestamps, `default=datetime.utcnow` is simpler and works fine.

## Constraints

### Unique Constraint

```python
# Single field unique
username: Mapped[str] = mapped_column(String(50), unique=True)

# Multiple fields unique together
from sqlalchemy import UniqueConstraint

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    room_id: Mapped[int]
    date: Mapped[date]

    # Can't book same room twice on same date
    __table_args__ = (
        UniqueConstraint('room_id', 'date', name='uq_room_date'),
    )
```

### Index

Indexes speed up queries:

```python
# Single field index
username: Mapped[str] = mapped_column(String(50), index=True)

# Compound index
from sqlalchemy import Index

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int]
    created_at: Mapped[datetime]

    # Index for "get author's recent posts" query
    __table_args__ = (
        Index('idx_author_created', 'author_id', 'created_at'),
    )
```

## Complete Model Example

```python
from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    """User account model."""
    __tablename__ = "users"

    # Primary key (auto-increment)
    id: Mapped[int] = mapped_column(primary_key=True)

    # Required string fields
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Optional text field
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Boolean with default
    is_active: Mapped[bool] = mapped_column(default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # String representation for debugging
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
```

This generates:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    bio TEXT,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

## Comparing to SQL CREATE TABLE

Understanding the mapping helps when you need to debug:

| SQLAlchemy | SQL |
|------------|-----|
| `id: Mapped[int] = mapped_column(primary_key=True)` | `id SERIAL PRIMARY KEY` |
| `username: Mapped[str] = mapped_column(String(50))` | `username VARCHAR(50) NOT NULL` |
| `bio: Mapped[str \| None] = mapped_column(Text, nullable=True)` | `bio TEXT` |
| `is_active: Mapped[bool] = mapped_column(default=True)` | `is_active BOOLEAN DEFAULT true NOT NULL` |
| `unique=True` | `UNIQUE` |
| `index=True` | `CREATE INDEX ...` |

## The `__repr__` Method

Always add a `__repr__` method for debugging:

```python
def __repr__(self) -> str:
    return f"<User(id={self.id}, username='{self.username}')>"
```

Without it, you see: `<User object at 0x7f8b8c0a3d90>`

With it, you see: `<User(id=1, username='alice')>`

## Key Takeaways

1. **Use `DeclarativeBase`** as the base class for all models
2. **`__tablename__`** is required - use lowercase plural names
3. **`Mapped[type]`** provides type hints for Python/IDE
4. **`mapped_column(...)`** defines database constraints
5. **`String(N)` for limited text, `Text` for unlimited**
6. **Fields are NOT NULL by default** - use `Mapped[type | None]` and `nullable=True` for optional fields
7. **Add indexes** to fields you'll search/filter by
8. **Always add `__repr__`** for better debugging
