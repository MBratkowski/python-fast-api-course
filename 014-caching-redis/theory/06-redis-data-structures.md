# Redis Data Structures

## Why This Matters

On mobile, local caching is almost always simple key-value: `UserDefaults` (iOS) stores strings, numbers, and data blobs by key. `SharedPreferences` (Android) stores primitives by key. You don't have built-in support for sets, sorted lists, or hash maps in your cache layer.

Redis goes far beyond simple key-value. It offers Strings, Hashes, Sets, Sorted Sets, and Lists as first-class data types with atomic operations on each. This means you can build features like leaderboards, unique visitor counters, rate limiters, and job queues directly in Redis without complex application logic.

## Strings

The most basic type. Stores a single value (text, number, or serialized JSON) per key.

```python
import redis

r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# Simple string
r.set("greeting", "Hello, World!")
value = r.get("greeting")  # "Hello, World!"

# Number (stored as string, but supports atomic increment)
r.set("page_views", 0)
r.incr("page_views")      # 1
r.incr("page_views")      # 2
r.incrby("page_views", 10)  # 12

# JSON (serialized as string)
import json
user = {"id": 42, "name": "Alice", "email": "alice@example.com"}
r.setex("user:42", 3600, json.dumps(user))
cached = json.loads(r.get("user:42"))
```

### When to Use Strings

- Simple caching (API responses, computed values)
- Counters (`INCR` is atomic -- safe for concurrent access)
- Rate limiting (increment counter per time window)
- Session storage (serialized session data)

## Hashes

Store a dictionary (field-value pairs) under a single key. Access individual fields without deserializing the whole object.

```python
# Store user as a hash
r.hset("user:42", mapping={
    "name": "Alice",
    "email": "alice@example.com",
    "role": "admin",
    "login_count": "0"
})

# Get single field
name = r.hget("user:42", "name")  # "Alice"

# Get multiple fields
data = r.hmget("user:42", "name", "email")  # ["Alice", "alice@example.com"]

# Get all fields
user = r.hgetall("user:42")
# {"name": "Alice", "email": "alice@example.com", "role": "admin", "login_count": "0"}

# Update single field (without touching others)
r.hset("user:42", "email", "newalice@example.com")

# Increment a field atomically
r.hincrby("user:42", "login_count", 1)  # "1"

# Check if field exists
exists = r.hexists("user:42", "name")  # True

# Delete a field
r.hdel("user:42", "role")
```

### When to Use Hashes

- Storing objects where you need partial reads/updates
- User profiles (update email without rewriting the entire object)
- Configuration maps (update one setting at a time)
- Counters per entity (e.g., per-user stats)

### Hashes vs JSON Strings

| Feature | Hash (`HSET`) | String (`SET` + JSON) |
|---------|---------------|----------------------|
| Partial read | `HGET` (one field) | Must deserialize entire JSON |
| Partial update | `HSET` (one field) | Read-modify-write entire JSON |
| Atomic field increment | `HINCRBY` | Not possible |
| Memory efficiency | Better for small objects | Better for large objects |
| TTL on fields | Not supported (TTL on whole key only) | N/A |

## Sets

Unordered collection of unique values. Supports union, intersection, and difference operations.

```python
# Track unique visitors
r.sadd("visitors:2024-01-15", "user:1")
r.sadd("visitors:2024-01-15", "user:2")
r.sadd("visitors:2024-01-15", "user:1")  # Ignored (duplicate)

# Count unique visitors
count = r.scard("visitors:2024-01-15")  # 2

# Check if user visited
visited = r.sismember("visitors:2024-01-15", "user:1")  # True

# Get all members
visitors = r.smembers("visitors:2024-01-15")  # {"user:1", "user:2"}

# Set operations
r.sadd("visitors:2024-01-16", "user:2", "user:3")

# Users who visited both days
both_days = r.sinter("visitors:2024-01-15", "visitors:2024-01-16")
# {"user:2"}

# All unique users across both days
all_users = r.sunion("visitors:2024-01-15", "visitors:2024-01-16")
# {"user:1", "user:2", "user:3"}

# Users who visited day 1 but not day 2
only_day1 = r.sdiff("visitors:2024-01-15", "visitors:2024-01-16")
# {"user:1"}
```

### When to Use Sets

- Unique visitor tracking
- Tag systems (which posts have tag X?)
- Online user lists
- Feature flags (which users are in the beta?)
- Friendship/following relationships

## Sorted Sets

Like Sets, but each member has a score. Members are ordered by score. Ideal for rankings and leaderboards.

```python
# Leaderboard: add players with scores
r.zadd("leaderboard", {"alice": 2500, "bob": 1800, "charlie": 3100})

# Get top 3 players (highest scores first)
top = r.zrevrange("leaderboard", 0, 2, withscores=True)
# [("charlie", 3100.0), ("alice", 2500.0), ("bob", 1800.0)]

# Get player's rank (0-indexed, highest first)
rank = r.zrevrank("leaderboard", "alice")  # 1 (second place)

# Get player's score
score = r.zscore("leaderboard", "alice")  # 2500.0

# Increment score (player earned points)
new_score = r.zincrby("leaderboard", 500, "bob")  # 2300.0

# Get players within a score range
mid_tier = r.zrangebyscore("leaderboard", 2000, 3000, withscores=True)
# [("bob", 2300.0), ("alice", 2500.0)]

# Count players in a score range
count = r.zcount("leaderboard", 2000, 3000)  # 2

# Remove a player
r.zrem("leaderboard", "bob")
```

### When to Use Sorted Sets

- Leaderboards and rankings
- Priority queues (score = priority)
- Time-based feeds (score = timestamp)
- Rate limiting with sliding windows (score = request timestamp)
- Autocomplete suggestions (score = popularity)

### Rate Limiting with Sorted Sets

```python
import time

async def is_rate_limited(
    cache: redis.Redis,
    user_id: str,
    max_requests: int = 100,
    window_seconds: int = 60
) -> bool:
    """Sliding window rate limiter using sorted set."""
    key = f"rate:{user_id}"
    now = time.time()
    window_start = now - window_seconds

    pipe = cache.pipeline()
    # Remove old entries outside the window
    pipe.zremrangebyscore(key, 0, window_start)
    # Add current request
    pipe.zadd(key, {str(now): now})
    # Count requests in window
    pipe.zcard(key)
    # Set TTL on the key itself
    pipe.expire(key, window_seconds)
    results = await pipe.execute()

    request_count = results[2]
    return request_count > max_requests
```

## Lists

Ordered sequence of values. Supports push/pop from both ends. Ideal for queues and activity feeds.

```python
# Activity feed (most recent first)
r.lpush("feed:user:42", "Liked a post")
r.lpush("feed:user:42", "Commented on photo")
r.lpush("feed:user:42", "Updated profile")

# Get last 10 activities
recent = r.lrange("feed:user:42", 0, 9)
# ["Updated profile", "Commented on photo", "Liked a post"]

# Trim to keep only last 100 entries (memory management)
r.ltrim("feed:user:42", 0, 99)

# Queue pattern (FIFO)
r.rpush("job_queue", "job:1")  # Add to end
r.rpush("job_queue", "job:2")
job = r.lpop("job_queue")      # Take from front: "job:1"

# Blocking pop (wait for item, useful for workers)
# job = r.blpop("job_queue", timeout=30)  # Wait up to 30 seconds
```

### When to Use Lists

- Activity feeds (recent N events)
- Job queues (FIFO with `RPUSH` / `LPOP`)
- Message history (chat messages)
- Undo stacks (push/pop operations)

## Choosing the Right Data Structure

| Need | Structure | Key Operation |
|------|-----------|--------------|
| Cache a value | String | `SET` / `GET` |
| Count things atomically | String | `INCR` / `INCRBY` |
| Store object fields | Hash | `HSET` / `HGET` |
| Track unique items | Set | `SADD` / `SISMEMBER` |
| Rank/sort items | Sorted Set | `ZADD` / `ZREVRANGE` |
| Queue or feed | List | `LPUSH` / `LPOP` |

## Pipelining

Reduce network round trips by sending multiple commands at once.

```python
# Without pipeline: 3 round trips
r.set("a", "1")
r.set("b", "2")
r.set("c", "3")

# With pipeline: 1 round trip
pipe = r.pipeline()
pipe.set("a", "1")
pipe.set("b", "2")
pipe.set("c", "3")
pipe.execute()  # All three commands sent at once
```

Pipelining is especially important when performing multiple operations (e.g., invalidating multiple cache keys).

## Mobile Platform Comparison

| Concept | iOS/Swift | Android/Kotlin | Python/Redis |
|---------|-----------|----------------|--------------|
| Key-value | `UserDefaults` | `SharedPreferences` | Strings (`SET`/`GET`) |
| Object fields | `UserDefaults` (flat) | `SharedPreferences` (flat) | Hashes (`HSET`/`HGET`) |
| Unique collection | `Set<String>` (in-memory) | `HashSet` (in-memory) | Sets (`SADD`/`SMEMBERS`) |
| Sorted/ranked | Custom sort on Array | Custom sort on List | Sorted Sets (built-in) |
| Queue | `DispatchQueue` (tasks) | `Channel` (coroutines) | Lists (`RPUSH`/`LPOP`) |
| Atomic counter | Not built-in (need lock) | `AtomicInteger` | `INCR` (built-in, atomic) |
| Batch operations | Not applicable | Not applicable | Pipeline (`pipe.execute()`) |

## Key Takeaways

- Redis offers 5 core data structures: Strings, Hashes, Sets, Sorted Sets, and Lists
- **Strings** are the default for simple caching -- use `INCR` for atomic counters
- **Hashes** store objects with partial read/update -- better than JSON for frequently changing fields
- **Sets** track unique items with set operations (union, intersection)
- **Sorted Sets** power leaderboards, rate limiting, and time-based queries
- **Lists** serve as queues and activity feeds with push/pop operations
- Use **pipelining** to batch multiple commands into a single network round trip
- Mobile parallel: `UserDefaults`/`SharedPreferences` only support key-value; Redis handles complex data structures natively
