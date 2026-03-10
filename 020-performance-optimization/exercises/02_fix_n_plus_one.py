"""
Exercise 2: Fix N+1 Query Problems Using SQLAlchemy Eager Loading

In this exercise, you'll identify and fix N+1 query problems using
SQLAlchemy's eager loading strategies (selectinload and joinedload).

Your task:
1. Implement get_authors_with_books() using selectinload to fetch authors
   and their books in 2 queries (instead of N+1).
2. Implement get_authors_with_books_joined() using joinedload for a
   single-query approach.
3. Implement count_queries() that counts how many SQL queries a function
   executes (using SQLAlchemy events).

Mobile analogy: This is like optimizing Core Data fetch requests with
relationshipKeyPathsForPrefetching on iOS, or using Room @Transaction
with @Relation on Android to batch-load related entities instead of
fetching them one by one.

Run: pytest 020-performance-optimization/exercises/02_fix_n_plus_one.py -v
"""

from sqlalchemy import create_engine, ForeignKey, select, event
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
    selectinload,
    joinedload,
)


# ============= Pre-built models and setup (do NOT modify) =============

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


# SQLite in-memory engine for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)


def setup_test_data(session: Session) -> None:
    """Create 5 authors with 3 books each."""
    for i in range(1, 6):
        author = Author(name=f"Author {i}")
        author.books = [
            Book(title=f"Book {i}-{j}")
            for j in range(1, 4)
        ]
        session.add(author)
    session.commit()


def get_authors_n_plus_one(session: Session) -> list[dict]:
    """Demonstrates the N+1 problem. DO NOT MODIFY.

    This fetches authors, then accesses .books on each one,
    causing a separate query per author (N+1 total queries).
    """
    authors = session.execute(select(Author)).scalars().all()
    result = []
    for author in authors:
        result.append({
            "name": author.name,
            "books": [book.title for book in author.books],
        })
    return result


# ============= TODO 1: Implement get_authors_with_books =============
# Use selectinload to fetch all authors and their books in 2 queries.
#
# Steps:
# 1. Build a select(Author) query
# 2. Add .options(selectinload(Author.books))
# 3. Execute and convert to list of dicts (same format as n_plus_one)
#
# Hints:
# - selectinload fires one extra SELECT with an IN clause
# - The result format must match get_authors_n_plus_one exactly

def get_authors_with_books(session: Session) -> list[dict]:
    """Fetch authors with books using selectinload (2 queries).

    Returns:
        List of dicts: [{"name": "Author 1", "books": ["Book 1-1", ...]}, ...]
    """
    # TODO: Implement this function
    pass


# ============= TODO 2: Implement get_authors_with_books_joined =============
# Use joinedload to fetch all authors and their books in a single JOIN query.
#
# Steps:
# 1. Build a select(Author) query
# 2. Add .options(joinedload(Author.books))
# 3. Call .unique() before .scalars() (JOIN produces duplicate rows)
# 4. Convert to list of dicts (same format as above)
#
# Hints:
# - joinedload uses LEFT OUTER JOIN
# - You MUST call .unique() to deduplicate rows from the JOIN

def get_authors_with_books_joined(session: Session) -> list[dict]:
    """Fetch authors with books using joinedload (1 JOIN query).

    Returns:
        List of dicts: [{"name": "Author 1", "books": ["Book 1-1", ...]}, ...]
    """
    # TODO: Implement this function
    pass


# ============= TODO 3: Implement count_queries =============
# Count how many SQL queries a function executes using SQLAlchemy events.
#
# Steps:
# 1. Create a list to track queries
# 2. Define a listener function that appends to the list on each query
# 3. Register the listener with event.listen(session.bind, "before_cursor_execute", ...)
# 4. Call the provided function
# 5. Remove the listener with event.remove(...)
# 6. Return len(queries)
#
# Hints:
# - event.listen(engine, "before_cursor_execute", listener) registers a listener
# - event.remove(engine, "before_cursor_execute", listener) removes it
# - The listener signature: def listener(conn, cursor, statement, parameters, context, executemany)

def count_queries(session: Session, func) -> int:
    """Count the number of SQL queries executed by calling func().

    Args:
        session: The SQLAlchemy session (use session.bind to get the engine).
        func: A callable that performs database operations.

    Returns:
        The number of SQL queries that were executed.
    """
    # TODO: Implement this function
    pass


# ============= TESTS (do not modify below) =============

import pytest


@pytest.fixture
def db_session():
    """Create a fresh database session with test data for each test."""
    # Recreate tables for isolation
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        setup_test_data(session)
        yield session


class TestSelectinload:
    """Tests for selectinload-based eager loading."""

    def test_returns_list(self, db_session):
        """get_authors_with_books should return a list."""
        result = get_authors_with_books(db_session)
        assert isinstance(result, list), (
            f"Expected a list, got {type(result).__name__}"
        )

    def test_returns_all_authors(self, db_session):
        """Should return all 5 authors."""
        result = get_authors_with_books(db_session)
        assert len(result) == 5, (
            f"Expected 5 authors, got {len(result)}"
        )

    def test_each_author_has_books(self, db_session):
        """Each author should have 3 books."""
        result = get_authors_with_books(db_session)
        for author in result:
            assert len(author["books"]) == 3, (
                f"Author '{author['name']}' should have 3 books, "
                f"got {len(author['books'])}"
            )

    def test_matches_n_plus_one_output(self, db_session):
        """Output should be identical to the N+1 version."""
        expected = get_authors_n_plus_one(db_session)
        actual = get_authors_with_books(db_session)
        assert actual == expected, (
            "get_authors_with_books should return the same data as "
            "get_authors_n_plus_one"
        )

    def test_uses_fewer_queries(self, db_session):
        """selectinload should use <= 2 queries (not N+1)."""
        if count_queries is None or count_queries(db_session, lambda: None) is None:
            pytest.skip("count_queries not implemented yet")
        query_count = count_queries(
            db_session,
            lambda: get_authors_with_books(db_session),
        )
        assert query_count <= 2, (
            f"selectinload should use <= 2 queries, got {query_count}. "
            f"Make sure you use .options(selectinload(Author.books))"
        )


class TestJoinedload:
    """Tests for joinedload-based eager loading."""

    def test_returns_list(self, db_session):
        """get_authors_with_books_joined should return a list."""
        result = get_authors_with_books_joined(db_session)
        assert isinstance(result, list), (
            f"Expected a list, got {type(result).__name__}"
        )

    def test_returns_all_authors(self, db_session):
        """Should return all 5 authors."""
        result = get_authors_with_books_joined(db_session)
        assert len(result) == 5, (
            f"Expected 5 authors, got {len(result)}. "
            f"Did you call .unique() before .scalars()?"
        )

    def test_each_author_has_books(self, db_session):
        """Each author should have 3 books."""
        result = get_authors_with_books_joined(db_session)
        for author in result:
            assert len(author["books"]) == 3, (
                f"Author '{author['name']}' should have 3 books, "
                f"got {len(author['books'])}"
            )

    def test_matches_n_plus_one_output(self, db_session):
        """Output should be identical to the N+1 version."""
        expected = get_authors_n_plus_one(db_session)
        actual = get_authors_with_books_joined(db_session)
        assert actual == expected, (
            "get_authors_with_books_joined should return the same data as "
            "get_authors_n_plus_one"
        )


class TestCountQueries:
    """Tests for the query counting utility."""

    def test_returns_int(self, db_session):
        """count_queries should return an integer."""
        result = count_queries(db_session, lambda: None)
        assert isinstance(result, int), (
            f"count_queries should return an int, got {type(result).__name__}"
        )

    def test_counts_zero_for_no_queries(self, db_session):
        """A function that executes no queries should return 0."""
        count = count_queries(db_session, lambda: "no queries here")
        assert count == 0, (
            f"Expected 0 queries for a no-op function, got {count}"
        )

    def test_counts_single_query(self, db_session):
        """A function that executes one query should return 1."""
        def one_query():
            db_session.execute(select(Author)).scalars().all()

        count = count_queries(db_session, one_query)
        assert count == 1, (
            f"Expected 1 query for a single SELECT, got {count}"
        )

    def test_n_plus_one_has_many_queries(self, db_session):
        """The N+1 version should execute more than 5 queries."""
        count = count_queries(
            db_session,
            lambda: get_authors_n_plus_one(db_session),
        )
        assert count > 5, (
            f"N+1 version should execute > 5 queries (1 + N), got {count}. "
            f"This validates that count_queries actually counts queries."
        )
