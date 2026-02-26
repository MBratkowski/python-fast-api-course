# Python Environment Setup

## Why This Matters

In mobile development, Xcode/Android Studio manages dependencies for you. In Python, you manage them yourself with **virtual environments**. Skip this, and you'll have version conflicts between projects.

## Virtual Environments

A virtual environment is an isolated Python installation for your project. Think of it like a separate "sandbox" for each project's dependencies.

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Your prompt changes to show you're in the venv
(.venv) $

# Deactivate when done
deactivate
```

## Package Management

`pip` is Python's package manager (like CocoaPods, Gradle, or pub).

```bash
# Install a package
pip install fastapi

# Install specific version
pip install fastapi==0.109.0

# Install from requirements file
pip install -r requirements.txt

# Save current packages to file
pip freeze > requirements.txt
```

## Project Structure for APIs

```
my-api/
├── .venv/              # Virtual environment (don't commit)
├── src/
│   ├── __init__.py     # Makes it a Python package
│   ├── main.py         # Entry point
│   ├── api/
│   │   └── routes.py
│   ├── models/
│   │   └── user.py
│   └── services/
│       └── user_service.py
├── tests/
│   └── test_api.py
├── requirements.txt    # Dependencies
├── .gitignore
└── .env               # Environment variables (don't commit)
```

## The `__init__.py` File

In Python, a directory with `__init__.py` becomes a **package** (importable module).

```python
# src/models/__init__.py
from .user import User
from .post import Post

# Now you can do:
from src.models import User, Post
```

## Environment Variables

Use `.env` files for configuration (API keys, database URLs):

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
DEBUG=true
```

```python
# Load with python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")
```

## Key Takeaways

1. **Always use virtual environments** - one per project
2. **requirements.txt** = your Podfile/build.gradle
3. **`__init__.py`** makes directories importable
4. **`.env`** for secrets (add to .gitignore!)
