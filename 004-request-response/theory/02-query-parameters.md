# Query Parameters

## Why This Matters

In your mobile app, when you filter a list of products by category or sort by price, those options are sent as query parameters: `/products?category=electronics&sort=price`. On the backend, you need to read those parameters to filter and sort the data. Query parameters are your API's way of accepting optional filters, sorting, pagination, and search options.

## What are Query Parameters?

Query parameters are key-value pairs that come after `?` in the URL. In FastAPI, any function parameter that's NOT in the path automatically becomes a query parameter.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    """
    skip and limit are query parameters because they're not in the path.
    GET /items?skip=20&limit=5
    """
    return {
        "skip": skip,
        "limit": limit,
        "items": ["item1", "item2"]
    }
```

**Request examples:**
- `GET /items` → `skip=0, limit=10` (uses defaults)
- `GET /items?skip=20` → `skip=20, limit=10` (partial override)
- `GET /items?skip=20&limit=5` → `skip=20, limit=5` (full override)

## Optional vs Required Query Parameters

```python
@app.get("/search")
async def search(
    q: str,                    # Required (no default)
    limit: int = 10,           # Optional with default
    category: str | None = None  # Optional, can be None
):
    """
    - q is REQUIRED: /search without ?q=... returns 422
    - limit is OPTIONAL: defaults to 10 if not provided
    - category is OPTIONAL and nullable
    """
    return {
        "query": q,
        "limit": limit,
        "category": category
    }
```

**Request validation:**
- `GET /search` → 422 (missing required `q`)
- `GET /search?q=laptop` → OK (q provided, others use defaults)
- `GET /search?q=laptop&category=electronics` → OK

## Query Parameter Validation

Use the `Query()` function to add constraints and metadata:

```python
from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()

@app.get("/products")
async def list_products(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[str | None, Query(max_length=100)] = None
):
    """
    - skip: must be >= 0 (non-negative)
    - limit: between 1 and 100
    - search: optional, max 100 characters
    """
    return {
        "skip": skip,
        "limit": limit,
        "search": search
    }
```

**Validation constraints:**
- `ge`, `le`, `gt`, `lt` (for numbers)
- `min_length`, `max_length` (for strings)
- `pattern` (regex for strings)
- `description` (for API documentation)

## Multiple Values for One Parameter

To accept multiple values for the same parameter (like multiple category filters):

```python
@app.get("/items")
async def filter_items(
    tags: Annotated[list[str], Query()] = []
):
    """
    GET /items?tags=electronics&tags=sale
    tags will be ["electronics", "sale"]
    """
    return {"tags": tags}
```

Or with default values:

```python
@app.get("/items")
async def filter_items(
    tags: Annotated[list[str] | None, Query()] = None
):
    """
    GET /items → tags is None
    GET /items?tags=electronics&tags=sale → tags is ["electronics", "sale"]
    """
    if tags is None:
        tags = []
    return {"tags": tags}
```

## Query String Encoding

URLs encode special characters:
- Space → `%20` or `+`
- `&` → `%26`
- `=` → `%3D`

FastAPI automatically decodes these:

```python
@app.get("/search")
async def search(q: str):
    """
    GET /search?q=python%20fastapi
    q will be "python fastapi" (decoded automatically)
    """
    return {"query": q}
```

## Boolean Query Parameters

FastAPI handles boolean conversion smartly:

```python
@app.get("/items")
async def list_items(active: bool = True):
    """
    GET /items?active=true → True
    GET /items?active=false → False
    GET /items?active=1 → True
    GET /items?active=0 → False
    GET /items?active=yes → 422 (invalid)
    """
    return {"active": active}
```

## Combining Path and Query Parameters

```python
@app.get("/users/{user_id}/posts")
async def get_user_posts(
    user_id: Annotated[int, Path(ge=1)],
    skip: int = 0,
    limit: int = 10,
    published: bool = True
):
    """
    GET /users/123/posts?skip=20&limit=5&published=true

    user_id comes from path
    skip, limit, published come from query string
    """
    return {
        "user_id": user_id,
        "skip": skip,
        "limit": limit,
        "published_only": published
    }
```

## Pagination Pattern

Standard pagination using query parameters:

```python
@app.get("/items")
async def list_items(
    skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items to return")] = 10
):
    """
    GET /items?skip=0&limit=10 (page 1)
    GET /items?skip=10&limit=10 (page 2)
    GET /items?skip=20&limit=10 (page 3)
    """
    # In real code, fetch from database with skip/limit
    total_items = 100
    items = [f"item_{i}" for i in range(skip, min(skip + limit, total_items))]

    return {
        "items": items,
        "skip": skip,
        "limit": limit,
        "total": total_items
    }
```

## Filtering and Sorting Pattern

```python
from enum import Enum

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@app.get("/products")
async def list_products(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "name",
    order: SortOrder = SortOrder.asc
):
    """
    GET /products?category=electronics&min_price=100&max_price=500&sort_by=price&order=desc
    """
    return {
        "filters": {
            "category": category,
            "price_range": [min_price, max_price]
        },
        "sort": {
            "field": sort_by,
            "order": order
        }
    }
```

## Mobile Developer Context

| Mobile API Call | FastAPI Query Params |
|-----------------|---------------------|
| `api.getProducts(category: "electronics")` | `@app.get("/products")` with `category` param |
| URLComponents queryItems | Function parameters with defaults |
| Retrofit @Query annotation | Type hints + `Query()` |
| Optional parameters | `param: type \| None = None` |

## Key Takeaways

1. **Any function parameter NOT in the path becomes a query parameter**
2. **Provide a default value to make it optional** - `limit: int = 10`
3. **Use `| None` for truly optional parameters** - `category: str | None = None`
4. **No default = required** - `q: str` requires `?q=value`
5. **`Query()` adds validation and documentation** - `ge`, `le`, `max_length`, etc.
6. **Multiple values use `list[type]`** - `tags: list[str]`
7. **Combine with path parameters freely** - path for identity, query for filters
