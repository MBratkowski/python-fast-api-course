"""
Exercise 3: Complex Queries with SQLAlchemy

Write queries with joins, aggregations, grouping, and filtering.

Run: pytest 007-sqlalchemy-orm/exercises/03_complex_queries.py -v
"""

from sqlalchemy import String, Integer, ForeignKey, Table, Column, create_engine, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# Models (provided - no TODOs here)
class Base(DeclarativeBase):
    pass


book_tags = Table(
    "book_tags",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")

    tags: Mapped[list["Tag"]] = relationship(secondary=book_tags, back_populates="books")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    books: Mapped[list["Book"]] = relationship(secondary=book_tags, back_populates="tags")


# Seed data function (provided)
def seed_data(session: Session):
    """Create test data for queries."""
    # Authors
    author1 = Author(name="Alice Author", email="alice@example.com")
    author2 = Author(name="Bob Writer", email="bob@example.com")
    author3 = Author(name="Charlie Novelist", email="charlie@example.com")

    # Tags
    fantasy = Tag(name="Fantasy")
    scifi = Tag(name="Science Fiction")
    mystery = Tag(name="Mystery")
    thriller = Tag(name="Thriller")
    romance = Tag(name="Romance")

    # Books for author1 (3 books)
    book1 = Book(title="Magic Quest", isbn="1111111111111", published_year=2020, author=author1)
    book1.tags.extend([fantasy])

    book2 = Book(title="Space Adventure", isbn="2222222222222", published_year=2021, author=author1)
    book2.tags.extend([scifi, thriller])

    book3 = Book(title="Love Story", isbn="3333333333333", published_year=2022, author=author1)
    book3.tags.extend([romance])

    # Books for author2 (2 books)
    book4 = Book(title="Murder Mystery", isbn="4444444444444", published_year=2019, author=author2)
    book4.tags.extend([mystery, thriller])

    book5 = Book(title="Detective Case", isbn="5555555555555", published_year=2020, author=author2)
    book5.tags.extend([mystery])

    # Books for author3 (3 books)
    book6 = Book(title="Fantasy World", isbn="6666666666666", published_year=2018, author=author3)
    book6.tags.extend([fantasy, romance])

    book7 = Book(title="Sci-Fi Epic", isbn="7777777777777", published_year=2021, author=author3)
    book7.tags.extend([scifi])

    book8 = Book(title="Old Book", isbn="8888888888888", published_year=2015, author=author3)
    book8.tags.extend([mystery])

    session.add_all([author1, author2, author3, fantasy, scifi, mystery, thriller, romance])
    session.commit()


# ============= TODO: Exercise 3.1 =============
# Get all authors with their book count, sorted by count descending.
# Use func.count() and group_by().
# Return list of dicts: [{"author": Author, "book_count": int}, ...]

def get_authors_with_book_count(session: Session) -> list[dict]:
    """
    Get authors with their book count, sorted by count descending.

    Returns: [{"author": Author, "book_count": int}, ...]
    """
    # TODO: Implement using select(), join(), func.count(), group_by(), order_by()
    pass


# ============= TODO: Exercise 3.2 =============
# Get books published between start_year and end_year (inclusive).
# Use .where() with comparisons.
# Return list of Book objects.

def get_books_by_year_range(session: Session, start_year: int, end_year: int) -> list[Book]:
    """Get books published between start_year and end_year (inclusive)."""
    # TODO: Implement using select().where() with >= and <=
    pass


# ============= TODO: Exercise 3.3 =============
# Get authors who have at least min_books books.
# Use join(), func.count(), group_by(), and having().
# Return list of Author objects.

def get_prolific_authors(session: Session, min_books: int) -> list[Author]:
    """Get authors with at least min_books books."""
    # TODO: Implement using select(), join(), group_by(), having()
    pass


# ============= TODO: Exercise 3.4 =============
# Get books that have ALL the specified tags.
# This is tricky - you need to check that the book has every tag in the list.
# Hint: Join book_tags, filter by tag names, group by book, count matches,
# and use HAVING count = len(tag_names).
# Return list of Book objects.

def get_books_with_tags(session: Session, tag_names: list[str]) -> list[Book]:
    """Get books that have ALL specified tags."""
    # TODO: Implement
    # Hint: This requires joining through book_tags, filtering by tag names,
    # grouping by book, and using HAVING to ensure all tags are present
    pass


# ============= TESTS =============
# Run with: pytest 007-sqlalchemy-orm/exercises/03_complex_queries.py -v


def test_get_authors_with_book_count():
    """Test getting authors with book counts."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_data(session)

        results = get_authors_with_book_count(session)

        assert len(results) == 3

        # Check sorted by count descending (3, 3, 2)
        assert results[0]["book_count"] == 3  # Alice or Charlie
        assert results[1]["book_count"] == 3  # Alice or Charlie
        assert results[2]["book_count"] == 2  # Bob

        # Verify authors are included
        authors = [r["author"] for r in results]
        author_names = [a.name for a in authors]
        assert "Alice Author" in author_names
        assert "Bob Writer" in author_names
        assert "Charlie Novelist" in author_names


def test_get_books_by_year_range():
    """Test getting books by year range."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_data(session)

        # Get books from 2019-2020
        books = get_books_by_year_range(session, 2019, 2020)
        titles = [b.title for b in books]

        assert len(books) == 3
        assert "Murder Mystery" in titles  # 2019
        assert "Magic Quest" in titles  # 2020
        assert "Detective Case" in titles  # 2020

        # Get books from 2021-2022
        books = get_books_by_year_range(session, 2021, 2022)
        titles = [b.title for b in books]

        assert len(books) == 3
        assert "Space Adventure" in titles  # 2021
        assert "Sci-Fi Epic" in titles  # 2021
        assert "Love Story" in titles  # 2022


def test_get_prolific_authors():
    """Test getting authors with minimum number of books."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_data(session)

        # Authors with at least 3 books
        authors = get_prolific_authors(session, 3)
        names = [a.name for a in authors]

        assert len(authors) == 2
        assert "Alice Author" in names
        assert "Charlie Novelist" in names
        assert "Bob Writer" not in names  # Only has 2 books

        # Authors with at least 2 books
        authors = get_prolific_authors(session, 2)
        names = [a.name for a in authors]

        assert len(authors) == 3  # All have at least 2

        # Authors with at least 4 books
        authors = get_prolific_authors(session, 4)
        assert len(authors) == 0  # None have 4+


def test_get_books_with_tags():
    """Test getting books with all specified tags."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_data(session)

        # Books with both "Science Fiction" and "Thriller"
        books = get_books_with_tags(session, ["Science Fiction", "Thriller"])
        titles = [b.title for b in books]

        assert len(books) == 1
        assert "Space Adventure" in titles

        # Books with "Mystery"
        books = get_books_with_tags(session, ["Mystery"])
        titles = [b.title for b in books]

        assert len(books) == 3
        assert "Murder Mystery" in titles
        assert "Detective Case" in titles
        assert "Old Book" in titles

        # Books with both "Fantasy" and "Romance"
        books = get_books_with_tags(session, ["Fantasy", "Romance"])
        titles = [b.title for b in books]

        assert len(books) == 1
        assert "Fantasy World" in titles

        # Books with tags that no book has together
        books = get_books_with_tags(session, ["Fantasy", "Science Fiction", "Mystery"])
        assert len(books) == 0
