# SQL CRUD Operations

## Why This Matters

In your mobile app, you call methods like `dao.insert()`, `dao.getAll()`, or `fetchRequest.execute()`. Those ORMs are generating SQL queries behind the scenes. Understanding the actual SQL helps you write efficient queries, debug performance issues, and know what your ORM is really doing.

Think of it like this:
- **Mobile ORM**: `userDao.findByUsername("alice")`
- **SQL equivalent**: `SELECT * FROM users WHERE username = 'alice'`

Learning SQL first makes you a better ORM user.

## The Four Operations: CRUD

**CRUD** = Create, Read, Update, Delete

| Operation | SQL Command | Mobile Equivalent |
|-----------|-------------|------------------|
| Create | `INSERT` | `dao.insert()` / `context.insert()` |
| Read | `SELECT` | `dao.getAll()` / `fetchRequest` |
| Update | `UPDATE` | `dao.update()` / `object.save()` |
| Delete | `DELETE` | `dao.delete()` / `context.delete()` |

## INSERT: Creating Data

Add new rows to a table.

### Single row
```sql
INSERT INTO users (username, email)
VALUES ('alice', 'alice@example.com');
```

### Multiple rows
```sql
INSERT INTO users (username, email)
VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com');
```

### With RETURNING (PostgreSQL)
Get the inserted row back (including auto-generated ID):

```sql
INSERT INTO users (username, email)
VALUES ('alice', 'alice@example.com')
RETURNING id, username, email, created_at;
```

This is super useful - you get the database-generated ID and timestamps in one query.

## SELECT: Reading Data

Fetch rows from a table.

### Basic select
```sql
-- Get all columns, all rows
SELECT * FROM users;

-- Get specific columns
SELECT id, username, email FROM users;

-- Get one row
SELECT * FROM users WHERE id = 1;
```

**Note**: Avoid `SELECT *` in production - specify columns explicitly.

### WHERE Clause

Filter rows with conditions:

```sql
-- Exact match
SELECT * FROM users WHERE username = 'alice';

-- Comparison operators
SELECT * FROM posts WHERE view_count > 100;
SELECT * FROM posts WHERE rating >= 4.0;

-- String pattern matching (LIKE)
SELECT * FROM users WHERE email LIKE '%@gmail.com';

-- Multiple conditions (AND)
SELECT * FROM posts WHERE is_published = true AND view_count > 100;

-- Either/or conditions (OR)
SELECT * FROM users WHERE username = 'alice' OR username = 'bob';

-- IN list
SELECT * FROM users WHERE id IN (1, 2, 3);

-- BETWEEN range
SELECT * FROM posts WHERE view_count BETWEEN 100 AND 1000;

-- NULL checks
SELECT * FROM users WHERE bio IS NULL;
SELECT * FROM users WHERE bio IS NOT NULL;
```

### ORDER BY

Sort results:

```sql
-- Ascending (default)
SELECT * FROM users ORDER BY username;

-- Descending
SELECT * FROM posts ORDER BY created_at DESC;

-- Multiple columns
SELECT * FROM posts ORDER BY is_published DESC, created_at DESC;
```

### LIMIT and OFFSET

Pagination (like mobile infinite scroll):

```sql
-- First 10 results
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10;

-- Skip 10, get next 10 (page 2)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 10;

-- Skip 20, get next 10 (page 3)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 20;
```

Mobile equivalent:
```kotlin
// Android Room
@Query("SELECT * FROM posts ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
fun getPosts(limit: Int, offset: Int): List<Post>
```

### Aggregate Functions

Calculate values across rows:

```sql
-- Count rows
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM users WHERE is_active = true;

-- Sum
SELECT SUM(view_count) FROM posts;

-- Average
SELECT AVG(rating) FROM posts WHERE is_published = true;

-- Min and Max
SELECT MIN(created_at) FROM users;  -- First user
SELECT MAX(view_count) FROM posts;  -- Most viewed post
```

### GROUP BY

Group rows and aggregate:

```sql
-- Count posts per user
SELECT author_id, COUNT(*) as post_count
FROM posts
GROUP BY author_id;

-- Average rating per user
SELECT author_id, AVG(rating) as avg_rating
FROM posts
GROUP BY author_id;

-- Filter groups with HAVING
SELECT author_id, COUNT(*) as post_count
FROM posts
GROUP BY author_id
HAVING COUNT(*) >= 5;  -- Only users with 5+ posts
```

**WHERE vs HAVING**:
- `WHERE` filters individual rows before grouping
- `HAVING` filters groups after aggregation

```sql
-- Filter rows first, then group
SELECT author_id, COUNT(*) as post_count
FROM posts
WHERE is_published = true  -- Filter posts first
GROUP BY author_id
HAVING COUNT(*) >= 3;  -- Then filter groups
```

## UPDATE: Modifying Data

Change existing rows.

### Update specific rows
```sql
UPDATE users
SET email = 'newalice@example.com'
WHERE username = 'alice';
```

### Update multiple columns
```sql
UPDATE users
SET
    email = 'newalice@example.com',
    is_active = false
WHERE username = 'alice';
```

### Increment values
```sql
UPDATE posts
SET view_count = view_count + 1
WHERE id = 42;
```

### Update with RETURNING
```sql
UPDATE users
SET is_active = false
WHERE username = 'alice'
RETURNING id, username, is_active, updated_at;
```

**WARNING**: Always use `WHERE` with `UPDATE`! Without it, you'll update **every row**.

```sql
-- DANGER: Updates ALL users!
UPDATE users SET is_active = false;

-- SAFE: Updates one user
UPDATE users SET is_active = false WHERE id = 1;
```

## DELETE: Removing Data

Remove rows from a table.

### Delete specific rows
```sql
DELETE FROM users WHERE id = 1;
```

### Delete multiple rows
```sql
DELETE FROM posts WHERE view_count < 10;
```

### Delete with RETURNING
```sql
DELETE FROM users WHERE id = 1
RETURNING id, username;  -- See what was deleted
```

**WARNING**: Always use `WHERE` with `DELETE`! Without it, you'll delete **all rows**.

```sql
-- DANGER: Deletes ALL users!
DELETE FROM users;

-- SAFE: Deletes one user
DELETE FROM users WHERE id = 1;
```

## Complete Example

Let's create a users table and perform CRUD operations:

```sql
-- Create table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INSERT: Create users
INSERT INTO users (username, email)
VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com')
RETURNING *;

-- SELECT: Read users
SELECT * FROM users WHERE is_active = true;
SELECT username, email FROM users ORDER BY created_at DESC LIMIT 2;

-- UPDATE: Deactivate a user
UPDATE users
SET is_active = false
WHERE username = 'bob'
RETURNING *;

-- DELETE: Remove a user
DELETE FROM users
WHERE username = 'charlie'
RETURNING username, email;

-- SELECT: Verify changes
SELECT * FROM users;
```

## Common Patterns

### Check if exists
```sql
SELECT EXISTS(SELECT 1 FROM users WHERE username = 'alice');
-- Returns true or false
```

### Upsert (INSERT or UPDATE)
```sql
INSERT INTO users (id, username, email)
VALUES (1, 'alice', 'alice@example.com')
ON CONFLICT (id)
DO UPDATE SET email = EXCLUDED.email;
-- If id=1 exists, update email. Otherwise, insert.
```

### Count with conditions
```sql
SELECT
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE is_active = true) as active_users,
    COUNT(*) FILTER (WHERE is_active = false) as inactive_users
FROM users;
```

## Key Takeaways

1. **CRUD** = Create (INSERT), Read (SELECT), Update (UPDATE), Delete (DELETE)
2. **WHERE** clause filters rows - always use it with UPDATE/DELETE to avoid affecting all rows
3. **ORDER BY** sorts results, **LIMIT/OFFSET** handles pagination
4. **Aggregate functions** (COUNT, SUM, AVG, MIN, MAX) calculate across rows
5. **GROUP BY** groups rows for aggregation, **HAVING** filters groups
6. **RETURNING** clause (PostgreSQL) returns modified rows in one query
7. Be explicit with columns in SELECT - avoid `SELECT *` in production code
