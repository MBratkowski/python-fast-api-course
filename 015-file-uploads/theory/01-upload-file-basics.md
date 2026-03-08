# UploadFile Basics

## Why This Matters

On mobile, uploading a file means building a multipart request with `URLSession` (iOS) or Retrofit's `@Multipart` (Android). You compress the image, set the content type, and fire it off. But what happens on the other end?

FastAPI provides the `UploadFile` class that handles the receiving side. It wraps Python's `SpooledTemporaryFile`, which means small files live in memory and large files automatically spill to disk. This is exactly the kind of server-side optimization that doesn't exist in mobile development -- because on mobile, you only deal with one file at a time.

## FastAPI's UploadFile Class

`UploadFile` is FastAPI's interface for handling uploaded files. It wraps the raw multipart data into a clean API.

```python
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile):
    """Receive an uploaded file."""
    return {
        "filename": file.filename,          # Original filename from client
        "content_type": file.content_type,  # MIME type (e.g., "image/jpeg")
        "size": file.size,                  # File size in bytes (if available)
    }
```

### Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `filename` | `str` | Original filename sent by the client |
| `content_type` | `str` | MIME type (e.g., `image/jpeg`, `application/pdf`) |
| `size` | `int \| None` | File size in bytes (available after read, or from headers) |
| `file` | `SpooledTemporaryFile` | The underlying file-like object |
| `headers` | `Headers` | The multipart headers for this file part |

### Key Methods

```python
@app.post("/upload")
async def upload_file(file: UploadFile):
    # Read entire file into memory (careful with large files!)
    contents = await file.read()

    # Read specific number of bytes
    chunk = await file.read(1024)  # Read 1 KB

    # Reset file position (like rewinding a tape)
    await file.seek(0)

    # Write to the underlying file
    await file.write(b"data")

    # Close the file (called automatically, but can be explicit)
    await file.close()
```

## SpooledTemporaryFile Under the Hood

`UploadFile` uses Python's `SpooledTemporaryFile` internally. This is a smart wrapper:

- **Small files** (under 1 MB by default): stored in memory as `BytesIO`
- **Large files**: automatically written to a temporary file on disk

This means your server doesn't run out of memory when someone uploads a large file. The threshold is configurable, but the default works well for most applications.

```
Client sends 500 KB image:
  -> SpooledTemporaryFile stores in memory (fast)

Client sends 50 MB video:
  -> SpooledTemporaryFile writes to /tmp/tmpXXXXXX (safe)
```

## multipart/form-data

File uploads use the `multipart/form-data` content type. This is the same encoding your mobile apps use when uploading files.

```
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

<binary data>
------WebKitFormBoundary--
```

FastAPI handles all the parsing. You just declare `file: UploadFile` in your endpoint.

## File() vs UploadFile

FastAPI offers two ways to receive files:

```python
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

# Option 1: File() -- receives raw bytes
@app.post("/upload-bytes")
async def upload_bytes(file: bytes = File()):
    """Entire file loaded into memory as bytes."""
    return {"size": len(file)}

# Option 2: UploadFile -- receives file object (RECOMMENDED)
@app.post("/upload-file")
async def upload_file(file: UploadFile):
    """File object with metadata and streaming support."""
    return {"filename": file.filename, "content_type": file.content_type}
```

**Always prefer `UploadFile` over `File(bytes)`:**

| Feature | `bytes = File()` | `UploadFile` |
|---------|-------------------|-------------|
| Memory usage | Entire file in memory | Spooled (memory + disk) |
| Filename access | No | Yes (`file.filename`) |
| Content type | No | Yes (`file.content_type`) |
| Streaming | No | Yes (`file.file`) |
| Large files | Dangerous (OOM risk) | Safe |

## Multiple File Uploads

Accept multiple files in a single request:

```python
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/upload-multiple")
async def upload_multiple(files: list[UploadFile]):
    """Receive multiple files in one request."""
    results = []
    for file in files:
        contents = await file.read()
        results.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents),
        })
    return {"uploaded": results}
```

**Mobile parallel:** This is like selecting multiple photos in the gallery picker. On iOS, you'd use `PHPickerViewController` to select multiple assets. On Android, you'd use `ACTION_OPEN_DOCUMENT` with `EXTRA_ALLOW_MULTIPLE`. The server receives them all in one multipart request.

## Mixing Files and Form Data

Upload files alongside regular form fields:

```python
from fastapi import FastAPI, UploadFile, Form

app = FastAPI()

@app.post("/profile")
async def update_profile(
    username: str = Form(),
    bio: str = Form(default=""),
    avatar: UploadFile = None,  # Optional file
):
    """Update profile with optional avatar upload."""
    result = {"username": username, "bio": bio}
    if avatar:
        result["avatar_filename"] = avatar.filename
    return result
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Receive file | N/A (client only) | N/A (client only) | `file: UploadFile` |
| File metadata | `URLSessionUploadTask` result | `ResponseBody` | `file.filename`, `file.content_type` |
| Multiple files | Multiple upload tasks | Multiple `@Part` | `files: list[UploadFile]` |
| Mixed data | Combine form fields and file parts | `@Part` + `@Part` | `Form()` + `UploadFile` |
| Memory management | NSData / Data | InputStream | SpooledTemporaryFile |

## Key Takeaways

- **UploadFile** is FastAPI's recommended way to receive uploaded files
- It uses **SpooledTemporaryFile** internally -- small files stay in memory, large files spill to disk
- Always prefer `UploadFile` over `bytes = File()` to avoid memory exhaustion
- Access **filename**, **content_type**, and **size** properties for file metadata
- Use `list[UploadFile]` for multiple file uploads
- Mix files and form fields with `Form()` and `UploadFile` together
- Files arrive as **multipart/form-data** -- the same encoding your mobile apps use
