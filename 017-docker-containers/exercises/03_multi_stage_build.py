"""
Exercise 3: Write a Multi-Stage Dockerfile

In this exercise, you'll define a multi-stage Dockerfile as a Python string.
The tests validate that your Dockerfile:
- Has 2+ FROM statements (multi-stage)
- Uses the AS keyword to name the builder stage
- Creates a non-root user in the runtime stage
- Uses COPY --from=builder to copy installed packages
- Uses a slim base image for the final stage

Instructions:
1. Fill in the MULTISTAGE_DOCKERFILE string with a multi-stage Dockerfile
2. Run the tests to verify your Dockerfile is correct

Run: pytest 017-docker-containers/exercises/03_multi_stage_build.py -v
"""

import re


# ============= TODO: Write your multi-stage Dockerfile =============
# Replace the empty string with a multi-stage Dockerfile:
#
# Stage 1 (builder):
# - FROM python:3.12-slim AS builder
# - Set WORKDIR
# - COPY requirements.txt
# - RUN pip install with --prefix=/install
#
# Stage 2 (runtime):
# - FROM python:3.12-slim (fresh, clean image)
# - Create a non-root user (groupadd + useradd)
# - Set WORKDIR
# - COPY --from=builder /install /usr/local
# - COPY application code
# - USER <non-root-user>
# - EXPOSE 8000
# - CMD in exec form
#
# Hints:
# - The builder stage installs deps to a custom prefix: --prefix=/install
# - The runtime stage copies ONLY the installed packages, not pip itself
# - Non-root user: RUN groupadd -r appuser && useradd -r -g appuser appuser
# - Switch user AFTER all COPY and RUN instructions

MULTISTAGE_DOCKERFILE = """\
# TODO: Write your multi-stage Dockerfile here
"""


# ============= TESTS (do not modify below) =============


def _parse_instructions(dockerfile: str) -> list[dict]:
    """Parse Dockerfile into a list of instructions."""
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


class TestMultiStageDockerfile:
    """Tests that validate your multi-stage Dockerfile."""

    def test_not_empty(self):
        """Dockerfile should not be empty or just a TODO comment."""
        content = MULTISTAGE_DOCKERFILE.strip()
        lines = [
            l for l in content.splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        assert len(lines) >= 6, (
            "Multi-stage Dockerfile should have at least 6 instructions. "
            "Replace the TODO with a real Dockerfile."
        )

    def test_has_multiple_from_statements(self):
        """Should have at least 2 FROM statements (multi-stage)."""
        instructions = _parse_instructions(MULTISTAGE_DOCKERFILE)
        from_instructions = [
            i for i in instructions if i["instruction"] == "FROM"
        ]
        assert len(from_instructions) >= 2, (
            f"Multi-stage build requires 2+ FROM statements, "
            f"found {len(from_instructions)}. "
            f"Stage 1: FROM python:3.12-slim AS builder, "
            f"Stage 2: FROM python:3.12-slim"
        )

    def test_uses_as_builder_pattern(self):
        """First stage should use AS keyword to name the builder stage."""
        instructions = _parse_instructions(MULTISTAGE_DOCKERFILE)
        from_instructions = [
            i for i in instructions if i["instruction"] == "FROM"
        ]
        first_from = from_instructions[0]["args"]
        assert re.search(r"\bAS\b", first_from, re.IGNORECASE), (
            f"First FROM should name the stage with AS: "
            f"FROM python:3.12-slim AS builder\n"
            f"Got: FROM {first_from}"
        )

    def test_uses_copy_from_builder(self):
        """Should use COPY --from=builder to copy from the builder stage."""
        instructions = _parse_instructions(MULTISTAGE_DOCKERFILE)
        copy_instructions = [
            i for i in instructions if i["instruction"] == "COPY"
        ]
        copy_from = [
            i for i in copy_instructions
            if "--from=" in i["args"].lower() or "--from=" in i["raw"].lower()
        ]
        assert len(copy_from) >= 1, (
            "Should have COPY --from=builder to copy installed packages "
            "from the builder stage to the runtime stage"
        )

    def test_creates_non_root_user(self):
        """Should create a non-root user for security."""
        content = MULTISTAGE_DOCKERFILE.lower()
        has_groupadd = "groupadd" in content
        has_useradd = "useradd" in content
        assert has_groupadd and has_useradd, (
            "Should create a non-root user with groupadd and useradd:\n"
            "RUN groupadd -r appuser && useradd -r -g appuser appuser"
        )

    def test_switches_to_non_root_user(self):
        """Should switch to non-root user with USER instruction."""
        instructions = _parse_instructions(MULTISTAGE_DOCKERFILE)
        user_instructions = [
            i for i in instructions if i["instruction"] == "USER"
        ]
        assert len(user_instructions) >= 1, (
            "Should have a USER instruction to switch to the non-root user"
        )
        # USER should not be root
        user_name = user_instructions[-1]["args"].strip()
        assert user_name.lower() != "root", (
            f"USER should be a non-root user, got: {user_name}"
        )

    def test_final_stage_uses_slim_image(self):
        """Final stage should use a slim base image."""
        instructions = _parse_instructions(MULTISTAGE_DOCKERFILE)
        from_instructions = [
            i for i in instructions if i["instruction"] == "FROM"
        ]
        last_from = from_instructions[-1]["args"].split()[0]  # Handle "AS ..."
        assert "slim" in last_from.lower() or "alpine" in last_from.lower(), (
            f"Final stage should use a slim or alpine base image, "
            f"got: {last_from}"
        )

    def test_has_exec_form_cmd(self):
        """Should use exec-form CMD in the final stage."""
        instructions = _parse_instructions(MULTISTAGE_DOCKERFILE)
        cmd_instructions = [
            i for i in instructions if i["instruction"] == "CMD"
        ]
        assert len(cmd_instructions) >= 1, "Should have a CMD instruction"
        cmd_args = cmd_instructions[-1]["args"]
        assert cmd_args.strip().startswith("["), (
            f"CMD should use exec form (JSON array), got: CMD {cmd_args}"
        )

    def test_user_comes_after_copy(self):
        """USER instruction should come after COPY instructions (need root to copy)."""
        instructions = _parse_instructions(MULTISTAGE_DOCKERFILE)

        # Find the last COPY line and the USER line
        last_copy_line = 0
        user_line = 0

        for inst in instructions:
            if inst["instruction"] == "COPY":
                last_copy_line = inst["line"]
            if inst["instruction"] == "USER":
                user_line = inst["line"]

        assert user_line > last_copy_line, (
            "USER instruction should come AFTER all COPY instructions. "
            "Root is needed to copy files; switch to non-root user afterward."
        )
