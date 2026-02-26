"""
Exercise 1: Hello World FastAPI

Create a basic FastAPI application with multiple endpoints.
Run: pytest 003-fastapi-basics/exercises/01_hello_world.py -v
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient


# Exercise 1.1: Create FastAPI app instance
# TODO: Create app
app = None  # TODO: Replace with FastAPI()


# Exercise 1.2: Create root endpoint
# TODO: Implement GET / endpoint that returns {"message": "Hello, World!"}
@app.get("/")
async def root():
    pass  # TODO: Implement


# Exercise 1.3: Create health check endpoint
# TODO: Implement GET /health endpoint that returns {"status": "healthy"}
@app.get("/health")
async def health_check():
    pass  # TODO: Implement


# Exercise 1.4: Create info endpoint
# TODO: Implement GET /info endpoint that returns {"app": "My API", "version": "0.1.0"}
@app.get("/info")
async def info():
    pass  # TODO: Implement


# ============= TESTS =============
# Run with: pytest 003-fastapi-basics/exercises/01_hello_world.py -v

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_info_endpoint():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert data["app"] == "My API"
    assert data["version"] == "0.1.0"
