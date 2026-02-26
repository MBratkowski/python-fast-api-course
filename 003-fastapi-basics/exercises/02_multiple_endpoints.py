"""
Exercise 2: Multiple Endpoints for a Resource

Build CRUD endpoints for a books resource.
Run: pytest 003-fastapi-basics/exercises/02_multiple_endpoints.py -v
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel


# Sample data
BOOKS = [
    {"id": 1, "title": "1984", "author": "George Orwell"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
]


# Pydantic model for request body
class BookCreate(BaseModel):
    title: str
    author: str


# Exercise 2.1: Create FastAPI app
# TODO: Create app
app = None  # TODO: Replace with FastAPI()


# Exercise 2.2: List all books
# TODO: Implement GET /books that returns {"books": BOOKS}
@app.get("/books")
async def list_books():
    pass  # TODO: Implement


# Exercise 2.3: Get single book by ID
# TODO: Implement GET /books/{book_id}
# Return the book if found, raise HTTPException(status_code=404) if not found
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    pass  # TODO: Implement


# Exercise 2.4: Create new book
# TODO: Implement POST /books
# Accept BookCreate in request body, add to BOOKS with next available ID
# Return the created book with 201 status code
@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    pass  # TODO: Implement


# Exercise 2.5: Delete book
# TODO: Implement DELETE /books/{book_id}
# Remove book from BOOKS list, return 204 status code
# Raise 404 if book not found
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 003-fastapi-basics/exercises/02_multiple_endpoints.py -v

client = TestClient(app)


def test_list_books():
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert "books" in data
    assert len(data["books"]) >= 3


def test_get_book_success():
    response = client.get("/books/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "title" in data
    assert "author" in data


def test_get_book_not_found():
    response = client.get("/books/999")
    assert response.status_code == 404


def test_create_book():
    new_book = {"title": "Brave New World", "author": "Aldous Huxley"}
    response = client.post("/books", json=new_book)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]


def test_delete_book():
    # First create a book to delete
    new_book = {"title": "Test Book", "author": "Test Author"}
    create_response = client.post("/books", json=new_book)
    book_id = create_response.json()["id"]

    # Delete it
    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404
