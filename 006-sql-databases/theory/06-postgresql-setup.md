# PostgreSQL Setup and psql

## Why This Matters

PostgreSQL is the **most popular database for Python backend development** (55.6% developer adoption in 2026). It's production-grade, open-source, and has excellent Python ecosystem support. Learning PostgreSQL now means you're using the same database that powers companies like Instagram, Spotify, and Reddit.

Think of PostgreSQL like:
- **Android Emulator** or **iOS Simulator** for mobile dev
- **Runs in an isolated environment** (Docker container)
- **Doesn't pollute your machine** with database files

## Why Docker Compose?

**Docker Compose** lets you run PostgreSQL in a container with one command. Benefits:

- **Isolated environment** - doesn't interfere with other projects
- **Easy cleanup** - delete container, everything's gone
- **Consistent across team** - everyone runs the same database version
- **No manual installation** - works on Mac, Linux, Windows

Mobile dev equivalent:
- Running Android Emulator instead of buying a physical phone
- iOS Simulator instead of deploying to an actual iPhone

## Installing Docker

### Mac
```bash
brew install docker docker-compose
# Or download Docker Desktop from docker.com
```

### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

### Windows
Download Docker Desktop from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

Verify installation:
```bash
docker --version
docker-compose --version
```

## Setting Up PostgreSQL with Docker Compose

### Step 1: Create docker-compose.yml

In your project root, create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine  # Lightweight PostgreSQL 15
    container_name: backend_postgres
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret123
      POSTGRES_DB: backend_dev
    ports:
      - "5432:5432"  # Host:Container port mapping
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist data
    restart: unless-stopped

volumes:
  postgres_data:  # Named volume for data persistence
```

**What this does**:
- **image**: Uses PostgreSQL 15 (alpine = smaller image)
- **environment**: Sets database name, user, password
- **ports**: Maps port 5432 (default PostgreSQL port) to your machine
- **volumes**: Persists data (survives container restarts)
- **restart**: Auto-restarts if it crashes

### Step 2: Start PostgreSQL

```bash
# Start database (first time: downloads image)
docker-compose up -d

# -d = detached mode (runs in background)
```

Output:
```
Creating network "project_default" with the default driver
Creating volume "project_postgres_data" with default driver
Creating backend_postgres ... done
```

### Step 3: Verify it's running

```bash
docker-compose ps
```

Output:
```
Name                  Command              State           Ports
---------------------------------------------------------------------------
backend_postgres   docker-entrypoint.sh postgres   Up      0.0.0.0:5432->5432/tcp
```

### Step 4: Stop/restart database

```bash
# Stop database (data persists)
docker-compose stop

# Start again
docker-compose start

# Stop and remove containers (data still persists in volume)
docker-compose down

# Stop and remove containers + volumes (DELETES ALL DATA)
docker-compose down -v
```

## Using psql (PostgreSQL CLI)

`psql` is the command-line interface for PostgreSQL (like `sqlite3` for SQLite or your mobile debugger console).

### Connect to database

```bash
# Connect via Docker
docker-compose exec postgres psql -U admin -d backend_dev

# Or if installed locally
psql -h localhost -U admin -d backend_dev
```

**Flags**:
- `-U admin`: Username
- `-d backend_dev`: Database name
- `-h localhost`: Host (if not using Docker exec)

You'll see the psql prompt:
```
backend_dev=#
```

### Essential psql Commands

| Command | Description | Example |
|---------|-------------|---------|
| `\l` | List all databases | `\l` |
| `\c dbname` | Connect to database | `\c backend_dev` |
| `\dt` | List all tables | `\dt` |
| `\d tablename` | Describe table schema | `\d users` |
| `\du` | List users/roles | `\du` |
| `\q` | Quit psql | `\q` |
| `\i file.sql` | Execute SQL file | `\i schema.sql` |
| `\?` | Show all commands | `\?` |

### Running SQL in psql

```sql
-- Create a table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert data
INSERT INTO users (username, email)
VALUES ('alice', 'alice@example.com');

-- Query data
SELECT * FROM users;

-- Describe table
\d users
```

### Executing SQL Files

Create a `schema.sql` file:
```sql
-- schema.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com');
```

Execute it:
```bash
# From host machine
docker-compose exec -T postgres psql -U admin -d backend_dev < schema.sql

# From inside psql
\i /path/to/schema.sql
```

## Connection String

When connecting from Python, use a **connection string**:

```
postgresql://username:password@host:port/database
```

For our Docker setup:
```
postgresql://admin:secret123@localhost:5432/backend_dev
```

**In Python (using psycopg)**:
```python
import psycopg

conn = psycopg.connect(
    "postgresql://admin:secret123@localhost:5432/backend_dev"
)
```

**With SQLAlchemy** (Module 007):
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg://admin:secret123@localhost:5432/backend_dev"
)
```

**Store in .env file** (best practice):
```bash
# .env
DATABASE_URL=postgresql://admin:secret123@localhost:5432/backend_dev
```

```python
# Python
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")
```

## Local Installation (Alternative)

If you prefer local installation instead of Docker:

### Mac
```bash
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb backend_dev

# Connect
psql backend_dev
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create user and database
sudo -u postgres createuser --interactive
sudo -u postgres createdb backend_dev

# Connect
psql -U your_username -d backend_dev
```

### Windows
Download installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)

**Recommendation**: Use Docker Compose for consistency across team/environments.

## Quick Reference

### Start/stop database
```bash
docker-compose up -d     # Start
docker-compose stop      # Stop (data persists)
docker-compose restart   # Restart
docker-compose down      # Stop and remove containers
docker-compose down -v   # Stop and DELETE ALL DATA
```

### Connect to psql
```bash
docker-compose exec postgres psql -U admin -d backend_dev
```

### View logs
```bash
docker-compose logs postgres
docker-compose logs -f postgres  # Follow logs
```

### Backup database
```bash
docker-compose exec -T postgres pg_dump -U admin backend_dev > backup.sql
```

### Restore database
```bash
docker-compose exec -T postgres psql -U admin -d backend_dev < backup.sql
```

## Common Issues

### Port 5432 already in use
Another PostgreSQL instance is running. Stop it:
```bash
# Mac
brew services stop postgresql

# Linux
sudo systemctl stop postgresql

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use port 5433 on host
```

### Permission denied
Add your user to docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Container won't start
Check logs:
```bash
docker-compose logs postgres
```

## Key Takeaways

1. **Docker Compose** runs PostgreSQL in an isolated container (like mobile emulator)
2. **docker-compose.yml** defines database config (user, password, port, volume)
3. **psql** is the PostgreSQL command-line interface for running SQL
4. **\dt** lists tables, **\d tablename** describes schema, **\q** quits
5. **Connection string** format: `postgresql://user:pass@host:port/db`
6. **Environment variables** (.env file) store connection strings securely
7. **Volumes** persist data across container restarts (unless you use `-v`)
8. PostgreSQL is production-grade and most popular for Python backends
