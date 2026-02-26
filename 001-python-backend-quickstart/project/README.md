# Project: User Data Processor

## Overview

Build a data processing module that demonstrates Python backend concepts. This simulates a common backend task: fetching data from multiple sources and combining it.

## Requirements

Create a `user_processor.py` file that:

1. **Defines Models** using dataclasses:
   - `User`: id, name, email
   - `UserProfile`: user, posts_count, followers_count, is_active

2. **Implements Async Functions**:
   - `fetch_user(user_id)` → User | None
   - `fetch_user_stats(user_id)` → dict with posts_count, followers_count
   - `get_full_profile(user_id)` → UserProfile | None (fetch both concurrently!)

3. **Uses Type Hints** everywhere

4. **Includes a Main Function** that:
   - Fetches profiles for users 1, 2, 3 concurrently
   - Prints results in a formatted way

## Example Output

```
$ python user_processor.py

Fetching profiles for users [1, 2, 3]...

User: Alice (alice@example.com)
  Posts: 42 | Followers: 1500 | Active: Yes

User: Bob (bob@example.com)
  Posts: 15 | Followers: 230 | Active: Yes

User 3: Not found
```

## Starter Template

```python
# user_processor.py
import asyncio
from dataclasses import dataclass
from typing import Optional

# TODO: Define User dataclass

# TODO: Define UserProfile dataclass

# Simulated data sources (use these)
USERS_DB = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}

STATS_DB = {
    1: {"posts_count": 42, "followers_count": 1500},
    2: {"posts_count": 15, "followers_count": 230},
}

async def fetch_user(user_id: int) -> ...:
    """Simulate fetching user from database."""
    await asyncio.sleep(0.1)  # Simulate latency
    # TODO: Implement

async def fetch_user_stats(user_id: int) -> ...:
    """Simulate fetching user stats."""
    await asyncio.sleep(0.1)
    # TODO: Implement

async def get_full_profile(user_id: int) -> ...:
    """Fetch user and stats concurrently, return UserProfile."""
    # TODO: Implement with asyncio.gather

async def main():
    """Fetch and display profiles for multiple users."""
    # TODO: Implement

if __name__ == "__main__":
    asyncio.run(main())
```

## Success Criteria

- [ ] Models defined with proper type hints
- [ ] Async functions work correctly
- [ ] `get_full_profile` uses concurrent fetching
- [ ] Main function processes multiple users concurrently
- [ ] Code passes mypy type checking
- [ ] Output is formatted nicely

## Stretch Goals

1. Add a `@timer` decorator to measure function execution time
2. Add error handling for missing users
3. Add a cache decorator to avoid refetching the same user
