# Networking and Volumes

## Why This Matters

On mobile, your app talks to a backend over HTTP -- you specify the hostname and port, and the OS handles DNS resolution, TLS, and routing. Storage is simple too: you write to the app sandbox, and the OS manages the lifecycle.

With Docker, you control both sides. You decide how containers find each other (networking) and where data lives (volumes). Understanding these concepts is critical because misconfigured networking means containers can't communicate, and missing volumes mean data disappears when you restart a container.

## Docker Networking

### Default Network Behavior

When you use Docker Compose, all services in the same `docker-compose.yml` are placed on a shared network automatically. Services can reach each other by name.

```yaml
services:
  api:
    build: .
    environment:
      # "db" is the service name -- Docker resolves it to the container's IP
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
      # "redis" is resolved the same way
      - REDIS_URL=redis://redis:6379/0

  db:
    image: postgres:16-alpine

  redis:
    image: redis:7-alpine
```

In this example:
- `api` can reach PostgreSQL at hostname `db` on port 5432
- `api` can reach Redis at hostname `redis` on port 6379
- `db` and `redis` can also reach `api` at hostname `api`

This is **service discovery by name** -- Docker's built-in DNS resolves service names to container IP addresses.

### Network Types

| Network Type | Description | When to Use |
|-------------|-------------|-------------|
| Bridge (default) | Isolated network for containers on one host | Development, single-machine deployments |
| Host | Container shares the host's network directly | Performance-critical, no isolation needed |
| None | No networking | Isolated processing tasks |
| Overlay | Network spanning multiple Docker hosts | Docker Swarm (multi-machine) |

For local development with Docker Compose, the default bridge network is almost always what you want.

### Custom Networks

For more control, define explicit networks:

```yaml
services:
  api:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend  # Only accessible from backend network

  nginx:
    networks:
      - frontend  # Only accessible from frontend network

networks:
  frontend:
  backend:
```

This creates network isolation: `nginx` can reach `api` but not `db`. This is a security best practice -- the database should not be directly accessible from the reverse proxy.

### Port Mapping

Ports in docker-compose.yml control external access:

```yaml
services:
  api:
    ports:
      - "8000:8000"    # host:container -- accessible from your machine

  db:
    ports:
      - "5432:5432"    # Accessible from your machine (useful for DB tools)
    # If you remove this, db is still accessible from other containers
    # but NOT from your host machine
```

```
Your Machine (localhost)
  |
  | port 8000 --> api container (port 8000)
  | port 5432 --> db container (port 5432)
  |
  +-- Docker Network (bridge) --+
  |   api <-> db (port 5432)    |
  |   api <-> redis (port 6379) |
  +-----------------------------+
```

**Key insight:** Containers on the same Docker network can communicate on any port without port mapping. Port mapping (`ports:`) is only needed for access from outside the Docker network (your host machine).

### DNS Resolution

Inside a Docker Compose network, service names resolve to container IPs:

```python
# Inside the 'api' container, these all work:
import redis
import psycopg2

# "db" resolves to the PostgreSQL container's IP
conn = psycopg2.connect("postgresql://user:pass@db:5432/appdb")

# "redis" resolves to the Redis container's IP
r = redis.Redis(host="redis", port=6379, db=0)
```

Mobile analogy: This is like Bonjour/mDNS on iOS, where devices discover each other by name on the local network. Docker provides the same for containers.

## Docker Volumes

Containers are ephemeral -- when you remove a container, all data inside it is lost. Volumes solve this by storing data outside the container's filesystem.

### The Problem Without Volumes

```bash
# Start PostgreSQL
docker compose up -d db

# Insert data, create tables, etc.

# Stop and remove containers
docker compose down

# Start again
docker compose up -d db
# ALL DATA IS GONE -- the database starts fresh
```

### Named Volumes

Named volumes are managed by Docker and persist across container restarts and removals.

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Named volume

volumes:
  postgres_data:  # Declare the named volume
```

Now:
```bash
docker compose down     # Data survives (volume is preserved)
docker compose up -d    # Data is still there

docker compose down -v  # Data is DELETED (-v removes volumes)
```

### Bind Mounts

Bind mounts map a directory on your host machine directly into the container. They're primarily used for development.

```yaml
services:
  api:
    volumes:
      - ./app:/code/app  # Bind mount: host_path:container_path
```

Changes to files in `./app` on your host machine are immediately visible inside the container (and vice versa). This enables hot-reload during development.

### Named Volumes vs Bind Mounts

| Aspect | Named Volume | Bind Mount |
|--------|-------------|------------|
| Syntax | `volume_name:/container/path` | `./host/path:/container/path` |
| Managed by | Docker | You (host filesystem) |
| Portability | Works anywhere | Depends on host path existing |
| Performance | Optimized by Docker | Direct filesystem access |
| Use case | Database data, persistent state | Development hot-reload, config files |
| Backup | `docker volume` commands | Standard filesystem tools |
| Declared in | `volumes:` section at bottom | No declaration needed |

### Volume Examples

```yaml
services:
  api:
    volumes:
      # Bind mount -- development hot reload
      - ./app:/code/app

      # Named volume -- persistent upload storage
      - uploads:/code/uploads

      # Read-only bind mount -- config files
      - ./config/settings.yaml:/code/config/settings.yaml:ro

  db:
    volumes:
      # Named volume -- database data (MUST persist)
      - postgres_data:/var/lib/postgresql/data

      # Bind mount -- initialization scripts (read-only)
      - ./init-db:/docker-entrypoint-initdb.d:ro

  redis:
    volumes:
      # Named volume -- Redis persistence
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
  uploads:
```

### Managing Volumes

```bash
# List all volumes
docker volume ls

# Inspect a volume (see mount point, creation date)
docker volume inspect myapp_postgres_data

# Remove a specific volume (data loss!)
docker volume rm myapp_postgres_data

# Remove all unused volumes (careful!)
docker volume prune

# Backup a volume (dump to tar file)
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

## Data Persistence Across Restarts

Here's how different `docker compose` commands affect your data:

| Command | Containers | Networks | Named Volumes | Bind Mounts |
|---------|-----------|----------|---------------|-------------|
| `docker compose stop` | Stopped (can restart) | Kept | Kept | N/A (host files) |
| `docker compose down` | Removed | Removed | **Kept** | N/A |
| `docker compose down -v` | Removed | Removed | **Removed** | N/A |
| `docker compose restart` | Restarted | Kept | Kept | N/A |

**Rule of thumb:** Use `docker compose down` freely. Only use `docker compose down -v` when you want to reset all data.

## Key Takeaways

- Docker Compose services find each other by name (built-in DNS on bridge network)
- Port mapping (`ports:`) is only needed for access from your host machine, not between containers
- Named volumes persist data across container restarts and removals -- essential for databases
- Bind mounts map host directories into containers -- use for development hot-reload
- `docker compose down` preserves volumes; `docker compose down -v` destroys them
- Custom networks provide isolation between service groups (e.g., frontend vs backend)
- Always use named volumes for database data to prevent data loss
