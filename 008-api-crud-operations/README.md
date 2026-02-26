# Module 008: Building CRUD APIs

## Why This Module?

Combine everything: FastAPI + Pydantic + SQLAlchemy to build complete REST APIs with Create, Read, Update, Delete operations.

## What You'll Learn

- Full CRUD endpoint implementation
- Dependency injection for database sessions
- Service layer pattern
- Error handling
- Pagination

## Topics

### Theory
1. CRUD Endpoint Design
2. FastAPI Depends() for DB Sessions
3. Service Layer Pattern
4. Handling Not Found
5. Pagination & Filtering
6. Bulk Operations

### Project
Build a complete CRUD API for a notes application.

## Example Structure

```
src/
├── api/
│   └── users.py      # Route handlers
├── models/
│   └── user.py       # SQLAlchemy model
├── schemas/
│   └── user.py       # Pydantic schemas
├── services/
│   └── user.py       # Business logic
└── db/
    └── session.py    # Database session
```

```python
# api/users.py
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```
