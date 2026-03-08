# Image Processing

## Why This Matters

On mobile, you've used `UIImage` (iOS) or `Bitmap` (Android) to resize images, generate thumbnails, and convert formats. On the server, the same operations happen -- but at scale. When a user uploads a profile photo, you might generate a 150x150 thumbnail, a 400x400 medium size, and keep the original. Pillow is Python's standard library for this.

## Pillow Basics

Pillow (PIL Fork) is the standard Python library for image manipulation.

```bash
pip install Pillow
```

```python
from PIL import Image
from pathlib import Path

# Open an image
img = Image.open("photo.jpg")

# Basic properties
print(img.size)      # (1920, 1080) -- width x height
print(img.format)    # "JPEG"
print(img.mode)      # "RGB"

# Resize (exact dimensions)
resized = img.resize((800, 600))
resized.save("photo_800x600.jpg")

# Thumbnail (maintains aspect ratio, fits within bounds)
img.thumbnail((200, 200))  # Modifies in place
img.save("photo_thumb.jpg")
```

### Resize vs Thumbnail

```python
from PIL import Image

img = Image.open("photo.jpg")  # 1920x1080

# resize() -- exact dimensions (may distort)
exact = img.resize((200, 200))  # 200x200 (stretched/squished)

# thumbnail() -- fits within bounds (preserves aspect ratio)
thumb = img.copy()
thumb.thumbnail((200, 200))  # 200x112 (fits within 200x200, keeps ratio)
```

**Always use `thumbnail()` for user-facing images** -- distorted images look unprofessional.

## Format Conversion

```python
from PIL import Image

img = Image.open("photo.jpg")

# JPEG to PNG
img.save("photo.png", format="PNG")

# JPEG to WebP (smaller file size, modern browsers)
img.save("photo.webp", format="WEBP", quality=85)

# PNG with transparency to JPEG (must convert mode)
png_with_alpha = Image.open("logo.png")  # RGBA mode
rgb_image = png_with_alpha.convert("RGB")  # Drop alpha channel
rgb_image.save("logo.jpg", format="JPEG", quality=90)
```

### Quality Settings

```python
# JPEG quality (1-95, default 75)
img.save("high.jpg", quality=95)    # Large file, best quality
img.save("medium.jpg", quality=75)  # Good balance
img.save("low.jpg", quality=40)     # Small file, visible artifacts

# WebP quality
img.save("photo.webp", format="WEBP", quality=80)  # ~30% smaller than JPEG
```

## EXIF Handling

Photos from mobile devices contain EXIF metadata: camera model, GPS location, orientation. You often need to handle orientation and strip sensitive data.

```python
from PIL import Image, ExifTags
from PIL.ExifTags import Tags

def fix_orientation(img: Image.Image) -> Image.Image:
    """Rotate image based on EXIF orientation tag."""
    try:
        exif = img.getexif()
        orientation_key = None
        for key, val in ExifTags.TAGS.items():
            if val == "Orientation":
                orientation_key = key
                break

        if orientation_key and orientation_key in exif:
            orientation = exif[orientation_key]
            rotations = {
                3: 180,
                6: 270,
                8: 90,
            }
            if orientation in rotations:
                img = img.rotate(rotations[orientation], expand=True)
    except Exception:
        pass  # No EXIF data, return as-is

    return img

def strip_exif(img: Image.Image) -> Image.Image:
    """Remove all EXIF metadata (privacy: strips GPS, device info)."""
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    return clean
```

## Processing Pipeline

A typical server-side image processing pipeline:

```python
from PIL import Image
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, UploadFile, HTTPException
import shutil
import io

app = FastAPI()

UPLOAD_DIR = Path("uploads")
THUMB_DIR = Path("uploads/thumbnails")
UPLOAD_DIR.mkdir(exist_ok=True)
THUMB_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB
THUMBNAIL_SIZE = (200, 200)
MEDIUM_SIZE = (800, 800)

@app.post("/upload/image")
async def upload_image(file: UploadFile):
    """Upload image -> validate -> process -> save original + thumbnail."""
    # Step 1: Validate type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Type '{file.content_type}' not allowed")

    # Step 2: Read file contents
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "Image too large (max 10 MB)")

    # Step 3: Open with Pillow (also validates it's a real image)
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()  # Verify it's actually an image
        img = Image.open(io.BytesIO(contents))  # Re-open after verify
    except Exception:
        raise HTTPException(400, "Invalid image file")

    # Step 4: Fix orientation from EXIF
    img = fix_orientation(img)

    # Step 5: Generate filenames
    unique_id = uuid4().hex
    ext = ".webp"  # Convert all to WebP for efficiency
    original_name = f"{unique_id}_original{ext}"
    thumb_name = f"{unique_id}_thumb{ext}"

    # Step 6: Save original (possibly resized if huge)
    if img.size[0] > 2000 or img.size[1] > 2000:
        img.thumbnail((2000, 2000))
    img.save(UPLOAD_DIR / original_name, format="WEBP", quality=85)

    # Step 7: Generate and save thumbnail
    thumb = img.copy()
    thumb.thumbnail(THUMBNAIL_SIZE)
    thumb.save(THUMB_DIR / thumb_name, format="WEBP", quality=75)

    return {
        "original": original_name,
        "thumbnail": thumb_name,
        "size": img.size,
        "format": "webp",
    }
```

## Generating Multiple Sizes

```python
from PIL import Image
from pathlib import Path
from uuid import uuid4

SIZES = {
    "thumb": (150, 150),
    "small": (300, 300),
    "medium": (800, 800),
    "large": (1600, 1600),
}

def generate_variants(
    img: Image.Image,
    output_dir: Path,
    base_name: str | None = None,
) -> dict[str, str]:
    """Generate multiple size variants of an image."""
    base_name = base_name or uuid4().hex
    variants = {}

    for size_name, dimensions in SIZES.items():
        variant = img.copy()
        variant.thumbnail(dimensions)

        filename = f"{base_name}_{size_name}.webp"
        variant.save(output_dir / filename, format="WEBP", quality=80)
        variants[size_name] = filename

    # Save original too
    original_name = f"{base_name}_original.webp"
    img.save(output_dir / original_name, format="WEBP", quality=90)
    variants["original"] = original_name

    return variants
```

## Image Validation with Pillow

Pillow can serve as an additional validation gate -- if a file isn't a valid image, Pillow will fail to open it:

```python
from PIL import Image
import io

async def validate_image(file_bytes: bytes) -> Image.Image:
    """Validate that bytes are actually a valid image."""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()  # Check file integrity

        # Re-open after verify (verify() can leave file in bad state)
        img = Image.open(io.BytesIO(file_bytes))
        img.load()  # Force full decode

        return img
    except Exception as e:
        raise ValueError(f"Invalid image: {e}")
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (Pillow) |
|---------|-------------|-------------------|------------------|
| Image library | UIImage / Core Image | Bitmap / Glide | Pillow (PIL) |
| Resize | `UIGraphicsImageRenderer` | `Bitmap.createScaledBitmap` | `img.resize()` / `img.thumbnail()` |
| Thumbnail | `prepareThumbnail(of:)` | Glide `.override(w, h)` | `img.thumbnail((w, h))` |
| Format conversion | `jpegData()` / `pngData()` | `Bitmap.compress()` | `img.save(format="WEBP")` |
| EXIF | `CGImageSource` | `ExifInterface` | `img.getexif()` |
| Orientation fix | `imageOrientation` | `ExifInterface.ORIENTATION_*` | Manual rotation from EXIF tag |

## Key Takeaways

- **Pillow** is Python's standard image processing library -- like UIImage/Bitmap for the server
- Use **`thumbnail()`** to maintain aspect ratio, **`resize()`** for exact dimensions
- Always **fix EXIF orientation** -- mobile cameras set orientation in metadata, not pixels
- Consider **stripping EXIF data** for privacy (removes GPS, device info)
- Generate **multiple size variants** on upload (thumb, small, medium, large, original)
- Convert to **WebP** for smaller file sizes (~30% smaller than JPEG at equivalent quality)
- Use **`img.verify()`** as an additional validation gate -- invalid images will raise exceptions
- Process images **after validation, before storage** -- the pipeline is validate -> process -> save
