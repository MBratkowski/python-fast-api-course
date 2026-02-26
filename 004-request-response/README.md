# Module 004: Request & Response Handling

## Why This Module?

Learn how to extract data from incoming requests and format responses. This is the core of API development.

## What You'll Learn

- Path parameters (`/users/{id}`)
- Query parameters (`/users?limit=10`)
- Request headers
- Request body (JSON)
- Response formatting
- Custom status codes

## Topics

### Theory
1. Path Parameters & Type Conversion
2. Query Parameters & Defaults
3. Request Headers
4. Response Models
5. Custom Response Classes
6. Status Codes & Headers

### Exercises
- Build endpoints with various parameter types
- Handle optional and required parameters
- Return different response formats

### Project
Build a product catalog API with filtering, pagination, and sorting.

## Examples

```python
from fastapi import FastAPI, Query, Header, Path

app = FastAPI()

@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(..., gt=0),  # Path param, must be > 0
    q: str | None = Query(None),      # Optional query param
    limit: int = Query(10, le=100),   # Query with default & max
    x_token: str = Header(...),       # Required header
):
    return {
        "item_id": item_id,
        "query": q,
        "limit": limit
    }
```
