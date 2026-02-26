# Project: Add Roles and Permissions to API

## Overview

Add complete Role-Based Access Control (RBAC) to an existing notes API. Implement user roles, role checking dependencies, resource ownership verification, and an admin panel for user management.

**Goal**: Secure your API with roles and permissions — users can only access their own resources unless they're admins or moderators.

## Requirements

### 1. User Model Updates

Update your User model to include:
- `role`: Enum field (Role.ADMIN, Role.USER, Role.MODERATOR), default USER
- `is_active`: Boolean field, default True

### 2. Note Model

Create a Note model:
- `id`: Primary key
- `title`: String
- `content`: Text
- `author_id`: Foreign key to users
- `is_public`: Boolean, default False

### 3. Authentication System

From Module 009:
- POST /auth/signup (always creates USER role)
- POST /auth/login (returns access token)
- POST /auth/refresh (optional)
- `get_current_user` dependency

### 4. Role Dependencies

Implement:
- `require_role(required_role: Role)` — Dependency factory for single role
- `require_any_role(allowed_roles: list[Role])` — Dependency factory for multiple roles

### 5. Protected Note Endpoints

**User permissions**:
- POST /notes — Create note (authenticated users)
- GET /notes — List own notes
- GET /notes/public — List all public notes
- GET /notes/{id} — Get note (own notes OR public notes)
- PUT /notes/{id} — Update note (owner only)
- DELETE /notes/{id} — Delete note (owner only)

**Moderator permissions**:
- All user permissions
- PATCH /notes/{id}/flag — Flag/unflag inappropriate notes
- GET /notes/flagged — List flagged notes

**Admin permissions**:
- All moderator permissions
- Full CRUD on any note

### 6. Admin Panel Endpoints

All require admin role (use router dependencies):

- GET /admin/users — List all users with roles
- PATCH /admin/users/{id}/role — Change user role (prevent escalation to admin, prevent changing own role)
- PATCH /admin/users/{id}/activate — Activate/deactivate user
- GET /admin/stats — System statistics (total users, active users, users by role, total notes, public notes)

### 7. Ownership Checks

Implement `get_note_or_403` dependency:
- Fetch note by ID
- Return 404 if not found
- Return 403 if user is not owner AND not admin/moderator AND note is not public
- Return note if authorized

## Success Criteria

- [ ] Users created with USER role by default (never admin)
- [ ] Users can only CRUD their own notes
- [ ] Users can read public notes from others
- [ ] Moderators can flag/unflag any note
- [ ] Admins can CRUD any note and manage users
- [ ] Admin endpoints protected by role dependency on router
- [ ] Cannot promote users to admin role via API
- [ ] Admins cannot change their own role
- [ ] All endpoints return 403 for authorization failures (not 401)
- [ ] Resource ownership verified for update/delete operations

## Starter Template

```python
"""
Notes API with Roles and Permissions
TODO: Implement RBAC for notes management
"""

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy import String, Boolean, Text, Enum as SQLEnum, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from typing import Annotated
from enum import Enum
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

# ============= Configuration =============

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# ============= Database Models =============

class Base(DeclarativeBase):
    pass


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    notes: Mapped[list["Note"]] = relationship(back_populates="author")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)

    author: Mapped["User"] = relationship(back_populates="notes")


# ============= Pydantic Schemas =============

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: Role
    is_active: bool


class NoteCreate(BaseModel):
    title: str
    content: str
    is_public: bool = False


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_public: bool | None = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author_id: int
    is_public: bool
    is_flagged: bool


# ============= Database Setup =============

engine = create_engine("sqlite:///./notes.db")
Base.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


# ============= Security Setup =============

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hash = PasswordHash.recommended()


# ============= Auth Utilities =============

def create_access_token(user: User) -> str:
    """Create JWT access token."""
    # TODO: Implement
    pass


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    # TODO: Implement
    pass


def require_role(required_role: Role):
    """Dependency factory for role checking."""
    # TODO: Implement
    pass


def require_any_role(allowed_roles: list[Role]):
    """Dependency factory for multiple roles."""
    # TODO: Implement
    pass


async def get_note_or_403(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> Note:
    """Get note if user owns it, is admin/moderator, or note is public."""
    # TODO: Implement
    pass


# ============= FastAPI App =============

app = FastAPI(title="Notes API with RBAC")

# ============= Note Endpoints =============

@app.post("/notes", status_code=status.HTTP_201_CREATED, response_model=NoteResponse)
async def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    """Create note."""
    # TODO: Implement
    pass


@app.get("/notes", response_model=list[NoteResponse])
async def list_my_notes(db: Session = Depends(get_db)):
    """List current user's notes."""
    # TODO: Implement
    pass


@app.get("/notes/public", response_model=list[NoteResponse])
async def list_public_notes(db: Session = Depends(get_db)):
    """List all public notes."""
    # TODO: Implement
    pass


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get note (own, public, or if admin/moderator)."""
    # TODO: Implement
    pass


@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note_data: NoteUpdate, db: Session = Depends(get_db)):
    """Update note (owner only)."""
    # TODO: Implement
    pass


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete note (owner only)."""
    # TODO: Implement
    pass


# ============= Moderator Endpoints =============

@app.patch("/notes/{note_id}/flag", response_model=NoteResponse)
async def toggle_flag_note(note_id: int, db: Session = Depends(get_db)):
    """Flag/unflag note (moderator or admin only)."""
    # TODO: Implement with require_any_role([Role.ADMIN, Role.MODERATOR])
    pass


@app.get("/notes/flagged", response_model=list[NoteResponse])
async def list_flagged_notes(db: Session = Depends(get_db)):
    """List flagged notes (moderator or admin only)."""
    # TODO: Implement
    pass


# ============= Admin Endpoints =============

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    # TODO: Add dependencies=[Depends(require_role(Role.ADMIN))]
)


@admin_router.get("/users", response_model=list[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    """List all users."""
    # TODO: Implement
    pass


@admin_router.patch("/users/{user_id}/role", response_model=UserResponse)
async def change_user_role(user_id: int, db: Session = Depends(get_db)):
    """Change user role (prevent escalation to admin, prevent changing own role)."""
    # TODO: Implement
    pass


@admin_router.patch("/users/{user_id}/activate", response_model=UserResponse)
async def toggle_user_active(user_id: int, db: Session = Depends(get_db)):
    """Activate/deactivate user."""
    # TODO: Implement
    pass


@admin_router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    # TODO: Implement
    pass


app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Stretch Goals

1. **Permission-based auth**: Create Permission model, map roles to permissions
2. **Audit log**: Track all admin actions in database
3. **OAuth2 scopes**: Implement scope-based access (read:notes, write:notes, etc.)
4. **Rate limiting per role**: Admins get higher rate limits than users
5. **Hierarchical roles**: Admins inherit all moderator permissions
6. **Note sharing**: Users can share private notes with specific users
7. **Group permissions**: Create groups with permissions, assign users to groups

## Resources

- [FastAPI Security Scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
- [RBAC Design Patterns](https://en.wikipedia.org/wiki/Role-based_access_control)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
