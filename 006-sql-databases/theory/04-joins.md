# Joins Explained

## Why This Matters

In mobile development, you often combine data from multiple sources:

```swift
// iOS - Merge two arrays
let users = fetchUsers()
let posts = fetchPosts()
let usersWithPosts = users.map { user in
    (user, posts.filter { $0.authorId == user.id })
}
```

SQL **JOINs** do this at the database level - way more efficient than fetching everything and filtering in code. Think of JOINs as "combining two tables based on a matching condition."

## INNER JOIN

Returns rows where there's a **match in both tables**.

### Syntax
```sql
SELECT columns
FROM table1
INNER JOIN table2 ON table1.column = table2.column;
```

### Example: Users with their posts
```sql
SELECT
    users.username,
    posts.title,
    posts.created_at
FROM users
INNER JOIN posts ON users.id = posts.author_id
ORDER BY posts.created_at DESC;
```

**Visual representation:**
```
users:               posts:
id | username        id | title     | author_id
1  | alice           1  | Post A    | 1
2  | bob             2  | Post B    | 1
3  | charlie         3  | Post C    | 2

Result (INNER JOIN on author_id = id):
username | title   | created_at
alice    | Post A  | 2026-02-20
alice    | Post B  | 2026-02-21
bob      | Post C  | 2026-02-22

(charlie is excluded - no posts)
```

**When to use**: When you only want rows that have matching data in both tables (e.g., "users who have posted").

## LEFT JOIN (LEFT OUTER JOIN)

Returns **all rows from the left table**, plus matching rows from the right table. If no match, right side is NULL.

### Syntax
```sql
SELECT columns
FROM table1
LEFT JOIN table2 ON table1.column = table2.column;
```

### Example: All users with their post count
```sql
SELECT
    users.username,
    COUNT(posts.id) as post_count
FROM users
LEFT JOIN posts ON users.id = posts.author_id
GROUP BY users.id, users.username
ORDER BY post_count DESC;
```

**Visual representation:**
```
users:               posts:
id | username        id | title     | author_id
1  | alice           1  | Post A    | 1
2  | bob             2  | Post B    | 1
3  | charlie         3  | Post C    | 2

Result (LEFT JOIN on author_id = id):
username | post_count
alice    | 2
bob      | 1
charlie  | 0  ← Included even though no posts!
```

**When to use**: When you want all rows from the first table, even if they don't have related data (e.g., "all users, including those without posts").

## RIGHT JOIN (RIGHT OUTER JOIN)

Returns **all rows from the right table**, plus matching rows from the left table. If no match, left side is NULL.

### Syntax
```sql
SELECT columns
FROM table1
RIGHT JOIN table2 ON table1.column = table2.column;
```

### Example: All posts with user info (including orphaned posts)
```sql
SELECT
    posts.title,
    users.username
FROM users
RIGHT JOIN posts ON users.id = posts.author_id;
```

**Visual representation:**
```
users:               posts:
id | username        id | title     | author_id
1  | alice           1  | Post A    | 1
2  | bob             2  | Post B    | 99  ← Author doesn't exist!

Result (RIGHT JOIN):
title   | username
Post A  | alice
Post B  | NULL  ← Post exists but no matching user
```

**When to use**: Rarely needed - usually you can rewrite as LEFT JOIN. Useful for finding orphaned records (posts without valid authors).

**Note**: `LEFT JOIN` is more common. `RIGHT JOIN` can always be rewritten as a `LEFT JOIN` by swapping table order.

## FULL OUTER JOIN

Returns **all rows from both tables**. If no match, fills missing side with NULL.

### Syntax
```sql
SELECT columns
FROM table1
FULL OUTER JOIN table2 ON table1.column = table2.column;
```

### Example: All users and posts (whether matched or not)
```sql
SELECT
    users.username,
    posts.title
FROM users
FULL OUTER JOIN posts ON users.id = posts.author_id;
```

**Visual representation:**
```
users:               posts:
id | username        id | title     | author_id
1  | alice           1  | Post A    | 1
2  | bob             2  | Post B    | 99

Result (FULL OUTER JOIN):
username | title
alice    | Post A
bob      | NULL    ← User with no posts
NULL     | Post B  ← Post with no valid author
```

**When to use**: When you need to see everything, including unmatched rows on both sides. Uncommon in typical applications.

## CROSS JOIN

Returns the **Cartesian product** - every row from table1 combined with every row from table2.

### Syntax
```sql
SELECT columns
FROM table1
CROSS JOIN table2;
```

### Example: All possible user-course combinations
```sql
SELECT
    students.name,
    courses.title
FROM students
CROSS JOIN courses;
```

**Visual representation:**
```
students:            courses:
id | name            id | title
1  | Alice           1  | Python
2  | Bob             2  | SQL

Result (CROSS JOIN):
name  | title
Alice | Python
Alice | SQL
Bob   | Python
Bob   | SQL
```

**When to use**: Generating all possible combinations. **Rarely used** - be careful with large tables (1000 × 1000 = 1 million rows!).

## JOIN Types Summary

```
INNER JOIN:
┌─────────┐
│  Left   │
│   ∩     │ ← Only matching rows
│  Right  │
└─────────┘

LEFT JOIN:
┌─────────┐
│  Left   │ ← All left rows
│   ∩     │   + matching right
│ (Right) │
└─────────┘

RIGHT JOIN:
┌─────────┐
│ (Left)  │
│   ∩     │   + matching left
│  Right  │ ← All right rows
└─────────┘

FULL OUTER JOIN:
┌─────────┐
│  Left   │ ← All left rows
│   ∩     │   + all right rows
│  Right  │   + all matches
└─────────┘
```

## Practical Examples

### Example 1: User posts with comment count
```sql
SELECT
    users.username,
    posts.title,
    COUNT(comments.id) as comment_count
FROM posts
INNER JOIN users ON posts.author_id = users.id
LEFT JOIN comments ON posts.id = comments.post_id
GROUP BY posts.id, users.username, posts.title
ORDER BY comment_count DESC;
```

This combines:
- INNER JOIN to get post authors (only posts with valid users)
- LEFT JOIN to count comments (including posts with 0 comments)

### Example 2: Find users without posts
```sql
SELECT users.username
FROM users
LEFT JOIN posts ON users.id = posts.author_id
WHERE posts.id IS NULL;
```

This uses LEFT JOIN + WHERE to find rows with no match.

### Example 3: Recent posts with author and tags
```sql
SELECT
    posts.title,
    users.username,
    STRING_AGG(tags.name, ', ') as tags
FROM posts
INNER JOIN users ON posts.author_id = users.id
LEFT JOIN post_tags ON posts.id = post_tags.post_id
LEFT JOIN tags ON post_tags.tag_id = tags.id
WHERE posts.created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY posts.id, posts.title, users.username
ORDER BY posts.created_at DESC;
```

This chains multiple JOINs:
- INNER JOIN for authors
- LEFT JOINs for optional tags (posts might not have tags)
- STRING_AGG combines tags into a comma-separated list

## Table Aliases

Use aliases to make queries more readable:

```sql
SELECT
    u.username,
    p.title,
    COUNT(c.id) as comment_count
FROM users u  -- Alias: u
INNER JOIN posts p ON u.id = p.author_id  -- Alias: p
LEFT JOIN comments c ON p.id = c.post_id  -- Alias: c
GROUP BY u.username, p.title;
```

**Best practice**: Use short, meaningful aliases (u for users, p for posts).

## Self-Joins

Join a table to itself (useful for hierarchical data like comments with replies):

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    parent_id INTEGER,  -- NULL for top-level, comment.id for replies
    FOREIGN KEY (parent_id) REFERENCES comments(id)
);

-- Get replies to a specific comment
SELECT
    c1.content as original_comment,
    c2.content as reply
FROM comments c1
INNER JOIN comments c2 ON c1.id = c2.parent_id
WHERE c1.id = 42;
```

## Mobile Dev Comparison

| Mobile Pattern | SQL Equivalent |
|----------------|----------------|
| `posts.filter { $0.authorId == user.id }` | `INNER JOIN posts ON users.id = posts.author_id` |
| `users.map { user in (user, postsForUser) }` | `LEFT JOIN posts ON users.id = posts.author_id` |
| Fetching related objects separately | JOIN fetches in one query (more efficient) |

## Performance Tips

1. **Index foreign keys** - JOINs are faster with indexes on join columns
2. **Filter before joining** - Use WHERE on individual tables first
3. **Select only needed columns** - Avoid `SELECT *` in JOINs
4. **Use INNER JOIN when possible** - Faster than LEFT/RIGHT JOIN

## Key Takeaways

1. **INNER JOIN** returns only matching rows from both tables (most common)
2. **LEFT JOIN** returns all left table rows + matches (use for "include all X")
3. **RIGHT JOIN** returns all right table rows + matches (rarely used)
4. **FULL OUTER JOIN** returns all rows from both tables (uncommon)
5. **CROSS JOIN** returns Cartesian product (use cautiously)
6. **Table aliases** (u, p, c) make multi-table queries readable
7. **Self-joins** join a table to itself (hierarchical data)
8. JOINs at the database level are more efficient than filtering in app code
