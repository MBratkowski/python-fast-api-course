"""
Exercise 2: Dataclasses Practice

Create data models using dataclasses.
Run: pytest 001-python-backend-quickstart/exercises/02_dataclasses.py -v
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# Exercise 2.1: Basic Dataclass
# Create a User dataclass with: id (int), username (str), email (str)
# TODO: Implement User dataclass


# Exercise 2.2: Dataclass with Defaults
# Create a Post dataclass with:
# - id: int
# - title: str
# - content: str
# - published: bool (default: False)
# - created_at: datetime (default: now)
# TODO: Implement Post dataclass


# Exercise 2.3: Dataclass with Optional Fields
# Create a Profile dataclass with:
# - user_id: int
# - bio: Optional[str] (default: None)
# - avatar_url: Optional[str] (default: None)
# - followers_count: int (default: 0)
# TODO: Implement Profile dataclass


# Exercise 2.4: Immutable Dataclass
# Create an immutable Point dataclass with x and y floats
# It should raise an error if you try to modify it after creation
# TODO: Implement Point dataclass


# Exercise 2.5: Dataclass with Methods
# Create an Order dataclass with:
# - id: int
# - items: list of dicts with 'name' and 'price'
# - Add a method total() that returns the sum of all item prices
# - Add a property item_count that returns number of items
# TODO: Implement Order dataclass


# ============= TESTS =============

def test_user():
    user = User(id=1, username="alice", email="alice@example.com")
    assert user.id == 1
    assert user.username == "alice"
    assert user.email == "alice@example.com"


def test_post_defaults():
    post = Post(id=1, title="Hello", content="World")
    assert post.published is False
    assert isinstance(post.created_at, datetime)


def test_profile_optional():
    profile = Profile(user_id=1)
    assert profile.bio is None
    assert profile.avatar_url is None
    assert profile.followers_count == 0

    profile2 = Profile(user_id=2, bio="Hello!", followers_count=100)
    assert profile2.bio == "Hello!"
    assert profile2.followers_count == 100


def test_point_immutable():
    point = Point(x=1.0, y=2.0)
    assert point.x == 1.0

    import pytest
    with pytest.raises(Exception):  # Should raise FrozenInstanceError
        point.x = 3.0


def test_order_methods():
    order = Order(
        id=1,
        items=[
            {"name": "Item A", "price": 10.0},
            {"name": "Item B", "price": 20.0},
            {"name": "Item C", "price": 15.0},
        ]
    )
    assert order.total() == 45.0
    assert order.item_count == 3
