"""
Exercise 2: CRUD Operations with SQLAlchemy Session

Implement create, read, update, and delete operations using SQLAlchemy session.

Run: pytest 007-sqlalchemy-orm/exercises/02_crud_operations.py -v
"""

from sqlalchemy import String, Integer, ForeignKey, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# Base and models (provided - no TODOs here)
class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    isbn: Mapped[str] = mapped_column(String(13), unique=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")


# ============= TODO: Exercise 2.1 =============
# Create an author with the given name and email.
# Add to session, commit, refresh, and return the author.

def create_author(session: Session, name: str, email: str) -> Author:
    """Create and return a new author."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.2 =============
# Get an author by ID.
# Return the Author object or None if not found.

def get_author_by_id(session: Session, author_id: int) -> Author | None:
    """Get author by ID, return None if not found."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.3 =============
# Search for authors where name contains the pattern (case-insensitive).
# Use .ilike() for case-insensitive matching: Author.name.ilike(f"%{pattern}%")
# Return list of matching authors.

def get_authors_by_name(session: Session, name_pattern: str) -> list[Author]:
    """Search authors by name pattern (case-insensitive)."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.4 =============
# Update an author's email.
# Get author by ID, update email field, commit, refresh, and return updated author.
# Return None if author not found.

def update_author_email(session: Session, author_id: int, new_email: str) -> Author | None:
    """Update author's email, return updated author or None."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.5 =============
# Delete an author by ID.
# Get author, delete it, commit, and return True if deleted.
# Return False if author not found.

def delete_author(session: Session, author_id: int) -> bool:
    """Delete author by ID, return True if deleted, False if not found."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.6 =============
# Create a book for an author.
# Check if author exists, create Book with author_id, commit, refresh, return book.
# Return None if author not found.

def create_book_for_author(
    session: Session,
    author_id: int,
    title: str,
    isbn: str
) -> Book | None:
    """Create book for author, return None if author not found."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 007-sqlalchemy-orm/exercises/02_crud_operations.py -v


def test_create_author():
    """Test creating an author."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        author = create_author(session, "Alice Smith", "alice@example.com")

        assert author is not None
        assert author.id is not None
        assert author.name == "Alice Smith"
        assert author.email == "alice@example.com"


def test_get_author_by_id():
    """Test getting author by ID."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author
        author = create_author(session, "Bob Jones", "bob@example.com")
        author_id = author.id

        # Get by ID
        found = get_author_by_id(session, author_id)
        assert found is not None
        assert found.id == author_id
        assert found.name == "Bob Jones"

        # Get non-existent
        not_found = get_author_by_id(session, 9999)
        assert not_found is None


def test_get_authors_by_name():
    """Test searching authors by name pattern."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create multiple authors
        create_author(session, "Alice Smith", "alice@example.com")
        create_author(session, "Bob Smith", "bob@example.com")
        create_author(session, "Charlie Jones", "charlie@example.com")

        # Search for "smith" (case-insensitive)
        results = get_authors_by_name(session, "smith")
        assert len(results) == 2
        assert any(a.name == "Alice Smith" for a in results)
        assert any(a.name == "Bob Smith" for a in results)

        # Search for "jones"
        results = get_authors_by_name(session, "jones")
        assert len(results) == 1
        assert results[0].name == "Charlie Jones"

        # Search with no matches
        results = get_authors_by_name(session, "nonexistent")
        assert len(results) == 0


def test_update_author_email():
    """Test updating author's email."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author
        author = create_author(session, "Dave Wilson", "dave@example.com")
        author_id = author.id

        # Update email
        updated = update_author_email(session, author_id, "dave.new@example.com")
        assert updated is not None
        assert updated.email == "dave.new@example.com"

        # Verify persistence
        found = get_author_by_id(session, author_id)
        assert found.email == "dave.new@example.com"

        # Update non-existent author
        result = update_author_email(session, 9999, "nobody@example.com")
        assert result is None


def test_delete_author():
    """Test deleting an author."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author
        author = create_author(session, "Eve Brown", "eve@example.com")
        author_id = author.id

        # Delete
        deleted = delete_author(session, author_id)
        assert deleted is True

        # Verify deleted
        found = get_author_by_id(session, author_id)
        assert found is None

        # Delete non-existent
        deleted = delete_author(session, 9999)
        assert deleted is False


def test_create_book_for_author():
    """Test creating a book for an author."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author
        author = create_author(session, "Frank Miller", "frank@example.com")
        author_id = author.id

        # Create book for author
        book = create_book_for_author(
            session,
            author_id,
            "The Dark Knight Returns",
            "1234567890123"
        )

        assert book is not None
        assert book.id is not None
        assert book.title == "The Dark Knight Returns"
        assert book.isbn == "1234567890123"
        assert book.author_id == author_id
        assert book.author.name == "Frank Miller"

        # Create book for non-existent author
        book = create_book_for_author(session, 9999, "No Author", "0000000000000")
        assert book is None


def test_cascade_delete():
    """Test that deleting author deletes their books (cascade)."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author with books
        author = create_author(session, "Grace Hopper", "grace@example.com")
        author_id = author.id

        book1 = create_book_for_author(session, author_id, "Book 1", "1111111111111")
        book2 = create_book_for_author(session, author_id, "Book 2", "2222222222222")

        book1_id = book1.id
        book2_id = book2.id

        # Delete author
        delete_author(session, author_id)

        # Verify books are also deleted (cascade)
        result = session.execute(select(Book).where(Book.id == book1_id))
        assert result.scalar_one_or_none() is None

        result = session.execute(select(Book).where(Book.id == book2_id))
        assert result.scalar_one_or_none() is None
