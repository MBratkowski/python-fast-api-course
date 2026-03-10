# Database Schema Design

## Why This Matters

In mobile development, you think about data models constantly -- Core Data entities in iOS, Room entities in Android. But there is a critical difference: mobile databases are local caches with eventual consistency, while your backend database is the source of truth with strict consistency guarantees. Every row matters. Every relationship constraint prevents a bug.

Schema design is where your API design meets reality. You can draw the most elegant endpoint diagram, but if the database cannot support it efficiently, your API will be slow, inconsistent, or both. A missing index means a 30-second query. A missing foreign key means orphaned records. A missing unique constraint means duplicate accounts.

This file synthesizes Modules 006-008 into a schema design workflow that starts from your API endpoints and produces a migration-ready database plan.

## Quick Review

- **SQL fundamentals** (Module 006): Tables, columns, types, constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL). JOINs connect related tables. Indexes speed up queries on specific columns.
- **SQLAlchemy ORM** (Module 007): Python classes map to tables. `Mapped[int]` defines typed columns. `relationship()` with `ForeignKey` defines connections. Alembic tracks schema changes as versioned migrations.
- **CRUD with service layer** (Module 008): The service layer sits between routes and the database. It handles business logic (validation, authorization checks) before executing queries. This separation means schema changes only affect the service layer, not route handlers.

## How They Compose

Your API endpoints define what data you need. Your schema defines how that data is stored. The connection is direct:

**Endpoints --> Entities --> Relationships --> Constraints --> Indexes --> Migrations**

1. **Endpoints to entities.** Each resource in your API (`/users`, `/posts`, `/comments`) maps to at least one table. Some resources require junction tables (many-to-many: users liking posts).

2. **Entities to relationships.** Look at your nested endpoints and foreign references. `GET /posts/{id}/comments` tells you comments belong to posts (one-to-many). `POST /posts/{id}/like` tells you users and posts have a many-to-many like relationship.

3. **Relationships to constraints.** Every relationship needs a foreign key. Every foreign key should have `ON DELETE` behavior defined. Do you cascade-delete comments when a post is deleted? Or set the post_id to NULL? Or block deletion until comments are removed?

4. **Constraints to indexes.** Every foreign key needs an index (SQLAlchemy does not create these automatically). Every column you filter or sort by in queries needs an index. Unique constraints automatically create indexes.

5. **Indexes to migrations.** Your initial migration creates the schema. Subsequent migrations evolve it. Never modify a migration that has been applied -- always create a new one.

### The N+1 Query Connection

Schema design directly affects query performance (Module 020). If you put user data in a separate table (which you should), then every post query that shows the author name requires a JOIN. SQLAlchemy's `selectinload()` and `joinedload()` strategies depend on your relationship definitions being correct.

```python
# Schema decision: separate users and posts tables
# Consequence: need relationship() for efficient loading
class Post(Base):
    __tablename__ = "posts"
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

# In service layer: use joinedload to avoid N+1
posts = session.scalars(
    select(Post).options(joinedload(Post.author)).limit(20)
).unique().all()
```

## Decision Framework

### Choosing Relationship Types

```
Two entities: A and B. How are they related?

1. Can one A have many B?
   No  --> 1:1 (rare -- consider merging into one table)
   Yes --> Continue

2. Can one B have many A?
   No  --> 1:N (A has many B, B belongs to one A)
         --> Put foreign_key in B pointing to A
   Yes --> M:N (many-to-many)
         --> Create junction table: a_b(a_id, b_id)
```

### Choosing Column Types

| Data | PostgreSQL Type | SQLAlchemy Type | Notes |
|------|----------------|-----------------|-------|
| IDs | `SERIAL` / `BIGSERIAL` | `Mapped[int]` with `primary_key=True` | Auto-incrementing |
| Short text | `VARCHAR(N)` | `Mapped[str]` with `String(N)` | Enforce max length |
| Long text | `TEXT` | `Mapped[str]` | No length limit |
| Timestamps | `TIMESTAMP WITH TIME ZONE` | `Mapped[datetime]` | Always use timezone-aware |
| Booleans | `BOOLEAN` | `Mapped[bool]` | Default value important |
| Money | `NUMERIC(10,2)` | `Mapped[Decimal]` | Never use FLOAT for money |
| Email | `VARCHAR(255)` | `Mapped[str]` with unique constraint | Add UNIQUE + index |
| Enum | `VARCHAR` or PostgreSQL `ENUM` | `Mapped[str]` or `Mapped[Enum]` | VARCHAR is more flexible |

### ON DELETE Strategy

| Relationship | Strategy | Example |
|-------------|----------|---------|
| User --> Posts | CASCADE | Delete user = delete all their posts |
| Post --> Comments | CASCADE | Delete post = delete all comments |
| User --> Likes | CASCADE | Delete user = remove their likes |
| Order --> User | SET NULL or RESTRICT | Keep order history even if user is deleted |
| Payment --> Order | RESTRICT | Cannot delete order with payments |

## Capstone Application

**E-Commerce API -- Schema Design**

Starting from the E-Commerce endpoint list, here is the schema design:

**Entities identified:** Users, Products, Categories, Orders, OrderItems, Reviews

**Schema plan:**

```sql
-- Users table (Module 009: stores auth credentials)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer',  -- customer, admin
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_seller ON products(seller_id);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, shipped, delivered, cancelled
    total_amount NUMERIC(10, 2) NOT NULL,
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);

-- OrderItems (junction: Order <-> Product)
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- Reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)  -- one review per user per product
);
CREATE INDEX idx_reviews_product ON reviews(product_id);
```

**Key design decisions explained:**

- `NUMERIC(10,2)` for money, never `FLOAT` -- floating point causes rounding errors in financial calculations
- `ON DELETE SET NULL` for orders -> users -- keep order history even if user account is deleted
- `ON DELETE RESTRICT` for order_items -> products -- cannot delete a product that has been ordered
- Composite unique constraint on reviews (user_id, product_id) -- enforces one review per user per product at the database level
- Indexes on every foreign key and on `status` (frequently filtered)

## Checklist

Before writing your first Alembic migration, verify:

- [ ] Every API resource has a corresponding table (or junction table for M:N)
- [ ] Every table has a primary key (typically auto-incrementing integer `id`)
- [ ] Every table has `created_at` timestamp (and `updated_at` where records change)
- [ ] All foreign keys defined with explicit `ON DELETE` behavior
- [ ] Indexes created on all foreign key columns
- [ ] Indexes created on columns used in WHERE clauses and ORDER BY
- [ ] Unique constraints on naturally unique fields (email, username, slugs)
- [ ] Money stored as `NUMERIC`, never `FLOAT`
- [ ] String columns have appropriate max length (`VARCHAR(N)`)
- [ ] Enum-like columns use `VARCHAR` with CHECK constraint or application-level validation

## Key Takeaways

1. **Schema design flows from API design.** Your endpoints tell you what entities and relationships you need. Do not design the schema in isolation.
2. **Foreign keys are not optional.** They enforce data integrity at the database level. Without them, you will have orphaned records and inconsistent data.
3. **Indexes are a performance contract.** Every query you plan to run frequently needs an index on the filtered/sorted column. Missing indexes are the number one cause of slow APIs.
4. **Plan your ON DELETE strategy before writing code.** CASCADE, SET NULL, or RESTRICT -- each has consequences. Decide based on business rules, not convenience.
5. **Migrations are immutable history.** Once applied, never edit a migration. Always create a new one. This is the database equivalent of "never rewrite git history on shared branches."
