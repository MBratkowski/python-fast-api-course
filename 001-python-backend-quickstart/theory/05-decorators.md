# Decorators

## Why This Matters

FastAPI uses decorators everywhere:

```python
@app.get("/users")        # This is a decorator
async def get_users():
    ...
```

Understanding decorators helps you read FastAPI code and write your own.

## What's a Decorator?

A decorator is a function that wraps another function to add behavior.

```python
# Without decorator syntax
def my_function():
    return "Hello"

my_function = some_decorator(my_function)

# With decorator syntax (same thing!)
@some_decorator
def my_function():
    return "Hello"
```

## Building a Decorator

```python
import functools
import time

def timer(func):
    """Measure function execution time"""
    @functools.wraps(func)  # Preserves function metadata
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

slow_function()  # Prints: slow_function took 1.00s
```

## Decorators with Arguments

```python
def repeat(times: int):
    """Repeat function call n times"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say_hello():
    print("Hello!")

say_hello()
# Hello!
# Hello!
# Hello!
```

## Async Decorators

For async functions:

```python
import functools
import time

def async_timer(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)  # await the async function
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

@async_timer
async def fetch_data():
    await asyncio.sleep(1)
    return {"data": "value"}
```

## Real-World Examples

### Authentication Decorator

```python
from functools import wraps
from fastapi import HTTPException

def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if user is authenticated
        request = kwargs.get('request')
        if not request.user.is_authenticated:
            raise HTTPException(status_code=401)
        return await func(*args, **kwargs)
    return wrapper
```

### Caching Decorator

```python
def cache(ttl_seconds: int = 60):
    def decorator(func):
        cache_data = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache_data:
                return cache_data[key]
            result = await func(*args, **kwargs)
            cache_data[key] = result
            return result
        return wrapper
    return decorator

@cache(ttl_seconds=300)
async def get_user(user_id: int):
    return await db.fetch_user(user_id)
```

## FastAPI Decorators

Now you understand what these do:

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/users/{user_id}")  # Registers route
@cache(ttl_seconds=60)        # Adds caching
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)  # Dependency injection
):
    return await db.get_user(user_id)
```

## Key Takeaways

1. **Decorators wrap functions** to add behavior
2. **`@functools.wraps`** preserves the original function's metadata
3. **`*args, **kwargs`** passes through all arguments
4. **FastAPI decorators** register routes and add functionality
5. You can **stack decorators** - they apply bottom to top
