# Table Relationships

## Why This Matters

In mobile development, you nest objects or use IDs to reference related data:

```swift
// iOS
class User {
    var id: Int
    var posts: [Post]  // Array of related objects
}

class Post {
    var id: Int
    var authorId: Int  // Reference to User
}
```

In SQL, **foreign keys** formalize these references. The database enforces them, preventing orphaned data (like a post with a non-existent author). This is more robust than app-level validation alone.

## Three Types of Relationships

| Type | Description | Example |
|------|-------------|---------|
| **One-to-One** | Each row relates to exactly one row in another table | User ↔ Profile |
| **One-to-Many** | One row relates to many rows in another table | User → Posts |
| **Many-to-Many** | Many rows relate to many rows | Students ↔ Courses |

## One-to-One Relationships

Each user has **exactly one** profile, and each profile belongs to **exactly one** user.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,  -- UNIQUE enforces 1:1
    bio TEXT,
    avatar_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

Key points:
- `user_id` is a **foreign key** referencing `users(id)`
- `UNIQUE` constraint on `user_id` ensures one profile per user
- `ON DELETE CASCADE` means deleting a user also deletes their profile

Mobile equivalent:
```kotlin
// Android Room
@Entity
data class User(
    @PrimaryKey val id: Int,
    val username: String
)

@Entity
data class Profile(
    @PrimaryKey val id: Int,
    val userId: Int,  // Foreign key
    val bio: String?
)
```

## One-to-Many Relationships

One user can have **many** posts, but each post belongs to **one** user.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,  -- Foreign key (no UNIQUE)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);
```

Key points:
- `author_id` is a **foreign key** referencing `users(id)`
- No `UNIQUE` on `author_id` (one user can have many posts)
- `ON DELETE CASCADE` means deleting a user also deletes all their posts

Insert example:
```sql
-- Insert user
INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com') RETURNING id;
-- Assume id = 1

-- Insert posts for that user
INSERT INTO posts (title, content, author_id)
VALUES
    ('First Post', 'Hello world', 1),
    ('Second Post', 'More content', 1);
```

Mobile equivalent:
```swift
// iOS Core Data
class User: NSManagedObject {
    @NSManaged var id: Int
    @NSManaged var posts: Set<Post>  // One-to-many
}

class Post: NSManagedObject {
    @NSManaged var id: Int
    @NSManaged var author: User  // Many-to-one (inverse)
}
```

## Many-to-Many Relationships

Students can enroll in **many** courses, and courses can have **many** students.

This requires a **junction table** (also called join table, association table, or pivot table):

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL
);

-- Junction table
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE (student_id, course_id)  -- Prevent duplicate enrollments
);
```

Key points:
- `enrollments` is the **junction table** linking students and courses
- Two foreign keys: `student_id` and `course_id`
- `UNIQUE (student_id, course_id)` prevents a student enrolling in the same course twice
- Can add extra fields like `enrolled_at`, `grade`, etc.

Insert example:
```sql
-- Insert students
INSERT INTO students (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');

-- Insert courses
INSERT INTO courses (title, code) VALUES
    ('Python Backend', 'PY101'),
    ('Database Design', 'DB201');

-- Enroll students in courses
INSERT INTO enrollments (student_id, course_id) VALUES
    (1, 1),  -- Alice in Python Backend
    (1, 2),  -- Alice in Database Design
    (2, 1);  -- Bob in Python Backend
```

Query example (see who's in Python Backend):
```sql
SELECT s.name, c.title
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id
WHERE c.code = 'PY101';
```

Mobile equivalent:
```kotlin
// Android Room (many-to-many)
@Entity
data class Student(
    @PrimaryKey val id: Int,
    val name: String
)

@Entity
data class Course(
    @PrimaryKey val id: Int,
    val title: String
)

@Entity(
    foreignKeys = [
        ForeignKey(entity = Student::class, parentColumns = ["id"], childColumns = ["studentId"]),
        ForeignKey(entity = Course::class, parentColumns = ["id"], childColumns = ["courseId"])
    ]
)
data class Enrollment(
    @PrimaryKey val id: Int,
    val studentId: Int,
    val courseId: Int
)
```

## Foreign Key Actions

When a referenced row is deleted or updated, what happens to rows that reference it?

```sql
FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE <action>
```

| Action | Behavior | Use Case |
|--------|----------|----------|
| `CASCADE` | Delete/update referencing rows too | Delete user → delete all their posts |
| `SET NULL` | Set foreign key to NULL | Delete user → set post author_id to NULL |
| `RESTRICT` | Prevent deletion if references exist | Can't delete user with posts |
| `NO ACTION` | Same as RESTRICT (default) | |
| `SET DEFAULT` | Set foreign key to default value | Rarely used |

Examples:

```sql
-- CASCADE: Deleting user deletes their posts
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- SET NULL: Deleting user keeps posts but nulls author_id
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER,  -- Must be nullable
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- RESTRICT: Can't delete user if they have posts
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE RESTRICT
);
```

## Normalization

**Normalization** = organizing data to reduce redundancy.

### Bad: Denormalized (duplicate data)
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    author_name VARCHAR(100),     -- Duplicated!
    author_email VARCHAR(255),    -- Duplicated!
    author_bio TEXT               -- Duplicated!
);
```

Problems:
- Author data duplicated in every post
- Updating author email requires updating all their posts
- Inconsistent data if one post has wrong email

### Good: Normalized (use foreign keys)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    bio TEXT
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id)
);
```

Benefits:
- Author data stored once
- Update author email in one place
- No data inconsistency

## Relationship Examples

### Blog Platform
```sql
-- One-to-many: User → Posts
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- One-to-many: Post → Comments
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Many-to-many: Posts ↔ Tags
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

## Key Takeaways

1. **Foreign keys** formalize relationships between tables
2. **One-to-One**: Use UNIQUE constraint on foreign key (User ↔ Profile)
3. **One-to-Many**: Foreign key without UNIQUE (User → Posts)
4. **Many-to-Many**: Requires junction table with two foreign keys (Students ↔ Courses)
5. **ON DELETE CASCADE** deletes related rows when parent is deleted
6. **ON DELETE SET NULL** keeps related rows but nulls the foreign key
7. **Normalization** reduces data duplication by using foreign keys
8. Junction tables can have additional columns (enrolled_at, grade, etc.)
