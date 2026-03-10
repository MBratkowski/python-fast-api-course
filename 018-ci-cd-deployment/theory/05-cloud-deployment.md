# Cloud Deployment

## Why This Matters

On mobile, "deployment" means submitting your app to the App Store or Play Store. You upload a build, it goes through review (1-3 days for iOS), and eventually users can download it. You cannot deploy a hotfix in 5 minutes -- you're at the mercy of the review process.

Backend deployment is fundamentally different. You push code, CI passes, and your API is live in minutes. No review process. No waiting. If you find a bug in production, you can fix and redeploy in under 10 minutes. This speed is both powerful and dangerous -- which is why CI/CD pipelines with automated tests are essential.

Think of it like TestFlight, but where every build that passes tests is immediately available to real users. That's continuous deployment for backends.

## Deployment Platforms

There are three tiers of deployment platforms, each with different trade-offs:

### Railway (Simplest)

Railway detects your Dockerfile, builds it, and deploys automatically. Zero infrastructure management.

**How it works:**
1. Connect your GitHub repository
2. Railway detects your Dockerfile
3. Every push to main triggers a build and deploy
4. Railway provides a public URL

**Configuration (`railway.toml`):**

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**GitHub Actions deployment:**

```yaml
  deploy:
    needs: [test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: my-fastapi-app
```

**Best for:** Side projects, prototypes, small production apps. Mobile analogy: Firebase App Distribution -- quick, easy, no configuration.

### Fly.io (More Control)

Fly.io runs your Docker containers on lightweight VMs (Firecracker) close to your users. You get more control over regions, scaling, and networking.

**Configuration (`fly.toml`):**

```toml
app = "my-fastapi-app"
primary_region = "waw"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

[checks]
  [checks.health]
    type = "http"
    port = 8000
    path = "/health"
    interval = "30s"
    timeout = "5s"
```

**Deployment command:**

```bash
fly deploy
```

**Best for:** Production apps that need geographic distribution. Mobile analogy: TestFlight with multiple test groups in different regions.

### AWS ECS (Production-Grade)

Amazon ECS (Elastic Container Service) runs Docker containers at scale. You define task definitions, services, and load balancers. Full control, full complexity.

**Simplified architecture:**

```
GitHub Actions -> ECR (image registry) -> ECS (container orchestration) -> ALB (load balancer) -> Users
```

**GitHub Actions deployment to ECS:**

```yaml
  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest

    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-central-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: task-definition.json
          service: my-api-service
          cluster: my-cluster
          wait-for-service-stability: true
```

**Best for:** Large-scale production systems. Mobile analogy: App Store Connect with all the advanced features -- phased rollout, multiple environments, detailed analytics.

## Staging vs Production Environments

Never deploy directly to production without testing in staging first.

```
main branch -> CI tests -> Build image -> Deploy to STAGING -> Manual approval -> Deploy to PRODUCTION
```

**GitHub Actions with environments:**

```yaml
  deploy-staging:
    needs: [test]
    runs-on: ubuntu-latest
    environment: staging              # GitHub Environment with its own secrets

    steps:
      - name: Deploy to staging
        run: echo "Deploying to staging..."

  deploy-production:
    needs: [deploy-staging]
    runs-on: ubuntu-latest
    environment: production           # Requires manual approval

    steps:
      - name: Deploy to production
        run: echo "Deploying to production..."
```

GitHub Environments let you set different secrets per environment and require manual approval before production deploys.

| Aspect | Staging | Production |
|--------|---------|------------|
| Purpose | Test before real users see it | Serve real users |
| Data | Seed/test data | Real user data |
| URL | `staging-api.example.com` | `api.example.com` |
| Access | Team only | Public |
| Mobile analogy | TestFlight / Internal Testing | App Store / Production Track |

## Health Check Endpoints

Every deployed application needs a health check endpoint. Deployment platforms use it to verify your app started correctly.

```python
# app/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Check if the app can serve requests (database is reachable)."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

**Liveness** (`/health`): Is the process running? Restart if not.
**Readiness** (`/health/ready`): Can the app serve requests? Stop sending traffic if not.

## Zero-Downtime Deployments

When you deploy a new version, you don't want users to see errors during the transition.

**Rolling update strategy:**

```
1. New version container starts alongside old version
2. Health check passes on new version
3. Traffic shifts to new version
4. Old version container stops
```

This happens automatically on Railway, Fly.io, and ECS. The key requirement: your health check endpoint must work correctly. If the new version fails health checks, the platform rolls back to the old version automatically.

Mobile analogy: This is like phased rollout on the Play Store -- 1% of users get the new version first, then 10%, then 100%. But faster: the rollout happens in seconds, not days.

## Mobile Distribution vs Backend Deployment

| Aspect | Mobile Distribution | Backend Deployment |
|--------|-------------------|-------------------|
| Artifact | .ipa / .aab | Docker image |
| Registry | App Store Connect / Play Console | Docker Hub / ECR / GHCR |
| Review process | 1-3 days (iOS) / hours (Android) | None -- instant |
| Rollback | Not possible (submit new version) | Instant (redeploy previous image) |
| Rollout speed | Hours to days | Seconds to minutes |
| Environments | TestFlight + App Store | Staging + Production |
| Downtime | N/A (client-side) | Zero-downtime with rolling updates |
| Hotfix time | Days (App Store Review) | Minutes |

## Key Takeaways

- Railway is the simplest deployment platform -- connect GitHub and push. Like Firebase App Distribution for backends
- Fly.io gives more control over regions, scaling, and networking while staying developer-friendly
- AWS ECS is production-grade but requires managing task definitions, services, and load balancers
- Always deploy to staging first, then production -- use GitHub Environments for approval gates
- Health check endpoints (`/health`) are required for deployment platforms to verify your app is running
- Zero-downtime deployments use rolling updates: new version starts, passes health check, then old version stops
- Backend deployment is instant compared to mobile -- no app store review, rollback in seconds
- Tag Docker images with git SHA so you always know exactly which commit is deployed
