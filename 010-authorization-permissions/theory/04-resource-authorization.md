# Resource-Level Authorization

## Why This Matters

In mobile apps, you only show edit/delete buttons for the user's own content. But a malicious user could call the API directly, bypassing your UI. Resource-level authorization prevents "just change the user_id in the request" attacks by verifying ownership server-side.

## The Confused Deputy Problem

**Problem**: Authenticated user accessing another user's data.

```python
# BAD - Any authenticated user can delete any post!
@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    db.delete(post)  # No ownership check!
    db.commit()
```

**Attack**:
```
User alice (id=1) creates post (id=42, author_id=1)
User bob (id=2) calls: DELETE /posts/42
→ Bob deletes Alice's post!
```

## Resource Ownership Dependency

Create a dependency that fetches the resource AND verifies ownership:

```python
from fastapi import Depends, HTTPException, status

async def get_post_or_403(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> Post:
    """Get post if user owns it or is admin."""
    # Fetch post
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Check ownership OR admin bypass
    if post.author_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    return post
```

**Usage**:

```python
@router.put("/posts/{post_id}")
async def update_post(
    post_data: PostUpdate,
    post: Annotated[Post, Depends(get_post_or_403)],
    db: Session = Depends(get_db)
):
    """Update post (only if you own it or are admin)."""
    post.title = post_data.title
    post.content = post_data.content
    db.commit()
    return post

@router.delete("/posts/{post_id}")
async def delete_post(
    post: Annotated[Post, Depends(get_post_or_403)],
    db: Session = Depends(get_db)
):
    """Delete post (only if you own it or are admin)."""
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

**What happens**:
1. Extract `post_id` from URL path
2. Load post from database
3. Check if `current_user.id == post.author_id` OR `current_user.role == ADMIN`
4. If authorized → return post, continue to endpoint
5. If not found → 404
6. If not authorized → 403

## Admin Bypass Pattern

Admins can access any resource:

```python
# Pattern: owner OR admin
if resource.owner_id != current_user.id and current_user.role != Role.ADMIN:
    raise HTTPException(status_code=403)
```

## GET vs PUT/DELETE Authorization

**Reading** (GET) might be more permissive than **writing** (PUT/DELETE):

```python
# Anyone can read posts
@router.get("/posts/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404)
    return post

# Only owner or admin can update/delete
@router.put("/posts/{post_id}")
async def update_post(
    post_data: PostUpdate,
    post: Annotated[Post, Depends(get_post_or_403)]
):
    # Ownership already verified by dependency
    post.title = post_data.title
    db.commit()
    return post
```

## Multiple Ownership Checks

For complex resources with multiple authorization rules:

```python
async def get_comment_or_403(
    comment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> Comment:
    """Get comment if user owns it OR owns the parent post OR is admin."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404)

    # Ownership rules:
    # 1. User is comment author
    # 2. User is post author (can moderate comments on their post)
    # 3. User is admin
    if (comment.author_id == current_user.id or
        comment.post.author_id == current_user.id or
        current_user.role == Role.ADMIN):
        return comment

    raise HTTPException(status_code=403)
```

## Testing Ownership

```python
def test_user_can_update_own_post(client: TestClient):
    """Test user can update their own post."""
    # Create user and login
    token = create_user_and_login(client, "alice", "pass123")

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
        json={"title": "Updated Title", "content": "Updated"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_user_cannot_update_others_post(client: TestClient):
    """Test user cannot update another user's post."""
    # Alice creates post
    alice_token = create_user_and_login(client, "alice", "pass123")
    response = client.post(
        "/posts",
        json={"title": "Alice Post", "content": "Content"},
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    post_id = response.json()["id"]

    # Bob tries to update Alice's post
    bob_token = create_user_and_login(client, "bob", "pass456")
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "Hacked", "content": "Hacked"},
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert response.status_code == 403

def test_admin_can_update_any_post(client: TestClient, db: Session):
    """Test admin can update any post."""
    # Alice creates post
    alice_token = create_user_and_login(client, "alice", "pass123")
    response = client.post(
        "/posts",
        json={"title": "Alice Post", "content": "Content"},
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    post_id = response.json()["id"]

    # Admin updates Alice's post
    admin_token = create_admin_and_login(client, db)
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "Moderated", "content": "Moderated"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
```

## Key Takeaways

1. **Resource ownership** prevents confused deputy attacks (user accessing others' data)
2. Create **dependency functions** like `get_post_or_403()` that fetch AND authorize
3. **Pattern**: Check `resource.owner_id == current_user.id OR current_user.role == ADMIN`
4. Use **404** if resource doesn't exist, **403** if unauthorized access
5. Reading (GET) often more permissive than writing (PUT/DELETE)
6. Test ownership enforcement with multiple users trying to access each other's resources
