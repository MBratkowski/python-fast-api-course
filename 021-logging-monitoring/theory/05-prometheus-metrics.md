# Prometheus Metrics

## Why This Matters

On mobile, Firebase Performance Monitoring tracks network request latency, app startup time, and custom traces. You can see P50/P95 response times, success rates, and trends over time. These are metrics -- numerical measurements collected over time that tell you how your app is performing.

Prometheus is the standard metrics system for backend applications. Instead of Firebase collecting metrics from your mobile app, Prometheus scrapes metrics from your API server. It collects time-series data (request count, response duration, error rate) and lets you build dashboards and alerts.

**Note:** This topic is theory only. Running Prometheus requires infrastructure (a Prometheus server, Grafana for dashboards). The concepts here prepare you for when you deploy with monitoring infrastructure.

## What Prometheus Does

Prometheus is a time-series database and monitoring system:

1. **Scrapes metrics** from your application at regular intervals (e.g., every 15 seconds)
2. **Stores time-series data** with labels for filtering (endpoint, method, status code)
3. **Queries with PromQL** -- a query language for aggregating and analyzing metrics
4. **Sends alerts** when thresholds are exceeded (via Alertmanager)

Your FastAPI app exposes a `/metrics` endpoint. Prometheus fetches it periodically:

```
Prometheus Server                    Your FastAPI App
     |                                      |
     |-- GET /metrics (every 15s) --------->|
     |                                      |-- Returns current metric values
     |<-- 200 OK (text/plain) --------------|
     |                                      |
     |   Stores: http_requests_total{       |
     |     method="GET",                    |
     |     endpoint="/users",               |
     |     status="200"                     |
     |   } = 1542                           |
```

## Metric Types

Prometheus has four metric types:

### 1. Counter

A value that only goes up. Reset to zero when the process restarts.

```
# Total HTTP requests served
http_requests_total{method="GET", endpoint="/users", status="200"} 1542
http_requests_total{method="POST", endpoint="/users", status="201"} 89
http_requests_total{method="GET", endpoint="/users", status="500"} 3
```

**Use for:** Request count, error count, bytes transferred, tasks completed.

**Mobile analogy:** Firebase event count -- `screen_view` count only goes up.

### 2. Gauge

A value that can go up or down. Represents a current state.

```
# Currently active connections
http_active_connections 47

# Current CPU usage
process_cpu_usage 0.23

# Items in queue
task_queue_size 12
```

**Use for:** Temperature, queue size, active connections, memory usage.

**Mobile analogy:** Current memory usage in Firebase Performance.

### 3. Histogram

Tracks the distribution of values. Groups observations into configurable buckets.

```
# Response time distribution
http_request_duration_seconds_bucket{le="0.1"} 980   # 980 requests under 100ms
http_request_duration_seconds_bucket{le="0.5"} 1450  # 1450 requests under 500ms
http_request_duration_seconds_bucket{le="1.0"} 1498  # 1498 requests under 1s
http_request_duration_seconds_bucket{le="+Inf"} 1500 # 1500 total requests
http_request_duration_seconds_sum 245.7               # Total seconds spent
http_request_duration_seconds_count 1500              # Total request count
```

**Use for:** Request duration, response size, database query time.

**Mobile analogy:** Firebase Performance traces with percentile breakdowns (P50, P95, P99).

### 4. Summary

Similar to histogram but calculates percentiles on the client side. Less commonly used.

```
http_request_duration_seconds{quantile="0.5"} 0.042   # P50
http_request_duration_seconds{quantile="0.95"} 0.287  # P95
http_request_duration_seconds{quantile="0.99"} 0.871  # P99
```

**Rule of thumb:** Prefer histograms over summaries. Histograms allow server-side aggregation across instances; summaries don't.

## Auto-Instrumenting FastAPI

The `prometheus-fastapi-instrumentator` library automatically collects metrics for every endpoint:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Add Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}
```

This automatically:
- Creates a `/metrics` endpoint on your app
- Tracks request count per endpoint, method, and status code
- Tracks request duration as a histogram
- Tracks request/response sizes
- Tracks in-progress requests

### What `/metrics` Returns

```
GET /metrics HTTP/1.1

# HELP http_requests_total Total number of requests by method, status and handler.
# TYPE http_requests_total counter
http_requests_total{handler="/users/{user_id}",method="GET",status="2xx"} 1542.0
http_requests_total{handler="/users/{user_id}",method="GET",status="4xx"} 23.0

# HELP http_request_duration_seconds Duration of HTTP requests in seconds.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{handler="/users/{user_id}",le="0.01"} 890.0
http_request_duration_seconds_bucket{handler="/users/{user_id}",le="0.05"} 1400.0
http_request_duration_seconds_bucket{handler="/users/{user_id}",le="0.1"} 1520.0
http_request_duration_seconds_bucket{handler="/users/{user_id}",le="+Inf"} 1565.0
```

### Custom Metrics

You can add your own metrics alongside the auto-instrumented ones:

```python
from prometheus_client import Counter, Histogram

# Custom counter for business events
login_counter = Counter(
    "user_logins_total",
    "Total number of user logins",
    labelnames=["method"],  # "password", "google", "apple"
)

# Custom histogram for business operations
order_processing_duration = Histogram(
    "order_processing_duration_seconds",
    "Time to process an order",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)


@app.post("/auth/login")
async def login(credentials: LoginRequest):
    user = await authenticate(credentials)
    login_counter.labels(method="password").inc()
    return {"access_token": create_token(user)}


@app.post("/orders")
async def create_order(order: OrderCreate):
    with order_processing_duration.time():
        result = await process_order(order)
    return result
```

## What to Monitor

The "Four Golden Signals" from Google's SRE book:

| Signal | What It Measures | Prometheus Metric | Alert Example |
|--------|-----------------|-------------------|---------------|
| **Latency** | Request duration | `http_request_duration_seconds` | P95 > 500ms for 5 minutes |
| **Traffic** | Request rate | `http_requests_total` | Rate drops > 50% in 5 minutes |
| **Errors** | Error rate | `http_requests_total{status="5xx"}` | Error rate > 1% for 5 minutes |
| **Saturation** | Resource usage | `process_cpu_usage`, memory | CPU > 80% for 10 minutes |

**Mobile analogy:** Firebase Performance gives you the same signals -- network latency, request count, error rate, and device CPU/memory.

## Grafana Dashboards

Prometheus stores the data; Grafana visualizes it. A typical FastAPI dashboard shows:

- **Request rate** -- requests per second over time
- **Error rate** -- percentage of 5xx responses
- **Latency percentiles** -- P50, P95, P99 response times
- **Active connections** -- current concurrent requests
- **Endpoint breakdown** -- which endpoints are slowest or most error-prone

Common PromQL queries for dashboards:

```promql
# Request rate (requests per second, averaged over 5 minutes)
rate(http_requests_total[5m])

# Error rate (percentage of 5xx responses)
sum(rate(http_requests_total{status="5xx"}[5m])) / sum(rate(http_requests_total[5m]))

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Slowest endpoints by P99
histogram_quantile(0.99, sum by (handler) (rate(http_request_duration_seconds_bucket[5m])))
```

## Key Takeaways

1. **Prometheus scrapes your app.** Your app exposes `/metrics`, and Prometheus pulls data at regular intervals. This is the opposite of mobile analytics where the app pushes data.
2. **Four metric types:** Counter (only goes up), Gauge (goes up and down), Histogram (distribution), Summary (percentiles). Use counters for events, gauges for current state, histograms for durations.
3. **Use `prometheus-fastapi-instrumentator`** for automatic HTTP metrics. It instruments every endpoint with zero code changes.
4. **Monitor the Four Golden Signals:** Latency, traffic, errors, and saturation. These cover the most critical aspects of API health.
5. **Custom metrics for business logic.** Track login methods, order processing times, payment success rates -- anything specific to your domain.
6. **Grafana for visualization.** Prometheus stores data; Grafana builds dashboards. Together they replace Firebase Performance dashboards for your backend.
