"""
Exercise 1: Write a Dockerfile for a FastAPI Application

In this exercise, you'll define Dockerfile content as a Python string.
The tests validate that your Dockerfile follows best practices:
- Uses python:3.12-slim as base image
- Sets a WORKDIR
- Copies requirements.txt before application code (layer caching)
- Uses exec-form CMD (not shell form)
- Exposes port 8000

Instructions:
1. Fill in the DOCKERFILE_CONTENT string with a valid Dockerfile
2. Run the tests to verify your Dockerfile is correct

Run: pytest 017-docker-containers/exercises/01_dockerfile.py -v
"""

import re


# ============= TODO: Write your Dockerfile =============
# Replace the empty string with a complete Dockerfile for a FastAPI app.
# Requirements:
# - Use python:3.12-slim as the base image
# - Set WORKDIR to /code
# - Copy requirements.txt FIRST (for layer caching)
# - Run pip install with --no-cache-dir
# - Copy application code AFTER installing dependencies
# - EXPOSE port 8000
# - Use exec-form CMD to run: fastapi run app/main.py --port 8000
#
# Hints:
# - Exec form looks like: CMD ["command", "arg1", "arg2"]
# - Shell form looks like: CMD command arg1 arg2 (DON'T use this)
# - Layer caching: things that change rarely go FIRST

DOCKERFILE_CONTENT = """\
# TODO: Write your Dockerfile here
"""


# ============= TESTS (do not modify below) =============


def _parse_instructions(dockerfile: str) -> list[dict]:
    """Parse Dockerfile into a list of instructions with line numbers."""
    instructions = []
    for i, line in enumerate(dockerfile.strip().splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split(None, 1)
        if parts:
            instructions.append({
                "instruction": parts[0].upper(),
                "args": parts[1] if len(parts) > 1 else "",
                "line": i,
                "raw": stripped,
            })
    return instructions


class TestDockerfile:
    """Tests that validate your Dockerfile content."""

    def test_not_empty(self):
        """Dockerfile should not be empty or just a TODO comment."""
        content = DOCKERFILE_CONTENT.strip()
        lines = [
            l for l in content.splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        assert len(lines) >= 4, (
            "Dockerfile should have at least 4 instructions. "
            "Replace the TODO with a real Dockerfile."
        )

    def test_uses_python_slim_base(self):
        """Should use python:3.12-slim as the base image."""
        instructions = _parse_instructions(DOCKERFILE_CONTENT)
        from_instructions = [i for i in instructions if i["instruction"] == "FROM"]
        assert len(from_instructions) >= 1, "Dockerfile must have a FROM instruction"
        base_image = from_instructions[0]["args"].split()[0]  # Handle "AS builder"
        assert "python" in base_image.lower(), (
            f"Base image should be python-based, got: {base_image}"
        )
        assert "slim" in base_image.lower(), (
            f"Use python:3.12-slim (not full or alpine), got: {base_image}"
        )

    def test_has_workdir(self):
        """Should set a WORKDIR."""
        instructions = _parse_instructions(DOCKERFILE_CONTENT)
        workdir_instructions = [
            i for i in instructions if i["instruction"] == "WORKDIR"
        ]
        assert len(workdir_instructions) >= 1, (
            "Dockerfile must have a WORKDIR instruction"
        )

    def test_copies_requirements_before_app_code(self):
        """Should copy requirements.txt BEFORE application code for layer caching."""
        instructions = _parse_instructions(DOCKERFILE_CONTENT)
        copy_instructions = [
            i for i in instructions if i["instruction"] == "COPY"
        ]
        assert len(copy_instructions) >= 2, (
            "Should have at least 2 COPY instructions: "
            "one for requirements.txt, one for app code"
        )

        # Find the COPY that includes requirements.txt
        req_copy_idx = None
        for idx, ci in enumerate(copy_instructions):
            if "requirements" in ci["args"].lower():
                req_copy_idx = idx
                break

        assert req_copy_idx is not None, (
            "One COPY instruction should copy requirements.txt"
        )
        assert req_copy_idx == 0, (
            "requirements.txt should be copied BEFORE application code "
            "(for Docker layer caching). The first COPY should be requirements.txt."
        )

    def test_has_pip_install(self):
        """Should run pip install."""
        instructions = _parse_instructions(DOCKERFILE_CONTENT)
        run_instructions = [i for i in instructions if i["instruction"] == "RUN"]
        pip_install = [
            i for i in run_instructions
            if "pip install" in i["args"] or "pip3 install" in i["args"]
        ]
        assert len(pip_install) >= 1, (
            "Should have a RUN instruction that runs pip install"
        )

    def test_pip_install_after_requirements_copy(self):
        """pip install should come after copying requirements.txt."""
        instructions = _parse_instructions(DOCKERFILE_CONTENT)

        req_copy_line = None
        pip_line = None

        for inst in instructions:
            if inst["instruction"] == "COPY" and "requirements" in inst["args"].lower():
                req_copy_line = inst["line"]
            if inst["instruction"] == "RUN" and "pip install" in inst["args"]:
                pip_line = inst["line"]

        assert req_copy_line is not None, "Should COPY requirements.txt"
        assert pip_line is not None, "Should RUN pip install"
        assert pip_line > req_copy_line, (
            "pip install should come AFTER copying requirements.txt"
        )

    def test_uses_exec_form_cmd(self):
        """Should use exec-form CMD (JSON array), not shell form."""
        instructions = _parse_instructions(DOCKERFILE_CONTENT)
        cmd_instructions = [i for i in instructions if i["instruction"] == "CMD"]
        assert len(cmd_instructions) >= 1, "Dockerfile must have a CMD instruction"

        cmd_args = cmd_instructions[-1]["args"]  # Last CMD wins
        assert cmd_args.strip().startswith("["), (
            f"CMD should use exec form (JSON array): CMD [\"command\", \"args\"]\n"
            f"Got shell form: CMD {cmd_args}\n"
            f"Shell form prevents graceful shutdown!"
        )

    def test_exposes_port_8000(self):
        """Should expose port 8000."""
        instructions = _parse_instructions(DOCKERFILE_CONTENT)
        expose_instructions = [
            i for i in instructions if i["instruction"] == "EXPOSE"
        ]
        assert len(expose_instructions) >= 1, "Should have an EXPOSE instruction"
        assert "8000" in expose_instructions[0]["args"], (
            f"Should expose port 8000, got: EXPOSE {expose_instructions[0]['args']}"
        )

    def test_no_deprecated_base_image(self):
        """Should NOT use the deprecated tiangolo/uvicorn-gunicorn-fastapi image."""
        assert "tiangolo" not in DOCKERFILE_CONTENT.lower(), (
            "Do not use tiangolo/uvicorn-gunicorn-fastapi -- it is deprecated. "
            "Use python:3.12-slim instead."
        )
