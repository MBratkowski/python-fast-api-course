# Module 018: CI/CD & Deployment

## Why This Module?

Automate testing and deployment. Push code, tests run, and your API deploys automatically.

## What You'll Learn

- GitHub Actions
- CI pipeline setup
- Automated testing
- Deployment strategies
- Environment management
- Popular hosting platforms

## Topics

### Theory
1. CI/CD Concepts
2. GitHub Actions Basics
3. Running Tests in CI
4. Docker Image Building
5. Deployment to Cloud (Railway, Fly.io, AWS)
6. Environment Variables & Secrets

### Project
Set up full CI/CD pipeline for your API.

## Example

```yaml
# .github/workflows/ci.yml
name: CI/CD

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
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r requirements.txt
      - run: pytest --cov

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
```
