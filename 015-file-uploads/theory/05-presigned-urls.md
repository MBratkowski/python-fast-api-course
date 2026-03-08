# Presigned URLs

## Why This Matters

In a typical file upload flow, the file goes: client -> your server -> S3. Your server is in the middle, proxying every byte. This wastes bandwidth, CPU, and memory. For large files, it's a bottleneck.

Presigned URLs flip this: your server generates a time-limited signed URL, and the client uploads directly to S3. The server never touches the file bytes. It's the same pattern behind Firebase Storage download URLs on mobile.

## What Presigned URLs Solve

```
Traditional Flow (server proxies):
  Client ---[file bytes]---> Your Server ---[file bytes]---> S3
  (slow, uses server resources)

Presigned URL Flow (direct upload):
  Client ---[request URL]---> Your Server ---[presigned URL]---> Client
  Client ---[file bytes]---> S3 (direct)
  (fast, server only generates URL)
```

**Benefits:**
- Server doesn't handle file bytes (saves bandwidth, memory, CPU)
- Client uploads directly to S3 (faster for large files)
- URLs expire after a set time (security)
- Works with any S3-compatible storage (MinIO, DigitalOcean Spaces, etc.)

## Generating Presigned URLs

### Presigned PUT URL (for uploads)

```python
import boto3
from uuid import uuid4
from pathlib import Path
from fastapi import FastAPI

app = FastAPI()
s3_client = boto3.client("s3")
BUCKET = "my-app-uploads"

@app.post("/upload-url")
async def get_upload_url(filename: str, content_type: str):
    """Generate a presigned URL for direct client-to-S3 upload."""
    # Generate unique key
    ext = Path(filename).suffix.lower()
    key = f"uploads/{uuid4().hex}{ext}"

    # Generate presigned PUT URL
    presigned_url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300,  # URL valid for 5 minutes
    )

    return {
        "upload_url": presigned_url,
        "key": key,
        "expires_in": 300,
    }
```

**Client usage (from mobile):**

```swift
// iOS: Upload directly to S3 using presigned URL
var request = URLRequest(url: presignedURL)
request.httpMethod = "PUT"
request.setValue(contentType, forHTTPHeaderField: "Content-Type")

let (_, response) = try await URLSession.shared.upload(for: request, from: fileData)
```

```kotlin
// Android: Upload directly to S3 using presigned URL
val request = Request.Builder()
    .url(presignedUrl)
    .put(fileData.toRequestBody(contentType.toMediaType()))
    .build()

OkHttpClient().newCall(request).execute()
```

### Presigned GET URL (for downloads)

```python
@app.get("/download-url/{file_key:path}")
async def get_download_url(file_key: str):
    """Generate a presigned URL for downloading a file."""
    presigned_url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": BUCKET,
            "Key": file_key,
        },
        ExpiresIn=3600,  # URL valid for 1 hour
    )

    return {
        "download_url": presigned_url,
        "expires_in": 3600,
    }
```

## Expiration Configuration

```python
# Short-lived (uploads) -- 5 minutes
upload_url = s3_client.generate_presigned_url(
    "put_object",
    Params={"Bucket": BUCKET, "Key": key},
    ExpiresIn=300,
)

# Medium-lived (downloads) -- 1 hour
download_url = s3_client.generate_presigned_url(
    "get_object",
    Params={"Bucket": BUCKET, "Key": key},
    ExpiresIn=3600,
)

# Long-lived (shared links) -- 7 days (maximum)
share_url = s3_client.generate_presigned_url(
    "get_object",
    Params={"Bucket": BUCKET, "Key": key},
    ExpiresIn=604800,
)
```

**Expiration guidelines:**

| Use Case | Recommended TTL | Why |
|----------|----------------|-----|
| Upload | 5-15 minutes | User should upload immediately |
| Download (auth'd) | 1 hour | Single session use |
| Shared link | 1-7 days | External sharing |
| Temporary preview | 5 minutes | Quick view only |

## Complete Upload Flow with Presigned URLs

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from pathlib import Path
import boto3

app = FastAPI()
s3_client = boto3.client("s3")
BUCKET = "my-app-uploads"

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB

class UploadRequest(BaseModel):
    filename: str
    content_type: str
    size: int  # Client reports expected size

class UploadResponse(BaseModel):
    upload_url: str
    key: str
    expires_in: int

@app.post("/uploads/request", response_model=UploadResponse)
async def request_upload(request: UploadRequest):
    """Step 1: Client requests a presigned upload URL."""
    # Validate before generating URL
    if request.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Type '{request.content_type}' not allowed")
    if request.size > MAX_SIZE:
        raise HTTPException(400, f"File too large (max {MAX_SIZE // (1024*1024)} MB)")

    # Generate unique key
    ext = Path(request.filename).suffix.lower()
    key = f"uploads/{uuid4().hex}{ext}"

    # Generate presigned URL with content-type constraint
    url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET,
            "Key": key,
            "ContentType": request.content_type,
        },
        ExpiresIn=300,
    )

    return UploadResponse(upload_url=url, key=key, expires_in=300)

@app.post("/uploads/confirm/{key:path}")
async def confirm_upload(key: str):
    """Step 2: Client confirms upload completed. Server verifies."""
    try:
        response = s3_client.head_object(Bucket=BUCKET, Key=key)
    except Exception:
        raise HTTPException(404, "File not found in storage")

    return {
        "key": key,
        "size": response["ContentLength"],
        "content_type": response["ContentType"],
        "status": "confirmed",
    }
```

## Security Benefits

1. **Server never handles file bytes** -- reduces attack surface
2. **URLs expire** -- even if leaked, they become invalid
3. **Content-type enforcement** -- presigned URL can require specific content type
4. **Bucket policy enforcement** -- S3 bucket policies still apply
5. **No server-side storage** -- no risk of filling server disk

**Security considerations:**
- Always validate file type and size BEFORE generating the URL
- Use short expiration times for upload URLs
- Implement a confirmation step to verify the upload completed correctly
- Set CORS on the S3 bucket to allow direct browser uploads

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI + boto3) |
|---------|-------------|-------------------|--------------------------|
| Direct upload | Amplify `Storage.uploadFile` | Firebase `putFile` | Presigned PUT URL |
| Download URL | Amplify `Storage.getURL` | `storageRef.downloadUrl` | Presigned GET URL |
| Expiration | Amplify handles TTL | Firebase tokens auto-refresh | `ExpiresIn` parameter |
| Auth check | Cognito integration | Firebase Auth | Server validates before generating URL |

## Key Takeaways

- Presigned URLs let clients **upload/download directly to/from S3** without your server proxying bytes
- Use **PUT presigned URLs** for uploads and **GET presigned URLs** for downloads
- Always **validate before generating** -- check file type and size on the request, not the upload
- Set **appropriate expiration times** -- short for uploads, longer for downloads
- Implement a **confirmation step** where the client tells the server the upload completed
- This pattern **scales better** than server-proxied uploads because your server only handles metadata
- Works with **any S3-compatible storage** (AWS S3, MinIO, DigitalOcean Spaces, Backblaze B2)
