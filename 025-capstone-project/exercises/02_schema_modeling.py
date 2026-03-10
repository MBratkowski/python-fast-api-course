"""
Exercise 2: Database Schema Modeling

Model your capstone database schema as Python data structures and
validate it meets relational design requirements from Modules 006-008.

You will define tables with columns, primary keys, foreign keys, and
constraints. The tests verify your schema follows relational design
best practices: primary keys, foreign key relationships, timestamps,
and proper nullable settings.

Run: pytest 025-capstone-project/exercises/02_schema_modeling.py -v
"""

from pydantic import BaseModel


# ============= SCHEMA MODELS (PROVIDED) =============


class Column(BaseModel):
    """Specification for a single database column."""

    name: str  # Column name (e.g., "id", "email", "created_at")
    type: str  # Data type (e.g., "integer", "varchar(255)", "text", "timestamp", "boolean")
    primary_key: bool = False
    nullable: bool = True
    foreign_key: str | None = None  # "table.column" format (e.g., "users.id")
    unique: bool = False
    default: str | None = None  # Default value (e.g., "NOW()", "true", "0")


class Table(BaseModel):
    """Specification for a single database table."""

    name: str  # Table name (e.g., "users", "posts")
    columns: list[Column]


class DatabaseSchema(BaseModel):
    """Complete database schema specification."""

    tables: list[Table]


# ============= TODO (IMPLEMENT) =============
# Design your capstone database schema.
#
# Requirements:
# - At least 4 tables (users + 3 domain-specific tables)
# - Every table has a primary key column
# - At least 3 foreign key relationships between tables
# - A "users" table for authentication
# - Every table has a "created_at" timestamp column
# - Foreign key columns should not be nullable (enforce referential integrity)


def create_schema() -> DatabaseSchema:
    """
    Design the database schema for your capstone project.

    Choose one of the three capstone projects and create a complete
    database schema with tables, columns, primary keys, foreign keys,
    and appropriate constraints.

    Returns:
        DatabaseSchema with at least 4 well-designed tables.
    """
    pass  # TODO: Implement


# ============= TESTS =============


def test_minimum_tables():
    """Schema should have at least 4 tables."""
    schema = create_schema()
    assert len(schema.tables) >= 4, (
        f"Need at least 4 tables, got {len(schema.tables)}"
    )


def test_all_tables_have_primary_key():
    """Every table must have at least one primary key column."""
    schema = create_schema()
    for table in schema.tables:
        pks = [c for c in table.columns if c.primary_key]
        assert len(pks) >= 1, (
            f"Table '{table.name}' needs at least one primary key column"
        )


def test_has_foreign_keys():
    """Schema should have at least 3 foreign key relationships."""
    schema = create_schema()
    fks = [
        c
        for table in schema.tables
        for c in table.columns
        if c.foreign_key is not None
    ]
    assert len(fks) >= 3, (
        f"Need at least 3 foreign key relationships, got {len(fks)}"
    )


def test_has_user_table():
    """Schema must include a users table for authentication."""
    schema = create_schema()
    table_names = [t.name.lower() for t in schema.tables]
    assert "users" in table_names or "user" in table_names, (
        f"Missing 'users' table. Found tables: {table_names}"
    )


def test_has_timestamps():
    """Every table should have a created_at column."""
    schema = create_schema()
    for table in schema.tables:
        col_names = [c.name for c in table.columns]
        assert "created_at" in col_names, (
            f"Table '{table.name}' needs a 'created_at' column"
        )


def test_no_nullable_foreign_keys():
    """Foreign key columns should not be nullable (enforce referential integrity)."""
    schema = create_schema()
    for table in schema.tables:
        for col in table.columns:
            if col.foreign_key is not None:
                assert not col.nullable, (
                    f"Table '{table.name}', column '{col.name}' is a foreign key "
                    f"but is nullable. Foreign keys should enforce referential integrity."
                )
