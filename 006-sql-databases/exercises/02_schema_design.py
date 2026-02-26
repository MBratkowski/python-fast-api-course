"""
Exercise 2: Designing Database Schemas

Design normalized database schemas as Python data structures. This builds
understanding of table design before working with ORMs.

Run: pytest 006-sql-databases/exercises/02_schema_design.py -v
"""


def design_user_schema() -> dict:
    """
    Design a users table schema.

    Returns:
        Dict with keys: table, columns, constraints

    Schema must include:
        - id: INTEGER, PRIMARY KEY
        - username: VARCHAR(50), UNIQUE, NOT NULL
        - email: VARCHAR(255), UNIQUE, NOT NULL
        - created_at: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
        - is_active: BOOLEAN, DEFAULT true

    Example structure:
        {
            "table": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "default": None},
                {"name": "username", "type": "VARCHAR(50)", "nullable": False, "default": None},
                ...
            ],
            "constraints": [
                {"type": "PRIMARY_KEY", "columns": ["id"]},
                {"type": "UNIQUE", "columns": ["username"]},
                ...
            ]
        }
    """
    pass


def design_blog_schema() -> list[dict]:
    """
    Design a complete blog schema with relationships.

    Returns:
        List of table schema dicts (users, posts, comments)

    Requirements:
        - users table: id, username, email
        - posts table: id, title, content, author_id (FK to users), created_at
        - comments table: id, content, post_id (FK to posts), author_id (FK to users)

    Foreign keys must have:
        - table, column (source)
        - references: {table, column} (target)
        - on_delete: "CASCADE" or "SET NULL"

    Example FK constraint:
        {
            "type": "FOREIGN_KEY",
            "column": "author_id",
            "references": {"table": "users", "column": "id"},
            "on_delete": "CASCADE"
        }
    """
    pass


def normalize_table(denormalized: list[dict]) -> dict:
    """
    Given denormalized data, suggest normalized schema.

    Args:
        denormalized: List of row dicts with repeated data

    Returns:
        Dict with keys: tables (list of table schemas), relationships (list)

    Example input (denormalized):
        [
            {"post_id": 1, "title": "Hello", "author_name": "Alice", "author_email": "alice@ex.com"},
            {"post_id": 2, "title": "World", "author_name": "Alice", "author_email": "alice@ex.com"},
        ]

    Example output (normalized):
        {
            "tables": [
                {
                    "name": "users",
                    "columns": ["id", "name", "email"],
                    "sample_data": [{"id": 1, "name": "Alice", "email": "alice@ex.com"}]
                },
                {
                    "name": "posts",
                    "columns": ["id", "title", "author_id"],
                    "sample_data": [
                        {"id": 1, "title": "Hello", "author_id": 1},
                        {"id": 2, "title": "World", "author_id": 1}
                    ]
                }
            ],
            "relationships": [
                {
                    "from_table": "posts",
                    "from_column": "author_id",
                    "to_table": "users",
                    "to_column": "id",
                    "type": "many-to-one"
                }
            ]
        }
    """
    pass


def identify_relationship_type(table_a: str, table_b: str, description: str) -> str:
    """
    Identify relationship type from description.

    Args:
        table_a: First table name
        table_b: Second table name
        description: Natural language description of relationship

    Returns:
        One of: "one-to-one", "one-to-many", "many-to-many"

    Examples:
        identify_relationship_type("users", "profiles", "Each user has exactly one profile")
        → "one-to-one"

        identify_relationship_type("users", "posts", "A user can have many posts")
        → "one-to-many"

        identify_relationship_type("students", "courses", "Students enroll in multiple courses")
        → "many-to-many"
    """
    pass


# ============= TESTS =============


def test_design_user_schema_structure():
    """Test user schema has correct structure."""
    schema = design_user_schema()
    assert "table" in schema
    assert schema["table"] == "users"
    assert "columns" in schema
    assert "constraints" in schema
    assert isinstance(schema["columns"], list)
    assert isinstance(schema["constraints"], list)


def test_design_user_schema_columns():
    """Test user schema has required columns."""
    schema = design_user_schema()
    column_names = [col["name"] for col in schema["columns"]]
    assert "id" in column_names
    assert "username" in column_names
    assert "email" in column_names
    assert "created_at" in column_names
    assert "is_active" in column_names


def test_design_user_schema_constraints():
    """Test user schema has correct constraints."""
    schema = design_user_schema()
    constraint_types = [c["type"] for c in schema["constraints"]]
    assert "PRIMARY_KEY" in constraint_types
    # Should have UNIQUE constraints
    unique_constraints = [c for c in schema["constraints"] if c["type"] == "UNIQUE"]
    assert len(unique_constraints) >= 2  # username and email


def test_design_blog_schema_tables():
    """Test blog schema has all required tables."""
    schemas = design_blog_schema()
    table_names = [s["table"] for s in schemas]
    assert "users" in table_names
    assert "posts" in table_names
    assert "comments" in table_names


def test_design_blog_schema_relationships():
    """Test blog schema has foreign keys."""
    schemas = design_blog_schema()
    posts_schema = next(s for s in schemas if s["table"] == "posts")
    comments_schema = next(s for s in schemas if s["table"] == "comments")

    # Posts should have author_id FK to users
    posts_fks = [c for c in posts_schema["constraints"] if c["type"] == "FOREIGN_KEY"]
    assert len(posts_fks) >= 1
    assert any(fk["references"]["table"] == "users" for fk in posts_fks)

    # Comments should have FKs to both posts and users
    comments_fks = [c for c in comments_schema["constraints"] if c["type"] == "FOREIGN_KEY"]
    assert len(comments_fks) >= 2


def test_normalize_table_creates_separate_tables():
    """Test normalization separates repeated data."""
    denormalized = [
        {"post_id": 1, "title": "Hello", "author_name": "Alice", "author_email": "alice@ex.com"},
        {"post_id": 2, "title": "World", "author_name": "Alice", "author_email": "alice@ex.com"},
    ]
    result = normalize_table(denormalized)
    assert "tables" in result
    assert "relationships" in result
    # Should create at least 2 tables (users and posts)
    assert len(result["tables"]) >= 2


def test_normalize_table_deduplicates_data():
    """Test normalization removes duplicates."""
    denormalized = [
        {"post_id": 1, "title": "Hello", "author_name": "Alice", "author_email": "alice@ex.com"},
        {"post_id": 2, "title": "World", "author_name": "Alice", "author_email": "alice@ex.com"},
    ]
    result = normalize_table(denormalized)
    # Find users table
    users_table = next(t for t in result["tables"] if "name" in t or "email" in str(t))
    # Should only have 1 user (Alice), not 2
    if "sample_data" in users_table:
        # If implementation includes sample data, check deduplication
        unique_authors = {row.get("name") or row.get("author_name") for row in users_table.get("sample_data", [])}
        assert len(unique_authors) <= 1


def test_identify_relationship_type_one_to_one():
    """Test identifying one-to-one relationships."""
    result = identify_relationship_type(
        "users", "profiles", "Each user has exactly one profile"
    )
    assert result == "one-to-one"

    result = identify_relationship_type(
        "users", "profiles", "A user has one profile"
    )
    assert result == "one-to-one"


def test_identify_relationship_type_one_to_many():
    """Test identifying one-to-many relationships."""
    result = identify_relationship_type(
        "users", "posts", "A user can have many posts, a post belongs to one user"
    )
    assert result == "one-to-many"

    result = identify_relationship_type(
        "users", "comments", "Users write multiple comments"
    )
    assert result == "one-to-many"


def test_identify_relationship_type_many_to_many():
    """Test identifying many-to-many relationships."""
    result = identify_relationship_type(
        "students", "courses", "Students enroll in multiple courses, courses have multiple students"
    )
    assert result == "many-to-many"

    result = identify_relationship_type(
        "posts", "tags", "Posts can have many tags, tags can be on many posts"
    )
    assert result == "many-to-many"
