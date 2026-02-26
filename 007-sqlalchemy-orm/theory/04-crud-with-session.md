# CRUD Operations with SQLAlchemy Session

## Why This Matters

In mobile development, you interact with databases through a **context** or **manager**: `NSManagedObjectContext` in Core Data, `RoomDatabase` in Room. SQLAlchemy's equivalent is the **Session** - it tracks changes, manages transactions, and executes queries.

## What is a Session?

The **Session** is your interface to the database. It:
- Tracks changes to objects
- Queues database operations
- Manages transactions (commit/rollback)
- Maintains an identity map (one object per database row)

Think of it like a "unit of work" - you make changes to objects, then commit them all at once.

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def create_user(session: AsyncSession, username: str, email: str):
    # Create object
    user = User(username=username, email=email)

    # Add to session (queued, not yet in database)
    session.add(user)

    # Commit transaction (executes INSERT)
    await session.commit()

    # Refresh to get database-generated values
    await session.refresh(user)

    return user
```

## Create (INSERT)

### Adding a Single Object

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def create_user(session: AsyncSession) -> User:
    # Create model instance
    user = User(
        username="alice",
        email="alice@example.com",
        is_active=True
    )

    # Add to session
    session.add(user)

    # Commit to database
    await session.commit()

    # Refresh to get auto-generated ID
    await session.refresh(user)

    print(user.id)  # Now has an ID from database
    return user
```

**Steps:**
1. **Create object** - Python class instance
2. **`session.add(obj)`** - Queue for insertion
3. **`await session.commit()`** - Execute INSERT query
4. **`await session.refresh(obj)`** - Reload from database (gets ID, defaults, etc.)

### Adding Multiple Objects

```python
async def create_multiple_users(session: AsyncSession) -> list[User]:
    users = [
        User(username="alice", email="alice@example.com"),
        User(username="bob", email="bob@example.com"),
        User(username="charlie", email="charlie@example.com"),
    ]

    # Add all at once
    session.add_all(users)

    await session.commit()

    # Note: refresh not needed if you don't need IDs immediately
    return users
```

### Creating with Relationships

```python
async def create_user_with_posts(session: AsyncSession) -> User:
    user = User(username="alice", email="alice@example.com")

    # Create related objects
    post1 = Post(title="First Post", content="Hello world!", author=user)
    post2 = Post(title="Second Post", content="More content", author=user)

    # Only need to add the user - cascade handles posts
    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user
```

## Read (SELECT)

### Get by Primary Key

```python
async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    # Simple primary key lookup
    user = await session.get(User, user_id)
    return user  # None if not found
```

**`session.get(Model, pk)`** is the simplest way to fetch by primary key.

### Query with WHERE Clause

```python
from sqlalchemy import select

async def get_user_by_username(
    session: AsyncSession,
    username: str
) -> User | None:
    # Build query
    query = select(User).where(User.username == username)

    # Execute query
    result = await session.execute(query)

    # Get single result or None
    user = result.scalar_one_or_none()

    return user
```

**Query building with `select()`:**
- **`select(User)`** - SELECT * FROM users
- **`.where(User.username == username)`** - WHERE username = ?
- **`scalar_one_or_none()`** - Return single object or None

### Query Multiple Results

```python
async def list_active_users(session: AsyncSession) -> list[User]:
    query = select(User).where(User.is_active == True)
    result = await session.execute(query)

    # Get all results
    users = result.scalars().all()

    return users
```

### Query with Ordering and Limits

```python
async def get_recent_users(
    session: AsyncSession,
    limit: int = 10
) -> list[User]:
    query = (
        select(User)
        .where(User.is_active == True)
        .order_by(User.created_at.desc())
        .limit(limit)
    )

    result = await session.execute(query)
    return result.scalars().all()
```

### Result Extraction Methods

| Method | Returns | When to Use |
|--------|---------|-------------|
| **`scalar_one()`** | Single object | Expect exactly 1 result (raises if 0 or >1) |
| **`scalar_one_or_none()`** | Object or None | Expect 0 or 1 result (raises if >1) |
| **`scalars().all()`** | List of objects | Expect multiple results |
| **`scalars().first()`** | First object or None | Want first result only |

```python
# Expect exactly one
user = result.scalar_one()  # Raises if not found or multiple

# Expect zero or one
user = result.scalar_one_or_none()  # Returns None if not found

# Expect multiple
users = result.scalars().all()  # Returns [] if none found

# Want first only
user = result.scalars().first()  # Returns None if none found
```

## Update (UPDATE)

### Update by Modifying Object

```python
async def update_user_email(
    session: AsyncSession,
    user_id: int,
    new_email: str
) -> User | None:
    # Fetch user
    user = await session.get(User, user_id)

    if not user:
        return None

    # Modify attribute
    user.email = new_email

    # Commit changes (session tracks modifications)
    await session.commit()

    # Refresh to get updated timestamp, etc.
    await session.refresh(user)

    return user
```

**Key point:** SQLAlchemy tracks changes. You don't manually say "UPDATE this field" - just modify the object and commit.

### Update Multiple Fields

```python
async def update_user_profile(
    session: AsyncSession,
    user_id: int,
    username: str | None = None,
    email: str | None = None,
    is_active: bool | None = None,
) -> User | None:
    user = await session.get(User, user_id)

    if not user:
        return None

    # Update only provided fields
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if is_active is not None:
        user.is_active = is_active

    await session.commit()
    await session.refresh(user)

    return user
```

### Bulk Update (Without Loading Objects)

```python
from sqlalchemy import update

async def deactivate_old_users(session: AsyncSession, cutoff_date) -> int:
    # Build update statement
    stmt = (
        update(User)
        .where(User.created_at < cutoff_date)
        .values(is_active=False)
    )

    # Execute (returns number of rows updated)
    result = await session.execute(stmt)
    await session.commit()

    return result.rowcount
```

This is more efficient than loading objects and modifying them one by one.

## Delete (DELETE)

### Delete by Object

```python
async def delete_user(session: AsyncSession, user_id: int) -> bool:
    # Fetch user
    user = await session.get(User, user_id)

    if not user:
        return False

    # Delete object
    await session.delete(user)

    # Commit
    await session.commit()

    return True
```

**With cascade:** If `User.posts` has `cascade="all, delete-orphan"`, deleting the user automatically deletes all their posts.

### Bulk Delete (Without Loading Objects)

```python
from sqlalchemy import delete

async def delete_inactive_users(session: AsyncSession) -> int:
    stmt = delete(User).where(User.is_active == False)

    result = await session.execute(stmt)
    await session.commit()

    return result.rowcount
```

## Transaction Management

### What is a Transaction?

A **transaction** is a group of database operations that succeed or fail together. Think of it like a "save point" - either all changes are saved, or none are.

```python
async def transfer_credits(
    session: AsyncSession,
    from_user_id: int,
    to_user_id: int,
    amount: int
):
    try:
        # Both operations happen in same transaction
        from_user = await session.get(User, from_user_id)
        to_user = await session.get(User, to_user_id)

        from_user.credits -= amount
        to_user.credits += amount

        # Commit - both updates succeed together
        await session.commit()

    except Exception as e:
        # Rollback - neither update happens
        await session.rollback()
        raise e
```

If commit fails (e.g., constraint violation), **neither** user's credits change.

### Explicit Transaction with `begin()`

```python
async def create_user_with_profile(
    session: AsyncSession,
    username: str,
    email: str,
    bio: str
):
    async with session.begin():
        # All operations in this block are one transaction
        user = User(username=username, email=email)
        session.add(user)

        # Need user.id before creating profile
        await session.flush()  # Executes INSERT, gets ID, but doesn't commit

        profile = UserProfile(user_id=user.id, bio=bio)
        session.add(profile)

        # Transaction commits when context exits
        # If any exception, automatically rolls back
```

### Flushing vs Committing

| Operation | What It Does |
|-----------|--------------|
| **`await session.flush()`** | Executes pending SQL (INSERT/UPDATE/DELETE) but doesn't commit |
| **`await session.commit()`** | Executes pending SQL AND commits transaction |

**Use `flush()` when:**
- You need a database-generated ID before proceeding
- You want to validate constraints before committing
- You're doing multiple steps in one transaction

```python
async def create_post_with_comments(session: AsyncSession):
    # Create post
    post = Post(title="Hello", content="World")
    session.add(post)

    # Flush to get post.id (but don't commit yet)
    await session.flush()

    # Now we can use post.id
    comment1 = Comment(post_id=post.id, text="First!")
    comment2 = Comment(post_id=post.id, text="Great post")

    session.add_all([comment1, comment2])

    # Commit everything together
    await session.commit()
```

## Complete CRUD Example

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    """Example repository pattern for User CRUD."""

    async def create(self, session: AsyncSession, username: str, email: str) -> User:
        """Create new user."""
        user = User(username=username, email=email, is_active=True)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        """Get user by ID."""
        return await session.get(User, user_id)

    async def get_by_username(
        self,
        session: AsyncSession,
        username: str
    ) -> User | None:
        """Get user by username."""
        result = await session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """List active users with pagination."""
        result = await session.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()

    async def update(
        self,
        session: AsyncSession,
        user_id: int,
        **updates
    ) -> User | None:
        """Update user fields."""
        user = await session.get(User, user_id)

        if not user:
            return None

        for key, value in updates.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession, user_id: int) -> bool:
        """Delete user."""
        user = await session.get(User, user_id)

        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True
```

## Key Takeaways

1. **Session is your database interface** - tracks changes, manages transactions
2. **Create:** `session.add()` → `commit()` → `refresh()` to get generated values
3. **Read:** Use `session.get(Model, pk)` for primary keys, `select().where()` for queries
4. **Update:** Modify object attributes, then `commit()` - session tracks changes
5. **Delete:** `session.delete(obj)` → `commit()`
6. **Result extraction:** `scalar_one_or_none()` for single result, `scalars().all()` for multiple
7. **Transactions:** All operations between commits are atomic (all succeed or all fail)
8. **`flush()` vs `commit()`:** Flush executes SQL without committing, commit finalizes transaction
9. **Always handle exceptions** and rollback on errors to prevent partial updates
