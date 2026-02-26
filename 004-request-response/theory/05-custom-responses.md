# Custom Response Classes

## Why This Matters

Most API responses are JSON, but sometimes you need to return HTML (for a web dashboard), plain text (for a health check), a file download, or a redirect. FastAPI provides response classes for each use case - just like how in mobile you might return different content types from a web view.

## Default: JSONResponse

By default, FastAPI returns JSON:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    """
    FastAPI automatically wraps this in JSONResponse.
    You don't need to specify it.
    """
    return {"message": "Hello World"}

# Client receives:
# Content-Type: application/json
# {"message": "Hello World"}
```

## PlainTextResponse

For returning plain text:

```python
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    """Returns plain text, not JSON."""
    return "OK"

# Client receives:
# Content-Type: text/plain
# OK
```

Or explicitly:

```python
@app.get("/readme")
async def get_readme():
    """Return plain text explicitly."""
    content = "# README\n\nThis is plain text documentation."
    return PlainTextResponse(content=content)
```

## HTMLResponse

For returning HTML (useful for simple dashboards or status pages):

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Returns HTML page."""
    html_content = """
    <html>
        <head><title>Dashboard</title></head>
        <body>
            <h1>API Dashboard</h1>
            <p>Status: <span style="color: green;">Online</span></p>
        </body>
    </html>
    """
    return html_content

# Client receives:
# Content-Type: text/html
# (HTML rendered in browser)
```

## RedirectResponse

For redirecting clients to another URL:

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/old-url")
async def old_endpoint():
    """Redirect to new URL."""
    return RedirectResponse(url="/new-url")

@app.get("/login")
async def login_redirect():
    """Redirect to OAuth provider."""
    return RedirectResponse(url="https://accounts.google.com/oauth")

# Client receives:
# HTTP 307 Temporary Redirect (default)
# Location: /new-url
```

Control redirect status code:

```python
@app.get("/moved")
async def moved_permanently():
    """301 Permanent Redirect - tells clients to cache new URL."""
    return RedirectResponse(url="/new-location", status_code=301)

@app.get("/found")
async def temporary_redirect():
    """302 Found - temporary redirect."""
    return RedirectResponse(url="/temp-location", status_code=302)
```

## FileResponse

For sending files (downloads):

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/download")
async def download_file():
    """Send file to client."""
    file_path = "report.pdf"
    return FileResponse(
        path=file_path,
        filename="monthly-report.pdf",  # What client saves it as
        media_type="application/pdf"
    )

# Client receives:
# Content-Disposition: attachment; filename="monthly-report.pdf"
# (file downloads)
```

For inline display (like images):

```python
@app.get("/image")
async def get_image():
    """Display image inline instead of downloading."""
    return FileResponse(
        path="logo.png",
        media_type="image/png",
        headers={"Content-Disposition": "inline"}
    )
```

## StreamingResponse

For sending data as a stream (large files, real-time data):

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import io

app = FastAPI()

@app.get("/stream")
async def stream_data():
    """Stream data to client."""
    def generate():
        for i in range(100):
            yield f"Line {i}\n"

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )
```

For large file downloads:

```python
@app.get("/large-file")
async def download_large_file():
    """Stream large file without loading into memory."""
    def file_iterator(file_path: str):
        with open(file_path, "rb") as file:
            chunk_size = 8192
            while chunk := file.read(chunk_size):
                yield chunk

    return StreamingResponse(
        file_iterator("large-video.mp4"),
        media_type="video/mp4"
    )
```

## Custom Headers and Cookies

All response classes support custom headers:

```python
from fastapi.responses import JSONResponse

@app.get("/data")
async def get_data():
    """Return JSON with custom headers."""
    content = {"message": "Hello"}
    headers = {
        "X-Custom-Header": "CustomValue",
        "Cache-Control": "max-age=300"
    }
    return JSONResponse(content=content, headers=headers)
```

Setting cookies:

```python
from fastapi.responses import JSONResponse

@app.post("/login")
async def login():
    """Set cookie on response."""
    response = JSONResponse(content={"message": "Logged in"})
    response.set_cookie(
        key="session_token",
        value="abc123",
        httponly=True,  # Not accessible via JavaScript
        secure=True,    # Only sent over HTTPS
        max_age=3600    # 1 hour
    )
    return response
```

## Response Status Codes

Control status codes with any response class:

```python
from fastapi.responses import JSONResponse
from fastapi import status

@app.post("/users")
async def create_user():
    """Return 201 Created."""
    return JSONResponse(
        content={"id": 123, "name": "Alice"},
        status_code=status.HTTP_201_CREATED
    )

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Return 204 No Content."""
    return JSONResponse(
        content=None,
        status_code=status.HTTP_204_NO_CONTENT
    )
```

## ORJSONResponse (Fast JSON)

For high-performance JSON serialization:

```python
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)

@app.get("/data")
async def get_data():
    """Uses orjson for faster serialization."""
    return {"large": "data" * 1000}
```

Install with: `pip install orjson`

## Content Negotiation

Return different formats based on Accept header:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse

app = FastAPI()

@app.get("/data")
async def get_data(request: Request):
    """Return different format based on Accept header."""
    accept = request.headers.get("accept", "")

    data = {"message": "Hello World"}

    if "text/html" in accept:
        html = f"<h1>{data['message']}</h1>"
        return HTMLResponse(content=html)

    elif "text/plain" in accept:
        text = data["message"]
        return PlainTextResponse(content=text)

    else:
        # Default to JSON
        return JSONResponse(content=data)
```

## Response with Custom Model

Combine response models with custom response classes:

```python
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=User, response_class=ORJSONResponse)
async def get_user(user_id: int):
    """Use custom response class with response model validation."""
    return {"id": user_id, "name": "Alice"}
```

## Byte Responses

For returning raw bytes (images, PDFs generated in memory):

```python
from fastapi.responses import Response
import qrcode
import io

@app.get("/qr")
async def generate_qr():
    """Generate QR code image on the fly."""
    # Generate QR code in memory
    qr = qrcode.QRCode()
    qr.add_data("https://example.com")
    qr.make()

    img = qr.make_image()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return Response(
        content=buf.getvalue(),
        media_type="image/png"
    )
```

## Mobile Developer Context

| Mobile Scenario | FastAPI Response |
|-----------------|------------------|
| JSON API response | `return {"data": ...}` (default JSONResponse) |
| Display HTML in WebView | `return HTMLResponse(content=html)` |
| Download file | `return FileResponse(path="file.pdf")` |
| Redirect to OAuth | `return RedirectResponse(url=oauth_url)` |
| Stream large video | `return StreamingResponse(file_iterator)` |
| Health check endpoint | `return PlainTextResponse("OK")` |

## Key Takeaways

1. **Default is JSONResponse** - you don't need to specify it
2. **PlainTextResponse for text** - health checks, logs
3. **HTMLResponse for HTML** - dashboards, status pages
4. **RedirectResponse for redirects** - use 301 for permanent, 302 for temporary
5. **FileResponse for file downloads** - PDFs, images, documents
6. **StreamingResponse for large data** - videos, large files, real-time streams
7. **Set custom headers and cookies** - all response classes support them
8. **ORJSONResponse for performance** - faster than standard JSON
