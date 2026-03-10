# Project: Complete CI/CD Pipeline

## Overview

Build a full CI/CD pipeline for a FastAPI application. You'll create GitHub Actions workflows that test against a real PostgreSQL database, build Docker images, and deploy to a cloud platform. This project ties together everything from Module 018 -- CI/CD concepts, GitHub Actions, service containers, Docker builds, deployment, and secrets management.

Mobile analogy: You've set up Xcode Cloud or Bitrise to build, test, and distribute your iOS app. Now you'll do the same for a backend API -- but with faster builds, instant deployments, and no App Store Review.

## Requirements

### 1. CI Testing Pipeline
- [ ] GitHub Actions workflow (`.github/workflows/ci.yml`) triggered on push and PR to main
- [ ] PostgreSQL 16 service container with health check
- [ ] Steps: checkout, setup Python 3.12, install dependencies, run migrations, run pytest
- [ ] DATABASE_URL environment variable pointing to the service container
- [ ] Test coverage reporting (pytest-cov with `--cov` flag)

### 2. Docker Image Build
- [ ] Multi-stage Dockerfile (builder stage for deps, runtime stage for app)
- [ ] GitHub Actions workflow (`.github/workflows/build.yml`) triggered on push to main only
- [ ] Docker login step using `docker/login-action@v3` with secrets
- [ ] Build and push step using `docker/build-push-action@v5`
- [ ] Tags: `latest` and git SHA (`${{ github.sha }}`)

### 3. Deployment
- [ ] Deploy to Railway or Fly.io after successful build
- [ ] Staging environment with its own secrets (GitHub Environment)
- [ ] Production environment with manual approval required
- [ ] Health check endpoint (`/health`) for deployment verification

### 4. Secrets Management
- [ ] All secrets stored in GitHub Secrets (never hardcoded)
- [ ] `.env.example` file with placeholder values committed to repo
- [ ] `.env` added to `.gitignore`
- [ ] Pydantic `BaseSettings` for configuration loading

## Starter Template

Create the following file structure:

```
my-api/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI testing pipeline
│       ├── build.yml           # Docker build and push
│       └── deploy.yml          # Deployment to cloud
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app with /health endpoint
│   └── core/
│       └── config.py           # Pydantic BaseSettings
├── tests/
│   ├── conftest.py
│   └── test_health.py
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Local development
├── requirements.txt
├── .env.example
├── .gitignore
└── alembic.ini                 # If using migrations
```

### .github/workflows/ci.yml (skeleton)

```yaml
name: CI Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -r requirements.txt
      # TODO: Add migration step
      # TODO: Add pytest step with DATABASE_URL and coverage
```

### app/core/config.py (skeleton)

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    secret_key: str = "dev-secret-change-in-production"
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


settings = Settings()
```

## Success Criteria

1. Pushing to a feature branch and opening a PR triggers CI tests against PostgreSQL
2. All tests pass in CI with the service container providing the database
3. Merging to main triggers a Docker image build and push to a registry
4. The Docker image is tagged with both `latest` and the git commit SHA
5. Deployment to staging happens automatically after a successful build
6. Production deployment requires manual approval through GitHub Environments

## Stretch Goals

- [ ] Add a test matrix for Python 3.11, 3.12, and 3.13
- [ ] Add Slack notifications on CI failure using `slackapi/slack-github-action`
- [ ] Implement canary deployments (deploy to 10% of traffic first)
- [ ] Add Docker image vulnerability scanning with `docker/scout-action`
