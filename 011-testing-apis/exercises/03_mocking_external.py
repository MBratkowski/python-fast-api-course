"""
Exercise 3: Mocking External APIs

Learn to mock external HTTP calls using unittest.mock and respx.
Test success cases, error cases, and timeouts without calling real APIs.

A FastAPI app that calls an external weather API is provided. Your job: mock it and test it.

Run: pytest 011-testing-apis/exercises/03_mocking_external.py -v
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import httpx
import respx

# ============= PROVIDED API (DO NOT MODIFY) =============

app = FastAPI()

WEATHER_API_URL = "https://api.weather.example.com"

@app.get("/weather/{city}")
async def get_weather(city: str):
    """Fetch weather for a city from external API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{WEATHER_API_URL}/current",
                params={"city": city},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return {
                "city": city,
                "temperature": data["temp"],
                "condition": data["condition"]
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Weather API error: {e.response.text}"
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Weather API timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/forecast/{city}")
def get_forecast_sync(city: str):
    """Fetch forecast using sync requests (for testing sync mocking)."""
    import requests
    try:
        response = requests.get(
            f"{WEATHER_API_URL}/forecast",
            params={"city": city},
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()
        return {"city": city, "forecast": data["days"]}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

client = TestClient(app)

# ============= TODO: Exercise 3.1 =============
# Test get_weather success case using respx
# - Use @respx.mock decorator
# - Mock GET request to {WEATHER_API_URL}/current?city=London
# - Return 200 with JSON: {"temp": 15, "condition": "cloudy"}
# - Call client.get("/weather/London")
# - Assert status 200 and correct response data

@respx.mock
def test_get_weather_success():
    """Test successful weather fetch with mocked API."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.2 =============
# Test get_weather with API returning 500 error
# - Use @respx.mock decorator
# - Mock GET request to return 500 status
# - Call client.get("/weather/InvalidCity")
# - Assert status 500 and error detail

@respx.mock
def test_get_weather_api_error():
    """Test handling weather API 500 error."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.3 =============
# Test get_weather with API timeout
# - Use @respx.mock decorator
# - Mock GET request to raise httpx.TimeoutException
# - Call client.get("/weather/SlowCity")
# - Assert status 504 (gateway timeout) and timeout error message

@respx.mock
def test_get_weather_timeout():
    """Test handling weather API timeout."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.4 =============
# Test get_forecast_sync using unittest.mock.patch
# - Use @patch("requests.get") decorator
# - Create mock response with .json() returning {"days": ["Mon", "Tue", "Wed"]}
# - Set mock_get.return_value to the mock response
# - Call client.get("/forecast/Paris")
# - Assert status 200 and correct forecast data

@patch("requests.get")
def test_get_forecast_success(mock_get):
    """Test forecast with mocked requests.get."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.5 =============
# Test get_forecast_sync with requests exception
# - Use @patch("requests.get") decorator
# - Set mock_get.side_effect to raise requests.RequestException("Connection failed")
# - Call client.get("/forecast/ErrorCity")
# - Assert status 500 and error message

@patch("requests.get")
def test_get_forecast_error(mock_get):
    """Test forecast with connection error."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.6 =============
# Test multiple cities with different responses
# - Use @respx.mock decorator
# - Mock two different city requests with different responses:
#   - London: 15°C, cloudy
#   - Paris: 20°C, sunny
# - Call client.get for both cities
# - Assert each returns correct data
# - (Tests that mocks can differentiate requests)

@respx.mock
def test_multiple_cities():
    """Test mocking multiple different requests."""
    # TODO: Implement
    pass


# ============= TESTS =============
# These tests verify YOUR implementations

def test_get_weather_success_implementation():
    """Verify test_get_weather_success is implemented."""
    test_get_weather_success()

def test_get_weather_api_error_implementation():
    """Verify test_get_weather_api_error is implemented."""
    test_get_weather_api_error()

def test_get_weather_timeout_implementation():
    """Verify test_get_weather_timeout is implemented."""
    test_get_weather_timeout()

def test_get_forecast_success_implementation():
    """Verify test_get_forecast_success is implemented."""
    # Create a mock for the test
    mock = Mock()
    test_get_forecast_success(mock)

def test_get_forecast_error_implementation():
    """Verify test_get_forecast_error is implemented."""
    # Create a mock for the test
    mock = Mock()
    test_get_forecast_error(mock)

def test_multiple_cities_implementation():
    """Verify test_multiple_cities is implemented."""
    test_multiple_cities()
