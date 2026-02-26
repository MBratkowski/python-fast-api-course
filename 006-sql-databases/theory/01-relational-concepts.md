# Relational Database Concepts

## Why This Matters

In mobile development, you've likely used Core Data (iOS), Room (Android), or SQLite for local storage. These are all relational databases. The difference? Backend databases like PostgreSQL are shared across all users, enforcing schema at the database level rather than in your app code.

Think of it this way:
- **Mobile local database** = Single user, schema defined in code, lightweight
- **Backend database** = Multi-user, schema enforced by database, production-grade

Understanding relational concepts means you'll know exactly what your ORM (SQLAlchemy) is doing under the hood.

## What is a Relational Database?

A **relational database** organizes data into **tables** (like spreadsheets). Each table has:
- **Rows** = individual records (instances)
- **Columns** = fields/properties
- **Schema** = structure definition (enforced by database)

Example: A `users` table

| id | username | email | created_at |
|----|----------|-------|------------|
| 1  | alice    | alice@example.com | 2026-01-15 |
| 2  | bob      | bob@example.com   | 2026-02-20 |

This is similar to a Swift struct or Kotlin data class, but stored persistently and queryable.

## Tables and Schemas

In SQL, you **define** tables with `CREATE TABLE`:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Key parts:
- **Table name**: `users` (plural convention)
- **Columns**: `id`, `username`, `email`, `created_at`
- **Data types**: Define what each column can hold
- **Constraints**: Rules like NOT NULL, PRIMARY KEY

## Primary Keys

Every table needs a **primary key** - a unique identifier for each row.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- SERIAL = auto-incrementing integer
    username VARCHAR(50)
);
```

Think of it like:
- iOS: `NSManagedObjectID` in Core Data
- Android: Room's `@PrimaryKey`
- General: The unique ID you use to look up objects

**Best practice**: Use auto-incrementing integers (`SERIAL`) or UUIDs for primary keys.

## Data Types

Common PostgreSQL types (with mobile equivalents):

| SQL Type | Mobile Equivalent | Example |
|----------|------------------|---------|
| `INTEGER` | Int | `age INTEGER` |
| `BIGINT` | Long/Int64 | `user_id BIGINT` |
| `VARCHAR(n)` | String (limited) | `username VARCHAR(50)` |
| `TEXT` | String (unlimited) | `bio TEXT` |
| `BOOLEAN` | Bool | `is_active BOOLEAN` |
| `TIMESTAMP` | Date/DateTime | `created_at TIMESTAMP` |
| `DECIMAL(p,s)` | Decimal/Double | `price DECIMAL(10,2)` |
| `JSON` / `JSONB` | Dictionary/Map | `metadata JSONB` |

Example with multiple types:

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    view_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT false,
    rating DECIMAL(3,2),  -- e.g., 4.75
    published_at TIMESTAMP,
    metadata JSONB
);
```

## Constraints

Constraints enforce data integrity at the database level:

### NOT NULL
Column must always have a value (no nulls allowed).

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,  -- Required field
    bio TEXT  -- Optional field (can be NULL)
);
```

### UNIQUE
Value must be unique across all rows.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,  -- No duplicate usernames
    email VARCHAR(255) UNIQUE     -- No duplicate emails
);
```

### DEFAULT
Provides a default value if none is specified.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,  -- New users are active by default
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Auto-set creation time
);
```

### CHECK
Validates values against a condition.

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5)  -- Must be 1-5
);
```

## Mobile Dev Comparison

| Mobile Concept | SQL Equivalent | Example |
|---------------|----------------|---------|
| Entity/Model class | Table | `@Entity class User` → `CREATE TABLE users` |
| Object property | Column | `var name: String` → `name VARCHAR(50)` |
| Object instance | Row | `User(id=1, name="Alice")` → Row with id=1 |
| Required property | NOT NULL | `var email: String` → `email VARCHAR NOT NULL` |
| Optional property | Nullable column | `var bio: String?` → `bio TEXT` |
| Unique ID | PRIMARY KEY | `@PrimaryKey val id: Int` → `id SERIAL PRIMARY KEY` |

## Try This

Create a simple table for tracking books:

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    page_count INTEGER CHECK (page_count > 0),
    is_available BOOLEAN DEFAULT true,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This demonstrates:
- Auto-incrementing ID
- Required text fields
- Unique constraint (ISBN)
- Check constraint (pages must be positive)
- Default values

## Key Takeaways

1. **Tables** organize data into rows and columns (like classes and objects)
2. **Primary keys** uniquely identify each row (like object IDs)
3. **Data types** define what each column can hold (similar to type annotations)
4. **Constraints** enforce rules at the database level (NOT NULL, UNIQUE, DEFAULT, CHECK)
5. **Schema** is defined with `CREATE TABLE` and enforced by the database
6. Backend databases are multi-user and production-grade vs mobile local databases
