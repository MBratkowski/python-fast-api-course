# Module 006: SQL & Database Fundamentals

## Why This Module?

Every backend needs persistent storage. Learn SQL and PostgreSQL - the most common production database for Python APIs.

## What You'll Learn

- SQL fundamentals (SELECT, INSERT, UPDATE, DELETE)
- Table design & relationships
- Joins and queries
- Indexes for performance
- PostgreSQL specifics
- Database design patterns

## Topics

### Theory
1. Relational Database Concepts
2. SQL CRUD Operations
3. Table Relationships (1:1, 1:N, N:M)
4. Joins Explained
5. Indexes & Performance
6. PostgreSQL Setup & psql

### Exercises
- Write SQL queries
- Design normalized schemas
- Optimize queries with indexes

### Project
Design and implement the database schema for a blog platform.

## Quick Reference

```sql
-- Create table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CRUD operations
SELECT * FROM users WHERE id = 1;
INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com');
UPDATE users SET email = 'new@example.com' WHERE id = 1;
DELETE FROM users WHERE id = 1;

-- Join
SELECT posts.title, users.username
FROM posts
JOIN users ON posts.user_id = users.id;
```
