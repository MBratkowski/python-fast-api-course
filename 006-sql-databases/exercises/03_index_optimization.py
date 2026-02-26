"""
Exercise 3: Index Optimization

Analyze queries and suggest index optimizations. This builds intuition for
when and where to add indexes.

Run: pytest 006-sql-databases/exercises/03_index_optimization.py -v
"""


def suggest_indexes(table_schema: dict, queries: list[str]) -> list[dict]:
    """
    Analyze queries and suggest which indexes to create.

    Args:
        table_schema: Dict with table name and columns
        queries: List of SQL query strings

    Returns:
        List of index suggestions with keys: table, columns, type, reason

    Look for:
        - WHERE clauses → index on filtered columns
        - JOIN conditions → index on join columns
        - ORDER BY → index on sort columns

    Example:
        table_schema = {
            "table": "users",
            "columns": ["id", "username", "email", "is_active"]
        }
        queries = [
            "SELECT * FROM users WHERE email = 'alice@example.com'",
            "SELECT * FROM users WHERE is_active = true ORDER BY username"
        ]

        Result:
        [
            {
                "table": "users",
                "columns": ["email"],
                "type": "INDEX",
                "reason": "Used in WHERE clause for equality"
            },
            {
                "table": "users",
                "columns": ["is_active", "username"],
                "type": "INDEX",
                "reason": "Used in WHERE and ORDER BY"
            }
        ]
    """
    pass


def estimate_query_cost(has_index: bool, table_size: int) -> str:
    """
    Estimate query cost based on index presence and table size.

    Args:
        has_index: Whether relevant index exists
        table_size: Number of rows in table

    Returns:
        One of: "index_scan", "small_table_scan", "full_table_scan"

    Rules:
        - has_index=True, any size → "index_scan"
        - has_index=False, size <= 1000 → "small_table_scan"
        - has_index=False, size > 1000 → "full_table_scan"

    Examples:
        estimate_query_cost(True, 10000) → "index_scan"
        estimate_query_cost(False, 500) → "small_table_scan"
        estimate_query_cost(False, 5000) → "full_table_scan"
    """
    pass


def analyze_query_plan(query: str, indexes: list[str]) -> dict:
    """
    Analyze a query and determine if it uses indexes.

    Args:
        query: SQL query string
        indexes: List of indexed column names

    Returns:
        Dict with keys: scan_type, estimated_rows, uses_index, index_name, recommendation

    Example:
        query = "SELECT * FROM users WHERE email = 'alice@example.com'"
        indexes = ["email", "username"]

        Result:
        {
            "scan_type": "index_scan",
            "estimated_rows": "1",
            "uses_index": True,
            "index_name": "email",
            "recommendation": "Query is optimized"
        }

        query = "SELECT * FROM users WHERE age > 18"
        indexes = ["email", "username"]

        Result:
        {
            "scan_type": "sequential_scan",
            "estimated_rows": "many",
            "uses_index": False,
            "index_name": None,
            "recommendation": "Add index on age column"
        }
    """
    pass


def is_over_indexed(table_schema: dict, indexes: list[dict]) -> list[str]:
    """
    Check if a table has too many or ineffective indexes.

    Args:
        table_schema: Dict with table and columns
        indexes: List of index dicts with columns and metadata

    Returns:
        List of warning strings

    Check for:
        - Boolean columns indexed (low cardinality)
        - TEXT columns indexed (expensive)
        - More than 7 indexes (write performance impact)
        - Duplicate/redundant indexes

    Example:
        table_schema = {
            "table": "users",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "is_active", "type": "BOOLEAN"},
                {"name": "bio", "type": "TEXT"}
            ]
        }
        indexes = [
            {"columns": ["is_active"]},
            {"columns": ["bio"]},
            {"columns": ["id"]},
            {"columns": ["username"]},
            {"columns": ["email"]},
            {"columns": ["created_at"]},
            {"columns": ["updated_at"]},
            {"columns": ["last_login"]},
        ]

        Result:
        [
            "Index on 'is_active' has low cardinality (boolean) - consider removing",
            "Index on 'bio' (TEXT) is expensive - consider partial index",
            "Table has 8 indexes - write performance may suffer"
        ]
    """
    pass


# ============= TESTS =============


def test_suggest_indexes_where_clause():
    """Test suggesting index for WHERE clause."""
    table_schema = {"table": "users", "columns": ["id", "email", "username"]}
    queries = ["SELECT * FROM users WHERE email = 'alice@example.com'"]
    suggestions = suggest_indexes(table_schema, queries)

    assert len(suggestions) >= 1
    # Should suggest index on email
    email_indexes = [s for s in suggestions if "email" in s["columns"]]
    assert len(email_indexes) >= 1


def test_suggest_indexes_join():
    """Test suggesting index for JOIN conditions."""
    table_schema = {"table": "posts", "columns": ["id", "title", "author_id"]}
    queries = ["SELECT * FROM posts JOIN users ON posts.author_id = users.id"]
    suggestions = suggest_indexes(table_schema, queries)

    # Should suggest index on author_id
    fk_indexes = [s for s in suggestions if "author_id" in s["columns"]]
    assert len(fk_indexes) >= 1


def test_suggest_indexes_order_by():
    """Test suggesting index for ORDER BY."""
    table_schema = {"table": "posts", "columns": ["id", "title", "created_at"]}
    queries = ["SELECT * FROM posts ORDER BY created_at DESC"]
    suggestions = suggest_indexes(table_schema, queries)

    # Should suggest index on created_at
    sort_indexes = [s for s in suggestions if "created_at" in s["columns"]]
    assert len(sort_indexes) >= 1


def test_suggest_indexes_composite():
    """Test suggesting composite index for multi-column queries."""
    table_schema = {"table": "posts", "columns": ["id", "author_id", "is_published"]}
    queries = ["SELECT * FROM posts WHERE author_id = 1 AND is_published = true"]
    suggestions = suggest_indexes(table_schema, queries)

    # Should suggest composite index or individual indexes
    assert len(suggestions) >= 1


def test_estimate_query_cost_with_index():
    """Test cost estimation with index."""
    assert estimate_query_cost(True, 10000) == "index_scan"
    assert estimate_query_cost(True, 100) == "index_scan"


def test_estimate_query_cost_without_index():
    """Test cost estimation without index."""
    assert estimate_query_cost(False, 500) == "small_table_scan"
    assert estimate_query_cost(False, 5000) == "full_table_scan"
    assert estimate_query_cost(False, 1000) == "small_table_scan"
    assert estimate_query_cost(False, 1001) == "full_table_scan"


def test_analyze_query_plan_with_index():
    """Test query analysis when index exists."""
    query = "SELECT * FROM users WHERE email = 'alice@example.com'"
    indexes = ["email", "username"]
    result = analyze_query_plan(query, indexes)

    assert result["uses_index"] is True
    assert result["scan_type"] == "index_scan"
    assert result["index_name"] == "email"


def test_analyze_query_plan_without_index():
    """Test query analysis when index missing."""
    query = "SELECT * FROM users WHERE age > 18"
    indexes = ["email", "username"]
    result = analyze_query_plan(query, indexes)

    assert result["uses_index"] is False
    assert result["scan_type"] == "sequential_scan"
    assert "age" in result["recommendation"]


def test_is_over_indexed_boolean():
    """Test detection of boolean column indexes."""
    table_schema = {
        "table": "users",
        "columns": [
            {"name": "id", "type": "INTEGER"},
            {"name": "is_active", "type": "BOOLEAN"}
        ]
    }
    indexes = [{"columns": ["is_active"]}]
    warnings = is_over_indexed(table_schema, indexes)

    # Should warn about boolean index
    boolean_warnings = [w for w in warnings if "boolean" in w.lower() or "is_active" in w]
    assert len(boolean_warnings) >= 1


def test_is_over_indexed_text():
    """Test detection of TEXT column indexes."""
    table_schema = {
        "table": "posts",
        "columns": [
            {"name": "id", "type": "INTEGER"},
            {"name": "content", "type": "TEXT"}
        ]
    }
    indexes = [{"columns": ["content"]}]
    warnings = is_over_indexed(table_schema, indexes)

    # Should warn about TEXT index
    text_warnings = [w for w in warnings if "text" in w.lower() or "content" in w]
    assert len(text_warnings) >= 1


def test_is_over_indexed_too_many():
    """Test detection of too many indexes."""
    table_schema = {"table": "users", "columns": [{"name": f"col{i}", "type": "INTEGER"} for i in range(10)]}
    indexes = [{"columns": [f"col{i}"]} for i in range(8)]
    warnings = is_over_indexed(table_schema, indexes)

    # Should warn about too many indexes
    count_warnings = [w for w in warnings if "8 indexes" in w or "many" in w.lower()]
    assert len(count_warnings) >= 1


def test_is_over_indexed_no_warnings():
    """Test no warnings for reasonable index setup."""
    table_schema = {
        "table": "users",
        "columns": [
            {"name": "id", "type": "INTEGER"},
            {"name": "username", "type": "VARCHAR(50)"},
            {"name": "email", "type": "VARCHAR(255)"}
        ]
    }
    indexes = [
        {"columns": ["username"]},
        {"columns": ["email"]}
    ]
    warnings = is_over_indexed(table_schema, indexes)

    # Should have no warnings (or very few)
    assert len(warnings) <= 1
