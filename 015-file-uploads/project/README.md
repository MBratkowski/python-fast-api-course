# Project: File Upload Service

## Overview

Build a complete file upload service with validation, local storage, file listing, download support, and image thumbnail generation. This project combines everything from Module 015 into a production-style application.

## Requirements

### Core Features

1. **Upload endpoint** (`POST /upload`)
   - Accept single file uploads
   - Validate content type (images and PDFs only)
   - Validate file size (max 10 MB)
   - Save with UUID-prefixed unique filename
   - Return file metadata (id, filename, original_name, content_type, size, upload_date)

2. **File listing endpoint** (`GET /files`)
   - List all uploaded files
   - Return metadata for each file
   - Support optional `content_type` query filter

3. **Download endpoint** (`GET /files/{file_id}`)
   - Serve the uploaded file
   - Set proper Content-Type and Content-Disposition headers
   - Return 404 for missing files

4. **Delete endpoint** (`DELETE /files/{file_id}`)
   - Delete file from storage and metadata
   - Return 404 for missing files

5. **Image thumbnail generation** (`GET /files/{file_id}/thumbnail`)
   - Generate 200x200 thumbnail for image files
   - Cache generated thumbnails
   - Return 400 for non-image files

### Technical Requirements

- Use FastAPI with proper error handling
- Store file metadata in memory (dict) -- no database needed
- Use `shutil.copyfileobj` for memory-efficient file saving
- Use `pathlib.Path` for all file operations
- Validate path safety (prevent path traversal)

## Starter Template

```python
"""
File Upload Service

A complete file upload API with validation, storage, and thumbnail generation.
"""

import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="File Upload Service")

UPLOAD_DIR = Path("uploads")
THUMB_DIR = Path("uploads/thumbnails")
UPLOAD_DIR.mkdir(exist_ok=True)
THUMB_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# In-memory file metadata store
files_db: dict[str, dict] = {}


class FileMetadata(BaseModel):
    id: str
    filename: str
    original_name: str
    content_type: str
    size: int
    upload_date: str


# TODO: Implement POST /upload
# - Validate content type against ALLOWED_TYPES
# - Validate file size against MAX_FILE_SIZE
# - Generate unique filename with uuid4
# - Save file using shutil.copyfileobj
# - Store metadata in files_db
# - Return FileMetadata


# TODO: Implement GET /files
# - Return list of all FileMetadata
# - Optional query parameter: content_type filter


# TODO: Implement GET /files/{file_id}
# - Look up file_id in files_db
# - Return FileResponse with proper headers
# - Handle missing files with 404


# TODO: Implement DELETE /files/{file_id}
# - Remove from files_db
# - Delete file from disk
# - Handle missing files with 404


# TODO: Implement GET /files/{file_id}/thumbnail
# - Check file is an image type
# - Generate 200x200 thumbnail using Pillow
# - Cache in THUMB_DIR
# - Return cached thumbnail on subsequent requests
# - Return 400 for non-image files
```

## Running the Project

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart Pillow

# Run the server
uvicorn project.main:app --reload --port 8000

# Test with curl
curl -X POST http://localhost:8000/upload \
  -F "file=@photo.jpg"

curl http://localhost:8000/files

curl http://localhost:8000/files/{file_id} --output downloaded.jpg

curl http://localhost:8000/files/{file_id}/thumbnail --output thumb.jpg

curl -X DELETE http://localhost:8000/files/{file_id}
```

## Success Criteria

- [ ] Files upload successfully and persist to disk
- [ ] Invalid file types are rejected with 400 status
- [ ] Oversized files are rejected with 400 status
- [ ] File listing returns all uploaded files
- [ ] Files are downloadable by ID
- [ ] Deleted files are removed from disk and metadata
- [ ] Image thumbnails are generated correctly
- [ ] Path traversal attacks are prevented
- [ ] Tests pass: `pytest project/ -v`

## Stretch Goals

1. **S3 storage backend** -- Swap local storage for boto3 S3 uploads (use environment variable to toggle)
2. **Presigned URLs** -- Add `GET /files/{file_id}/presigned-url` endpoint for direct S3 access
3. **Async upload processing** -- Use BackgroundTasks to generate thumbnails after response
4. **Virus scanning placeholder** -- Add a `scan_file()` function stub in the validation pipeline
5. **Upload progress** -- Track upload progress using chunked reads and a status endpoint
6. **Batch operations** -- `POST /upload-batch` for multiple files, `DELETE /files/batch` for bulk delete
