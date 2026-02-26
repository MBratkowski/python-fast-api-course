# Module 020: Performance Optimization

## Why This Module?

Fast APIs mean happy users. Learn to identify bottlenecks and optimize your backend.

## What You'll Learn

- Profiling Python code
- Database query optimization
- N+1 query problem
- Connection pooling
- Async optimization
- Load testing

## Topics

### Theory
1. Profiling with cProfile
2. Database Query Analysis
3. Solving N+1 Queries
4. Connection Pooling
5. Async Best Practices
6. Load Testing with locust

### Project
Profile and optimize a slow API endpoint.

## Common Optimizations

```python
# N+1 Problem - BAD
users = await session.execute(select(User))
for user in users:
    posts = await session.execute(
        select(Post).where(Post.user_id == user.id)
    )  # N queries!

# N+1 Solution - GOOD
users = await session.execute(
    select(User).options(selectinload(User.posts))
)  # 2 queries total

# Connection pooling
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
)

# Async gather for concurrent operations
async def get_dashboard(user_id: int):
    user, posts, stats = await asyncio.gather(
        get_user(user_id),
        get_posts(user_id),
        get_stats(user_id),
    )
    return {"user": user, "posts": posts, "stats": stats}
```
