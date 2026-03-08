# When to Use Microservices

## Why This Matters

As a mobile developer, you have seen both approaches. Google runs Maps and Waze as separate apps (services), but they share underlying data. Facebook split Messenger into a separate app. On the other hand, Apple keeps most functionality inside one iOS app. The decision to split is never purely technical -- it involves team structure, deployment speed, and scaling needs.

The most common mistake junior backend developers make is starting with microservices. Starting with a monolith and splitting later is almost always the right approach. This section teaches you how to recognize when a monolith becomes painful enough to justify the complexity of microservices.

## Monolith vs Microservices

### Monolith Architecture

One application, one codebase, one deployment.

```
┌─────────────────────────────────────┐
│           Monolith App              │
│                                     │
│  ┌──────────┐  ┌──────────────────┐ │
│  │  Users   │  │  Orders          │ │
│  │  Module  │  │  Module          │ │
│  └────┬─────┘  └────┬─────────────┘ │
│       │              │               │
│  ┌────┴──────────────┴─────────────┐ │
│  │       Shared Database           │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Pros:**
- Simple to develop, test, and deploy
- One codebase to understand
- No network calls between modules (function calls are fast)
- Easy data consistency (one database, one transaction)
- Simple debugging (one log stream, one debugger)

**Cons:**
- Entire app redeploys for any change
- All modules scale together (even if only one needs it)
- Large codebase becomes hard to navigate
- One slow module can slow down everything
- Team coupling: changes in one area can break another

### Microservices Architecture

Multiple services, each independently deployed.

```
┌──────────────┐     ┌──────────────┐
│ User Service │     │ Order Service│
│              │◄───►│              │
│   Port 8001  │HTTP │   Port 8002  │
│   ┌──────┐   │     │   ┌──────┐   │
│   │Users │   │     │   │Orders│   │
│   │  DB  │   │     │   │  DB  │   │
│   └──────┘   │     │   └──────┘   │
└──────────────┘     └──────────────┘
```

**Pros:**
- Independent deployment per service
- Independent scaling (scale order service without scaling user service)
- Team autonomy (each team owns a service)
- Technology flexibility (Python for ML, Go for performance)
- Fault isolation (one service down does not crash everything)

**Cons:**
- Network complexity (HTTP calls, timeouts, retries)
- Data consistency is hard (no cross-service transactions)
- Operational overhead (monitoring, logging, deployment for each service)
- Debugging across services is challenging (distributed tracing needed)
- Testing integration between services is complex

## When to Decompose

### Signals That You Need Microservices

| Signal | Why It Matters |
|--------|---------------|
| Multiple teams working on same codebase | Frequent merge conflicts, deployment coordination |
| One module needs different scaling | Paying to scale the entire app when only one part is hot |
| Deployment takes too long | Full test suite runs for every small change |
| One module's failure crashes everything | No fault isolation |
| Different parts need different tech | ML in Python, real-time in Go |

### Signals to Stay with a Monolith

| Signal | Why It Matters |
|--------|---------------|
| Small team (< 10 developers) | Microservices overhead exceeds team capacity |
| Early-stage product | Requirements change too fast to define service boundaries |
| Tightly coupled data | Services would need constant cross-service queries |
| Simple scaling needs | Horizontal scaling of the monolith is sufficient |

## The Premature Microservices Anti-Pattern

```
DON'T do this:

Day 1: "Let's build a microservices architecture!"
Day 30: 15 services, 0 users, 3 developers drowning in infrastructure

DO this:

Day 1: Build a modular monolith
Day 180: 10,000 users, identify bottleneck in payment processing
Day 181: Extract payment service as first microservice
Day 365: Extract notification service (different scaling needs)
```

### The Modular Monolith: Best of Both Worlds

Start with a monolith but keep strong module boundaries:

```python
# Good monolith structure (easy to split later)
project/
├── src/
│   ├── users/          # Could become user-service
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── routes.py
│   ├── orders/         # Could become order-service
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── routes.py
│   └── main.py         # Combines all modules
```

**Rule:** Modules communicate through defined interfaces (service layer), not by reaching into each other's database tables. This makes future extraction straightforward.

## Real-World Examples

### Companies That Started Monolith

| Company | Started As | Split When | Why |
|---------|-----------|------------|-----|
| Amazon | Monolith | ~2002 | Teams stepping on each other |
| Netflix | Monolith | ~2009 | Scaling needs for streaming |
| Shopify | Monolith (Ruby on Rails) | Still mostly monolith | Modular monolith works at scale |
| Basecamp | Monolith | Never split | Small team, monolith is simpler |

### Mobile Analogy: App Suites

- **Google**: Maps, Waze, Search -- separate apps (services) that share data
- **Facebook**: Facebook, Messenger, Instagram -- split for team autonomy and performance
- **Apple**: Mail, Calendar, Contacts -- separate apps but deeply integrated

The same forces apply: team size, performance isolation, and independent release schedules drive the decision to split.

## Decision Framework

```
Question 1: Do you have multiple teams?
  No  → Stay monolith
  Yes → Continue

Question 2: Are teams blocking each other on deployments?
  No  → Stay monolith (use feature flags)
  Yes → Continue

Question 3: Do parts of your system have different scaling needs?
  No  → Stay monolith
  Yes → Consider splitting THAT part

Question 4: Can you define clear service boundaries?
  No  → Stay monolith (unclear boundaries = distributed monolith)
  Yes → Extract that service
```

## Key Takeaways

1. **Start with a monolith** -- it is simpler to develop, test, deploy, and debug
2. **Premature microservices** are worse than a monolith -- you get all the complexity with none of the benefits
3. **Split when you feel pain** -- not before. Signals: team conflicts, scaling bottlenecks, deployment friction
4. **Keep module boundaries clean** in your monolith so extraction is easy when the time comes
5. **Microservices add complexity** -- network calls, distributed data, operational overhead. Only pay this cost when you must
6. **A "distributed monolith"** (microservices with tight coupling) is the worst of both worlds
