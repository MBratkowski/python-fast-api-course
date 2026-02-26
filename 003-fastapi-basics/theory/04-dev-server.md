# Running the Development Server

## Why This Matters

This is like running `flutter run` or hitting "Run" in Xcode. You'll use Uvicorn to start your API server with hot-reload during development.

## What is Uvicorn?

Uvicorn is an ASGI server that runs your FastAPI application. Think of it as:
- The runtime that executes your code
- Like the iOS Simulator or Android Emulator for your API
- Handles incoming HTTP requests and passes them to FastAPI

**ASGI** (Asynchronous Server Gateway Interface) is Python's standard for async web servers - it's what enables FastAPI's async capabilities.

## Basic Command

```bash
uvicorn main:app
```

Breaking down `main:app`:
- `main` - Python file name (main.py)
- `:` - Separator
- `app` - Variable name of your FastAPI instance

```python
# main.py
from fastapi import FastAPI

app = FastAPI()  # ← This is what "app" refers to
```

**Mobile analogy**: Like specifying the target to run in Xcode (MyApp scheme).

## Development Mode with Auto-Reload

```bash
uvicorn main:app --reload
```

The `--reload` flag:
- Watches your Python files for changes
- Automatically restarts the server when you save
- Like Xcode's hot reload or Flutter's hot restart

**Don't use --reload in production** - it's only for development.

## Specifying Port

```bash
uvicorn main:app --reload --port 8080
```

Default port is 8000. Change it if:
- Port 8000 is already in use
- You want to run multiple APIs simultaneously
- You need a specific port for testing

## Binding to All Interfaces

```bash
uvicorn main:app --reload --host 0.0.0.0
```

- Default: `127.0.0.1` (localhost only)
- `0.0.0.0`: Accessible from other devices on network
- Useful for testing on physical mobile devices

**Mobile testing setup**:
```bash
# Start server accessible on network
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Find your machine's IP (macOS)
ifconfig | grep "inet "

# Use in mobile app
http://192.168.1.100:8000/api/users
```

## Server Output

When you start Uvicorn, you'll see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**When you make a request**:
```
INFO:     127.0.0.1:54321 - "GET /users HTTP/1.1" 200 OK
```

Shows: client IP, HTTP method, path, status code.

## Hot Reload in Action

1. Save your Python file
2. See in terminal:
   ```
   INFO:     Detected file change in 'main.py'. Reloading...
   INFO:     Shutting down
   INFO:     Application startup complete.
   ```
3. Server restarts automatically
4. Your changes are live

**Mobile analogy**: Like saving a Swift file and seeing UI update immediately.

## Stopping the Server

Press `Ctrl+C` in terminal:
```
^C
INFO:     Shutting down
INFO:     Finished server process [12346]
INFO:     Stopping reloader process [12345]
```

## Running from Different Directories

**If main.py is in src/ directory**:
```bash
uvicorn src.main:app --reload
```

**If using a different module structure**:
```bash
uvicorn api.main:app --reload
```

The path before `:app` follows Python import syntax.

## Environment Variables

Set configuration via environment variables:

```bash
# macOS/Linux
export DATABASE_URL=postgresql://localhost/mydb
uvicorn main:app --reload

# Windows (Command Prompt)
set DATABASE_URL=postgresql://localhost/mydb
uvicorn main:app --reload

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://localhost/mydb"
uvicorn main:app --reload
```

Or use a `.env` file:
```bash
# .env
DATABASE_URL=postgresql://localhost/mydb
DEBUG=true
```

Load with python-dotenv:
```python
# main.py
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
```

## Production vs Development

**Development** (what you're doing now):
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- Hot reload enabled
- Detailed logging
- Single worker
- Localhost only

**Production** (later):
```bash
uvicorn main:app --host 0.0.0.0 --port 80 --workers 4
```
- No reload
- Multiple workers for concurrency
- Exposed on network
- Production logging

## Accessing Your API

After starting the server:

**Root endpoint**:
```
http://localhost:8000/
```

**Specific endpoints**:
```
http://localhost:8000/users
http://localhost:8000/users/123
```

**Interactive documentation**:
```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
http://localhost:8000/openapi.json  # OpenAPI schema
```

**Mobile analogy**: Like your base URL in URLSession or Retrofit configuration.

## Testing with curl

```bash
# GET request
curl http://localhost:8000/users

# GET with query params
curl "http://localhost:8000/items?skip=10&limit=20"

# POST with JSON
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# DELETE
curl -X DELETE http://localhost:8000/users/123
```

Or use the interactive docs at `/docs` - easier than curl!

## Common Issues

**Port already in use**:
```
ERROR: [Errno 48] Address already in use
```
Solution: Change port or kill existing process
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

**Module not found**:
```
ERROR: Error loading ASGI app. Could not import module "main"
```
Solution: Check you're in correct directory and file exists
```bash
ls main.py  # Should exist
```

**No app instance**:
```
ERROR: Error loading ASGI app. Attribute "app" not found in module "main"
```
Solution: Ensure `app = FastAPI()` exists in your file

## Key Takeaways

1. Use `uvicorn main:app --reload` to start development server
2. `--reload` enables hot-reload (development only)
3. `--port` changes port (default 8000)
4. `--host 0.0.0.0` allows network access (for mobile device testing)
5. Save files to trigger auto-restart
6. Visit `/docs` for interactive API testing
7. Use Ctrl+C to stop server
8. Server output shows request logs (method, path, status)
