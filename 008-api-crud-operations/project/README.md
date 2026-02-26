# Project: Notes Application CRUD API

## Overview

Build a complete CRUD API for a notes application with proper architecture: service layer, dependency injection, pagination, filtering, and error handling. This project brings together everything from this module and Module 007.

## Requirements

### 1. Database Setup (SQLAlchemy + SQLite)

**Models:**

**User:**
- `id`: int, primary key
- `username`: str (max 50), unique, indexed
- `email`: str (max 255), unique, indexed
- `created_at`: datetime, default now

**Note:**
- `id`: int, primary key
- `title`: str (max 200), not null
- `content`: text, not null
- `author_id`: int, foreign key to users.id
- `is_pinned`: bool, default false
- `created_at`: datetime, default now
- `updated_at`: datetime, default now, update on change
- Relationship: `author` (many-to-one to User)

**Tag:**
- `id`: int, primary key
- `name`: str (max 50), unique

**Note Tags (association table):**
- `note_id`: int, FK to notes.id
- `tag_id`: int, FK to tags.id
- Many-to-many relationship between Note and Tag

### 2. Pydantic Schemas

**User Schemas:**
- `UserCreate`: username, email
- `UserResponse`: id, username, email, created_at

**Note Schemas:**
- `NoteCreate`: title, content, tag_names (list[str], optional)
- `NoteUpdate`: title, content, is_pinned, tag_names (all optional)
- `NoteResponse`: id, title, content, is_pinned, created_at, updated_at, author (UserResponse), tags (list[str])

**Tag Schemas:**
- `TagResponse`: id, name

### 3. Service Layer

**UserService:**
- `create(user_data)` - create user with duplicate checking
- `get_by_id(user_id)` - get user or None
- `get_by_username(username)` - get user or None
- `list(skip, limit)` - paginated list

**NoteService:**
- `create(author_id, note_data)` - create note with tags
- `get_by_id(note_id)` - get note with author and tags
- `list_user_notes(user_id, skip, limit, ...)` - user's notes with filters
- `update(note_id, note_data)` - update note and tags
- `delete(note_id)` - delete note
- `search(query, user_id, ...)` - search in title/content

### 4. API Endpoints

**Users:**
- `POST /users` - Create user
- `GET /users/{user_id}` - Get user
- `GET /users` - List users (paginated)

**Notes:**
- `POST /notes` - Create note
- `GET /notes/{note_id}` - Get note with author and tags
- `GET /notes` - List all notes (paginated, with filters)
- `GET /users/{user_id}/notes` - List user's notes (paginated, with filters)
- `PATCH /notes/{note_id}` - Update note
- `DELETE /notes/{note_id}` - Delete note

**Filters for note listing:**
- `is_pinned`: bool - filter pinned/unpinned
- `tag`: str - filter by tag name
- `search`: str - search in title and content
- `sort_by`: "created_at" | "updated_at" | "title"
- `sort_order`: "asc" | "desc"

**Tags:**
- `GET /tags` - List all tags
- `GET /tags/{tag_id}/notes` - List notes with tag

### 5. Pagination

Use `PaginatedResponse` schema:
- `items`: list of items
- `total`: total count
- `page`: current page
- `page_size`: items per page
- `total_pages`: total pages

### 6. Error Handling

- 400 Bad Request - validation errors, duplicate username/email
- 404 Not Found - user/note/tag not found
- 422 Unprocessable Entity - Pydantic validation errors

## Starter Template

```python
# notes_api.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Table, Column, Integer
from sqlalchemy import create_engine, select, or_, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar


# ============= Models =============

class Base(DeclarativeBase):
    pass


note_tags = Table(
    "note_tags",
    Base.metadata,
    # TODO: Define columns
)


class User(Base):
    __tablename__ = "users"
    # TODO: Define fields and relationships


class Note(Base):
    __tablename__ = "notes"
    # TODO: Define fields and relationships


class Tag(Base):
    __tablename__ = "tags"
    # TODO: Define fields and relationships


# ============= Schemas =============

class UserCreate(BaseModel):
    # TODO: Define


class UserResponse(BaseModel):
    # TODO: Define


class NoteCreate(BaseModel):
    # TODO: Define


class NoteUpdate(BaseModel):
    # TODO: Define


class TagResponse(BaseModel):
    # TODO: Define


class NoteResponse(BaseModel):
    # TODO: Define (include author and tags)


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    # TODO: Define


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# ============= Database Setup =============

engine = create_engine("sqlite:///notes.db", echo=True)
Base.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


# ============= Services =============

class UserService:
    def __init__(self, db: Session):
        self.db = db

    # TODO: Implement methods


class NoteService:
    def __init__(self, db: Session):
        self.db = db

    # TODO: Implement methods


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_note_service(db: Session = Depends(get_db)) -> NoteService:
    return NoteService(db)


# ============= API Routes =============

app = FastAPI(title="Notes API", version="1.0.0")


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, service: UserService = Depends(get_user_service)):
    # TODO: Implement
    pass


# Note endpoints
@app.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(note_data: NoteCreate, service: NoteService = Depends(get_note_service)):
    # TODO: Implement (hardcode author_id=1 for now, or add as query param)
    pass


@app.get("/notes", response_model=PaginatedResponse[NoteResponse])
async def list_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_pinned: bool | None = None,
    tag: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: SortOrder = SortOrder.desc,
    service: NoteService = Depends(get_note_service)
):
    # TODO: Implement
    pass


# ... Add remaining endpoints


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Success Criteria

- [ ] All models defined with correct relationships
- [ ] All Pydantic schemas created
- [ ] UserService fully implemented with validation
- [ ] NoteService fully implemented with tag handling
- [ ] Can create users with duplicate checking
- [ ] Can create notes with tags
- [ ] Can list notes with pagination
- [ ] Can filter notes by pinned status, tag, search query
- [ ] Can sort notes by different fields and orders
- [ ] Can update notes including tags
- [ ] Can delete notes
- [ ] Pagination returns correct metadata
- [ ] All endpoints return appropriate error codes
- [ ] Tag relationship works correctly (many-to-many)

## Testing Your Implementation

```bash
# Start the API
python notes_api.py

# In another terminal:
# Create user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com"}'

# Create note with tags
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Note", "content": "Hello world!", "tag_names": ["personal", "ideas"]}'

# List notes
curl "http://localhost:8000/notes?page=1&page_size=10"

# Search notes
curl "http://localhost:8000/notes?search=hello"

# Filter by tag
curl "http://localhost:8000/notes?tag=ideas"

# Get note with details
curl http://localhost:8000/notes/1
```

## Stretch Goals

1. **User Authentication:**
   - Add password field (hashed)
   - Create `/auth/login` endpoint returning token
   - Add `get_current_user` dependency
   - Protect endpoints - users can only access their own notes

2. **Note Sharing:**
   - Add `SharedNote` model (note_id, shared_with_user_id)
   - Add endpoints: `POST /notes/{note_id}/share`, `GET /shared-with-me`
   - Users can share notes with other users

3. **Full-Text Search:**
   - Add database indexes for text search
   - Implement ranking by relevance
   - Highlight search terms in results

4. **Note Versions:**
   - Add `NoteVersion` model to track edits
   - Store previous versions when updating
   - Add endpoint to view version history

5. **Bulk Operations:**
   - `POST /notes/bulk` - create multiple notes
   - `DELETE /notes/bulk` - delete multiple notes by IDs
   - `PATCH /notes/bulk/pin` - pin/unpin multiple notes
