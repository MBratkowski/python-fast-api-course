"""
Exercise 3: Storage Patterns

Implement file storage utilities: UUID-prefixed unique filenames,
date-based directory organization, and file cleanup for old files.

All exercises use temporary directories -- no cloud dependencies.

Run: pytest 015-file-uploads/exercises/03_storage_patterns.py -v
"""

import os
import time
import tempfile
from pathlib import Path
from uuid import uuid4
from datetime import datetime

import pytest


# ============= TODO: Exercise 3.1 =============
# Create a function save_with_unique_name that:
# - Takes: content (bytes), original_filename (str), directory (Path)
# - Generates a unique filename: UUID hex + original extension
#   e.g., "photo.jpg" -> "a1b2c3d4e5f6...hex.jpg"
# - Saves the content to directory / unique_filename
# - Returns the unique filename (str)
#
# Hints:
# - Use uuid4().hex for the UUID part
# - Use Path(original_filename).suffix for the extension
# - Use Path.write_bytes() to save

def save_with_unique_name(
    content: bytes,
    original_filename: str,
    directory: Path,
) -> str:
    """Save file with UUID-prefixed unique filename. Returns the new filename."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.2 =============
# Create a function save_organized_by_date that:
# - Takes: content (bytes), original_filename (str), base_directory (Path)
# - Creates a subdirectory structure: base_directory / YYYY / MM /
#   e.g., uploads/2026/03/
# - Generates a unique filename (same as 3.1)
# - Saves the file in the date-based subdirectory
# - Returns the relative path from base_directory (e.g., "2026/03/abc123.jpg")
#
# Hints:
# - Use datetime.utcnow() for current date
# - Use f"{now.year}/{now.month:02d}" for the path
# - Use Path.mkdir(parents=True, exist_ok=True) to create nested dirs

def save_organized_by_date(
    content: bytes,
    original_filename: str,
    base_directory: Path,
) -> str:
    """Save file in date-based directory structure. Returns relative path."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 3.3 =============
# Create a function cleanup_old_files that:
# - Takes: directory (Path), max_age_seconds (int)
# - Iterates over all files in the directory (not subdirectories)
# - Checks each file's modification time (Path.stat().st_mtime)
# - Deletes files older than max_age_seconds
# - Returns the number of files deleted (int)
#
# Hints:
# - Use time.time() for current timestamp
# - Use Path.iterdir() to list files
# - Use Path.is_file() to skip directories
# - Use Path.unlink() to delete

def cleanup_old_files(directory: Path, max_age_seconds: int) -> int:
    """Delete files older than max_age_seconds. Returns count of deleted files."""
    # TODO: Implement
    pass


# ============= TESTS (DO NOT MODIFY) =============


class TestUniqueFilename:
    """Tests for Exercise 3.1: UUID-prefixed unique filenames."""

    def test_returns_string(self, tmp_path):
        result = save_with_unique_name(b"data", "test.txt", tmp_path)
        assert isinstance(result, str)

    def test_preserves_extension(self, tmp_path):
        result = save_with_unique_name(b"data", "photo.jpg", tmp_path)
        assert result.endswith(".jpg")

    def test_preserves_png_extension(self, tmp_path):
        result = save_with_unique_name(b"data", "image.png", tmp_path)
        assert result.endswith(".png")

    def test_generates_unique_names(self, tmp_path):
        name1 = save_with_unique_name(b"data1", "file.txt", tmp_path)
        name2 = save_with_unique_name(b"data2", "file.txt", tmp_path)
        assert name1 != name2  # Same input filename, different output

    def test_file_is_saved(self, tmp_path):
        name = save_with_unique_name(b"hello world", "test.txt", tmp_path)
        saved_path = tmp_path / name
        assert saved_path.exists()
        assert saved_path.read_bytes() == b"hello world"

    def test_name_is_uuid_format(self, tmp_path):
        name = save_with_unique_name(b"data", "test.txt", tmp_path)
        stem = Path(name).stem  # Remove extension
        assert len(stem) == 32  # UUID hex is 32 chars


class TestDateOrganization:
    """Tests for Exercise 3.2: Date-based directory organization."""

    def test_returns_relative_path(self, tmp_path):
        result = save_organized_by_date(b"data", "test.txt", tmp_path)
        assert isinstance(result, str)
        # Should contain year/month pattern
        parts = result.split("/")
        assert len(parts) == 3  # YYYY/MM/filename

    def test_creates_date_directories(self, tmp_path):
        save_organized_by_date(b"data", "test.txt", tmp_path)
        now = datetime.utcnow()
        year_dir = tmp_path / str(now.year)
        month_dir = year_dir / f"{now.month:02d}"
        assert year_dir.is_dir()
        assert month_dir.is_dir()

    def test_file_exists_at_path(self, tmp_path):
        relative_path = save_organized_by_date(b"content", "doc.pdf", tmp_path)
        full_path = tmp_path / relative_path
        assert full_path.exists()
        assert full_path.read_bytes() == b"content"

    def test_preserves_extension(self, tmp_path):
        result = save_organized_by_date(b"data", "image.png", tmp_path)
        assert result.endswith(".png")

    def test_unique_names_in_same_directory(self, tmp_path):
        path1 = save_organized_by_date(b"data1", "file.txt", tmp_path)
        path2 = save_organized_by_date(b"data2", "file.txt", tmp_path)
        assert path1 != path2


class TestCleanup:
    """Tests for Exercise 3.3: File cleanup."""

    def test_deletes_old_files(self, tmp_path):
        # Create a file and set its mtime to 100 seconds ago
        old_file = tmp_path / "old.txt"
        old_file.write_text("old content")
        old_mtime = time.time() - 100
        os.utime(old_file, (old_mtime, old_mtime))

        deleted = cleanup_old_files(tmp_path, max_age_seconds=50)
        assert deleted == 1
        assert not old_file.exists()

    def test_keeps_recent_files(self, tmp_path):
        # Create a recent file
        recent_file = tmp_path / "recent.txt"
        recent_file.write_text("recent content")

        deleted = cleanup_old_files(tmp_path, max_age_seconds=60)
        assert deleted == 0
        assert recent_file.exists()

    def test_mixed_old_and_new(self, tmp_path):
        # Create old file
        old_file = tmp_path / "old.txt"
        old_file.write_text("old")
        old_mtime = time.time() - 200
        os.utime(old_file, (old_mtime, old_mtime))

        # Create recent file
        new_file = tmp_path / "new.txt"
        new_file.write_text("new")

        deleted = cleanup_old_files(tmp_path, max_age_seconds=100)
        assert deleted == 1
        assert not old_file.exists()
        assert new_file.exists()

    def test_returns_count(self, tmp_path):
        # Create 3 old files
        for i in range(3):
            f = tmp_path / f"old_{i}.txt"
            f.write_text(f"old {i}")
            old_mtime = time.time() - 300
            os.utime(f, (old_mtime, old_mtime))

        deleted = cleanup_old_files(tmp_path, max_age_seconds=100)
        assert deleted == 3

    def test_skips_directories(self, tmp_path):
        # Create a subdirectory (should not be deleted)
        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()

        deleted = cleanup_old_files(tmp_path, max_age_seconds=0)
        assert deleted == 0
        assert sub_dir.exists()

    def test_empty_directory(self, tmp_path):
        deleted = cleanup_old_files(tmp_path, max_age_seconds=60)
        assert deleted == 0
