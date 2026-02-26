"""
Exercise 1: Build Complete CRUD Endpoints

Build all five standard CRUD endpoints for an Item resource.

Run: pytest 008-api-crud-operations/exercises/01_crud_endpoints.py -v
"""

from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Float, Boolean, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# ============= Models and Schemas (provided) =============

class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    in_stock: bool = True


class ItemUpdate(BaseModel):
    name: str
    description: str | None = None
    price: float
    in_stock: bool


class ItemPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    in_stock: bool | None = None


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: float
    in_stock: bool


# Database setup
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)


def get_db():
    """Database session dependency."""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


# ============= TODO: Exercise 1.1 =============
# Create POST /items endpoint
# - Accept ItemCreate schema
# - Create item in database
# - Return 201 Created status
# - Return ItemResponse

@app.post("/items")
async def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    """Create new item."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.2 =============
# Create GET /items endpoint
# - Return list of all items
# - Return 200 OK status
# - Return list[ItemResponse]

@app.get("/items")
async def list_items(db: Session = Depends(get_db)):
    """List all items."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.3 =============
# Create GET /items/{item_id} endpoint
# - Get single item by ID
# - Return 200 OK if found
# - Return 404 Not Found if not found
# - Return ItemResponse

@app.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item by ID."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.4 =============
# Create PUT /items/{item_id} endpoint
# - Accept ItemUpdate schema (full update - all fields required)
# - Update all item fields
# - Return 200 OK if found and updated
# - Return 404 Not Found if not found
# - Return ItemResponse

@app.put("/items/{item_id}")
async def update_item(item_id: int, item_data: ItemUpdate, db: Session = Depends(get_db)):
    """Update item (full update)."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.5 =============
# Create PATCH /items/{item_id} endpoint
# - Accept ItemPatch schema (partial update - all fields optional)
# - Update only provided fields (use exclude_unset=True)
# - Return 200 OK if found and updated
# - Return 404 Not Found if not found
# - Return ItemResponse

@app.patch("/items/{item_id}")
async def patch_item(item_id: int, item_data: ItemPatch, db: Session = Depends(get_db)):
    """Update item (partial update)."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.6 =============
# Create DELETE /items/{item_id} endpoint
# - Delete item by ID
# - Return 204 No Content if found and deleted
# - Return 404 Not Found if not found
# - Use Response(status_code=204)

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete item."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 008-api-crud-operations/exercises/01_crud_endpoints.py -v

client = TestClient(app)


def test_create_item():
    """Test creating an item."""
    response = client.post("/items", json={
        "name": "Laptop",
        "description": "Gaming laptop",
        "price": 1299.99,
        "in_stock": True
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["description"] == "Gaming laptop"
    assert data["price"] == 1299.99
    assert data["in_stock"] is True
    assert "id" in data


def test_list_items():
    """Test listing items."""
    # Create items
    client.post("/items", json={"name": "Item 1", "price": 10.0})
    client.post("/items", json={"name": "Item 2", "price": 20.0})

    # List
    response = client.get("/items")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_item():
    """Test getting item by ID."""
    # Create item
    create_response = client.post("/items", json={
        "name": "Keyboard",
        "price": 79.99
    })
    item_id = create_response.json()["id"]

    # Get item
    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Keyboard"


def test_get_item_not_found():
    """Test 404 when item doesn't exist."""
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_update_item():
    """Test full update (PUT)."""
    # Create item
    create_response = client.post("/items", json={
        "name": "Mouse",
        "price": 29.99,
        "in_stock": True
    })
    item_id = create_response.json()["id"]

    # Update item
    response = client.put(f"/items/{item_id}", json={
        "name": "Gaming Mouse",
        "description": "RGB mouse",
        "price": 59.99,
        "in_stock": False
    })

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Gaming Mouse"
    assert data["description"] == "RGB mouse"
    assert data["price"] == 59.99
    assert data["in_stock"] is False


def test_patch_item():
    """Test partial update (PATCH)."""
    # Create item
    create_response = client.post("/items", json={
        "name": "Monitor",
        "price": 299.99,
        "in_stock": True
    })
    item_id = create_response.json()["id"]

    # Patch item (only update price)
    response = client.patch(f"/items/{item_id}", json={
        "price": 249.99
    })

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Monitor"  # Unchanged
    assert data["price"] == 249.99  # Updated
    assert data["in_stock"] is True  # Unchanged


def test_delete_item():
    """Test deleting an item."""
    # Create item
    create_response = client.post("/items", json={
        "name": "Webcam",
        "price": 89.99
    })
    item_id = create_response.json()["id"]

    # Delete item
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_item_not_found():
    """Test 404 when deleting non-existent item."""
    response = client.delete("/items/99999")
    assert response.status_code == 404
