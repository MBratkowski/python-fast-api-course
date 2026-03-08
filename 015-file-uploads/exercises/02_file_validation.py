"""
Exercise 2: File Validation

Implement content-type validation, file size validation, and a combined
validation endpoint that rejects invalid files with proper HTTP errors.

All exercises use local validation -- no cloud dependencies.

Run: pytest 015-file-uploads/exercises/02_file_validation.py -v
"""

import io

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.testclient import TestClient

# ============= APP SETUP =============

app = FastAPI()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


# ============= TODO: Exercise 2.1 =============
# Create a function validate_content_type that:
# - Takes a content_type string and an allowed_types set
# - Returns True if content_type is in allowed_types
# - Returns False otherwise
#
# Then create a POST endpoint at /check-type that:
# - Accepts a file upload
# - Uses validate_content_type to check against ALLOWED_TYPES
# - Returns {"valid": True, "content_type": "..."} if valid
# - Raises HTTPException(400) with detail message if invalid

def validate_content_type(content_type: str, allowed_types: set[str]) -> bool:
    """Check if content_type is in the allowed set."""
    # TODO: Implement
    pass


@app.post("/check-type")
async def check_type(file: UploadFile):
    """Validate file content type."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.2 =============
# Create an async function validate_file_size that:
# - Takes an UploadFile and max_size (int, bytes)
# - Reads the file in chunks of 1024 * 1024 bytes (1 MB)
# - Tracks total bytes read
# - If total exceeds max_size, raises HTTPException(400) with size info
# - Resets file position with await file.seek(0) when done
# - Returns the total size in bytes
#
# Then create a POST endpoint at /check-size that:
# - Accepts a file upload
# - Uses validate_file_size with MAX_FILE_SIZE
# - Returns {"valid": True, "size": <bytes>, "max_size": MAX_FILE_SIZE}

async def validate_file_size(file: UploadFile, max_size: int) -> int:
    """Validate file size by reading in chunks. Returns size in bytes."""
    # TODO: Implement
    pass


@app.post("/check-size")
async def check_size(file: UploadFile):
    """Validate file size."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.3 =============
# Create a POST endpoint at /upload-validated that:
# - Accepts a file upload
# - Validates content type using validate_content_type
# - Validates file size using validate_file_size
# - If BOTH pass, returns {"valid": True, "filename": "...", "content_type": "...", "size": <bytes>}
# - If either fails, the appropriate HTTPException is raised (from the validation functions)
#
# This combines both validation gates into a single endpoint.

@app.post("/upload-validated")
async def upload_validated(file: UploadFile):
    """Validate both content type and file size before accepting."""
    # TODO: Implement
    pass


# ============= TESTS (DO NOT MODIFY) =============

client = TestClient(app)


def _make_file(
    content: bytes = b"test",
    filename: str = "test.txt",
    content_type: str = "text/plain",
):
    """Helper to create upload file tuple."""
    return ("file", (filename, io.BytesIO(content), content_type))


class TestContentTypeValidation:
    """Tests for Exercise 2.1: Content-type validation."""

    def test_validate_allowed_type(self):
        assert validate_content_type("image/jpeg", ALLOWED_TYPES) is True

    def test_validate_disallowed_type(self):
        assert validate_content_type("text/plain", ALLOWED_TYPES) is False

    def test_validate_all_allowed_types(self):
        for mime in ALLOWED_TYPES:
            assert validate_content_type(mime, ALLOWED_TYPES) is True

    def test_check_type_valid_jpeg(self):
        response = client.post(
            "/check-type",
            files=[_make_file(content_type="image/jpeg", filename="photo.jpg")],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["content_type"] == "image/jpeg"

    def test_check_type_valid_pdf(self):
        response = client.post(
            "/check-type",
            files=[_make_file(content_type="application/pdf", filename="doc.pdf")],
        )
        assert response.status_code == 200
        assert response.json()["valid"] is True

    def test_check_type_invalid_returns_400(self):
        response = client.post(
            "/check-type",
            files=[_make_file(content_type="text/plain")],
        )
        assert response.status_code == 400

    def test_check_type_invalid_executable(self):
        response = client.post(
            "/check-type",
            files=[_make_file(content_type="application/x-executable")],
        )
        assert response.status_code == 400


class TestFileSizeValidation:
    """Tests for Exercise 2.2: File size validation."""

    def test_small_file_passes(self):
        content = b"x" * 1024  # 1 KB
        response = client.post("/check-size", files=[_make_file(content=content)])
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["size"] == 1024

    def test_exact_limit_passes(self):
        content = b"x" * MAX_FILE_SIZE  # Exactly at limit
        response = client.post("/check-size", files=[_make_file(content=content)])
        assert response.status_code == 200

    def test_oversized_file_returns_400(self):
        content = b"x" * (MAX_FILE_SIZE + 1)  # 1 byte over limit
        response = client.post("/check-size", files=[_make_file(content=content)])
        assert response.status_code == 400

    def test_returns_max_size(self):
        content = b"x" * 100
        response = client.post("/check-size", files=[_make_file(content=content)])
        data = response.json()
        assert data["max_size"] == MAX_FILE_SIZE


class TestCombinedValidation:
    """Tests for Exercise 2.3: Combined validation endpoint."""

    def test_valid_file_accepted(self):
        content = b"x" * 1024
        response = client.post(
            "/upload-validated",
            files=[_make_file(
                content=content,
                content_type="image/jpeg",
                filename="photo.jpg",
            )],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["filename"] == "photo.jpg"
        assert data["content_type"] == "image/jpeg"
        assert data["size"] == 1024

    def test_invalid_type_rejected(self):
        response = client.post(
            "/upload-validated",
            files=[_make_file(content_type="text/html", filename="page.html")],
        )
        assert response.status_code == 400

    def test_oversized_file_rejected(self):
        content = b"x" * (MAX_FILE_SIZE + 1000)
        response = client.post(
            "/upload-validated",
            files=[_make_file(
                content=content,
                content_type="image/png",
                filename="big.png",
            )],
        )
        assert response.status_code == 400

    def test_valid_pdf_accepted(self):
        content = b"x" * 500
        response = client.post(
            "/upload-validated",
            files=[_make_file(
                content=content,
                content_type="application/pdf",
                filename="doc.pdf",
            )],
        )
        assert response.status_code == 200
        assert response.json()["valid"] is True
