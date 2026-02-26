"""
Exercise 1: Writing and Analyzing SQL Queries

Build and analyze SQL queries using Python. This simulates understanding what
your ORM is generating and how to construct efficient queries.

Run: pytest 006-sql-databases/exercises/01_sql_queries.py -v
"""


def build_select_query(table: str, columns: list[str], where: dict | None = None) -> str:
    """
    Build a SELECT query string.

    Args:
        table: Table name
        columns: List of column names
        where: Optional dict of column: value conditions (AND logic)

    Returns:
        SQL query string

    Examples:
        build_select_query("users", ["name", "email"])
        → "SELECT name, email FROM users"

        build_select_query("users", ["*"], {"is_active": True})
        → "SELECT * FROM users WHERE is_active = true"

        build_select_query("posts", ["title"], {"author_id": 1, "is_published": True})
        → "SELECT title FROM posts WHERE author_id = 1 AND is_published = true"
    """
    pass


def build_insert_query(table: str, data: dict) -> str:
    """
    Build an INSERT query string.

    Args:
        table: Table name
        data: Dict of column: value pairs

    Returns:
        SQL query string

    Examples:
        build_insert_query("users", {"name": "Alice", "email": "alice@example.com"})
        → "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')"

        build_insert_query("posts", {"title": "Hello", "view_count": 0})
        → "INSERT INTO posts (title, view_count) VALUES ('Hello', 0)"
    """
    pass


def parse_where_clause(clause: str) -> list[dict]:
    """
    Parse a WHERE clause string into structured conditions.

    Args:
        clause: WHERE clause string (without "WHERE")

    Returns:
        List of dicts with keys: column, operator, value

    Examples:
        parse_where_clause("age > 18")
        → [{"column": "age", "operator": ">", "value": "18"}]

        parse_where_clause("age > 18 AND status = 'active'")
        → [
            {"column": "age", "operator": ">", "value": "18"},
            {"column": "status", "operator": "=", "value": "active"}
        ]

    Supported operators: =, !=, >, <, >=, <=
    """
    pass


def calculate_query_result(
    rows: list[dict], query_type: str, column: str | None = None
) -> int | float:
    """
    Simulate aggregate functions on in-memory data.

    Args:
        rows: List of row dicts
        query_type: One of "COUNT", "SUM", "AVG", "MIN", "MAX"
        column: Column name (None for COUNT(*))

    Returns:
        Aggregate result

    Examples:
        rows = [{"age": 25}, {"age": 30}, {"age": 35}]
        calculate_query_result(rows, "COUNT") → 3
        calculate_query_result(rows, "SUM", "age") → 90
        calculate_query_result(rows, "AVG", "age") → 30.0
        calculate_query_result(rows, "MIN", "age") → 25
        calculate_query_result(rows, "MAX", "age") → 35
    """
    pass


# ============= TESTS =============


def test_build_select_query_basic():
    """Test basic SELECT queries."""
    assert build_select_query("users", ["name", "email"]) == "SELECT name, email FROM users"
    assert build_select_query("posts", ["*"]) == "SELECT * FROM posts"


def test_build_select_query_with_where():
    """Test SELECT with WHERE conditions."""
    result = build_select_query("users", ["*"], {"is_active": True})
    assert result == "SELECT * FROM users WHERE is_active = true"

    result = build_select_query("posts", ["title"], {"author_id": 1})
    assert result == "SELECT title FROM posts WHERE author_id = 1"


def test_build_select_query_multiple_conditions():
    """Test SELECT with multiple WHERE conditions."""
    result = build_select_query("posts", ["*"], {"author_id": 1, "is_published": True})
    # Should contain both conditions with AND
    assert "WHERE" in result
    assert "author_id = 1" in result
    assert "is_published = true" in result
    assert "AND" in result


def test_build_insert_query():
    """Test INSERT query building."""
    result = build_insert_query("users", {"name": "Alice", "email": "alice@example.com"})
    assert "INSERT INTO users" in result
    assert "name" in result and "email" in result
    assert "'Alice'" in result
    assert "'alice@example.com'" in result


def test_build_insert_query_numeric():
    """Test INSERT with numeric values."""
    result = build_insert_query("posts", {"title": "Hello", "view_count": 0})
    assert "INSERT INTO posts" in result
    assert "'Hello'" in result  # String gets quotes
    assert "view_count" in result
    # Numeric value should not have quotes
    assert ", 0)" in result or "0)" in result


def test_parse_where_clause_single():
    """Test parsing single WHERE condition."""
    result = parse_where_clause("age > 18")
    assert len(result) == 1
    assert result[0]["column"] == "age"
    assert result[0]["operator"] == ">"
    assert result[0]["value"] == "18"


def test_parse_where_clause_multiple():
    """Test parsing multiple WHERE conditions."""
    result = parse_where_clause("age > 18 AND status = 'active'")
    assert len(result) == 2
    assert result[0]["column"] == "age"
    assert result[0]["operator"] == ">"
    assert result[0]["value"] == "18"
    assert result[1]["column"] == "status"
    assert result[1]["operator"] == "="
    assert result[1]["value"] == "active"


def test_parse_where_clause_operators():
    """Test different operators."""
    result = parse_where_clause("age >= 18")
    assert result[0]["operator"] == ">="

    result = parse_where_clause("status != 'inactive'")
    assert result[0]["operator"] == "!="


def test_calculate_query_result_count():
    """Test COUNT aggregate."""
    rows = [{"age": 25}, {"age": 30}, {"age": 35}]
    assert calculate_query_result(rows, "COUNT") == 3

    empty_rows = []
    assert calculate_query_result(empty_rows, "COUNT") == 0


def test_calculate_query_result_sum():
    """Test SUM aggregate."""
    rows = [{"age": 25}, {"age": 30}, {"age": 35}]
    assert calculate_query_result(rows, "SUM", "age") == 90


def test_calculate_query_result_avg():
    """Test AVG aggregate."""
    rows = [{"age": 20}, {"age": 30}, {"age": 40}]
    assert calculate_query_result(rows, "AVG", "age") == 30.0


def test_calculate_query_result_min_max():
    """Test MIN and MAX aggregates."""
    rows = [{"age": 25}, {"age": 30}, {"age": 35}]
    assert calculate_query_result(rows, "MIN", "age") == 25
    assert calculate_query_result(rows, "MAX", "age") == 35
