# Data Consistency in Microservices

## Why This Matters

In a monolith, you wrap related database operations in a transaction -- either everything succeeds or nothing does. But in microservices, each service has its own database. You cannot use a single transaction across two databases on different servers. This is the fundamental data consistency challenge of distributed systems.

Understanding these concepts helps you make informed decisions about when to accept eventual consistency, when to use compensating actions, and when the complexity of microservices is not worth the tradeoff.

## CAP Theorem

The CAP theorem states that a distributed system can only guarantee two of three properties simultaneously:

```
                Consistency
                    /\
                   /  \
                  /    \
                 /      \
                /  Pick  \
               /   Two    \
              /            \
             /              \
            /________________\
    Availability      Partition
                      Tolerance
```

| Property | Meaning |
|----------|---------|
| **Consistency** | Every read returns the most recent write |
| **Availability** | Every request receives a response (even if not the latest data) |
| **Partition tolerance** | System works even when network between nodes fails |

**In practice:** Network partitions always happen in distributed systems, so you must choose between consistency and availability:

- **CP (Consistency + Partition tolerance):** System may become unavailable during partitions but never returns stale data. Example: banking systems.
- **AP (Availability + Partition tolerance):** System stays available during partitions but may return stale data. Example: social media feeds.

**For most APIs:** Choose AP (availability) with eventual consistency. Users can tolerate seeing a slightly stale product listing; they cannot tolerate the app being down.

## Eventual Consistency

In a microservices system, data is **eventually** consistent -- after an update, there is a brief period where different services have different views. Given enough time (usually milliseconds to seconds), all services converge to the same state.

```
Timeline of an order creation:

T0: Order Service creates order (order exists in Order DB)
T1: Order Service publishes "order_created" event
T2: Inventory Service receives event, decrements stock
T3: Email Service receives event, sends confirmation
T4: Analytics Service receives event, updates metrics

Between T0 and T4: services have inconsistent views
After T4: all services are consistent
Duration: typically 10-100ms
```

### When Eventual Consistency is OK

| Scenario | Acceptable? | Why |
|----------|-------------|-----|
| Order confirmation email sent 2 seconds late | Yes | User does not notice |
| Analytics dashboard 30 seconds behind | Yes | Analytics are always approximate |
| Inventory shows 5 items but only 4 remain | Depends | May oversell if not handled |
| Bank balance incorrect for 5 seconds | No | Financial data must be immediately consistent |

## Saga Pattern

A saga is a sequence of local transactions across services, with compensating actions for rollback.

```
Traditional Transaction (monolith):
  BEGIN TRANSACTION
    1. Create order
    2. Charge payment
    3. Update inventory
  COMMIT (all succeed) or ROLLBACK (any fails)


Saga (microservices):
  Step 1: Order Service → Create order (status: pending)
  Step 2: Payment Service → Charge payment
    If fails → Compensate Step 1: Cancel order
  Step 3: Inventory Service → Reserve items
    If fails → Compensate Step 2: Refund payment
               Compensate Step 1: Cancel order
  Step 4: Order Service → Update order (status: confirmed)
```

### Choreography-Based Saga

Each service listens for events and acts independently:

```
Order Service                Payment Service              Inventory Service
    │                             │                             │
    │ publish:                    │                             │
    │ "order_created"             │                             │
    │─────────────────────────────│                             │
    │                             │ subscribe:                  │
    │                             │ "order_created"             │
    │                             │ → charge payment            │
    │                             │                             │
    │                             │ publish:                    │
    │                             │ "payment_completed"         │
    │                             │─────────────────────────────│
    │                             │                             │ subscribe:
    │                             │                             │ "payment_completed"
    │                             │                             │ → reserve items
    │                             │                             │
    │                             │                             │ publish:
    │◄────────────────────────────│─────────────────────────────│ "items_reserved"
    │ subscribe:                  │                             │
    │ "items_reserved"            │                             │
    │ → confirm order             │                             │
```

### Orchestration-Based Saga

A central orchestrator coordinates the steps:

```python
class OrderSaga:
    """Orchestrator that coordinates the order creation saga."""

    async def execute(self, order_data: dict):
        """Execute the order saga with compensating actions."""
        # Step 1: Create order
        order = await self.create_order(order_data)

        try:
            # Step 2: Process payment
            payment = await self.process_payment(order)
        except PaymentError:
            # Compensate Step 1
            await self.cancel_order(order["id"])
            raise

        try:
            # Step 3: Reserve inventory
            await self.reserve_inventory(order)
        except InventoryError:
            # Compensate Step 2 and Step 1
            await self.refund_payment(payment["id"])
            await self.cancel_order(order["id"])
            raise

        # Step 4: Confirm order
        await self.confirm_order(order["id"])
        return order
```

## Idempotency

In distributed systems, messages can be delivered more than once (network retries, consumer restarts). Operations must be **idempotent** -- processing the same message twice should produce the same result.

```python
# NOT idempotent: processing twice doubles the charge
async def process_payment(order_id: int, amount: float):
    await charge_credit_card(amount)  # Charged twice if message is retried!

# Idempotent: processing twice has no additional effect
async def process_payment(order_id: int, amount: float, idempotency_key: str):
    # Check if this payment was already processed
    existing = await db.get_payment(idempotency_key=idempotency_key)
    if existing:
        return existing  # Already processed, return existing result

    # Process new payment
    payment = await charge_credit_card(amount)
    await db.save_payment(payment, idempotency_key=idempotency_key)
    return payment
```

### Idempotency Strategies

| Strategy | How It Works | Example |
|----------|-------------|---------|
| Idempotency key | Client sends unique key; server checks for duplicates | Payment processing |
| Event ID deduplication | Store processed event IDs; skip duplicates | Event consumers |
| Upsert operations | INSERT or UPDATE based on unique constraint | Database writes |
| Version checking | Compare version/timestamp before updating | Optimistic locking |

## Distributed Transactions: Why to Avoid Them

Two-phase commit (2PC) is the traditional solution for distributed transactions, but it has serious problems:

```
Two-Phase Commit:

Phase 1 (Prepare):
  Coordinator → Service A: "Can you commit?"  → "Yes"
  Coordinator → Service B: "Can you commit?"  → "Yes"

Phase 2 (Commit):
  Coordinator → Service A: "Commit!"  → Done
  Coordinator → Service B: "Commit!"  → Done

Problems:
  - If coordinator crashes between phases → all services locked
  - Holding locks across network → high latency
  - One slow service blocks everything
  - Does not scale to many services
```

**Recommendation:** Use sagas instead of distributed transactions. Accept eventual consistency where possible. Reserve strong consistency for operations that truly require it (financial transactions).

## Practical Guidelines

### 1. Accept Eventual Consistency Where Possible

Most operations do not need immediate consistency:
- Send email after order is created (eventual)
- Update search index after product changes (eventual)
- Aggregate analytics data (eventual)

### 2. Use Idempotent Operations Everywhere

Every event handler, every API endpoint, every background task should be idempotent.

### 3. Keep Sagas Simple

Start with 2-3 step sagas. If a saga has 10 steps with 10 compensating actions, your service boundaries are probably wrong.

### 4. Monitor Inconsistencies

Track when services are inconsistent and for how long:
- Log event processing delays
- Alert on events that are not consumed within expected time
- Periodically reconcile data between services

## Key Takeaways

1. **CAP theorem:** In distributed systems, choose between consistency and availability. Most APIs choose availability (AP)
2. **Eventual consistency** is the norm in microservices -- services converge to the same state over time
3. **Saga pattern** replaces transactions with a sequence of local transactions plus compensating actions
4. **Idempotency** is essential -- every operation must safely handle being executed multiple times
5. **Avoid distributed transactions** (2PC) -- they are slow, fragile, and do not scale
6. **If consistency requirements are complex**, question whether microservices are the right architecture -- a monolith with one database may be simpler and more correct
