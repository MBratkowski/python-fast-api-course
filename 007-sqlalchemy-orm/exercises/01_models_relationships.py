"""
Exercise 1: Define SQLAlchemy Models with Relationships

Create Author, Book, and Tag models with one-to-many and many-to-many relationships.

Run: pytest 007-sqlalchemy-orm/exercises/01_models_relationships.py -v
"""

from sqlalchemy import String, Integer, ForeignKey, Table, Column, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# Base class for all models
class Base(DeclarativeBase):
    pass


# ============= TODO: Exercise 1.1 =============
# Create the Author model with:
# - id: int, primary key
# - name: str, max 100 characters, not null
# - email: str, max 255 characters, unique
# - bio: str or None, no length limit (Text)
# - books: relationship to Book (one-to-many), back_populates="author"

class Author(Base):
    __tablename__ = "authors"

    # TODO: Add fields and relationship
    pass


# ============= TODO: Exercise 1.2 =============
# Create the Book model with:
# - id: int, primary key
# - title: str, max 200 characters, not null
# - isbn: str, max 13 characters, unique
# - published_year: int or None, nullable
# - author_id: int, foreign key to authors.id
# - author: relationship to Author, back_populates="books"
# - tags: relationship to Tag (many-to-many), back_populates="books", secondary=book_tags

class Book(Base):
    __tablename__ = "books"

    # TODO: Add fields and relationships
    pass


# ============= TODO: Exercise 1.3 =============
# Create the association table for Book <-> Tag many-to-many:
# - book_id: int, ForeignKey to books.id, primary key
# - tag_id: int, ForeignKey to tags.id, primary key

book_tags = Table(
    "book_tags",
    Base.metadata,
    # TODO: Add columns
)


# ============= TODO: Exercise 1.4 =============
# Create the Tag model with:
# - id: int, primary key
# - name: str, max 50 characters, unique
# - books: relationship to Book (many-to-many), back_populates="tags", secondary=book_tags

class Tag(Base):
    __tablename__ = "tags"

    # TODO: Add fields and relationship
    pass


# ============= TESTS =============
# Run with: pytest 007-sqlalchemy-orm/exercises/01_models_relationships.py -v


def test_author_model():
    """Test Author model definition."""
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author
        author = Author(
            name="J.K. Rowling",
            email="jk@example.com",
            bio="British author"
        )

        session.add(author)
        session.commit()
        session.refresh(author)

        # Verify
        assert author.id is not None
        assert author.name == "J.K. Rowling"
        assert author.email == "jk@example.com"
        assert author.bio == "British author"
        assert author.books == []  # No books yet


def test_book_model():
    """Test Book model definition."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author
        author = Author(name="George Orwell", email="george@example.com")
        session.add(author)
        session.commit()
        session.refresh(author)

        # Create book
        book = Book(
            title="1984",
            isbn="9780451524935",
            published_year=1949,
            author_id=author.id
        )

        session.add(book)
        session.commit()
        session.refresh(book)

        # Verify
        assert book.id is not None
        assert book.title == "1984"
        assert book.isbn == "9780451524935"
        assert book.published_year == 1949
        assert book.author_id == author.id


def test_one_to_many_relationship():
    """Test Author -> Books one-to-many relationship."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create author with books
        author = Author(name="Brandon Sanderson", email="brandon@example.com")

        book1 = Book(
            title="Mistborn",
            isbn="1234567890123",
            published_year=2006,
            author=author
        )

        book2 = Book(
            title="Elantris",
            isbn="9876543210987",
            published_year=2005,
            author=author
        )

        session.add(author)
        session.commit()
        session.refresh(author)

        # Verify relationship navigation
        assert len(author.books) == 2
        assert book1 in author.books
        assert book2 in author.books
        assert book1.author == author
        assert book2.author == author


def test_many_to_many_relationship():
    """Test Book <-> Tag many-to-many relationship."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create tags
        fantasy_tag = Tag(name="Fantasy")
        scifi_tag = Tag(name="Science Fiction")
        young_adult_tag = Tag(name="Young Adult")

        # Create author and book
        author = Author(name="Suzanne Collins", email="suzanne@example.com")
        book = Book(
            title="The Hunger Games",
            isbn="1111111111111",
            published_year=2008,
            author=author
        )

        # Add tags to book
        book.tags.append(scifi_tag)
        book.tags.append(young_adult_tag)

        session.add_all([fantasy_tag, scifi_tag, young_adult_tag, author])
        session.commit()

        # Verify many-to-many
        assert len(book.tags) == 2
        assert scifi_tag in book.tags
        assert young_adult_tag in book.tags
        assert fantasy_tag not in book.tags

        # Verify reverse relationship
        assert book in scifi_tag.books
        assert book in young_adult_tag.books


def test_unique_constraints():
    """Test unique constraints on email and ISBN."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create first author
        author1 = Author(name="Author One", email="same@example.com")
        session.add(author1)
        session.commit()

        # Try to create second author with same email
        author2 = Author(name="Author Two", email="same@example.com")
        session.add(author2)

        try:
            session.commit()
            assert False, "Should have raised unique constraint error"
        except Exception as e:
            session.rollback()
            assert "unique" in str(e).lower() or "constraint" in str(e).lower()


def test_nullable_fields():
    """Test that bio and published_year are nullable."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Author without bio
        author = Author(name="No Bio Author", email="nobio@example.com", bio=None)
        session.add(author)

        # Book without published year
        book = Book(
            title="Unknown Year",
            isbn="0000000000000",
            published_year=None,
            author=author
        )
        session.add(book)

        session.commit()

        # Should succeed
        assert author.bio is None
        assert book.published_year is None
