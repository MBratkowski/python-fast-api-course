# Bulk Operations

## Why This Matters

In mobile development, you often need to sync multiple items at once: upload 50 offline photos, sync 100 changed notes, delete 20 selected items. Doing this one-by-one is slow - 50 requests instead of 1.

Bulk operations let clients send many items in a single request, dramatically improving performance and reducing network overhead.

## Bulk Create

Create multiple items in one request:

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str

class BulkCreateResponse(BaseModel):
    created: int
    items: list[UserResponse]

@router.post("/users/bulk", response_model=BulkCreateResponse, status_code=201)
async def bulk_create_users(
    users_data: list[UserCreate],
    db: AsyncSession = Depends(get_db)
):
    """Create multiple users at once."""
    users = [User(**user_data.model_dump()) for user_data in users_data]

    db.add_all(users)
    await db.commit()

    # Refresh all to get IDs
    for user in users:
        await db.refresh(user)

    return BulkCreateResponse(
        created=len(users),
        items=users
    )
```

**Request:**

```json
POST /users/bulk
[
    {"username": "alice", "email": "alice@example.com"},
    {"username": "bob", "email": "bob@example.com"},
    {"username": "charlie", "email": "charlie@example.com"}
]
```

**Response:**

```json
HTTP/1.1 201 Created
{
    "created": 3,
    "items": [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "bob", "email": "bob@example.com"},
        {"id": 3, "username": "charlie", "email": "charlie@example.com"}
    ]
}
```

### With Validation

Handle partial failures:

```python
class BulkCreateResult(BaseModel):
    created: list[UserResponse]
    failed: list[dict]

@router.post("/users/bulk", response_model=BulkCreateResult, status_code=201)
async def bulk_create_users(
    users_data: list[UserCreate],
    db: AsyncSession = Depends(get_db)
):
    """Create multiple users, report successes and failures."""
    created = []
    failed = []

    for index, user_data in enumerate(users_data):
        try:
            # Check if username exists
            result = await db.execute(
                select(User).where(User.username == user_data.username)
            )
            if result.scalar_one_or_none():
                failed.append({
                    "index": index,
                    "data": user_data.model_dump(),
                    "error": "Username already exists"
                })
                continue

            # Create user
            user = User(**user_data.model_dump())
            db.add(user)
            await db.flush()  # Get ID without committing
            await db.refresh(user)

            created.append(user)

        except Exception as e:
            failed.append({
                "index": index,
                "data": user_data.model_dump(),
                "error": str(e)
            })

    # Commit all successful creates
    await db.commit()

    return BulkCreateResult(created=created, failed=failed)
```

**Response with partial failures:**

```json
{
    "created": [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "charlie", "email": "charlie@example.com"}
    ],
    "failed": [
        {
            "index": 1,
            "data": {"username": "bob", "email": "bob@example.com"},
            "error": "Username already exists"
        }
    ]
}
```

## Bulk Update

Update multiple items:

```python
class BulkUpdateItem(BaseModel):
    id: int
    data: UserUpdate

@router.patch("/users/bulk")
async def bulk_update_users(
    updates: list[BulkUpdateItem],
    db: AsyncSession = Depends(get_db)
):
    """Update multiple users."""
    updated = []
    failed = []

    for item in updates:
        user = await db.get(User, item.id)

        if not user:
            failed.append({
                "id": item.id,
                "error": "User not found"
            })
            continue

        # Update fields
        for key, value in item.data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await db.flush()
        await db.refresh(user)
        updated.append(user)

    await db.commit()

    return {
        "updated": updated,
        "failed": failed
    }
```

**Request:**

```json
PATCH /users/bulk
[
    {"id": 1, "data": {"is_active": false}},
    {"id": 2, "data": {"email": "newemail@example.com"}},
    {"id": 3, "data": {"username": "newusername"}}
]
```

### Bulk Update by Criteria

Update all items matching criteria (no IDs needed):

```python
@router.patch("/users/bulk/deactivate")
async def bulk_deactivate_users(
    user_ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """Deactivate multiple users by ID."""
    stmt = (
        update(User)
        .where(User.id.in_(user_ids))
        .values(is_active=False)
    )

    result = await db.execute(stmt)
    await db.commit()

    return {
        "updated": result.rowcount,
        "user_ids": user_ids
    }
```

**Request:**

```json
PATCH /users/bulk/deactivate
[1, 2, 3, 4, 5]
```

**Response:**

```json
{
    "updated": 5,
    "user_ids": [1, 2, 3, 4, 5]
}
```

## Bulk Delete

Delete multiple items:

```python
@router.delete("/users/bulk")
async def bulk_delete_users(
    user_ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """Delete multiple users by ID."""
    stmt = delete(User).where(User.id.in_(user_ids))

    result = await db.execute(stmt)
    await db.commit()

    return {
        "deleted": result.rowcount,
        "user_ids": user_ids
    }
```

**Request:**

```json
DELETE /users/bulk
[1, 2, 3]
```

**Response:**

```json
{
    "deleted": 3,
    "user_ids": [1, 2, 3]
}
```

### With Validation

Check each item exists before deleting:

```python
@router.delete("/users/bulk")
async def bulk_delete_users(
    user_ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """Delete multiple users with validation."""
    deleted = []
    not_found = []

    for user_id in user_ids:
        user = await db.get(User, user_id)

        if not user:
            not_found.append(user_id)
            continue

        await db.delete(user)
        deleted.append(user_id)

    await db.commit()

    return {
        "deleted": deleted,
        "not_found": not_found
    }
```

## Transaction Management for Bulk Operations

### All-or-Nothing (Atomic)

Either all succeed or none do:

```python
@router.post("/users/bulk")
async def bulk_create_users(
    users_data: list[UserCreate],
    db: AsyncSession = Depends(get_db)
):
    """Create users atomically - all succeed or all fail."""
    try:
        users = [User(**user_data.model_dump()) for user_data in users_data]
        db.add_all(users)
        await db.commit()

        for user in users:
            await db.refresh(user)

        return {"created": len(users), "items": users}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Bulk create failed: {str(e)}"
        )
```

If **any** user fails (duplicate username, etc.), **all** are rolled back.

### Best-Effort (Partial Success)

Some can succeed, some can fail:

```python
@router.post("/users/bulk")
async def bulk_create_users(
    users_data: list[UserCreate],
    db: AsyncSession = Depends(get_db)
):
    """Create users with partial success allowed."""
    created = []
    failed = []

    for index, user_data in enumerate(users_data):
        try:
            user = User(**user_data.model_dump())
            db.add(user)
            await db.flush()  # Attempt insert
            await db.refresh(user)
            created.append(user)

        except Exception as e:
            await db.rollback()  # Rollback this item
            failed.append({
                "index": index,
                "error": str(e)
            })

    await db.commit()  # Commit successful items

    return {
        "created": created,
        "failed": failed
    }
```

Each item is independent - failures don't affect others.

## Performance Optimization

### Use Bulk Insert

```python
# ❌ Slow - N database round-trips
for user_data in users_data:
    user = User(**user_data.model_dump())
    db.add(user)
    await db.commit()  # Commit each one!

# ✅ Fast - 1 database round-trip
users = [User(**user_data.model_dump()) for user_data in users_data]
db.add_all(users)
await db.commit()  # Commit all at once
```

### Batch Processing for Large Sets

For thousands of items, process in batches:

```python
@router.post("/users/bulk")
async def bulk_create_users(
    users_data: list[UserCreate],
    db: AsyncSession = Depends(get_db)
):
    """Create users in batches of 100."""
    batch_size = 100
    total_created = 0

    for i in range(0, len(users_data), batch_size):
        batch = users_data[i:i + batch_size]

        users = [User(**user_data.model_dump()) for user_data in batch]
        db.add_all(users)
        await db.commit()

        total_created += len(users)

    return {"created": total_created}
```

This prevents memory issues and long-running transactions.

## Mobile Sync Pattern

Common pattern for offline-first mobile apps:

```python
class SyncItem(BaseModel):
    local_id: str  # Client-generated ID
    action: str  # "create", "update", "delete"
    data: dict | None

@router.post("/sync")
async def sync_items(
    items: list[SyncItem],
    db: AsyncSession = Depends(get_db)
):
    """Sync offline changes from mobile app."""
    results = []

    for item in items:
        try:
            if item.action == "create":
                obj = User(**item.data)
                db.add(obj)
                await db.flush()
                await db.refresh(obj)

                results.append({
                    "local_id": item.local_id,
                    "server_id": obj.id,
                    "status": "created"
                })

            elif item.action == "update":
                obj = await db.get(User, item.data["id"])
                for key, value in item.data.items():
                    setattr(obj, key, value)

                results.append({
                    "local_id": item.local_id,
                    "server_id": obj.id,
                    "status": "updated"
                })

            elif item.action == "delete":
                obj = await db.get(User, item.data["id"])
                await db.delete(obj)

                results.append({
                    "local_id": item.local_id,
                    "status": "deleted"
                })

        except Exception as e:
            results.append({
                "local_id": item.local_id,
                "status": "failed",
                "error": str(e)
            })

    await db.commit()

    return {"results": results}
```

**Request from mobile app:**

```json
POST /sync
[
    {"local_id": "temp-1", "action": "create", "data": {"username": "alice", "email": "alice@example.com"}},
    {"local_id": "temp-2", "action": "update", "data": {"id": 5, "email": "newemail@example.com"}},
    {"local_id": "temp-3", "action": "delete", "data": {"id": 10}}
]
```

**Response:**

```json
{
    "results": [
        {"local_id": "temp-1", "server_id": 42, "status": "created"},
        {"local_id": "temp-2", "server_id": 5, "status": "updated"},
        {"local_id": "temp-3", "status": "deleted"}
    ]
}
```

Mobile app uses `local_id` to match responses to local items, then replaces local IDs with `server_id`.

## Limits and Safety

### Limit Batch Size

```python
@router.post("/users/bulk")
async def bulk_create_users(
    users_data: list[UserCreate] = Body(..., max_items=1000),
    db: AsyncSession = Depends(get_db)
):
    """Create users - max 1000 per request."""
    if len(users_data) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 items per request")

    # Process...
```

Prevents abuse and timeouts.

### Set Request Timeout

```python
# In FastAPI app configuration
app = FastAPI()

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=30.0)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")
```

Prevents requests from running forever.

## Key Takeaways

1. **Bulk operations reduce network overhead** - one request instead of many
2. **Bulk create:** `POST /resource/bulk` with array of items
3. **Bulk update:** `PATCH /resource/bulk` with array of updates
4. **Bulk delete:** `DELETE /resource/bulk` with array of IDs
5. **Choose transaction strategy:** all-or-nothing vs partial success
6. **Use `add_all()` and `flush()`** for efficient database operations
7. **Process large sets in batches** to avoid memory/timeout issues
8. **Limit maximum batch size** to prevent abuse
9. **Return detailed results** - what succeeded, what failed, why
10. **Sync pattern for mobile apps** - create/update/delete in single request
