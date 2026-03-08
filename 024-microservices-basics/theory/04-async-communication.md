# Asynchronous Communication

## Why This Matters

On iOS, you use `NotificationCenter` to broadcast events that multiple observers can handle independently. On Android, `SharedFlow` and `EventBus` decouple publishers from subscribers. Backend microservices use the same pattern: instead of calling another service directly (HTTP), you publish an event and let interested services react to it.

Synchronous communication (HTTP calls) creates tight coupling -- the caller waits for a response and breaks if the callee is down. Asynchronous communication (events/messages) decouples services -- the publisher does not know or care who consumes the event, and it does not wait for them.

## Sync vs Async Communication

```
Synchronous (HTTP):

Order Service ──HTTP──→ User Service
    │                        │
    │   Waits for response   │
    │◄───── Response ────────│
    │
    If User Service is down, Order Service fails too!


Asynchronous (Events):

Order Service ──publish──→ Redis Channel ──→ User Service
    │                                       Email Service
    │ Does NOT wait                         Analytics Service
    │
    Continues immediately. If subscribers are down,
    they process events when they come back up.
```

### When to Use Each

| Use Case | Sync (HTTP) | Async (Events) |
|----------|-------------|-----------------|
| Need immediate response | Yes | No |
| Query data from another service | Yes | No |
| Notify about an event | No | Yes |
| Trigger a background process | No | Yes |
| Send notifications | No | Yes |
| Update a read model/cache | No | Yes |

**Rule of thumb:** Use sync for queries ("get me this data"), async for events ("something happened").

## Redis Pub/Sub

Redis pub/sub is a lightweight messaging system built into Redis. It is perfect for simple event-driven communication between services.

```
Publisher (Order Service):
    redis.publish("order_events", '{"type": "order_created", ...}')

                    │
                    ▼

Redis Channel: "order_events"

                    │
           ┌────────┼────────┐
           ▼        ▼        ▼

Subscriber 1    Subscriber 2    Subscriber 3
(Email svc)     (Analytics)     (Inventory)
```

### Publisher

```python
import json
import time
from datetime import datetime, timezone

import redis.asyncio as redis


async def publish_event(
    redis_client: redis.Redis,
    channel: str,
    event_type: str,
    payload: dict,
) -> None:
    """
    Publish an event to a Redis channel.

    Event format:
    {
        "event_type": "order_created",
        "timestamp": "2024-03-08T12:00:00Z",
        "payload": { ... }
    }
    """
    event = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    await redis_client.publish(channel, json.dumps(event))


# Usage in Order Service
async def create_order(order_data: dict, redis_client: redis.Redis):
    # 1. Save order to database
    order = save_order(order_data)

    # 2. Publish event (fire and forget)
    await publish_event(
        redis_client,
        channel="order_events",
        event_type="order_created",
        payload={
            "order_id": order["id"],
            "user_id": order["user_id"],
            "total": order["total"],
        },
    )

    return order
```

### Subscriber

```python
import json
import redis.asyncio as redis


async def subscribe_to_events(
    redis_client: redis.Redis,
    channel: str,
    handler,
):
    """
    Subscribe to a Redis channel and process events.

    The handler function receives each event as a dict.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    async for message in pubsub.listen():
        if message["type"] == "message":
            event = json.loads(message["data"])
            await handler(event)


# Event handler in Email Service
async def handle_order_event(event: dict):
    """Process order events."""
    if event["event_type"] == "order_created":
        order_id = event["payload"]["order_id"]
        user_id = event["payload"]["user_id"]
        print(f"Sending confirmation email for order {order_id} to user {user_id}")
        # await send_email(user_id, "Order Confirmation", ...)

    elif event["event_type"] == "order_cancelled":
        order_id = event["payload"]["order_id"]
        print(f"Sending cancellation email for order {order_id}")
        # await send_email(user_id, "Order Cancelled", ...)
```

## Message Format Conventions

Standardize your event format across all services:

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import uuid


class EventType(str, Enum):
    ORDER_CREATED = "order_created"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_SHIPPED = "order_shipped"
    USER_REGISTERED = "user_registered"
    PAYMENT_COMPLETED = "payment_completed"


@dataclass
class Event:
    """Standard event format for all services."""
    event_id: str           # Unique ID for idempotency
    event_type: str         # What happened
    timestamp: str          # When it happened (ISO 8601)
    source: str             # Which service published it
    payload: dict           # Event-specific data

    @classmethod
    def create(cls, event_type: EventType, source: str, payload: dict) -> "Event":
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type.value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=source,
            payload=payload,
        )

    def to_json(self) -> str:
        return json.dumps({
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "source": self.source,
            "payload": self.payload,
        })

    @classmethod
    def from_json(cls, data: str) -> "Event":
        d = json.loads(data)
        return cls(**d)
```

## Eventual Consistency

With async communication, data is **eventually** consistent -- there is a brief period where services have different views of the data.

```
Timeline:

T0: Order Service creates order → order exists in Order DB
T1: Event published: "order_created"
T2: Email Service receives event → sends email
T3: Analytics Service receives event → updates dashboard
T4: Inventory Service receives event → decrements stock

Between T0 and T4, the services have inconsistent views.
By T4, everything is consistent -- this is "eventual consistency."
```

**This is usually acceptable.** Most business processes do not need instant consistency. The user does not need their analytics dashboard updated in the same millisecond as their order.

## Complete Example: Order Events

```python
import json
from datetime import datetime, timezone
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI


# === Order Service ===

@asynccontextmanager
async def order_lifespan(app: FastAPI):
    app.state.redis = redis.from_url("redis://localhost:6379")
    yield
    await app.state.redis.aclose()

order_service = FastAPI(lifespan=order_lifespan)

orders = {}
next_id = 1

@order_service.post("/orders")
async def create_order(user_id: int, total: float):
    global next_id
    order = {"id": next_id, "user_id": user_id, "total": total, "status": "created"}
    orders[next_id] = order
    next_id += 1

    # Publish event
    event = {
        "event_type": "order_created",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": order,
    }
    await order_service.state.redis.publish("order_events", json.dumps(event))

    return order


@order_service.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int):
    order = orders.get(order_id)
    if not order:
        return {"error": "Not found"}

    order["status"] = "cancelled"

    event = {
        "event_type": "order_cancelled",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {"order_id": order_id, "user_id": order["user_id"]},
    }
    await order_service.state.redis.publish("order_events", json.dumps(event))

    return order
```

## Mobile Analogy

The pub/sub pattern maps directly to mobile event systems:

| Platform | Publish | Subscribe | Channel |
|----------|---------|-----------|---------|
| iOS | `NotificationCenter.default.post(name:)` | `.addObserver(forName:)` | `Notification.Name` |
| Android | `sharedFlow.emit(event)` | `sharedFlow.collect { }` | `SharedFlow<Event>` |
| Redis | `redis.publish(channel, data)` | `pubsub.subscribe(channel)` | String channel name |

The key difference: mobile events are in-process (instant), Redis events are across-network (milliseconds of delay, but decoupled services).

## Key Takeaways

1. **Use sync for queries, async for events** -- "get me data" = HTTP, "something happened" = pub/sub
2. **Redis pub/sub** is the simplest way to start with event-driven architecture
3. **Standardize event format** with event_type, timestamp, source, and payload
4. **Include event_id** for idempotency -- subscribers may receive duplicates
5. **Eventual consistency is normal** -- services will have briefly inconsistent views of data
6. **Fire and forget**: the publisher does not wait for subscribers, making it faster and more resilient
