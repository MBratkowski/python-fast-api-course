# File Validation

## Why This Matters

On mobile, you use the OS to determine file types -- `UTType` on iOS, `ContentResolver.getType()` on Android. You trust the system because you control the file picker. On the server, you can't trust anything. The client can send a `.exe` file labeled as `image/jpeg`. Your server is the last line of defense.

File validation is a security-critical operation. Without it, attackers can upload malicious files, exhaust your storage, or exploit image processing vulnerabilities. Think of it like input validation for binary data.

## The Three Gates of File Validation

Every uploaded file should pass through three validation gates:

```
Gate 1: Content-Type Check (fast, unreliable alone)
  |
  v
Gate 2: Magic Number Check (reliable, requires reading bytes)
  |
  v
Gate 3: File Size Check (prevents resource exhaustion)
  |
  v
  ACCEPTED
```

### Gate 1: Content-Type Validation

The content-type header is the first check -- fast but easily spoofed.

```python
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}

@app.post("/upload")
async def upload_file(file: UploadFile):
    # Gate 1: Content-type whitelist
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. "
                   f"Allowed: {', '.join(ALLOWED_TYPES)}"
        )
    return {"filename": file.filename, "type": file.content_type}
```

**Why this alone is not enough:** A malicious client can set any content-type header. A script disguised as `image/jpeg` would pass this gate.

### Gate 2: Magic Number Validation

Magic numbers are the first few bytes of a file that identify its true type. This is what the OS uses internally.

```
JPEG: FF D8 FF
PNG:  89 50 4E 47 0D 0A 1A 0A
PDF:  25 50 44 46
GIF:  47 49 46 38
```

**Using the `filetype` library** (pure Python, no system dependencies):

```python
import filetype
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

async def validate_file_type(file: UploadFile) -> str:
    """Validate file type using magic numbers (not content-type header)."""
    # Read first 261 bytes (enough for magic number detection)
    header = await file.read(261)
    await file.seek(0)  # Reset position for later use

    kind = filetype.match(header)
    if kind is None:
        raise HTTPException(400, "Could not determine file type")

    if kind.mime not in ALLOWED_MIMES:
        raise HTTPException(
            400,
            f"File type '{kind.mime}' not allowed"
        )
    return kind.mime

@app.post("/upload")
async def upload_file(file: UploadFile):
    actual_type = await validate_file_type(file)
    return {"filename": file.filename, "verified_type": actual_type}
```

**Using `python-magic`** (requires `libmagic` system library):

```python
import magic
from fastapi import UploadFile, HTTPException

async def validate_with_magic(file: UploadFile) -> str:
    """Validate using python-magic (requires libmagic)."""
    header = await file.read(2048)
    await file.seek(0)

    mime = magic.from_buffer(header, mime=True)
    if mime not in ALLOWED_MIMES:
        raise HTTPException(400, f"File type '{mime}' not allowed")
    return mime
```

| Library | Pros | Cons |
|---------|------|------|
| `filetype` | Pure Python, no system deps | Fewer file types supported |
| `python-magic` | Comprehensive detection | Requires `libmagic` system library |

### Gate 3: File Size Validation

Prevent resource exhaustion by checking file size before processing.

```python
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

async def validate_file_size(file: UploadFile, max_size: int = MAX_FILE_SIZE):
    """Validate file size by reading in chunks (memory-efficient)."""
    size = 0
    chunk_size = 1024 * 1024  # 1 MB chunks

    while chunk := await file.read(chunk_size):
        size += len(chunk)
        if size > max_size:
            raise HTTPException(
                400,
                f"File too large. Maximum size: {max_size // (1024*1024)} MB"
            )

    await file.seek(0)  # Reset for later use
    return size
```

**Anti-pattern: Reading entire file for size check:**

```python
# BAD -- loads entire file into memory
contents = await file.read()
if len(contents) > MAX_FILE_SIZE:
    raise HTTPException(400, "Too large")

# GOOD -- check size in chunks (above pattern)
# Or check Content-Length header (but client can lie)
```

## Combined Validation Function

Bring all three gates together:

```python
from fastapi import UploadFile, HTTPException
import filetype

ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

async def validate_upload(
    file: UploadFile,
    allowed_types: set[str] = ALLOWED_MIMES,
    max_size: int = MAX_FILE_SIZE,
) -> dict:
    """
    Three-gate file validation.

    Returns file metadata if valid, raises HTTPException if not.
    """
    # Gate 1: Content-type (fast first check)
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Content type '{file.content_type}' not allowed")

    # Gate 2: Magic number (reliable type check)
    header = await file.read(261)
    await file.seek(0)
    kind = filetype.match(header)
    if kind is None or kind.mime not in allowed_types:
        actual = kind.mime if kind else "unknown"
        raise HTTPException(400, f"File content is '{actual}', not an allowed type")

    # Gate 3: File size (resource protection)
    size = 0
    chunk_size = 1024 * 1024
    while chunk := await file.read(chunk_size):
        size += len(chunk)
        if size > max_size:
            raise HTTPException(400, f"File exceeds {max_size // (1024*1024)} MB limit")
    await file.seek(0)

    return {
        "filename": file.filename,
        "content_type": kind.mime,
        "size": size,
    }
```

## Anti-Pattern: Trusting File Extensions

```python
# NEVER DO THIS
def is_valid_image(filename: str) -> bool:
    return filename.endswith(('.jpg', '.png', '.gif'))

# File extensions are trivially spoofed:
# malware.exe -> malware.jpg (still passes extension check)
```

**Always validate file content, not the filename.** Extensions are a hint, not a guarantee.

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (FastAPI) |
|---------|-------------|-------------------|------------------|
| Type detection | `UTType` from filename/data | `ContentResolver.getType()` | `filetype.match()` or `python-magic` |
| Size check | `Data.count` | `File.length()` | Chunked read or `file.size` |
| Whitelist | Check `UTType.conforms(to:)` | Check MIME type | Set of allowed MIME strings |
| Trust level | High (OS controls picker) | High (OS controls picker) | Low (client can spoof anything) |

## Key Takeaways

- **Never trust content-type alone** -- it's set by the client and easily spoofed
- Use **three-gate validation**: content-type, magic numbers, file size
- **Magic numbers** are the reliable way to detect file type (first bytes of the file)
- Use `filetype` (pure Python) or `python-magic` (comprehensive) for magic number detection
- **Read in chunks** for size validation -- never load the entire file into memory
- Always **reset file position** with `await file.seek(0)` after reading for validation
- On the server, **you are the security boundary** -- unlike mobile where the OS mediates
