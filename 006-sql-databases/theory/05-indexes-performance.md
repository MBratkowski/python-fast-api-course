# Indexes and Performance

## Why This Matters

Imagine searching for a word in a book without an index - you'd have to scan every page. Databases face the same problem. An **index** is like a book's index: it lets the database find rows quickly without scanning the entire table.

In mobile development, you've probably seen this:
```kotlin
// Android Room - Add index for faster queries
@Entity(indices = [Index(value = ["email"])])
data class User(
    @PrimaryKey val id: Int,
    val email: String
)
```

That `@Index` annotation creates a database index. Understanding indexes helps you write queries that scale from 100 rows to 1 million rows.

## What is an Index?

An **index** is a data structure that improves query speed, like:
- A book's index (word → page numbers)
- A phone book (sorted by name for fast lookup)
- A library catalog (organized for quick searching)

**Without index** (full table scan):
```
Query: SELECT * FROM users WHERE email = 'alice@example.com'
Database: Checks row 1, row 2, row 3... row 1,000,000 ❌ Slow!
```

**With index** on email:
```
Query: SELECT * FROM users WHERE email = 'alice@example.com'
Database: Looks up email in index → jumps directly to matching row ✅ Fast!
```

## Creating Indexes

### Basic syntax
```sql
CREATE INDEX index_name ON table_name (column_name);
```

### Examples
```sql
-- Index on single column
CREATE INDEX idx_users_email ON users(email);

-- Index on multiple columns (composite index)
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at);

-- Unique index (also enforces uniqueness)
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Partial index (only index rows matching condition)
CREATE INDEX idx_active_users_email ON users(email) WHERE is_active = true;
```

**Note**: Primary keys and UNIQUE constraints automatically create indexes.

## When to Add Indexes

Add indexes on columns used in:

### 1. WHERE clauses
```sql
-- Query
SELECT * FROM users WHERE email = 'alice@example.com';

-- Add index
CREATE INDEX idx_users_email ON users(email);
```

### 2. JOIN conditions
```sql
-- Query
SELECT * FROM posts
INNER JOIN users ON posts.author_id = users.id;

-- Add indexes
CREATE INDEX idx_posts_author_id ON posts(author_id);
-- Note: users.id is already indexed (primary key)
```

### 3. ORDER BY columns
```sql
-- Query
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10;

-- Add index
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

### 4. Frequently queried columns
```sql
-- Common query pattern
SELECT * FROM posts WHERE is_published = true AND category = 'tech';

-- Add composite index
CREATE INDEX idx_posts_published_category ON posts(is_published, category);
```

## When NOT to Index

Indexes aren't free - they cost storage and slow down writes. **Don't index** when:

### 1. Small tables
If a table has < 1000 rows, full table scans are fast enough. Indexes add overhead without benefit.

### 2. Rarely queried columns
```sql
-- Bad: This column is rarely used in WHERE clauses
CREATE INDEX idx_users_bio ON users(bio);
```

### 3. Columns with low cardinality
**Cardinality** = number of distinct values.

```sql
-- Bad: Only 2 possible values (true/false)
CREATE INDEX idx_users_is_active ON users(is_active);
```

Boolean columns have low cardinality - indexes don't help much. Exception: partial indexes.

```sql
-- Better: Partial index for active users only
CREATE INDEX idx_active_users ON users(id) WHERE is_active = true;
```

### 4. Frequently updated columns
Each UPDATE/INSERT/DELETE must update all indexes on that table. Too many indexes slow down writes.

**Rule of thumb**: Start with 3-5 indexes per table. Add more only if profiling shows benefit.

## Composite Indexes

Index multiple columns together (order matters!):

```sql
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at);
```

This index helps queries like:

```sql
-- ✅ Uses index (author_id is first column)
SELECT * FROM posts WHERE author_id = 1;

-- ✅ Uses index (both columns)
SELECT * FROM posts WHERE author_id = 1 AND created_at > '2026-01-01';

-- ✅ Uses index (leftmost columns)
SELECT * FROM posts WHERE author_id = 1 ORDER BY created_at DESC;

-- ❌ Doesn't use index (created_at is not first column)
SELECT * FROM posts WHERE created_at > '2026-01-01';
```

**Leftmost prefix rule**: Composite index `(a, b, c)` can be used for queries on `a`, `a+b`, or `a+b+c`, but not `b`, `c`, or `b+c`.

## Index Types

PostgreSQL supports several index types:

| Type | Description | Use Case |
|------|-------------|----------|
| **B-tree** | Default, balanced tree | Most queries (=, <, >, <=, >=, BETWEEN) |
| **Hash** | Hash table | Equality only (=) |
| **GIN** | Generalized Inverted | Full-text search, JSON, arrays |
| **GiST** | Generalized Search Tree | Geometric data, full-text |
| **BRIN** | Block Range Index | Very large tables, sequential data |

**Default is B-tree** - use it unless you have a specific reason not to.

```sql
-- Explicit B-tree (default)
CREATE INDEX idx_users_email ON users USING BTREE (email);

-- Hash index (equality only)
CREATE INDEX idx_users_username ON users USING HASH (username);

-- GIN index for full-text search
CREATE INDEX idx_posts_content_search ON posts USING GIN (to_tsvector('english', content));
```

## Analyzing Query Performance

Use `EXPLAIN` to see if a query uses indexes:

```sql
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
```

Output (without index):
```
Seq Scan on users  (cost=0.00..15.00 rows=1 width=100)
  Filter: (email = 'alice@example.com'::text)
```

`Seq Scan` = **sequential scan** (full table scan) ❌ Slow!

Output (with index):
```
Index Scan using idx_users_email on users  (cost=0.29..8.30 rows=1 width=100)
  Index Cond: (email = 'alice@example.com'::text)
```

`Index Scan` = using index ✅ Fast!

### Use EXPLAIN ANALYZE for actual execution
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';
```

Shows actual query time and row counts.

## Real-World Example

Let's optimize a slow query:

```sql
-- Slow query: Find recent posts by active users
SELECT
    posts.title,
    posts.created_at,
    users.username
FROM posts
INNER JOIN users ON posts.author_id = users.id
WHERE
    users.is_active = true
    AND posts.created_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY posts.created_at DESC
LIMIT 10;
```

**Step 1**: Check current performance
```sql
EXPLAIN ANALYZE <query>;
```

**Step 2**: Add indexes based on WHERE, JOIN, ORDER BY
```sql
-- Index for JOIN condition (foreign key)
CREATE INDEX idx_posts_author_id ON posts(author_id);

-- Index for ORDER BY + date filter
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- Partial index for active users
CREATE INDEX idx_active_users ON users(id) WHERE is_active = true;
```

**Step 3**: Re-run EXPLAIN ANALYZE to verify improvement

## Index Maintenance

### View existing indexes
```sql
-- All indexes on a table
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'users';
```

### Drop unused indexes
```sql
DROP INDEX idx_users_bio;
```

### Rebuild indexes (if they become fragmented)
```sql
REINDEX INDEX idx_users_email;
REINDEX TABLE users;  -- Rebuild all indexes on table
```

## Over-Indexing Example

**Bad**: Too many indexes
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(255),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    bio TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP
);

-- 10 indexes! Way too many!
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);
CREATE INDEX idx_first_name ON users(first_name);
CREATE INDEX idx_last_name ON users(last_name);
CREATE INDEX idx_bio ON users(bio);
CREATE INDEX idx_is_active ON users(is_active);
CREATE INDEX idx_created_at ON users(created_at);
CREATE INDEX idx_name ON users(first_name, last_name);
CREATE INDEX idx_active_created ON users(is_active, created_at);
CREATE INDEX idx_search ON users(username, email);
```

**Good**: Strategic indexes
```sql
-- Only 3 indexes based on actual query patterns
CREATE UNIQUE INDEX idx_users_username ON users(username);  -- Unique constraint
CREATE UNIQUE INDEX idx_users_email ON users(email);  -- Unique constraint
CREATE INDEX idx_users_created_at ON users(created_at DESC);  -- For sorting recent users
```

## Mobile Dev Comparison

| Mobile Context | SQL Context |
|---------------|-------------|
| `@Index(value = ["email"])` in Room | `CREATE INDEX idx_users_email ON users(email)` |
| Core Data fetch request with predicate | SQL WHERE clause (index helps both) |
| Sorting large lists in memory | ORDER BY with index (much faster) |
| Manual filtering of arrays | Database index does it automatically |

## Performance Rules of Thumb

1. **Index foreign keys** - Almost always beneficial for JOINs
2. **Index WHERE columns** - If used in > 50% of queries
3. **Composite indexes** - For multi-column WHERE clauses
4. **Don't over-index** - More indexes = slower writes
5. **Profile first** - Use EXPLAIN ANALYZE before adding indexes
6. **Partial indexes** - For subset queries (e.g., WHERE is_active = true)

## Key Takeaways

1. **Indexes** speed up reads by creating lookup structures (like a book's index)
2. **Add indexes** on columns in WHERE, JOIN, ORDER BY clauses
3. **Don't index** small tables, rarely-queried columns, low-cardinality columns
4. **Composite indexes** follow leftmost prefix rule (order matters!)
5. **B-tree** is the default index type (covers most use cases)
6. **EXPLAIN** shows if a query uses indexes (Seq Scan = bad, Index Scan = good)
7. **Trade-off**: Indexes speed up reads but slow down writes
8. **Over-indexing** hurts performance - start with 3-5 indexes per table
