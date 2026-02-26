# Database Migrations with Alembic

## Why This Matters

In mobile development, when your app's data model changes, you write **migrations** to update user databases. Core Data has lightweight migrations and migration policies. Room has migration strategies. SQLAlchemy uses **Alembic** - the standard migration tool for Python.

Without migrations, you'd have to manually write ALTER TABLE statements and keep track of what schema changes have been applied. Alembic automates this.

## What is Alembic?

**Alembic** is a database migration tool for SQLAlchemy. It:
- Generates migration scripts from model changes
- Tracks which migrations have been applied
- Lets you upgrade (apply changes) or downgrade (undo changes)
- Works like version control for your database schema

Think of it as **Git for your database schema**.

## Why Use Migrations?

### Version Control for Schema
Your database schema evolves over time:
- v1: Users table with username, email
- v2: Add `created_at` column
- v3: Add Posts table with foreign key
- v4: Add index on `email`

Migrations track each change as a versioned script.

### Team Collaboration
When a teammate pulls code with a new model field, they run:

```bash
alembic upgrade head
```

Their local database is updated to match the new schema. No manual SQL needed.

### Rollback Capability
If a schema change causes problems:

```bash
alembic downgrade -1  # Undo last migration
```

The database reverts to the previous schema.

### Deployment
Migrations run automatically during deployment:

```bash
# In your deploy script:
alembic upgrade head  # Apply all pending migrations
python -m uvicorn main:app --host 0.0.0.0  # Start app
```

## Installing Alembic

```bash
pip install alembic
```

Requires Python 3.10+ for the latest version.

## Setting Up Alembic

### 1. Initialize Alembic

In your project root:

```bash
alembic init alembic
```

This creates:

```
your-project/
├── alembic/
│   ├── versions/         # Migration scripts go here
│   ├── env.py            # Alembic environment configuration
│   ├── script.py.mako    # Template for new migrations
│   └── README
└── alembic.ini           # Alembic configuration file
```

### 2. Configure Database URL

Edit `alembic.ini`:

```ini
# alembic.ini

# Replace this line:
sqlalchemy.url = driver://user:pass@localhost/dbname

# With your database URL:
sqlalchemy.url = postgresql+asyncpg://postgres:password@localhost:5432/myapp
```

**Better approach:** Use environment variables:

```ini
# alembic.ini - comment out the URL line:
# sqlalchemy.url = ...
```

Then edit `alembic/env.py` to read from environment:

```python
# alembic/env.py
import os
from src.db.session import Base  # Import your Base

# Get database URL from environment
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/myapp")
)
```

### 3. Configure Target Metadata

Edit `alembic/env.py` to tell Alembic about your models:

```python
# alembic/env.py
from src.db.session import Base
from src.models import user, post, comment  # Import ALL model modules

# Set target metadata
target_metadata = Base.metadata
```

**Critical:** You must import all model modules for autogenerate to work. If you add a new model file, import it here.

### 4. Configure for Async (if using async SQLAlchemy)

If you're using async SQLAlchemy, update `alembic/env.py`:

```python
# alembic/env.py
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Change run_migrations_online() to use async:
def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_migrations(connection: Connection) -> None:
        await connection.run_sync(do_migrations)

    def do_migrations(connection: Connection) -> None:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    import asyncio
    asyncio.run(connectable.connect().__aenter__().do_run_migrations())
```

**Note:** For simplicity, many projects use a sync PostgreSQL connection just for migrations (with `psycopg2` driver), even if the app uses async.

## Creating Migrations

### Auto-Generate Migration from Model Changes

This is the most common workflow:

**1. Change your models:**

```python
# src/models/user.py
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))

    # NEW: Add bio field
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**2. Generate migration:**

```bash
alembic revision --autogenerate -m "add user bio field"
```

Alembic compares your models to the current database schema and generates a migration script.

**3. Review the generated migration:**

```python
# alembic/versions/xxxx_add_user_bio_field.py
"""add user bio field

Revision ID: xxxx
Revises: yyyy
Create Date: 2026-02-26 10:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xxxx'
down_revision = 'yyyy'  # Previous migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add bio column to users table."""
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))

def downgrade() -> None:
    """Remove bio column from users table."""
    op.drop_column('users', 'bio')
```

**4. Apply the migration:**

```bash
alembic upgrade head
```

This executes the `upgrade()` function, which runs `ALTER TABLE users ADD COLUMN bio TEXT;`

### Manual Migration

For complex changes that autogenerate can't detect:

```bash
alembic revision -m "add index on email"
```

Then edit the generated file:

```python
def upgrade() -> None:
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('idx_users_email', 'users')
```

## Common Migration Operations

### Add Column

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

def downgrade() -> None:
    op.drop_column('users', 'is_active')
```

### Remove Column

```python
def upgrade() -> None:
    op.drop_column('users', 'middle_name')

def downgrade() -> None:
    op.add_column('users', sa.Column('middle_name', sa.String(50), nullable=True))
```

### Rename Column

```python
def upgrade() -> None:
    op.alter_column('users', 'username', new_column_name='user_name')

def downgrade() -> None:
    op.alter_column('users', 'user_name', new_column_name='username')
```

### Create Table

```python
def upgrade() -> None:
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('posts')
```

### Add Index

```python
def upgrade() -> None:
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('idx_users_email', 'users')
```

### Add Foreign Key

```python
def upgrade() -> None:
    op.add_column('posts', sa.Column('author_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_posts_author', 'posts', 'users', ['author_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_posts_author', 'posts', type_='foreignkey')
    op.drop_column('posts', 'author_id')
```

## Alembic Commands

### Create Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description"

# Manual migration (empty template)
alembic revision -m "description"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade abc123
```

### Revert Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Downgrade to base (remove all migrations)
alembic downgrade base
```

### View Migration Status

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show detailed history
alembic history --verbose

# Show pending migrations
alembic heads
```

### Other Commands

```bash
# Show SQL without executing
alembic upgrade head --sql

# Stamp database with version (without running migration)
alembic stamp head
```

## Migration Workflow

### Development

1. **Change models** (add/remove fields, create new models)
2. **Generate migration:** `alembic revision --autogenerate -m "description"`
3. **Review generated migration** - make sure it's correct
4. **Apply migration:** `alembic upgrade head`
5. **Test your changes**
6. **Commit migration file** to version control

### Team Workflow

**When pulling changes with new migrations:**

```bash
git pull
alembic upgrade head  # Apply any new migrations
```

**Before merging feature branches:**

Make sure your migrations don't conflict. Alembic uses a linear version chain:

```
base → abc123 → def456 → ghi789 → head
```

If two people create migrations from the same parent, you'll need to merge them manually.

### Production Deployment

```bash
# In your deployment script:
alembic upgrade head  # Apply all pending migrations
python -m uvicorn main:app  # Start application
```

**Best practice:** Run migrations before starting the app. If a migration fails, the app won't start with a mismatched schema.

## `create_all()` vs Alembic

### `Base.metadata.create_all()`

```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

**Creates tables from models.** Use only for:
- ✅ Development (quick setup)
- ✅ Tests (fresh database each test)
- ❌ **NOT for production**

**Problems:**
- No version tracking
- Can't rollback
- Can't handle schema changes
- No team collaboration

### Alembic Migrations

```bash
alembic upgrade head
```

**Applies versioned migration scripts.** Use for:
- ✅ Production
- ✅ Team projects
- ✅ Any project that will change over time

**Benefits:**
- Version controlled
- Rollback capability
- Handles schema evolution
- Team-friendly

**Rule:** Use `create_all()` for tests, Alembic for everything else.

## Common Pitfalls

### 1. Forgot to Import Models

```python
# alembic/env.py

# Bad - autogenerate won't detect this model
from src.models import user

# Good - import all model modules
from src.models import user, post, comment, tag
```

If autogenerate says "no changes detected" when you added a model, you forgot to import it in `env.py`.

### 2. Mixing `create_all()` and Alembic

```python
# Don't do this in production!
if not tables_exist:
    Base.metadata.create_all()  # ❌ Bad

# Use Alembic instead
# $ alembic upgrade head
```

Choose one approach: either `create_all()` (dev/test) OR Alembic (production).

### 3. Not Reviewing Auto-Generated Migrations

Autogenerate doesn't catch everything:
- ❌ Data migrations (moving data between columns)
- ❌ Some renames (sees them as drop + add)
- ❌ Complex constraints

Always review and test generated migrations before applying to production.

### 4. Editing Applied Migrations

```python
# Don't edit this after it's been applied to production!
# alembic/versions/abc123_add_user_bio.py
```

Once a migration is applied (especially in production), **never edit it**. Create a new migration instead.

## Key Takeaways

1. **Alembic is Git for database schema** - tracks versions, allows rollback
2. **Setup:** `alembic init` → configure `alembic.ini` → import models in `env.py`
3. **Workflow:** Change models → `alembic revision --autogenerate` → review → `alembic upgrade head`
4. **Use autogenerate** for most changes, but always review generated SQL
5. **`upgrade head`** applies all pending migrations to latest version
6. **`downgrade -1`** reverts the last migration
7. **Use Alembic for production** - use `create_all()` only for tests
8. **Commit migration files** to version control
9. **Review auto-generated migrations** - they're not always perfect
10. **Never edit applied migrations** - create a new migration instead
