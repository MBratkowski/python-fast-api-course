# Module 022: API Versioning

## Why This Module?

APIs evolve. Learn to version your API so existing mobile apps don't break when you add features.

## What You'll Learn

- Versioning strategies
- URL versioning (/v1/, /v2/)
- Header versioning
- Deprecation handling
- Breaking vs non-breaking changes
- Migration strategies

## Topics

### Theory
1. Why Version APIs?
2. URL Path Versioning
3. Header Versioning
4. Breaking vs Non-Breaking Changes
5. Deprecation Notices
6. Maintaining Multiple Versions

### Project
Add versioning to your API with migration path.

## Example

```python
from fastapi import APIRouter, Header

# URL versioning
v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    return {"id": user_id, "name": "Alice"}  # Old format

@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    return {
        "data": {"id": user_id, "name": "Alice"},
        "meta": {"version": "2.0"}
    }  # New format

app.include_router(v1_router)
app.include_router(v2_router)

# Header versioning alternative
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    api_version: str = Header("1.0", alias="X-API-Version")
):
    if api_version == "2.0":
        return {"data": {...}, "meta": {...}}
    return {"id": user_id, "name": "Alice"}
```
