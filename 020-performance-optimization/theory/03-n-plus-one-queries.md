# Solving N+1 Queries

## Why This Matters

On iOS, Core Data uses faulting: when you access a relationship on a managed object, Core Data fires a fetch request behind the scenes. If you iterate over 100 objects and access a relationship on each, that's 100 extra fetch requests -- a classic N+1 problem. The fix on iOS is to use `relationshipKeyPathsForPrefetching` or batch fetching. On Android, Room's `@Relation` with `@Transaction` handles this by fetching related entities in a single transaction.

The N+1 problem is the single most common performance issue in backend applications using ORMs. SQLAlchemy's default lazy loading behaves exactly like Core Data faulting -- it fires a query every time you access a relationship. On a backend server talking to a database over a network, each of those extra queries adds network round-trip latency. Fix this, and you often see 10x-100x improvements.

## What N+1 Is

The "N+1" means: 1 query to fetch the parent objects, then N additional queries to fetch each parent's related children.

```python
from sqlalchemy import select

# Query 1: Fetch all authors
authors = session.execute(select(Author)).scalars().all()

# N queries: For each author, fetch their books
for author in authors:
    print(f"{author.name}: {author.books}")  # Each access = 1 query!
```

If you have 100 authors, this generates **101 queries**:

```sql
-- Query 1
SELECT * FROM authors;

-- Query 2 (author_id=1)
SELECT * FROM books WHERE author_id = 1;

-- Query 3 (author_id=2)
SELECT * FROM books WHERE author_id = 2;

-- ... 98 more queries ...
```

## Demonstrating the Problem

Here is a complete example showing N+1 in action:

```python
from sqlalchemy import create_engine, ForeignKey, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")


engine = create_engine("sqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)

with Session(engine) as session:
    # Create test data
    for i in range(5):
        author = Author(name=f"Author {i}")
        author.books = [Book(title=f"Book {j}") for j in range(3)]
        session.add(author)
    session.commit()

    # N+1 problem: watch the console output
    authors = session.execute(select(Author)).scalars().all()
    for author in authors:
        print(f"{author.name} has {len(author.books)} books")
        # Each .books access fires a SELECT!
```

With `echo=True`, you will see 6 SELECT statements: 1 for authors + 5 for each author's books.

## Solution 1: selectinload()

`selectinload` fires one extra SELECT with an IN clause:

```python
from sqlalchemy.orm import selectinload

# 2 queries total: SELECT authors + SELECT books WHERE author_id IN (1,2,3,4,5)
authors = session.execute(
    select(Author).options(selectinload(Author.books))
).scalars().all()

for author in authors:
    print(f"{author.name} has {len(author.books)} books")
    # No extra queries -- books are already loaded!
```

SQL generated:

```sql
-- Query 1
SELECT * FROM authors;

-- Query 2 (all books in one query)
SELECT * FROM books WHERE books.author_id IN (1, 2, 3, 4, 5);
```

**When to use:** Best for one-to-many relationships (collections). This is the most common fix.

## Solution 2: joinedload()

`joinedload` uses a LEFT OUTER JOIN to fetch everything in a single query:

```python
from sqlalchemy.orm import joinedload

# 1 query total: SELECT authors LEFT JOIN books
authors = session.execute(
    select(Author).options(joinedload(Author.books))
).unique().scalars().all()
```

SQL generated:

```sql
SELECT authors.id, authors.name, books.id, books.title, books.author_id
FROM authors
LEFT OUTER JOIN books ON authors.id = books.author_id;
```

**Important:** When using `joinedload` with `scalars()`, you must call `.unique()` because the JOIN produces duplicate author rows (one per book).

**When to use:** Best for many-to-one relationships (single objects). For example, loading a book with its author.

```python
# Good use of joinedload: each book has exactly one author
books = session.execute(
    select(Book).options(joinedload(Book.author))
).scalars().all()
```

## Solution 3: subqueryload()

`subqueryload` uses a subquery to fetch related objects:

```python
from sqlalchemy.orm import subqueryload

authors = session.execute(
    select(Author).options(subqueryload(Author.books))
).scalars().all()
```

SQL generated:

```sql
-- Query 1
SELECT * FROM authors;

-- Query 2 (subquery approach)
SELECT books.*, anon_1.id AS anon_1_id
FROM (SELECT authors.id FROM authors) AS anon_1
JOIN books ON anon_1.id = books.author_id;
```

**When to use:** Rarely. `selectinload` is preferred in most cases. Use `subqueryload` when the parent query is complex and the IN clause would be too large.

## When to Use Which Strategy

| Strategy | Queries | Best For | Avoid When |
|----------|---------|----------|------------|
| `selectinload` | 2 | Collections (one-to-many) | Parent query returns thousands of IDs |
| `joinedload` | 1 | Single objects (many-to-one) | Collections (causes row duplication) |
| `subqueryload` | 2 | Complex parent queries | Simple cases (selectinload is simpler) |
| `lazy="select"` (default) | N+1 | Never in production loops | Always when iterating |

**Rule of thumb:**
- Loading a list of books, each with its author? `joinedload(Book.author)`
- Loading a list of authors, each with their books? `selectinload(Author.books)`
- Not sure? Start with `selectinload` -- it's safe and predictable

## Nested Eager Loading

You can chain eager loading for deeper relationships:

```python
# Load authors -> books -> reviews (3 levels)
authors = session.execute(
    select(Author).options(
        selectinload(Author.books).selectinload(Book.reviews)
    )
).scalars().all()
```

## Detecting N+1 in Development

### Method 1: Count queries with echo

Enable `echo=True` and count the SELECT statements. If you see N+1 SELECTs, you have the problem.

### Method 2: Count queries in tests

Use SQLAlchemy events to count queries programmatically:

```python
from sqlalchemy import event


def count_queries(session, func):
    """Count the number of SQL queries executed by func."""
    queries = []

    def track(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(session.bind, "before_cursor_execute", track)
    try:
        result = func()
    finally:
        event.remove(session.bind, "before_cursor_execute", track)

    return len(queries), result


# In your test:
count, authors = count_queries(session, lambda: get_authors_with_books(session))
assert count <= 2, f"Expected <= 2 queries, got {count} (likely N+1)"
```

## Key Takeaways

1. **N+1 is the most common ORM performance bug.** One query for parents + N queries for children. Always look for it when iterating over objects with relationships.
2. **Use `selectinload()` for collections.** It fires 2 queries regardless of how many parent objects you have. This is the default fix for one-to-many.
3. **Use `joinedload()` for single objects.** Loading a book with its author? One JOIN query is optimal.
4. **Always call `.unique()` with `joinedload()` on collections.** The JOIN produces duplicate rows that need deduplication.
5. **Count queries in tests.** Use SQLAlchemy events to verify your eager loading actually works. If a function executes more than 2-3 queries for a list endpoint, investigate.
6. **The fix is almost always 1 line.** Adding `.options(selectinload(Parent.children))` to your query typically solves the problem completely.
