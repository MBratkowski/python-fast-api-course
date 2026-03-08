# Secrets Management

## Why This Matters

On mobile, you store sensitive data in the Keychain (iOS) or EncryptedSharedPreferences (Android) -- the OS provides a secure, hardware-backed storage system. On the server, there is no Keychain. You must manage secrets yourself: database passwords, API keys, JWT signing keys, and third-party service credentials.

The most common mistake? Hardcoding secrets in your source code. Once a secret is in a git commit, it lives in the repository history forever -- even if you delete it later. If the repo is public (or ever becomes public), every secret ever committed is exposed.

## Never Hardcode Secrets

```python
# NEVER DO THIS -- secret is in your git history forever
SECRET_KEY = "my-super-secret-jwt-key-12345"
DATABASE_URL = "postgresql://admin:password123@db.example.com/myapp"
STRIPE_API_KEY = "sk_live_abc123def456"
```

If you commit this and push to GitHub, automated bots will find and exploit these secrets within minutes. GitHub even has "secret scanning" that alerts you when known secret patterns are detected in public repos.

## Environment Variables with python-dotenv

The standard approach for local development is `.env` files loaded by `python-dotenv`:

### Step 1: Create a .env File

```bash
# .env (NEVER commit this file)
SECRET_KEY=a9f2k4m7p1q8r3t6v0w5x2y4z7b9c1d3
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_test_abc123
SMTP_PASSWORD=email-service-password
```

### Step 2: Add .env to .gitignore

```gitignore
# .gitignore
.env
.env.local
.env.production
*.pem
*.key
```

**This is non-negotiable.** If `.env` is not in `.gitignore`, it will be committed.

### Step 3: Load Environment Variables

```python
# src/core/config.py
import os
from dotenv import load_dotenv

# Load .env file (only affects current process)
load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")

settings = Settings()
```

### Using Pydantic BaseSettings (Recommended)

Pydantic provides a cleaner approach with automatic type conversion and validation:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# Usage
settings = Settings()
# Raises ValidationError if required vars are missing
```

**Install:** `pip install pydantic-settings`

## Provide a .env.example Template

Since `.env` is not committed, provide a template so other developers know what variables are needed:

```bash
# .env.example (commit this file)
# Copy this to .env and fill in your values
SECRET_KEY=generate-a-random-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_test_your_key_here
DEBUG=true
```

## Docker Runtime Environment Variables

In Docker, pass secrets as runtime environment variables -- never bake them into the image:

```yaml
# docker-compose.yml
services:
  api:
    build: .
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    env_file:
      - .env  # Load from .env file
```

**Critical:** Never `COPY .env` in a Dockerfile. Docker image layers are visible with `docker history`, exposing any files copied during build.

```dockerfile
# BAD: Secret is baked into the image layer
COPY .env /code/.env

# BAD: Secret is visible in image history
ENV SECRET_KEY=my-secret-key

# GOOD: Use runtime env vars (passed by docker-compose or docker run)
# No secrets in the Dockerfile at all
```

## CI/CD Secrets (GitHub Actions)

GitHub Actions provides encrypted secrets that are masked in logs:

### Setting Secrets

1. Go to your repository on GitHub
2. Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add `SECRET_KEY`, `DATABASE_URL`, etc.

### Using Secrets in Workflows

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
        env:
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

**Security features:**
- Secrets are encrypted at rest
- They are masked in logs (replaced with `***`)
- They are not available in pull requests from forks
- They cannot be read by workflows, only used as environment variables

## Generating Strong Secrets

```python
import secrets

# Generate a secure random key (32 bytes, URL-safe base64)
key = secrets.token_urlsafe(32)
# Example: "dBjftJeZ4CVP-mB92pCbV_xbZ4GqRR1kPnXkqQzYoMs"

# Generate a hex key (64 hex characters = 32 bytes)
hex_key = secrets.token_hex(32)
# Example: "a9f2k4m7p1q8r3t6v0w5x2y4z7b9c1d3e5f7g9h1j3k5l7m9"
```

```bash
# From the command line
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using openssl
openssl rand -base64 32
```

## Secrets Rotation

Secrets should be rotated periodically (JWT keys, database passwords, API keys):

```python
# Support multiple JWT keys for rotation
import os
from datetime import datetime, timezone

# Current key for signing new tokens
CURRENT_KEY = os.getenv("JWT_SECRET_KEY")
# Previous key for validating existing tokens during rotation
PREVIOUS_KEY = os.getenv("JWT_PREVIOUS_SECRET_KEY", "")

def verify_token(token: str) -> dict:
    """Try current key first, then previous key for rotation."""
    try:
        return jwt.decode(token, CURRENT_KEY, algorithms=["HS256"])
    except jwt.InvalidSignatureError:
        if PREVIOUS_KEY:
            return jwt.decode(token, PREVIOUS_KEY, algorithms=["HS256"])
        raise
```

**Rotation process:**
1. Generate a new secret key
2. Set the current key as `JWT_PREVIOUS_SECRET_KEY`
3. Set the new key as `JWT_SECRET_KEY`
4. Deploy -- existing tokens validate with the previous key, new tokens use the new key
5. After all old tokens expire, remove `JWT_PREVIOUS_SECRET_KEY`

## Summary: Where Secrets Live

| Environment | Where Secrets Live | How They're Accessed |
|-------------|-------------------|---------------------|
| Local development | `.env` file (git-ignored) | `python-dotenv` or `pydantic-settings` |
| Docker Compose | `docker-compose.yml` env vars or `.env` | Runtime environment variables |
| CI/CD | GitHub Actions Secrets | `${{ secrets.NAME }}` |
| Production | Cloud secrets manager (AWS SSM, GCP Secret Manager) | SDK or injected env vars |

## Key Takeaways

1. **Never hardcode secrets** -- not in code, not in Dockerfiles, not in git
2. **Use `.env` files** for local development, always git-ignored
3. **Provide `.env.example`** so developers know which variables are required
4. **Use runtime environment variables** in Docker -- never COPY .env into images
5. **Use GitHub Actions Secrets** for CI/CD pipelines
6. **Generate strong keys** with `secrets.token_urlsafe(32)` -- never use human-readable passwords
7. **Mobile analogy:** `.env` files are your server's Keychain/EncryptedSharedPreferences
