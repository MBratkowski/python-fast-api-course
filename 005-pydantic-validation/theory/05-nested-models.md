# Nested Models

## Why This Matters

Real APIs return complex nested data: an Order contains Items, each Item has a Product, Product has a Category. In mobile apps, you decode these nested structures with Codable/data classes. Pydantic handles nested models the same way, with validation at every level. If any nested field is invalid, you get a clear error showing the exact path.

## Basic Nested Models

Models can contain other models:

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    email: str
    address: Address

# Create with nested data
user = User(
    name="Alice",
    email="alice@example.com",
    address={
        "street": "123 Main St",
        "city": "Springfield",
        "zip_code": "12345"
    }
)

# Access nested fields
print(user.address.city)  # "Springfield"
```

Pydantic validates the nested Address automatically.

## Lists of Nested Models

```python
class Item(BaseModel):
    name: str
    price: float

class Order(BaseModel):
    order_id: int
    items: list[Item]

# Create with list of nested models
order = Order(
    order_id=1,
    items=[
        {"name": "Laptop", "price": 999.99},
        {"name": "Mouse", "price": 29.99}
    ]
)

# Access items
for item in order.items:
    print(f"{item.name}: ${item.price}")
```

## Deeply Nested Models

```python
class Category(BaseModel):
    name: str

class Product(BaseModel):
    name: str
    price: float
    category: Category

class OrderItem(BaseModel):
    product: Product
    quantity: int

class Order(BaseModel):
    order_id: int
    customer_name: str
    items: list[OrderItem]

# Deep nesting
order = Order(
    order_id=1,
    customer_name="Alice",
    items=[
        {
            "product": {
                "name": "Laptop",
                "price": 999.99,
                "category": {"name": "Electronics"}
            },
            "quantity": 1
        }
    ]
)

print(order.items[0].product.category.name)  # "Electronics"
```

## Validation in Nested Models

Validation happens at all levels:

```python
try:
    order = Order(
        order_id=1,
        customer_name="Bob",
        items=[
            {
                "product": {
                    "name": "Phone",
                    "price": "invalid",  # ❌ Should be float
                    "category": {"name": "Electronics"}
                },
                "quantity": 2
            }
        ]
    )
except ValidationError as e:
    print(e)
    # Error shows exact path: items[0].product.price
```

## Optional Nested Models

```python
class Profile(BaseModel):
    bio: str
    website: str | None = None

class User(BaseModel):
    name: str
    profile: Profile | None = None

# User without profile
user1 = User(name="Alice")
print(user1.profile)  # None

# User with profile
user2 = User(
    name="Bob",
    profile={"bio": "Developer", "website": "https://bob.dev"}
)
```

## Dict of Nested Models

```python
class Permission(BaseModel):
    read: bool
    write: bool
    delete: bool

class UserPermissions(BaseModel):
    user_id: int
    permissions: dict[str, Permission]

user_perms = UserPermissions(
    user_id=1,
    permissions={
        "posts": {"read": True, "write": True, "delete": False},
        "comments": {"read": True, "write": False, "delete": False}
    }
)

print(user_perms.permissions["posts"].write)  # True
```

## Recursive Models

Models can reference themselves:

```python
from pydantic import BaseModel

class Comment(BaseModel):
    text: str
    replies: list['Comment'] = []

# Nested comments
comment = Comment(
    text="Great post!",
    replies=[
        {
            "text": "Thanks!",
            "replies": [
                {"text": "You're welcome!"}
            ]
        }
    ]
)
```

## Serialization of Nested Models

```python
order = Order(...)  # Complex nested order

# Convert to dict (all nested models converted)
order_dict = order.model_dump()

# Convert to JSON
order_json = order.model_dump_json()
```

All nested models are automatically serialized.

## Forward References

When models reference each other:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    posts: list['Post'] = []

class Post(BaseModel):
    title: str
    author: User

# Use model_rebuild() after defining both
User.model_rebuild()
```

## Mobile Developer Context

| Mobile | Pydantic |
|--------|----------|
| `struct User { let address: Address }` | `class User(BaseModel): address: Address` |
| Array of models | `items: list[Item]` |
| Optional nested | `profile: Profile \| None = None` |
| Deep nesting | Models within models within models |
| Validation propagates | Errors show exact nested path |

## Key Takeaways

1. **Models can contain other models** - just use model type as field type
2. **Use `list[Model]` for arrays** - all items validated
3. **Validation cascades down** - errors show full path (`items[0].product.price`)
4. **Optional nested models** - `field: Model | None = None`
5. **Dict of models** - `dict[str, Model]`
6. **Recursive models need quotes** - `'Comment'` for self-reference
7. **Serialization is automatic** - `model_dump()` handles nested models
