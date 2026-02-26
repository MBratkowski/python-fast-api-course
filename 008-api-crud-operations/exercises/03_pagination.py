"""
Exercise 3: Implement Pagination and Filtering

Add pagination, filtering, and sorting to a list endpoint.

Run: pytest 008-api-crud-operations/exercises/03_pagination.py -v
"""

from fastapi import FastAPI, Depends, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Float, create_engine, select, func, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from enum import Enum


# ============= Models and Schemas (provided) =============

class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    price: Mapped[float] = mapped_column(Float)
    in_stock: Mapped[bool]


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: float
    in_stock: bool


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# ============= TODO: Exercise 3.1 =============
# Create PaginatedResponse schema
# - items: list[ProductResponse]
# - total: int
# - page: int
# - page_size: int
# - total_pages: int

class PaginatedResponse(BaseModel):
    """Paginated response schema."""
    # TODO: Implement fields
    pass


# Database setup with seed data
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)


def seed_data():
    """Create test products."""
    db = Session(engine)

    products = [
        Product(name="Laptop Pro", category="Electronics", price=1299.99, in_stock=True),
        Product(name="Wireless Mouse", category="Electronics", price=29.99, in_stock=True),
        Product(name="USB Cable", category="Electronics", price=9.99, in_stock=False),
        Product(name="Desk Chair", category="Furniture", price=199.99, in_stock=True),
        Product(name="Standing Desk", category="Furniture", price=499.99, in_stock=True),
        Product(name="Monitor Stand", category="Furniture", price=39.99, in_stock=False),
        Product(name="Coffee Mug", category="Kitchen", price=12.99, in_stock=True),
        Product(name="Water Bottle", category="Kitchen", price=19.99, in_stock=True),
        Product(name="Notebook", category="Stationery", price=5.99, in_stock=True),
        Product(name="Pen Set", category="Stationery", price=14.99, in_stock=True),
        Product(name="Backpack", category="Accessories", price=49.99, in_stock=True),
        Product(name="Phone Case", category="Accessories", price=24.99, in_stock=False),
        Product(name="Headphones", category="Electronics", price=149.99, in_stock=True),
        Product(name="Keyboard", category="Electronics", price=79.99, in_stock=True),
        Product(name="Desk Lamp", category="Furniture", price=34.99, in_stock=True),
    ]

    db.add_all(products)
    db.commit()
    db.close()


seed_data()


def get_db():
    """Database session dependency."""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


# ============= TODO: Exercise 3.2 =============
# Implement GET /products endpoint with:
#
# Query parameters:
# - page: int = Query(1, ge=1) - Page number
# - page_size: int = Query(10, ge=1, le=100) - Items per page
# - category: str | None = None - Filter by category
# - min_price: float | None = None - Min price filter
# - max_price: float | None = None - Max price filter
# - in_stock: bool | None = None - Filter by stock status
# - search: str | None = None - Search in name (case-insensitive)
# - sort_by: str = "name" - Field to sort by
# - sort_order: SortOrder = SortOrder.asc - Sort order
#
# Logic:
# 1. Build base query
# 2. Apply filters (category, price range, in_stock, search)
# 3. Get total count (before pagination)
# 4. Apply sorting
# 5. Apply pagination (offset and limit)
# 6. Execute query
# 7. Calculate total_pages = (total + page_size - 1) // page_size
# 8. Return PaginatedResponse

@app.get("/products", response_model=PaginatedResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Filter by category"),
    min_price: float | None = Query(None, description="Minimum price"),
    max_price: float | None = Query(None, description="Maximum price"),
    in_stock: bool | None = Query(None, description="Filter by stock status"),
    search: str | None = Query(None, description="Search in product name"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.asc, description="Sort order"),
    db: Session = Depends(get_db)
):
    """List products with pagination, filtering, and sorting."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 008-api-crud-operations/exercises/03_pagination.py -v

client = TestClient(app)


def test_basic_pagination():
    """Test basic pagination."""
    response = client.get("/products?page=1&page_size=5")

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data

    assert len(data["items"]) <= 5
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total"] == 15  # Total seed products


def test_pagination_pages():
    """Test different pages."""
    # Page 1
    response1 = client.get("/products?page=1&page_size=10")
    data1 = response1.json()
    assert len(data1["items"]) == 10

    # Page 2
    response2 = client.get("/products?page=2&page_size=10")
    data2 = response2.json()
    assert len(data2["items"]) == 5  # Remaining items

    # Verify different items
    ids_page1 = [item["id"] for item in data1["items"]]
    ids_page2 = [item["id"] for item in data2["items"]]
    assert len(set(ids_page1) & set(ids_page2)) == 0  # No overlap


def test_filter_by_category():
    """Test filtering by category."""
    response = client.get("/products?category=Electronics")

    data = response.json()
    assert all(item["category"] == "Electronics" for item in data["items"])
    assert data["total"] == 5  # 5 electronics in seed data


def test_filter_by_price_range():
    """Test price range filtering."""
    response = client.get("/products?min_price=10&max_price=50")

    data = response.json()
    assert all(10 <= item["price"] <= 50 for item in data["items"])


def test_filter_by_stock_status():
    """Test filtering by stock status."""
    response = client.get("/products?in_stock=true")

    data = response.json()
    assert all(item["in_stock"] is True for item in data["items"])


def test_search():
    """Test search functionality."""
    response = client.get("/products?search=desk")

    data = response.json()
    # Should find "Desk Chair", "Standing Desk"
    assert data["total"] >= 2
    assert all("desk" in item["name"].lower() for item in data["items"])


def test_sorting_ascending():
    """Test sorting in ascending order."""
    response = client.get("/products?sort_by=price&sort_order=asc&page_size=100")

    data = response.json()
    prices = [item["price"] for item in data["items"]]
    assert prices == sorted(prices)


def test_sorting_descending():
    """Test sorting in descending order."""
    response = client.get("/products?sort_by=price&sort_order=desc&page_size=100")

    data = response.json()
    prices = [item["price"] for item in data["items"]]
    assert prices == sorted(prices, reverse=True)


def test_combined_filters():
    """Test combining multiple filters."""
    response = client.get(
        "/products?category=Electronics&min_price=50&in_stock=true&sort_by=price&sort_order=desc"
    )

    data = response.json()

    # Verify all filters applied
    for item in data["items"]:
        assert item["category"] == "Electronics"
        assert item["price"] >= 50
        assert item["in_stock"] is True

    # Verify sorting
    prices = [item["price"] for item in data["items"]]
    assert prices == sorted(prices, reverse=True)


def test_total_pages_calculation():
    """Test total pages calculation."""
    response = client.get("/products?page_size=7")

    data = response.json()
    # 15 items / 7 per page = 3 pages (15/7 = 2.14... rounded up)
    assert data["total_pages"] == 3
    assert data["total"] == 15
