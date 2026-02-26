# Pagination and Filtering

## Why This Matters

Every mobile app with a list view needs pagination. You can't load 10,000 users into memory - you load 20 at a time and fetch more as the user scrolls. Your API needs to support this.

Filtering lets users narrow down results: "show me active users" or "posts from the last week". Good APIs make filtering intuitive through query parameters.

## Offset-Based Pagination

The simplest pagination pattern: skip N items, take M items.

### Using `skip` and `limit`

```python
from fastapi import Query

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db)
):
    """List users with pagination."""
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return users
```

**Request:** `GET /users?skip=20&limit=10`

**Response:** Users 21-30

**SQL generated:**

```sql
SELECT * FROM users
ORDER BY created_at DESC
OFFSET 20 LIMIT 10;
```

### Using `page` and `page_size`

More intuitive for clients:

```python
@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """List users with page-based pagination."""
    skip = (page - 1) * page_size
    limit = page_size

    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return {"users": users, "page": page, "page_size": page_size}
```

**Request:** `GET /users?page=3&page_size=10`

**Response:** Page 3 (users 21-30)

## Paginated Response with Metadata

Include total count and page information:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List users with full pagination metadata."""
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar()

    # Get paginated results
    skip = (page - 1) * page_size
    result = await db.execute(
        select(User).offset(skip).limit(page_size).order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size  # Ceiling division

    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
```

**Response:**

```json
{
    "items": [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "bob", "email": "bob@example.com"}
    ],
    "total": 42,
    "page": 1,
    "page_size": 10,
    "total_pages": 5
}
```

Mobile app can now show: "Page 1 of 5" or "Showing 10 of 42 users".

## Filtering with Query Parameters

### Simple Filters

```python
@router.get("/users")
async def list_users(
    is_active: bool | None = Query(None, description="Filter by active status"),
    role: str | None = Query(None, description="Filter by role"),
    db: AsyncSession = Depends(get_db)
):
    """List users with filters."""
    query = select(User)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if role is not None:
        query = query.where(User.role == role)

    result = await db.execute(query.order_by(User.created_at.desc()))
    users = result.scalars().all()

    return users
```

**Requests:**
- `GET /users` - All users
- `GET /users?is_active=true` - Only active users
- `GET /users?role=admin` - Only admins
- `GET /users?is_active=true&role=admin` - Active admins

### Search Filters

```python
@router.get("/users")
async def list_users(
    search: str | None = Query(None, description="Search in username and email"),
    db: AsyncSession = Depends(get_db)
):
    """Search users by username or email."""
    query = select(User)

    if search:
        # Case-insensitive search in username and email
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    result = await db.execute(query.order_by(User.created_at.desc()))
    users = result.scalars().all()

    return users
```

**Request:** `GET /users?search=alice`

**SQL:**

```sql
SELECT * FROM users
WHERE username ILIKE '%alice%' OR email ILIKE '%alice%'
ORDER BY created_at DESC;
```

### Date Range Filters

```python
from datetime import datetime

@router.get("/posts")
async def list_posts(
    created_after: datetime | None = Query(None, description="Filter posts created after this date"),
    created_before: datetime | None = Query(None, description="Filter posts created before this date"),
    db: AsyncSession = Depends(get_db)
):
    """List posts with date range filter."""
    query = select(Post)

    if created_after:
        query = query.where(Post.created_at >= created_after)

    if created_before:
        query = query.where(Post.created_at <= created_before)

    result = await db.execute(query.order_by(Post.created_at.desc()))
    posts = result.scalars().all()

    return posts
```

**Request:** `GET /posts?created_after=2024-01-01&created_before=2024-12-31`

## Sorting

Allow clients to choose sort field and order:

```python
from enum import Enum

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/users")
async def list_users(
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort order"),
    db: AsyncSession = Depends(get_db)
):
    """List users with sorting."""
    # Map string to model column
    sort_columns = {
        "created_at": User.created_at,
        "username": User.username,
        "email": User.email
    }

    # Get column or default to created_at
    sort_column = sort_columns.get(sort_by, User.created_at)

    # Apply sort order
    if sort_order == SortOrder.desc:
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    result = await db.execute(
        select(User).order_by(sort_column)
    )
    users = result.scalars().all()

    return users
```

**Requests:**
- `GET /users?sort_by=username&sort_order=asc` - Alphabetically by username
- `GET /users?sort_by=created_at&sort_order=desc` - Newest first

## Combining Pagination, Filtering, and Sorting

Complete example with all features:

```python
@router.get("/users")
async def list_users(
    # Pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),

    # Filters
    is_active: bool | None = None,
    role: str | None = None,
    search: str | None = None,

    # Sorting
    sort_by: str = Query("created_at"),
    sort_order: SortOrder = Query(SortOrder.desc),

    db: AsyncSession = Depends(get_db)
):
    """List users with pagination, filtering, and sorting."""
    # Build base query
    query = select(User)

    # Apply filters
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if role is not None:
        query = query.where(User.role == role)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    # Get total count (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_columns = {
        "created_at": User.created_at,
        "username": User.username,
        "email": User.email
    }
    sort_column = sort_columns.get(sort_by, User.created_at)

    if sort_order == SortOrder.desc:
        sort_column = sort_column.desc()

    query = query.order_by(sort_column)

    # Apply pagination
    skip = (page - 1) * page_size
    query = query.offset(skip).limit(page_size)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Build response
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
```

**Request:** `GET /users?page=2&page_size=20&is_active=true&search=john&sort_by=username&sort_order=asc`

Finds active users matching "john", sorted by username, page 2 (20 per page).

## Mobile App Integration

This API design maps directly to mobile list views:

```swift
// iOS example
class UserListViewModel {
    var page = 1
    let pageSize = 20

    func loadUsers() async {
        let url = "https://api.example.com/users?page=\(page)&page_size=\(pageSize)&is_active=true"
        let response = try await fetch(url)

        self.users = response.items
        self.totalPages = response.total_pages
    }

    func loadMore() {
        page += 1
        loadUsers()
    }
}
```

## Performance Considerations

### Always Use Indexes

```python
# In your model
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), index=True)  # Indexed!
    created_at: Mapped[datetime] = mapped_column(index=True)  # Indexed!
```

Filtering/sorting on indexed columns is fast. Without indexes, queries slow down as data grows.

### Limit Maximum Page Size

```python
page_size: int = Query(10, ge=1, le=100)  # Max 100 items per page
```

Prevents clients from requesting 1 million items and crashing your database.

### Count Queries Can Be Expensive

For large datasets, counting all rows is slow:

```python
# Slow with millions of rows
total = await db.scalar(select(func.count()).select_from(User))
```

**Optimization:** Cache the count or estimate it:

```python
# Estimate from PostgreSQL stats (fast but approximate)
total = await db.scalar(text("SELECT reltuples::bigint FROM pg_class WHERE relname = 'users'"))
```

## Key Takeaways

1. **Offset pagination:** `skip` + `limit` or `page` + `page_size`
2. **Include metadata:** total count, total pages, current page
3. **Filters via query parameters:** `?is_active=true&role=admin`
4. **Search with ILIKE:** Case-insensitive pattern matching
5. **Sorting:** Let clients choose field and order
6. **Combine all three:** Pagination + filtering + sorting in one endpoint
7. **Index frequently filtered/sorted columns** for performance
8. **Limit maximum page size** to prevent abuse
9. **Count queries can be slow** - cache or estimate for large datasets
