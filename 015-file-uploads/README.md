# Module 015: File Uploads and Storage

## Why This Module?

As a mobile developer, you've built the client side of file uploads countless times -- selecting photos from the gallery, compressing images, sending multipart requests to the server. Now you'll build the server side: receiving those uploads, validating them, storing them safely, and serving them back.

This is one of those features where the backend perspective is fundamentally different from the client perspective. On mobile, you worry about "did the upload succeed?" On the server, you worry about "is this file safe? Where do I store it? How do I serve it efficiently? What if someone uploads a 2GB file?"

## What You'll Learn

- FastAPI's UploadFile class and multipart/form-data handling
- Content-type and magic number validation (never trust the client)
- Local file storage with streaming writes
- AWS S3 integration with boto3
- Presigned URLs for direct client-to-S3 uploads
- Image processing with Pillow (resize, thumbnails, format conversion)

## Mobile Developer Context

You've sent files from mobile apps. Now you receive and store them on the server.

**File Upload Across Platforms:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Upload API | `URLSession.uploadTask` | Retrofit `@Multipart` | `UploadFile` (multipart/form-data) |
| File type check | `UTType` | `ContentResolver.getType()` | `content_type` + magic numbers |
| Image resize | `UIImage` / Core Image | `Bitmap.createScaledBitmap` | Pillow `Image.resize()` |
| Cloud storage | AWS Amplify Storage | Firebase Storage | boto3 / S3 presigned URLs |
| Progress tracking | `URLSessionTaskDelegate` | OkHttp Interceptor | Chunked read (server-side) |

**Key Differences from Mobile:**
- On mobile, you send one file at a time. On the server, you handle thousands of concurrent uploads
- On mobile, you trust the OS to tell you the file type. On the server, you must validate independently (clients can lie)
- On mobile, files live in the app sandbox. On the server, you need a storage strategy (local disk, S3, CDN)
- On mobile, you compress before upload. On the server, you validate, resize, and generate variants (thumbnails)

## Quick Assessment

Before starting, you should be comfortable with:
- [ ] FastAPI route handlers and request/response models (Module 003-004)
- [ ] HTTP status codes and error handling (Module 003)
- [ ] Python `pathlib.Path` for file operations
- [ ] async/await basics (Module 012)

## Topics

### Theory
1. UploadFile Basics -- FastAPI's file handling interface
2. File Validation -- Content-type, magic numbers, size limits
3. Local Storage -- Saving files to disk with streaming
4. S3 Integration -- Cloud storage with boto3
5. Presigned URLs -- Direct client-to-S3 uploads
6. Image Processing -- Resize, thumbnails, format conversion with Pillow

### Exercises
1. File Upload Endpoints -- Single and multiple file uploads
2. File Validation -- Content-type and size validation
3. Storage Patterns -- UUID naming, date organization, cleanup

### Project
File upload service with validation, local storage, and thumbnail generation.

## Time Estimate

- Theory: ~90 minutes
- Exercises: ~60 minutes
- Project: ~90 minutes

## Example

```python
from fastapi import FastAPI, UploadFile, HTTPException
import shutil
from pathlib import Path
from uuid import uuid4

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/upload")
async def upload_file(file: UploadFile):
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Type {file.content_type} not allowed")

    # Generate unique filename
    ext = Path(file.filename).suffix
    unique_name = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    # Stream to disk (memory-efficient)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"filename": unique_name, "content_type": file.content_type}
```
