"""
Exercise 1: File Upload Endpoints

Learn to receive and handle file uploads with FastAPI's UploadFile.
Implement single file upload, multiple file upload, and file metadata endpoints.

All exercises use local temporary storage -- no cloud dependencies.

Run: pytest 015-file-uploads/exercises/01_file_upload.py -v
"""

import io
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient

# ============= APP SETUP =============

app = FastAPI()

# Use a temp directory for uploads (cleaned up automatically)
UPLOAD_DIR = Path(tempfile.mkdtemp())


# ============= TODO: Exercise 1.1 =============
# Create a POST endpoint at /upload that:
# - Accepts a single file upload (parameter name: "file")
# - Saves the file to UPLOAD_DIR using shutil.copyfileobj
# - Returns JSON with: filename, content_type, and size (in bytes)
#
# Hints:
# - Use file.file to access the underlying file object
# - Use shutil.copyfileobj(file.file, destination) to save
# - Get size from the saved file using Path.stat().st_size

@app.post("/upload")
async def upload_file(file: UploadFile):
    """Upload a single file and return its metadata."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.2 =============
# Create a POST endpoint at /upload-multiple that:
# - Accepts multiple files (parameter name: "files", type: list[UploadFile])
# - Saves each file to UPLOAD_DIR
# - Returns JSON with: count (number of files) and files (list of {filename, size})
#
# Hints:
# - Use list[UploadFile] as the parameter type
# - Loop through files and save each one

@app.post("/upload-multiple")
async def upload_multiple(files: list[UploadFile]):
    """Upload multiple files and return metadata for each."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 1.3 =============
# Create a POST endpoint at /file-info that:
# - Accepts a file upload (parameter name: "file")
# - Does NOT save the file
# - Returns JSON with: filename, content_type, size (read the content to get size)
# - Resets file position after reading (await file.seek(0))
#
# Hints:
# - Use await file.read() to get contents and len() for size
# - Remember to seek back to 0 after reading

@app.post("/file-info")
async def file_info(file: UploadFile):
    """Return file metadata without saving."""
    # TODO: Implement
    pass


# ============= TESTS (DO NOT MODIFY) =============

client = TestClient(app)


def _make_test_file(
    content: bytes = b"test file content",
    filename: str = "test.txt",
    content_type: str = "text/plain",
):
    """Helper to create a test file for upload."""
    return ("file", (filename, io.BytesIO(content), content_type))


def _make_test_files(count: int = 3):
    """Helper to create multiple test files."""
    files = []
    for i in range(count):
        content = f"file {i} content".encode()
        files.append(
            ("files", (f"test_{i}.txt", io.BytesIO(content), "text/plain"))
        )
    return files


class TestSingleUpload:
    """Tests for Exercise 1.1: Single file upload."""

    def test_upload_returns_200(self):
        response = client.post("/upload", files=[_make_test_file()])
        assert response.status_code == 200

    def test_upload_returns_filename(self):
        response = client.post(
            "/upload",
            files=[_make_test_file(filename="photo.jpg")],
        )
        data = response.json()
        assert data["filename"] == "photo.jpg"

    def test_upload_returns_content_type(self):
        response = client.post(
            "/upload",
            files=[_make_test_file(content_type="image/jpeg", filename="pic.jpg")],
        )
        data = response.json()
        assert data["content_type"] == "image/jpeg"

    def test_upload_returns_size(self):
        content = b"hello world 12345"
        response = client.post(
            "/upload",
            files=[_make_test_file(content=content)],
        )
        data = response.json()
        assert data["size"] == len(content)

    def test_upload_saves_file_to_disk(self):
        content = b"persistent content"
        response = client.post(
            "/upload",
            files=[_make_test_file(content=content, filename="saved.txt")],
        )
        saved_path = UPLOAD_DIR / "saved.txt"
        assert saved_path.exists()
        assert saved_path.read_bytes() == content


class TestMultipleUpload:
    """Tests for Exercise 1.2: Multiple file upload."""

    def test_upload_multiple_returns_200(self):
        response = client.post("/upload-multiple", files=_make_test_files(2))
        assert response.status_code == 200

    def test_upload_multiple_returns_count(self):
        response = client.post("/upload-multiple", files=_make_test_files(3))
        data = response.json()
        assert data["count"] == 3

    def test_upload_multiple_returns_file_list(self):
        response = client.post("/upload-multiple", files=_make_test_files(2))
        data = response.json()
        assert len(data["files"]) == 2
        assert all("filename" in f for f in data["files"])
        assert all("size" in f for f in data["files"])

    def test_upload_multiple_saves_all_files(self):
        response = client.post("/upload-multiple", files=_make_test_files(3))
        for i in range(3):
            assert (UPLOAD_DIR / f"test_{i}.txt").exists()


class TestFileInfo:
    """Tests for Exercise 1.3: File info without saving."""

    def test_file_info_returns_200(self):
        response = client.post("/file-info", files=[_make_test_file()])
        assert response.status_code == 200

    def test_file_info_returns_filename(self):
        response = client.post(
            "/file-info",
            files=[_make_test_file(filename="report.pdf")],
        )
        data = response.json()
        assert data["filename"] == "report.pdf"

    def test_file_info_returns_content_type(self):
        response = client.post(
            "/file-info",
            files=[_make_test_file(content_type="application/pdf", filename="doc.pdf")],
        )
        data = response.json()
        assert data["content_type"] == "application/pdf"

    def test_file_info_returns_size(self):
        content = b"a" * 1024  # 1 KB
        response = client.post(
            "/file-info",
            files=[_make_test_file(content=content)],
        )
        data = response.json()
        assert data["size"] == 1024
