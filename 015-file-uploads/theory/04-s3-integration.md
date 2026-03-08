# S3 Integration

## Why This Matters

Local file storage works for development, but production systems need cloud storage. If your server dies, the files die with it. If you scale to multiple servers, each has its own files -- users might upload to server A but download from server B.

AWS S3 (Simple Storage Service) solves this: durable, scalable, globally accessible object storage. On mobile, you've used AWS Amplify Storage (iOS) or Firebase Storage (Android). S3 is what those services are built on top of.

## boto3: The AWS SDK for Python

`boto3` is the official AWS SDK for Python. It provides a high-level interface to S3.

```bash
pip install boto3
```

### Basic S3 Client Setup

```python
import boto3
from botocore.exceptions import ClientError

# Create S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id="YOUR_ACCESS_KEY",      # From environment in production
    aws_secret_access_key="YOUR_SECRET_KEY",
    region_name="us-east-1",
)

# Better: use environment variables (boto3 reads them automatically)
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
s3_client = boto3.client("s3")  # Reads credentials from environment
```

**Production configuration:**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    s3_bucket_name: str

    class Config:
        env_file = ".env"

settings = Settings()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)
```

## Uploading Files to S3

### upload_fileobj: Streaming Upload

Use `upload_fileobj` for streaming -- it reads the file in chunks without loading it entirely into memory.

```python
from fastapi import FastAPI, UploadFile, HTTPException
from uuid import uuid4
from pathlib import Path
import boto3

app = FastAPI()
BUCKET = "my-app-uploads"

s3_client = boto3.client("s3")

@app.post("/upload")
async def upload_to_s3(file: UploadFile):
    """Upload file directly to S3 (streaming)."""
    # Generate unique key
    ext = Path(file.filename).suffix.lower()
    s3_key = f"uploads/{uuid4().hex}{ext}"

    try:
        # Stream upload -- file.file is a file-like object
        s3_client.upload_fileobj(
            file.file,
            BUCKET,
            s3_key,
            ExtraArgs={
                "ContentType": file.content_type,
                "Metadata": {
                    "original-filename": file.filename,
                },
            },
        )
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

    return {
        "key": s3_key,
        "bucket": BUCKET,
        "url": f"https://{BUCKET}.s3.amazonaws.com/{s3_key}",
    }
```

### Organizing with Key Prefixes

S3 is a flat key-value store, but prefixes act like directories:

```python
from datetime import datetime
from uuid import uuid4
from pathlib import Path

def generate_s3_key(filename: str, prefix: str = "uploads") -> str:
    """Generate organized S3 key with date-based prefixing."""
    now = datetime.utcnow()
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid4().hex}{ext}"

    # Result: uploads/2026/03/a1b2c3d4.jpg
    return f"{prefix}/{now.year}/{now.month:02d}/{unique_name}"
```

**Common prefix patterns:**

```
uploads/2026/03/photo.jpg          # Date-based
users/123/avatar.jpg               # User-based
products/456/images/main.jpg       # Entity-based
temp/processing/job-789.pdf        # Temporary processing
```

## Downloading from S3

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import boto3
from botocore.exceptions import ClientError

app = FastAPI()
s3_client = boto3.client("s3")
BUCKET = "my-app-uploads"

@app.get("/files/{file_key:path}")
async def download_from_s3(file_key: str):
    """Stream a file from S3 to the client."""
    try:
        response = s3_client.get_object(Bucket=BUCKET, Key=file_key)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(404, "File not found")
        raise HTTPException(500, "Download failed")

    return StreamingResponse(
        response["Body"],
        media_type=response["ContentType"],
        headers={
            "Content-Disposition": f"attachment; filename={file_key.split('/')[-1]}",
        },
    )
```

## Bucket Configuration

```python
import boto3

s3_client = boto3.client("s3")

# Create bucket
s3_client.create_bucket(
    Bucket="my-app-uploads",
    CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
)

# Enable versioning (keep file history)
s3_client.put_bucket_versioning(
    Bucket="my-app-uploads",
    VersioningConfiguration={"Status": "Enabled"},
)

# Set lifecycle policy (auto-delete after 90 days)
s3_client.put_bucket_lifecycle_configuration(
    Bucket="my-app-uploads",
    LifecycleConfiguration={
        "Rules": [
            {
                "ID": "delete-old-uploads",
                "Status": "Enabled",
                "Filter": {"Prefix": "temp/"},
                "Expiration": {"Days": 90},
            }
        ]
    },
)
```

## S3 Upload Service Pattern

A clean service layer for S3 operations:

```python
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

class S3StorageService:
    """Service for S3 file operations."""

    def __init__(self, bucket: str, client=None):
        self.bucket = bucket
        self.client = client or boto3.client("s3")

    def _generate_key(self, filename: str, prefix: str = "uploads") -> str:
        now = datetime.utcnow()
        ext = Path(filename).suffix.lower()
        return f"{prefix}/{now.year}/{now.month:02d}/{uuid4().hex}{ext}"

    async def upload(self, file: UploadFile, prefix: str = "uploads") -> dict:
        """Upload a file to S3."""
        key = self._generate_key(file.filename, prefix)

        self.client.upload_fileobj(
            file.file,
            self.bucket,
            key,
            ExtraArgs={"ContentType": file.content_type},
        )

        return {
            "key": key,
            "url": f"https://{self.bucket}.s3.amazonaws.com/{key}",
        }

    def delete(self, key: str) -> None:
        """Delete a file from S3."""
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def exists(self, key: str) -> bool:
        """Check if a file exists in S3."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False
```

**Mobile Platform Comparison:**

| Concept | iOS (Swift) | Android (Kotlin) | Python (boto3) |
|---------|-------------|-------------------|------------------|
| Cloud storage | AWS Amplify `Storage.uploadFile` | Firebase `StorageReference.putFile` | `s3_client.upload_fileobj()` |
| Download | `Storage.downloadData` | `storageRef.getBytes()` | `s3_client.get_object()` |
| Delete | `Storage.remove` | `storageRef.delete()` | `s3_client.delete_object()` |
| Organization | Key paths | Storage paths | Key prefixes |
| Auth | Cognito/IAM | Firebase Auth | IAM credentials |

## Key Takeaways

- Use **`upload_fileobj`** for streaming uploads -- it reads in chunks, never loads entire file into memory
- Always use **environment variables** for AWS credentials, never hardcode them
- Organize S3 keys with **prefixes** (date-based, user-based, or entity-based)
- Set **Content-Type metadata** when uploading so browsers handle downloads correctly
- Use **lifecycle policies** to auto-delete temporary files
- S3 is a **flat key-value store** -- prefixes simulate directories but aren't real folders
- In exercises, we use local storage. S3 is covered here for production understanding
