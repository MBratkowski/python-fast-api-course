# Module 015: File Uploads & Storage

## Why This Module?

Handle user uploads: images, documents, media. Learn local and cloud storage (S3).

## What You'll Learn

- FastAPI file uploads
- File validation
- Local file storage
- S3/Cloud storage
- Image processing
- Streaming large files

## Topics

### Theory
1. FastAPI UploadFile
2. File Validation (type, size)
3. Local Storage Patterns
4. AWS S3 Integration
5. Presigned URLs
6. Image Processing with Pillow

### Project
Build a file upload service with S3 storage.

## Example

```python
from fastapi import UploadFile, File, HTTPException
import boto3

ALLOWED_TYPES = ["image/jpeg", "image/png"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large")

    # Upload to S3
    s3 = boto3.client("s3")
    key = f"uploads/{current_user.id}/{file.filename}"
    s3.put_object(Bucket="my-bucket", Key=key, Body=content)

    return {"url": f"https://my-bucket.s3.amazonaws.com/{key}"}
```
