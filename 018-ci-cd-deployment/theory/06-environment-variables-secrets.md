# Environment Variables and Secrets

## Why This Matters

On iOS, you manage different configurations through Xcode schemes and `.xcconfig` files. Your debug scheme uses a staging API URL; your release scheme uses production. Sensitive values like API keys go into the Keychain or are injected via Xcode Cloud environment variables. On Android, you use `build.gradle` flavors and `BuildConfig` fields, with secrets stored in encrypted properties files or CI environment variables.

Backend configuration follows the same principle: different values for different environments, with secrets kept out of your source code. But instead of Xcode schemes, you use environment variables. Instead of the Keychain, you use GitHub Secrets. And instead of `.xcconfig` files, you use `.env` files locally and CI secret stores in production.

The stakes are higher on the backend. A leaked database password exposes every user's data. A committed API key gets scraped by bots within minutes. Secret management isn't optional -- it's a core backend skill.

## GitHub Secrets

GitHub Secrets are encrypted values stored in your repository settings. They're injected into workflows as environment variables.

### Creating Secrets

1. Go to repository Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Enter name (e.g., `DATABASE_URL`) and value
4. Click "Add secret"

### Using Secrets in Workflows

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy with secrets
        run: |
          echo "Deploying to production..."
          # Secrets are available as environment variables
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          DOCKER_TOKEN: ${{ secrets.DOCKER_TOKEN }}
```

**Security rules:**
- Secrets are never printed in logs (GitHub masks them automatically)
- Secrets are not available in forked repository PRs (prevents secret theft)
- Secrets cannot be read back from the UI -- only overwritten

## Environment-Specific Configuration

Most applications need different settings for development, staging, and production.

```
Development (local)    Staging (CI/test)     Production
------------------     -----------------     ----------
SQLite / local PG      PostgreSQL (CI)       PostgreSQL (managed)
DEBUG=True             DEBUG=False           DEBUG=False
localhost:8000         staging.example.com   api.example.com
Fake email sender      Sandbox email         Real email
```

### Pydantic Settings for FastAPI

Pydantic's `BaseSettings` loads values from environment variables automatically. This is the standard pattern for FastAPI configuration.

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./dev.db"

    # Security
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 30

    # Application
    app_name: str = "My FastAPI App"
    debug: bool = False

    # External services
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""

    model_config = {
        "env_file": ".env",        # Load from .env file if it exists
        "env_file_encoding": "utf-8",
        "case_sensitive": False,    # DATABASE_URL or database_url both work
    }

settings = Settings()
```

**How it works:**
1. Pydantic checks environment variables first (highest priority)
2. Falls back to `.env` file values
3. Falls back to default values in the class

```python
# Usage in FastAPI
from app.core.config import settings

@app.get("/info")
async def info():
    return {"app": settings.app_name, "debug": settings.debug}
```

## Local Development with .env Files

Locally, store configuration in a `.env` file at the project root:

```bash
# .env -- NEVER commit this file
DATABASE_URL=postgresql://postgres:localpass@localhost:5432/myapp
SECRET_KEY=my-local-dev-secret-key
DEBUG=True
SMTP_HOST=localhost
SMTP_PORT=1025
```

### Critical: Never Commit .env Files

Add `.env` to `.gitignore` immediately:

```gitignore
# .gitignore
.env
.env.local
.env.production
*.env
```

Provide a template for other developers:

```bash
# .env.example -- commit this file (no real values)
DATABASE_URL=postgresql://postgres:password@localhost:5432/myapp
SECRET_KEY=change-me-in-production
DEBUG=True
SMTP_HOST=localhost
SMTP_PORT=587
```

## Secrets in CI/CD

In GitHub Actions, secrets replace the `.env` file:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: pytest -v
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          SECRET_KEY: ${{ secrets.SECRET_KEY }}

  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
          SECRET_KEY: ${{ secrets.PROD_SECRET_KEY }}
          DOCKER_TOKEN: ${{ secrets.DOCKER_TOKEN }}
        run: |
          # Deploy with production secrets
          echo "Deploying..."
```

### GitHub Environments for Per-Environment Secrets

```yaml
  deploy-staging:
    environment: staging    # Uses staging secrets
    steps:
      - run: echo "Using $DATABASE_URL"
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          # Resolves to staging DATABASE_URL

  deploy-production:
    environment: production  # Uses production secrets
    steps:
      - run: echo "Using $DATABASE_URL"
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          # Resolves to production DATABASE_URL
```

Same secret name (`DATABASE_URL`), different values per environment. Clean and explicit.

## Secret Rotation

Secrets should be rotated (changed) regularly. When you rotate a secret:

1. Generate new secret value
2. Update the service that uses it (e.g., create new database password)
3. Update GitHub Secrets with new value
4. Redeploy the application
5. Verify the application works with the new secret
6. Revoke the old secret value

```bash
# Example: rotating a database password
# 1. Generate new password
openssl rand -base64 32

# 2. Update PostgreSQL user password
psql -c "ALTER USER myapp_user WITH PASSWORD 'new-password-here';"

# 3. Update GitHub Secret (via CLI)
gh secret set DATABASE_URL --body "postgresql://myapp_user:new-password-here@db.example.com:5432/myapp"

# 4. Redeploy
git commit --allow-empty -m "trigger: rotate database credentials"
git push
```

## Common Mistakes

### 1. Hardcoded Secrets

```python
# WRONG -- secret in source code
DATABASE_URL = "postgresql://admin:SuperSecret123@prod-db.example.com:5432/myapp"

# RIGHT -- load from environment
import os
DATABASE_URL = os.environ["DATABASE_URL"]

# BEST -- use Pydantic Settings
from app.core.config import settings
DATABASE_URL = settings.database_url
```

### 2. Logging Secrets

```python
# WRONG -- prints secret to logs
logger.info(f"Connecting to {settings.database_url}")

# RIGHT -- mask sensitive parts
logger.info(f"Connecting to database at {settings.database_url.split('@')[1]}")

# BEST -- don't log connection strings at all
logger.info("Database connection established")
```

### 3. Committing .env Files

```bash
# Check if .env is tracked by git
git ls-files .env

# If it shows up, remove it from tracking (keeps the local file)
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "Remove .env from tracking"
```

### 4. Using Default Secrets in Production

```python
class Settings(BaseSettings):
    # This default is fine for local dev, dangerous if used in production
    secret_key: str = "dev-secret-change-in-production"

# Add a startup check
@app.on_event("startup")
async def validate_settings():
    if settings.secret_key == "dev-secret-change-in-production":
        if not settings.debug:
            raise ValueError("Production must use a real SECRET_KEY")
```

## Mobile vs Backend Secret Management

| Aspect | Mobile (iOS/Android) | Backend (FastAPI) |
|--------|---------------------|-------------------|
| Local secrets | .xcconfig / local.properties | .env file |
| Secret storage | Keychain / EncryptedSharedPrefs | Environment variables |
| CI secrets | Xcode Cloud env vars | GitHub Secrets |
| Config per env | Xcode schemes / build flavors | Pydantic Settings + env vars |
| Secret template | Not common | .env.example (committed) |
| Risk of leak | App binary (can be decompiled) | Server logs, git history |
| Rotation | App update required | Redeploy (minutes) |
| Impact of leak | API key abuse | Full database access |

## Key Takeaways

- Never commit secrets to git -- use `.env` locally and GitHub Secrets in CI/CD
- Pydantic `BaseSettings` is the standard way to load configuration in FastAPI (env vars > .env file > defaults)
- Always provide a `.env.example` template with placeholder values for other developers
- GitHub Secrets are encrypted, masked in logs, and unavailable to forked PRs
- Use GitHub Environments to manage per-environment secrets (staging vs production)
- Rotate secrets regularly -- generate new value, update service, update secret, redeploy, verify
- Never log connection strings or secret values -- log that a connection was made, not how
- Add startup validation to catch default/missing secrets before serving production traffic
