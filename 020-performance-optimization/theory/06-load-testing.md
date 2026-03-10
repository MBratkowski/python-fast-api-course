# Load Testing with Locust

## Why This Matters

On iOS, you write `measure {}` blocks in XCTest to benchmark individual methods and track performance regressions. On Android, the Benchmark library (Jetpack Benchmark or Macrobenchmark) measures startup time, frame rendering, and function execution with statistical rigor. Both platforms focus on client-side performance.

Backend performance testing is different. You need to know: how many requests per second can your API handle? What happens to response time when 500 users hit it simultaneously? At what point does it break? Load testing answers these questions before your users find out in production. Locust is the Python-native tool for this.

## What Load Testing Validates

| Metric | What It Tells You | Acceptable Range |
|--------|-------------------|-----------------|
| **RPS (Requests Per Second)** | Throughput -- how many requests your API handles | Depends on your expected traffic |
| **p50 (median)** | Response time for the typical request | < 200ms for most APIs |
| **p95** | Response time for 95% of requests | < 500ms |
| **p99** | Response time for 99% of requests (worst case minus outliers) | < 1000ms |
| **Error rate** | Percentage of requests that fail under load | < 1% |
| **Time to first error** | When your system starts failing | Should survive expected peak load |

**Mobile analogy:** p50/p95/p99 latency percentiles are like frame rendering times. p50 = typical frame, p95 = occasional jank, p99 = the worst stutter. You track percentiles, not averages, because averages hide the bad cases.

## Locust Introduction

Locust is a Python load testing framework. You write test scenarios as Python classes:

```python
# locustfile.py
from locust import HttpUser, task, between


class APIUser(HttpUser):
    """Simulates a user interacting with the API."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task(3)  # Weight: 3x more likely than weight-1 tasks
    def get_users(self):
        self.client.get("/users")

    @task(1)
    def create_user(self):
        self.client.post("/users", json={
            "name": "Test User",
            "email": f"test{self.environment.runner.user_count}@example.com",
        })

    @task(2)
    def get_user_detail(self):
        self.client.get("/users/1")

    def on_start(self):
        """Called when a simulated user starts. Use for login/setup."""
        response = self.client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass",
        })
        token = response.json().get("access_token")
        self.client.headers["Authorization"] = f"Bearer {token}"
```

### Key Locust Concepts

| Concept | What It Does |
|---------|-------------|
| `HttpUser` | Base class for a simulated user that makes HTTP requests |
| `@task(weight)` | Marks a method as a task. Weight controls relative frequency |
| `wait_time` | Time each user waits between tasks (simulates think time) |
| `between(min, max)` | Random wait time between min and max seconds |
| `on_start()` | Setup method called once when a simulated user starts |
| `self.client` | An HTTP client (based on requests) scoped to this user |

## Writing a Locustfile for FastAPI

A realistic locustfile tests your actual API endpoints with realistic data:

```python
# locustfile.py
import random
from locust import HttpUser, task, between


class FastAPIUser(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        """Authenticate and store the token."""
        resp = self.client.post("/auth/login", data={
            "username": "loadtest@example.com",
            "password": "testpassword123",
        })
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.token}"

    @task(5)
    def list_items(self):
        """Most common operation: browsing."""
        self.client.get("/api/items", params={"page": random.randint(1, 10)})

    @task(3)
    def get_item_detail(self):
        """Viewing a single item."""
        item_id = random.randint(1, 100)
        self.client.get(f"/api/items/{item_id}")

    @task(1)
    def create_item(self):
        """Less common: creating an item."""
        self.client.post("/api/items", json={
            "title": f"Load Test Item {random.randint(1, 10000)}",
            "description": "Created during load test",
            "price": round(random.uniform(1.0, 100.0), 2),
        })

    @task(1)
    def search_items(self):
        """Search functionality."""
        terms = ["python", "fastapi", "backend", "api", "test"]
        self.client.get("/api/items/search", params={
            "q": random.choice(terms),
        })
```

## Running Locust

### Web UI mode (development)

```bash
# Start Locust with web UI
locust -f locustfile.py --host http://localhost:8000

# Open browser at http://localhost:8089
# Set number of users, spawn rate, and click Start
```

### Headless mode (CI)

```bash
# Run without web UI -- perfect for CI pipelines
locust -f locustfile.py \
    --host http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 60s \
    --headless \
    --csv results
```

Parameters:
- `--users 100`: Simulate 100 concurrent users
- `--spawn-rate 10`: Add 10 users per second until reaching 100
- `--run-time 60s`: Run for 60 seconds then stop
- `--headless`: No web UI
- `--csv results`: Export results to CSV files

## Interpreting Results

Locust output (web UI or CSV) shows:

```
Name             # Reqs  # Fails  Avg   Min   Max   p50   p95   p99   RPS
GET /users         4521     0     45    12    890   38    120   450   75.4
POST /users        1504     3     120   45    2100  95    350   1200  25.1
GET /users/1       3012     0     32    8     450   25    85    290   50.2
Total              9037     3     58    8     2100  42    150   650   150.6
```

**How to read it:**
- **Avg 45ms** for GET /users -- your typical list endpoint
- **p95 120ms** -- 95% of requests complete within 120ms
- **p99 450ms** -- 99% within 450ms (the long tail)
- **RPS 75.4** -- handling 75 list requests per second
- **3 failures** on POST -- investigate why

**Red flags:**
- p99 >> p95 -- you have outlier requests; check for occasional slow queries or GC pauses
- Increasing latency over time -- likely a resource leak (connections, memory)
- Errors appear at a specific user count -- you've found your capacity limit

## Simple Benchmarking with timeit

For micro-benchmarks (comparing two implementations), you don't need Locust:

```python
import timeit

# Compare two implementations
def approach_a():
    return sum(range(10000))

def approach_b():
    return 10000 * 9999 // 2

# timeit runs the function many times and returns total seconds
time_a = timeit.timeit(approach_a, number=10000)
time_b = timeit.timeit(approach_b, number=10000)

print(f"Approach A: {time_a:.4f}s")  # e.g., 1.2345s
print(f"Approach B: {time_b:.4f}s")  # e.g., 0.0012s
```

### Using time.perf_counter for manual timing

```python
import time
import statistics

def benchmark(func, iterations=100):
    """Run a function N times and return timing statistics."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return {
        "min": min(times),
        "max": max(times),
        "avg": statistics.mean(times),
        "p95": sorted(times)[int(len(times) * 0.95)],
    }

result = benchmark(approach_a, iterations=1000)
print(f"avg={result['avg']*1000:.2f}ms  p95={result['p95']*1000:.2f}ms")
```

## Load Testing in CI

Add load testing to your CI pipeline to catch performance regressions:

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  pull_request:
    branches: [main]

jobs:
  load-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r requirements.txt locust

      - name: Start API server
        run: uvicorn main:app --host 0.0.0.0 --port 8000 &
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/testdb

      - name: Wait for server
        run: |
          for i in {1..30}; do
            curl -s http://localhost:8000/health && break
            sleep 1
          done

      - name: Run load test
        run: |
          locust -f locustfile.py \
            --host http://localhost:8000 \
            --users 50 \
            --spawn-rate 5 \
            --run-time 30s \
            --headless \
            --csv results

      - name: Check results
        run: |
          # Fail if p95 > 500ms or error rate > 1%
          python check_results.py results_stats.csv
```

## Key Takeaways

1. **Load test before deploying.** Finding out your API breaks at 200 concurrent users is better in staging than in production.
2. **Measure percentiles, not averages.** p95 and p99 tell you about the worst-case experience. An average of 50ms hides the fact that 5% of users wait 2 seconds.
3. **Use Locust for HTTP load testing.** It's Python-native, easy to write, and supports both web UI and headless (CI) modes.
4. **Use `timeit` or `time.perf_counter` for micro-benchmarks.** Comparing two function implementations doesn't need a full load test framework.
5. **Test realistic scenarios.** Weight your tasks to match real usage patterns (more reads than writes, authentication flows, pagination).
6. **Watch for increasing latency over time.** If response times grow during a load test, you likely have a resource leak (connection pool exhaustion, memory growth).
