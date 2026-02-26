# SQLAlchemy Relationships

## Why This Matters

In mobile development, you navigate between related objects: a User has Posts, a Post has Comments. In Core Data, you define relationships in the model editor. In Room, you use `@Relation`. SQLAlchemy uses `relationship()` to link models together, just like foreign keys link database tables.

## The Two Parts of a Relationship

Every relationship has **two sides**:

1. **Foreign Key** (database constraint) - tells PostgreSQL how tables connect
2. **Relationship** (Python navigation) - lets you access related objects in code

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))

    # Relationship - navigate from user to posts
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    # Foreign key - database constraint
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationship - navigate from post to user
    author: Mapped["User"] = relationship(back_populates="posts")
```

Now you can navigate in Python:

```python
user = await session.get(User, 1)
print(user.posts)  # List of Post objects

post = await session.get(Post, 1)
print(post.author)  # User object
```

## One-to-Many Relationship

**The most common relationship type.** One user has many posts.

```python
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))

    # "One" side - user has MANY posts
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)

    # "Many" side - post has ONE author
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
```

**Key points:**
- The **"many" side** has the foreign key column (`author_id`)
- The **"one" side** has a list type: `Mapped[list["Post"]]`
- The **"many" side** has a single object: `Mapped["User"]`
- **`back_populates`** links the two sides together

Usage:

```python
# Create user and posts
user = User(username="alice")
post1 = Post(title="Hello", content="...", author=user)
post2 = Post(title="World", content="...", author=user)

session.add(user)
await session.commit()

# Navigate relationship
print(user.posts)  # [<Post(id=1)>, <Post(id=2)>]
print(post1.author)  # <User(id=1, username='alice')>
```

## One-to-One Relationship

One user has one profile. Use `uselist=False` on the "one" side:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))

    # One-to-one - user has ONE profile (not a list)
    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[str] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Foreign key - profile belongs to one user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="profile")
```

**Key difference from one-to-many:**
- Use **`uselist=False`** (returns single object, not list)
- Add **`unique=True`** on the foreign key (enforces one-to-one in database)

Usage:

```python
user = User(username="alice")
profile = UserProfile(bio="Python developer", user=user)

session.add(user)
await session.commit()

# Navigate - returns single object, not list
print(user.profile)  # <UserProfile(id=1)>
print(profile.user)  # <User(id=1)>
```

## Many-to-Many Relationship

Students can enroll in multiple courses. Courses have multiple students.

Requires an **association table** (join table):

```python
from sqlalchemy import Table, Column, Integer, ForeignKey

# Association table (no model class needed)
student_courses = Table(
    "student_courses",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # Many-to-many - student has MANY courses
    courses: Mapped[list["Course"]] = relationship(
        secondary=student_courses,
        back_populates="students"
    )

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    # Many-to-many - course has MANY students
    students: Mapped[list["Student"]] = relationship(
        secondary=student_courses,
        back_populates="courses"
    )
```

**Key points:**
- **Association table** has two foreign keys (one to each side)
- Use **`secondary=student_courses`** in both relationships
- Both sides are **lists**: `Mapped[list[...]]`

Usage:

```python
# Create students and courses
alice = Student(name="Alice")
bob = Student(name="Bob")

python_course = Course(title="Python 101")
data_course = Course(title="Data Science")

# Enroll students
alice.courses.append(python_course)
alice.courses.append(data_course)
bob.courses.append(python_course)

session.add_all([alice, bob])
await session.commit()

# Navigate both directions
print(alice.courses)  # [<Course(title='Python 101')>, <Course(title='Data Science')>]
print(python_course.students)  # [<Student(name='Alice')>, <Student(name='Bob')>]
```

## Eager Loading (Preventing N+1 Queries)

**The N+1 problem** is when you accidentally trigger one query per related object:

```python
# Bad: N+1 queries (lazy loading)
users = await session.execute(select(User))
for user in users.scalars():  # 1 query: load all users
    print(user.posts)  # N queries: one per user! 💥
```

If you have 100 users, this runs **101 queries** (1 for users + 100 for posts).

### Solution: Eager Loading with `selectinload()`

```python
from sqlalchemy.orm import selectinload

# Good: 2 queries total (eager loading)
result = await session.execute(
    select(User).options(selectinload(User.posts))
)
users = result.scalars().all()

for user in users:
    print(user.posts)  # No additional queries! ✅
```

This runs **2 queries**:
1. `SELECT * FROM users`
2. `SELECT * FROM posts WHERE author_id IN (1, 2, 3, ...)`

### `selectinload()` vs `joinedload()`

| Strategy | When to Use | SQL Generated |
|----------|-------------|---------------|
| **`selectinload()`** | One-to-many, many-to-many | Separate queries with `IN` clause |
| **`joinedload()`** | Many-to-one, one-to-one | Single query with `JOIN` |

```python
from sqlalchemy.orm import selectinload, joinedload

# Load users with their posts (one-to-many)
result = await session.execute(
    select(User).options(selectinload(User.posts))
)

# Load posts with their author (many-to-one)
result = await session.execute(
    select(Post).options(joinedload(Post.author))
)
```

**Rule of thumb:**
- Loading collections? Use **`selectinload()`**
- Loading single objects? Use **`joinedload()`**

## The `cascade` Parameter

Controls what happens to related objects when parent is deleted:

```python
posts: Mapped[list["Post"]] = relationship(
    back_populates="author",
    cascade="all, delete-orphan"
)
```

**`cascade="all, delete-orphan"`** means:
- When user is deleted, delete all their posts
- When a post is removed from `user.posts`, delete it from database

```python
user = await session.get(User, 1)
await session.delete(user)
await session.commit()
# All of user's posts are also deleted 🗑️
```

Without cascade, you'd get a foreign key constraint error (posts still reference deleted user).

## Common cascade Options

| Cascade | What It Does |
|---------|--------------|
| `all, delete-orphan` | Delete related objects when parent deleted or relationship removed |
| `all` | Cascade all operations except orphan deletion |
| `delete` | Delete related objects when parent deleted |
| `save-update` | Save related objects when parent saved |
| (none) | Don't cascade - keep related objects |

For most one-to-many relationships, use **`cascade="all, delete-orphan"`**.

## Detecting Lazy Loading in Async Code

In async code, lazy loading raises an error:

```python
# This will FAIL in async
user = await session.get(User, 1)
print(user.posts)  # 💥 MissingGreenlet error
```

**Why?** Lazy loading tries to run a sync query in an async context.

**Solution:** Always use eager loading in async:

```python
# Correct async pattern
result = await session.execute(
    select(User)
    .where(User.id == 1)
    .options(selectinload(User.posts))
)
user = result.scalar_one()
print(user.posts)  # ✅ Works
```

### Development Tip: Use `lazy='raise'`

During development, make lazy loading fail immediately:

```python
posts: Mapped[list["Post"]] = relationship(
    back_populates="author",
    lazy='raise'  # Raises error if you forget eager loading
)
```

This catches lazy loading bugs early instead of in production.

## Complete Relationship Example

```python
from sqlalchemy import String, Text, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Many-to-many association table
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # One-to-many
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)

    # Many-to-one (post -> user)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

    # Many-to-many (post <-> tags)
    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts"
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Many-to-many (tag <-> posts)
    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags"
    )
```

## Key Takeaways

1. **Relationships have two parts:** foreign key (database) + relationship (Python navigation)
2. **One-to-many:** most common, "many" side has foreign key, "one" side has list
3. **One-to-one:** use `uselist=False` and `unique=True` on foreign key
4. **Many-to-many:** requires association table with `secondary=`
5. **Always use eager loading** in async code: `selectinload()` for collections, `joinedload()` for single objects
6. **N+1 query problem:** loading related objects in a loop is inefficient
7. **Use `cascade="all, delete-orphan"`** for automatic cleanup of child objects
8. **Use `lazy='raise'` during development** to catch lazy loading bugs early
