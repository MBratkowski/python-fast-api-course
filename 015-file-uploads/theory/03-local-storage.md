# Local File Storage

## Why This Matters

On mobile, files go into the app's sandbox (`Documents/`, `Caches/`). The OS manages storage, cleanup, and access control. On the server, you manage everything yourself: where files go, how they're named, how they're served back, and when they get cleaned up.

Local storage is the simplest approach -- files go directly onto the server's disk. It's perfect for development, small deployments, and learning the fundamentals before moving to cloud storage.

## Saving Files with shutil.copyfileobj

The key function for writing uploaded files to disk is `shutil.copyfileobj`. It streams data in chunks, so you never load the entire file into memory.

```python
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile):
    """Upload a file and save to local storage."""
    file_path = UPLOAD_DIR / file.filename

    # Stream file to disk (memory-efficient)
    with open(file_path, "wb") as dest:
        shutil.copyfileobj(file.file, dest)

    return {
        "filename": file.filename,
        "path": str(file_path),
    }
```

### Why shutil.copyfileobj?

```python
# BAD -- loads entire file into memory
contents = await file.read()
with open(path, "wb") as f:
    f.write(contents)

# GOOD -- streams in chunks (default 16 KB)
shutil.copyfileobj(file.file, dest)

# GOOD -- streams with custom chunk size
shutil.copyfileobj(file.file, dest, length=1024 * 1024)  # 1 MB chunks
```

**Anti-pattern: `await file.read()` for large files.** If 10 users upload 100 MB files simultaneously, that's 1 GB of memory just for file contents. `shutil.copyfileobj` uses a fixed buffer regardless of file size.

## Unique Filename Generation

Never use the original filename directly. It can contain path traversal attacks (`../../etc/passwd`), duplicates, or special characters.

```python
from uuid import uuid4
from pathlib import Path

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename preserving the original extension."""
    ext = Path(original_filename).suffix.lower()  # .jpg, .png, etc.
    return f"{uuid4().hex}{ext}"

# Examples:
# "photo.jpg"      -> "a1b2c3d4e5f6...jpg"
# "My File (2).png" -> "f7e8d9c0b1a2...png"
# "../../hack.sh"  -> "d4c3b2a1e5f6...sh"  (extension preserved, path stripped)
```

### Complete Upload + Save Endpoint

```python
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/upload")
async def upload_file(file: UploadFile):
    """Upload, validate, and save a file."""
    # Validate type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Type '{file.content_type}' not allowed")

    # Generate unique name
    ext = Path(file.filename).suffix.lower()
    unique_name = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    # Stream to disk
    with open(file_path, "wb") as dest:
        shutil.copyfileobj(file.file, dest)

    # Get actual size from saved file
    size = file_path.stat().st_size
    if size > MAX_SIZE:
        file_path.unlink()  # Delete oversized file
        raise HTTPException(400, f"File too large ({size} bytes, max {MAX_SIZE})")

    return {
        "filename": unique_name,
        "original_name": file.filename,
        "size": size,
        "content_type": file.content_type,
    }
```

## Serving Static Files

FastAPI can serve uploaded files back to clients using Starlette's `StaticFiles`:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount the uploads directory as a static route
app.mount("/files", StaticFiles(directory="uploads"), name="uploaded-files")

# Now files are accessible at:
# GET /files/a1b2c3d4.jpg -> serves uploads/a1b2c3d4.jpg
```

### Download Endpoint (More Control)

For more control over file serving (auth, logging, custom headers):

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()
UPLOAD_DIR = Path("uploads")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a file with proper headers."""
    file_path = UPLOAD_DIR / filename

    # Prevent path traversal
    if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(400, "Invalid filename")

    if not file_path.exists():
        raise HTTPException(404, "File not found")

    return FileResponse(
        path=file_path,
        filename=filename,  # Sets Content-Disposition header
        media_type="application/octet-stream",
    )
```

## Path Operations

Python's `pathlib.Path` is essential for file operations:

```python
from pathlib import Path

upload_dir = Path("uploads")

# Create directories
upload_dir.mkdir(exist_ok=True)                        # Create if missing
(upload_dir / "images").mkdir(parents=True, exist_ok=True)  # Nested

# File operations
file_path = upload_dir / "photo.jpg"
file_path.exists()          # True/False
file_path.stat().st_size    # File size in bytes
file_path.suffix            # ".jpg"
file_path.stem              # "photo"
file_path.name              # "photo.jpg"
file_path.unlink()          # Delete file

# Path safety
file_path.resolve()         # Absolute path (resolves ..)
file_path.is_relative_to(upload_dir)  # Path traversal check

# List files
list(upload_dir.glob("*.jpg"))       # All JPGs
list(upload_dir.rglob("*.png"))      # Recursive search
```

## Cleanup Strategies

Files accumulate. You need a cleanup strategy.

```python
import time
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_files(directory: Path, max_age_days: int = 30):
    """Delete files older than max_age_days."""
    cutoff = time.time() - (max_age_days * 86400)

    deleted = 0
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.stat().st_mtime < cutoff:
            file_path.unlink()
            deleted += 1

    return deleted
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (Server) |
|---------|-------------|-------------------|------------------|
| Storage location | `Documents/` or `Caches/` | `getFilesDir()` or `getCacheDir()` | Custom `uploads/` directory |
| Unique names | `UUID().uuidString` | `UUID.randomUUID()` | `uuid4().hex` |
| Path API | `FileManager` + `URL` | `java.nio.file.Path` | `pathlib.Path` |
| Serve files | N/A (local only) | N/A (local only) | `StaticFiles` mount or `FileResponse` |
| Cleanup | OS manages cache eviction | OS manages cache eviction | Manual cleanup (cron, background task) |
| Max storage | Device-limited | Device-limited | Disk-limited (plan capacity) |

## Key Takeaways

- Use `shutil.copyfileobj` to **stream files to disk** -- never `await file.read()` for large files
- Generate **unique filenames** with UUID to prevent collisions and path traversal
- Always **validate path safety** with `resolve()` and `is_relative_to()` before serving files
- Mount `StaticFiles` for simple file serving, or use `FileResponse` for controlled downloads
- Use `pathlib.Path` for all file operations -- it's safer and more readable than `os.path`
- Plan a **cleanup strategy** from the start -- files accumulate faster than you think
- On the server, **you manage the filesystem** -- there's no OS sandbox doing cleanup for you
