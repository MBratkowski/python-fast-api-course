"""
Exercise 2: Redis Pub/Sub Message Passing

Implement event-driven communication between services using Redis pub/sub.
A publisher sends events to a channel, and an EventCollector subscribes
and collects received messages.

Run: pytest 024-microservices-basics/exercises/02_message_passing.py -v

Requirements: pip install fakeredis pytest pytest-asyncio
"""

import asyncio
import json

import fakeredis.aioredis
import pytest
import pytest_asyncio


# ============= TODO: Exercise 2.1 =============
# Implement the publish_event function.
#
# This function publishes a JSON-serialized event to a Redis channel.
#
# The event format should be:
# {
#     "event_type": event_type,
#     "payload": payload
# }
#
# Steps:
# 1. Create a dict with "event_type" and "payload" keys
# 2. Serialize the dict to a JSON string using json.dumps()
# 3. Publish the JSON string to the channel using redis_client.publish(channel, data)
# 4. Return the number of subscribers that received the message (the return value of publish)

async def publish_event(
    redis_client,
    channel: str,
    event_type: str,
    payload: dict,
) -> int:
    """
    Publish an event to a Redis pub/sub channel.

    Args:
        redis_client: Redis (or fakeredis) async client
        channel: The channel name to publish to
        event_type: Type of event (e.g., "order_created")
        payload: Event data as a dictionary

    Returns:
        Number of subscribers that received the message.
    """
    # TODO: Implement
    # 1. Build event dict: {"event_type": event_type, "payload": payload}
    # 2. Serialize to JSON: json.dumps(event)
    # 3. Publish: await redis_client.publish(channel, json_string)
    # 4. Return the result of publish (subscriber count)
    pass


# ============= TODO: Exercise 2.2 =============
# Implement the EventCollector class.
#
# EventCollector subscribes to a Redis channel and collects all
# received messages into a list. This is useful for testing that
# events are correctly published and received.
#
# The class should:
# 1. Subscribe to a channel using redis_client.pubsub()
# 2. Collect messages by listening for messages on the subscription
# 3. Store received events (parsed from JSON) in self.events list
# 4. Support collecting a specific number of events with a timeout

class EventCollector:
    """
    Subscribes to a Redis pub/sub channel and collects received events.

    Usage:
        collector = EventCollector(redis_client, "my_channel")
        await collector.start()
        # ... publish events ...
        events = await collector.collect(count=3, timeout=5.0)
        await collector.stop()
    """

    def __init__(self, redis_client, channel: str):
        """
        Args:
            redis_client: Redis (or fakeredis) async client
            channel: The channel to subscribe to
        """
        self.redis = redis_client
        self.channel = channel
        self.events: list[dict] = []
        self.pubsub = None

    async def start(self):
        """
        Start subscribing to the channel.

        Steps:
        1. Create pubsub object: self.redis.pubsub()
        2. Subscribe to self.channel: await self.pubsub.subscribe(self.channel)
        3. Store pubsub for later use
        """
        # TODO: Implement
        # 1. self.pubsub = self.redis.pubsub()
        # 2. await self.pubsub.subscribe(self.channel)
        pass

    async def collect(self, count: int = 1, timeout: float = 5.0) -> list[dict]:
        """
        Collect a specific number of events from the channel.

        Listens for messages and collects them until either:
        - `count` events have been received, or
        - `timeout` seconds have passed

        Steps:
        1. Use asyncio.wait_for with timeout to prevent hanging
        2. Loop through messages from self.pubsub.listen()
        3. Filter for messages where message["type"] == "message"
        4. Parse message["data"] from JSON: json.loads(message["data"])
        5. Append parsed event to self.events
        6. Stop when len(self.events) >= count

        Returns:
            List of collected event dicts.
        """
        # TODO: Implement
        # Hint: Use async for message in self.pubsub.listen():
        #       Check message["type"] == "message" (skip subscribe confirmations)
        #       Parse JSON: json.loads(message["data"])
        #       Append to self.events
        #       Break when enough events collected
        pass

    async def stop(self):
        """
        Unsubscribe and clean up.

        Steps:
        1. Unsubscribe from channel: await self.pubsub.unsubscribe(self.channel)
        2. Close pubsub: await self.pubsub.aclose()
        """
        # TODO: Implement
        # 1. await self.pubsub.unsubscribe(self.channel)
        # 2. await self.pubsub.aclose()
        pass


# ============= TESTS =============
# Run with: pytest 024-microservices-basics/exercises/02_message_passing.py -v


@pytest_asyncio.fixture
async def redis_client():
    """Create a fresh fakeredis async instance for each test."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()


@pytest.mark.asyncio
async def test_publish_event_format(redis_client):
    """Published event should be valid JSON with event_type and payload."""
    collector = EventCollector(redis_client, "test_channel")
    await collector.start()

    # Publish an event
    await publish_event(
        redis_client,
        channel="test_channel",
        event_type="order_created",
        payload={"order_id": 1, "total": 99.99},
    )

    # Collect and verify
    events = await collector.collect(count=1, timeout=2.0)
    await collector.stop()

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "order_created"
    assert event["payload"]["order_id"] == 1
    assert event["payload"]["total"] == 99.99


@pytest.mark.asyncio
async def test_publish_multiple_events(redis_client):
    """Multiple events on the same channel should all be received."""
    collector = EventCollector(redis_client, "test_channel")
    await collector.start()

    # Publish multiple events
    await publish_event(redis_client, "test_channel", "event_1", {"id": 1})
    await publish_event(redis_client, "test_channel", "event_2", {"id": 2})
    await publish_event(redis_client, "test_channel", "event_3", {"id": 3})

    # Collect all three
    events = await collector.collect(count=3, timeout=2.0)
    await collector.stop()

    assert len(events) == 3
    event_types = [e["event_type"] for e in events]
    assert "event_1" in event_types
    assert "event_2" in event_types
    assert "event_3" in event_types


@pytest.mark.asyncio
async def test_publish_returns_subscriber_count(redis_client):
    """publish_event should return the number of subscribers."""
    # No subscribers yet
    count = await publish_event(redis_client, "empty_channel", "test", {"data": 1})
    assert count == 0, "Should return 0 when no subscribers"

    # Add a subscriber
    collector = EventCollector(redis_client, "test_channel")
    await collector.start()

    count = await publish_event(redis_client, "test_channel", "test", {"data": 1})
    assert count >= 1, "Should return at least 1 when subscriber exists"

    await collector.collect(count=1, timeout=2.0)
    await collector.stop()


@pytest.mark.asyncio
async def test_event_data_preserved(redis_client):
    """Complex payload data should survive JSON serialization."""
    collector = EventCollector(redis_client, "test_channel")
    await collector.start()

    complex_payload = {
        "user_id": 42,
        "items": [
            {"name": "Widget", "price": 9.99},
            {"name": "Gadget", "price": 19.99},
        ],
        "metadata": {"source": "web", "version": "2.0"},
    }

    await publish_event(redis_client, "test_channel", "complex_event", complex_payload)

    events = await collector.collect(count=1, timeout=2.0)
    await collector.stop()

    assert events[0]["payload"] == complex_payload


@pytest.mark.asyncio
async def test_different_channels_independent(redis_client):
    """Events on different channels should not interfere."""
    collector_a = EventCollector(redis_client, "channel_a")
    collector_b = EventCollector(redis_client, "channel_b")
    await collector_a.start()
    await collector_b.start()

    # Publish to channel_a only
    await publish_event(redis_client, "channel_a", "event_a", {"for": "a"})

    # Collector A should receive it
    events_a = await collector_a.collect(count=1, timeout=2.0)
    assert len(events_a) == 1
    assert events_a[0]["event_type"] == "event_a"

    # Collector B should have no events (different channel)
    assert len(collector_b.events) == 0

    await collector_a.stop()
    await collector_b.stop()
