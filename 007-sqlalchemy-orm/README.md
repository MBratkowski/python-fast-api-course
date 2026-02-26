# Module 007: SQLAlchemy ORM

## Why This Module?

Writing raw SQL is tedious and error-prone. SQLAlchemy lets you work with Python objects instead of SQL strings - like Core Data or Room, but for the server.

## What You'll Learn

- SQLAlchemy models
- Relationships (foreign keys)
- Querying with ORM
- Migrations with Alembic
- Async SQLAlchemy
- Session management

## Topics

### Theory
1. ORM Concepts
2. Defining Models
3. Relationships (relationship(), ForeignKey)
4. CRUD with Session
5. Async SQLAlchemy Setup
6. Alembic Migrations

### Exercises
- Create models with relationships
- Perform CRUD operations
- Write complex queries

### Project
Build the data layer for a task management app.

## Examples

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
```
