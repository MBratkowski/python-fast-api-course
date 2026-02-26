"""
Exercise 2: Resource Ownership Verification

Implement resource-level authorization to verify ownership.

Run: pytest 010-authorization-permissions/exercises/02_resource_ownership.py -v
"""

from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from typing import Annotated
from enum import Enum
import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash


# ============= Setup (provided) =============

class Base(DeclarativeBase):
    pass


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(1000))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")


# Pydantic schemas
class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author_id: int


# Database
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

# Auth setup
password_hash = PasswordHash.recommended()
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"


def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401)
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401)


@app.post("/posts", status_code=201, response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create post (provided)."""
    post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=current_user.id
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


# ============= TODO: Exercise 2.1 =============
# Implement get_post_or_403 dependency
# - Accept post_id, current_user (Depends(get_current_user)), db
# - Fetch post by ID
# - If not found: raise 404
# - If current_user is NOT the author AND NOT an admin: raise 403
# - Return post if authorized

async def get_post_or_403(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> Post:
    """Get post if user owns it or is admin."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.2 =============
# Implement PUT /posts/{post_id}
# - Use Depends(get_post_or_403) to verify ownership
# - Accept PostUpdate schema
# - Update title and/or content (only if provided)
# - Return updated PostResponse

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db)):
    """Update post (owner or admin only)."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.3 =============
# Implement DELETE /posts/{post_id}
# - Use Depends(get_post_or_403) to verify ownership
# - Delete the post
# - Return 204 No Content

@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete post (owner or admin only)."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.4 =============
# Implement GET /posts/{post_id}
# - Any authenticated user can read any post (no ownership check)
# - Return PostResponse
# - Return 404 if not found

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get single post (any authenticated user)."""
    # TODO: Implement
    pass


# ============= TESTS =============

client = TestClient(app)


def create_user_and_login(username: str, role: Role = Role.USER) -> tuple[int, str]:
    """Helper: Create user and return (user_id, token)."""
    db = next(get_db())
    user = User(
        username=username,
        hashed_password=password_hash.hash("password123"),
        role=role
    )
    db.add(user)
    db.commit()
    user_id = user.id
    token = create_access_token(user)
    return user_id, token


def test_user_can_update_own_post():
    user_id, token = create_user_and_login("alice")

    # Create post
    response = client.post(
        "/posts",
        json={"title": "My Post", "content": "Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = response.json()["id"]

    # Update own post
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "Updated Title", "content": "Updated Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_user_cannot_update_others_post():
    _, alice_token = create_user_and_login("alice2")
    _, bob_token = create_user_and_login("bob")

    # Alice creates post
    response = client.post(
        "/posts",
        json={"title": "Alice Post", "content": "Content"},
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    post_id = response.json()["id"]

    # Bob tries to update
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "Hacked", "content": "Hacked"},
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert response.status_code == 403


def test_admin_can_update_any_post():
    _, user_token = create_user_and_login("user")
    _, admin_token = create_user_and_login("admin", Role.ADMIN)

    # User creates post
    response = client.post(
        "/posts",
        json={"title": "User Post", "content": "Content"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    post_id = response.json()["id"]

    # Admin updates
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "Moderated", "content": "Moderated"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_user_can_delete_own_post():
    _, token = create_user_and_login("user2")

    # Create post
    response = client.post(
        "/posts",
        json={"title": "My Post", "content": "Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = response.json()["id"]

    # Delete own post
    response = client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


def test_user_cannot_delete_others_post():
    _, alice_token = create_user_and_login("alice3")
    _, bob_token = create_user_and_login("bob2")

    # Alice creates post
    response = client.post(
        "/posts",
        json={"title": "Alice Post", "content": "Content"},
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    post_id = response.json()["id"]

    # Bob tries to delete
    response = client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert response.status_code == 403


def test_admin_can_delete_any_post():
    _, user_token = create_user_and_login("user3")
    _, admin_token = create_user_and_login("admin2", Role.ADMIN)

    # User creates post
    response = client.post(
        "/posts",
        json={"title": "User Post", "content": "Content"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    post_id = response.json()["id"]

    # Admin deletes
    response = client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204


def test_any_user_can_read_any_post():
    _, alice_token = create_user_and_login("alice4")
    _, bob_token = create_user_and_login("bob3")

    # Alice creates post
    response = client.post(
        "/posts",
        json={"title": "Alice Post", "content": "Content"},
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    post_id = response.json()["id"]

    # Bob reads Alice's post
    response = client.get(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Alice Post"


def test_updating_nonexistent_post_returns_404():
    _, token = create_user_and_login("user4")

    response = client.put(
        "/posts/99999",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
