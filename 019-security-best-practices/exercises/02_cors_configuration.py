"""
Exercise 2: CORS Configuration

Configure FastAPI's CORSMiddleware correctly for different scenarios.
Learn the critical rule: never use allow_origins=["*"] with allow_credentials=True.

Run: pytest 019-security-best-practices/exercises/02_cors_configuration.py -v
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

# ============= TODO: Exercise 2.1 -- Production CORS =============
# Create a FastAPI app with CORSMiddleware configured for production:
# - Allow origins: "https://myapp.com" and "https://admin.myapp.com"
# - Allow credentials: True (for JWT auth)
# - Allow methods: GET, POST, PUT, DELETE
# - Allow headers: Authorization, Content-Type
# - Max age: 600 seconds (cache preflight for 10 minutes)
#
# Hints:
# - Use app.add_middleware(CORSMiddleware, ...)
# - List specific origins (never wildcard with credentials)

app_production = FastAPI()


# TODO: Add CORSMiddleware to app_production with the configuration above


@app_production.get("/api/data")
async def get_data():
    return {"message": "Hello from the API"}


# ============= TODO: Exercise 2.2 -- Development CORS =============
# Create a FastAPI app with CORSMiddleware configured for development:
# - Allow origins: "http://localhost:3000" and "http://localhost:5173"
# - Allow credentials: True
# - Allow methods: all (use ["*"])
# - Allow headers: all (use ["*"])
#
# Hints:
# - Development config is more permissive but still lists specific origins
# - Wildcard is fine for methods and headers, NOT for origins with credentials

app_development = FastAPI()


# TODO: Add CORSMiddleware to app_development with the configuration above


@app_development.get("/api/data")
async def get_dev_data():
    return {"message": "Hello from dev API"}


# ============= TODO: Exercise 2.3 -- Public API CORS =============
# Create a FastAPI app with CORSMiddleware for a public, read-only API:
# - Allow origins: ["*"] (any origin can access)
# - Allow credentials: False (no auth needed)
# - Allow methods: GET only
# - Allow headers: default (no custom headers needed)
#
# Hints:
# - Wildcard origins are fine when credentials=False
# - A public API only needs GET method

app_public = FastAPI()


# TODO: Add CORSMiddleware to app_public with the configuration above


@app_public.get("/api/public")
async def get_public_data():
    return {"message": "Public data"}


# ============= TESTS =============

client_prod = TestClient(app_production)
client_dev = TestClient(app_development)
client_public = TestClient(app_public)


# --- Tests for Exercise 2.1: Production CORS ---


def test_production_allows_myapp_origin():
    """Preflight from https://myapp.com should be allowed."""
    response = client_prod.options(
        "/api/data",
        headers={
            "Origin": "https://myapp.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://myapp.com"


def test_production_allows_admin_origin():
    """Preflight from https://admin.myapp.com should be allowed."""
    response = client_prod.options(
        "/api/data",
        headers={
            "Origin": "https://admin.myapp.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"] == "https://admin.myapp.com"
    )


def test_production_blocks_unknown_origin():
    """Preflight from https://evil.com should NOT include CORS allow header."""
    response = client_prod.options(
        "/api/data",
        headers={
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "https://evil.com"


def test_production_allows_credentials():
    """Production CORS should allow credentials."""
    response = client_prod.options(
        "/api/data",
        headers={
            "Origin": "https://myapp.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_production_allows_authorization_header():
    """Production CORS should allow the Authorization header."""
    response = client_prod.options(
        "/api/data",
        headers={
            "Origin": "https://myapp.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200
    allowed_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allowed_headers


def test_production_allows_put_method():
    """Production CORS should allow PUT method."""
    response = client_prod.options(
        "/api/data",
        headers={
            "Origin": "https://myapp.com",
            "Access-Control-Request-Method": "PUT",
        },
    )
    assert response.status_code == 200
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "PUT" in allowed_methods


def test_production_has_max_age():
    """Production CORS should cache preflight for 600 seconds."""
    response = client_prod.options(
        "/api/data",
        headers={
            "Origin": "https://myapp.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-max-age") == "600"


# --- Tests for Exercise 2.2: Development CORS ---


def test_development_allows_localhost_3000():
    """Development CORS should allow localhost:3000."""
    response = client_dev.options(
        "/api/data",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"] == "http://localhost:3000"
    )


def test_development_allows_localhost_5173():
    """Development CORS should allow localhost:5173 (Vite)."""
    response = client_dev.options(
        "/api/data",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"] == "http://localhost:5173"
    )


def test_development_allows_credentials():
    """Development CORS should allow credentials."""
    response = client_dev.options(
        "/api/data",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-credentials") == "true"


# --- Tests for Exercise 2.3: Public API CORS ---


def test_public_allows_any_origin():
    """Public API should allow any origin."""
    response = client_public.options(
        "/api/public",
        headers={
            "Origin": "https://random-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"


def test_public_does_not_allow_credentials():
    """Public API should NOT allow credentials (wildcard + credentials is invalid)."""
    response = client_public.options(
        "/api/public",
        headers={
            "Origin": "https://random-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # credentials header should either be absent or not "true"
    creds = response.headers.get("access-control-allow-credentials", "false")
    assert creds != "true"


def test_public_allows_get_only():
    """Public API should only allow GET method."""
    response = client_public.options(
        "/api/public",
        headers={
            "Origin": "https://random-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "GET" in allowed_methods
