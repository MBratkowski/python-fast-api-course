# Project: Blog Platform Database Schema

## Overview

Design and implement the complete database schema for a blog platform. This project brings together everything from Module 006: table design, relationships, SQL queries, and index optimization.

You'll create tables, write CREATE TABLE statements, insert seed data, write analytical queries, and design indexes for performance.

## Requirements

### 1. Design Tables

Create schemas for the following tables with appropriate columns and constraints:

**users**
- id (primary key, auto-increment)
- username (unique, not null, max 50 chars)
- email (unique, not null, max 255 chars)
- bio (text, optional)
- created_at (timestamp, default current time)

**posts**
- id (primary key, auto-increment)
- title (not null, max 200 chars)
- content (text, not null)
- author_id (foreign key to users, not null, cascade on delete)
- category_id (foreign key to categories, optional, set null on delete)
- view_count (integer, default 0)
- is_published (boolean, default false)
- created_at (timestamp, default current time)

**categories**
- id (primary key, auto-increment)
- name (unique, not null, max 50 chars)
- description (text, optional)

**tags**
- id (primary key, auto-increment)
- name (unique, not null, max 50 chars)

**post_tags** (junction table for many-to-many)
- post_id (foreign key to posts, cascade on delete)
- tag_id (foreign key to tags, cascade on delete)
- Primary key: (post_id, tag_id) composite

**comments**
- id (primary key, auto-increment)
- content (text, not null)
- post_id (foreign key to posts, not null, cascade on delete)
- author_id (foreign key to users, not null, cascade on delete)
- parent_id (foreign key to comments, optional, cascade on delete - for nested replies)
- created_at (timestamp, default current time)

### 2. Write CREATE TABLE Statements

Write the SQL CREATE TABLE statements for all 6 tables with:
- Proper data types
- Primary keys
- Foreign keys with ON DELETE actions
- UNIQUE and NOT NULL constraints
- DEFAULT values

### 3. Insert Seed Data

Write INSERT statements for:
- 3 users (alice, bob, charlie)
- 3 categories (Technology, Lifestyle, Travel)
- 5 posts (distributed across authors and categories)
- 5 tags (python, sql, tutorial, beginner, advanced)
- Tag assignments (connect posts to tags via post_tags)
- 8 comments (including at least 2 nested replies using parent_id)

### 4. Write Analytical Queries

Write SQL queries for the following:

1. **Get all posts by a specific user** (with user info)
2. **Get all posts in a category** (with author and category names)
3. **Get posts with comment count** (ordered by most commented)
4. **Get most active commenters** (users with most comments)
5. **Get recent posts with full details** (author, category, tags - last 7 days)

Each query should use appropriate JOINs, WHERE clauses, and aggregations.

### 5. Design Indexes

Identify and create indexes for:
- Foreign keys (author_id, category_id, post_id, tag_id, parent_id)
- Frequently queried columns (username, email, category name)
- Sort columns (created_at for posts and comments)
- Composite indexes where beneficial

## Starter Template

Create a `blog_schema.sql` file with the following structure:

```sql
-- ============================================
-- Blog Platform Database Schema
-- ============================================

-- TODO: Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS post_tags CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- CREATE TABLES
-- ============================================

-- TODO: Create users table
CREATE TABLE users (
    -- Add columns here
);

-- TODO: Create categories table
CREATE TABLE categories (
    -- Add columns here
);

-- TODO: Create posts table
CREATE TABLE posts (
    -- Add columns here
);

-- TODO: Create tags table
CREATE TABLE tags (
    -- Add columns here
);

-- TODO: Create post_tags junction table
CREATE TABLE post_tags (
    -- Add columns here
);

-- TODO: Create comments table with parent_id for nested replies
CREATE TABLE comments (
    -- Add columns here
);

-- ============================================
-- SEED DATA
-- ============================================

-- TODO: Insert users
INSERT INTO users (username, email, bio) VALUES
    -- Add user data
;

-- TODO: Insert categories
INSERT INTO categories (name, description) VALUES
    -- Add category data
;

-- TODO: Insert posts
INSERT INTO posts (title, content, author_id, category_id, is_published) VALUES
    -- Add post data
;

-- TODO: Insert tags
INSERT INTO tags (name) VALUES
    -- Add tag data
;

-- TODO: Insert post-tag associations
INSERT INTO post_tags (post_id, tag_id) VALUES
    -- Add associations
;

-- TODO: Insert comments (including nested replies)
INSERT INTO comments (content, post_id, author_id, parent_id) VALUES
    -- Add comments (parent_id NULL for top-level, comment.id for replies)
;

-- ============================================
-- ANALYTICAL QUERIES
-- ============================================

-- Query 1: Get all posts by a specific user (alice)
-- TODO: Write query with JOIN to get username

-- Query 2: Get all posts in "Technology" category
-- TODO: Write query with JOINs for author and category names

-- Query 3: Get posts with comment count (ordered by most commented)
-- TODO: Write query with LEFT JOIN and COUNT

-- Query 4: Get most active commenters (top 3)
-- TODO: Write query with GROUP BY and COUNT

-- Query 5: Get recent posts with full details (last 7 days)
-- TODO: Write query with multiple JOINs and STRING_AGG for tags

-- ============================================
-- INDEXES
-- ============================================

-- TODO: Create indexes for foreign keys
-- CREATE INDEX idx_posts_author_id ON posts(author_id);

-- TODO: Create indexes for WHERE clauses
-- CREATE INDEX idx_users_username ON users(username);

-- TODO: Create indexes for ORDER BY
-- CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- TODO: Create composite indexes where beneficial
```

## Success Criteria

- [ ] All 6 tables created with proper schemas
- [ ] Foreign keys have appropriate ON DELETE actions (CASCADE or SET NULL)
- [ ] Seed data inserted successfully (3 users, 3 categories, 5 posts, 5 tags, 8 comments)
- [ ] Junction table (post_tags) connects posts and tags with composite primary key
- [ ] Comments table supports nested replies via parent_id
- [ ] All 5 analytical queries return correct results
- [ ] Queries use appropriate JOIN types (INNER, LEFT)
- [ ] Aggregate functions used correctly (COUNT, STRING_AGG)
- [ ] Indexes created for all foreign keys
- [ ] Indexes created for frequently queried/sorted columns
- [ ] Schema can be executed multiple times (DROP TABLE IF EXISTS)

## Testing Your Schema

Run your schema file in PostgreSQL:

```bash
# Start PostgreSQL (Docker)
docker-compose up -d

# Execute schema
docker-compose exec -T postgres psql -U admin -d backend_dev < blog_schema.sql

# Or from psql
psql -U admin -d backend_dev
\i blog_schema.sql
```

Verify:
```sql
-- List tables
\dt

-- Check table schemas
\d users
\d posts
\d comments

-- Run your analytical queries
-- Should return expected data
```

## Stretch Goals

1. **Full-Text Search**: Add GIN index on post content for search
   ```sql
   CREATE INDEX idx_posts_content_search ON posts USING GIN (to_tsvector('english', content));
   ```

2. **View Tracking**: Add a `post_views` table to track individual views with timestamps
   - Columns: id, post_id, user_id (nullable for anonymous), viewed_at
   - Query: "Most viewed posts in last 30 days"

3. **Related Posts**: Write a query to find "related posts" based on shared tags
   - Input: post_id
   - Output: Other posts with most tag overlap, ordered by overlap count

4. **User Activity Summary**: Write a query for user profile with:
   - Total posts published
   - Total comments written
   - Most used category
   - Most used tag

5. **Database Functions**: Create a PostgreSQL function to automatically increment post view_count
   ```sql
   CREATE OR REPLACE FUNCTION increment_view_count(p_post_id INTEGER)
   RETURNS void AS $$
   BEGIN
       UPDATE posts SET view_count = view_count + 1 WHERE id = p_post_id;
   END;
   $$ LANGUAGE plpgsql;
   ```

## Learning Outcomes

After completing this project, you'll be able to:

- Design normalized database schemas with proper relationships
- Choose appropriate data types and constraints
- Use foreign keys with correct ON DELETE behavior
- Write complex queries with multiple JOINs and aggregations
- Handle many-to-many relationships with junction tables
- Implement hierarchical data (nested comments) with self-referencing foreign keys
- Optimize queries with strategic index placement
- Understand trade-offs between normalization and query complexity

This is the foundation for Module 007 (SQLAlchemy ORM) and Module 008 (CRUD APIs).
