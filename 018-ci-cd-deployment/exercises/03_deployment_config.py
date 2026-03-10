"""
Exercise 3: Create a Docker Image Build and Push Workflow

In this exercise, you'll define a GitHub Actions workflow that builds a Docker image
and pushes it to a container registry.

Mobile analogy: This is like configuring App Store Connect deployment in Xcode Cloud.
When you push to main, Xcode Cloud archives your app and uploads it to App Store Connect.
Here, when you push to main, GitHub Actions builds your Docker image and pushes it to
Docker Hub. Same concept, different artifact.

Instructions:
1. Implement the create_docker_build_workflow() function
2. Return a dict representing a Docker build and push workflow
3. Run the tests to verify your workflow is correct

Run: pytest 018-ci-cd-deployment/exercises/03_deployment_config.py -v
"""


# ============= TODO: Implement this function =============
# Create a GitHub Actions workflow dict with these requirements:
# - Workflow name: "Build and Push"
# - Trigger: push to main ONLY (no pull_request trigger)
# - One job called "build" running on ubuntu-latest
# - Steps:
#   1. Checkout code (uses: actions/checkout@v4)
#   2. Docker login (uses: docker/login-action@v3)
#      - with: username=${{ secrets.DOCKER_USERNAME }},
#              password=${{ secrets.DOCKER_TOKEN }}
#   3. Build and push (uses: docker/build-push-action@v5)
#      - with: context=., push=true,
#              tags=myuser/myapp:latest
#
# Hints:
# - Only push trigger (no pull_request) -- you don't want to push images for PRs
# - docker/login-action requires "username" and "password" in "with"
# - docker/build-push-action requires "push" (boolean) and "tags" in "with"
# - Use ${{ secrets.NAME }} syntax for secret references (as strings in Python)

def create_docker_build_workflow() -> dict:
    """Return a dict representing a Docker build and push workflow."""
    # TODO: Replace with your workflow definition
    return {}


# ============= TESTS (do not modify below) =============


class TestDockerBuildWorkflow:
    """Tests that validate your Docker build and push workflow."""

    def setup_method(self):
        self.workflow = create_docker_build_workflow()

    def test_has_name(self):
        """Workflow should have a name."""
        assert "name" in self.workflow, "Workflow must have a 'name' field"

    def test_triggers_on_push_only(self):
        """Should trigger on push only, NOT pull_request."""
        triggers = self.workflow.get("on") or self.workflow.get(True)
        assert triggers is not None, "Workflow must have triggers"
        assert "push" in triggers, "Should trigger on push"
        assert "pull_request" not in triggers, (
            "Should NOT trigger on pull_request -- "
            "you don't want to build and push Docker images for every PR"
        )

    def test_push_trigger_targets_main(self):
        """Push trigger should target the main branch."""
        triggers = self.workflow.get("on") or self.workflow.get(True)
        push_config = triggers["push"]
        assert "branches" in push_config, "Push trigger should specify branches"
        assert "main" in push_config["branches"], (
            "Push trigger should target 'main' branch"
        )

    def test_has_build_job(self):
        """Should have a 'build' job."""
        assert "jobs" in self.workflow, "Workflow must have 'jobs'"
        assert "build" in self.workflow["jobs"], "Should have a 'build' job"

    def test_has_checkout_step(self):
        """Should have a checkout step."""
        steps = self.workflow["jobs"]["build"]["steps"]
        checkout_steps = [
            s for s in steps
            if s.get("uses", "").startswith("actions/checkout")
        ]
        assert len(checkout_steps) >= 1, (
            "Should have a step using actions/checkout"
        )

    def test_has_docker_login_step(self):
        """Should have a Docker login step."""
        steps = self.workflow["jobs"]["build"]["steps"]
        login_steps = [
            s for s in steps
            if "docker/login-action" in s.get("uses", "")
        ]
        assert len(login_steps) >= 1, (
            "Should have a step using docker/login-action"
        )

    def test_docker_login_uses_secrets(self):
        """Docker login should use secrets for credentials."""
        steps = self.workflow["jobs"]["build"]["steps"]
        login_steps = [
            s for s in steps
            if "docker/login-action" in s.get("uses", "")
        ]
        login_step = login_steps[0]
        assert "with" in login_step, (
            "Docker login step must have a 'with' section"
        )
        with_config = login_step["with"]
        assert "username" in with_config, (
            "Docker login must include 'username' in 'with'"
        )
        assert "password" in with_config, (
            "Docker login must include 'password' in 'with'"
        )
        username = str(with_config["username"])
        password = str(with_config["password"])
        assert "secrets" in username.lower() or "secrets" in username, (
            f"Username should reference a secret (secrets.DOCKER_USERNAME), got: {username}"
        )
        assert "secrets" in password.lower() or "secrets" in password, (
            f"Password should reference a secret (secrets.DOCKER_TOKEN), got: {password}"
        )

    def test_has_build_push_step(self):
        """Should have a Docker build and push step."""
        steps = self.workflow["jobs"]["build"]["steps"]
        build_steps = [
            s for s in steps
            if "docker/build-push-action" in s.get("uses", "")
        ]
        assert len(build_steps) >= 1, (
            "Should have a step using docker/build-push-action"
        )

    def test_build_push_has_push_enabled(self):
        """Build and push step should have push set to true."""
        steps = self.workflow["jobs"]["build"]["steps"]
        build_steps = [
            s for s in steps
            if "docker/build-push-action" in s.get("uses", "")
        ]
        build_step = build_steps[0]
        assert "with" in build_step, (
            "Build-push step must have a 'with' section"
        )
        with_config = build_step["with"]
        # Accept both boolean True and string "true"
        push_value = with_config.get("push")
        assert push_value is True or str(push_value).lower() == "true", (
            f"Build-push step should have push=true, got: {push_value}"
        )

    def test_build_push_has_tags(self):
        """Build and push step should specify image tags."""
        steps = self.workflow["jobs"]["build"]["steps"]
        build_steps = [
            s for s in steps
            if "docker/build-push-action" in s.get("uses", "")
        ]
        build_step = build_steps[0]
        with_config = build_step.get("with", {})
        assert "tags" in with_config, (
            "Build-push step should specify 'tags' for the Docker image"
        )
        tags = str(with_config["tags"])
        assert "/" in tags, (
            f"Tags should include a repository name (user/image:tag), got: {tags}"
        )

    def test_build_push_has_context(self):
        """Build and push step should specify build context."""
        steps = self.workflow["jobs"]["build"]["steps"]
        build_steps = [
            s for s in steps
            if "docker/build-push-action" in s.get("uses", "")
        ]
        build_step = build_steps[0]
        with_config = build_step.get("with", {})
        assert "context" in with_config, (
            "Build-push step should specify 'context' (usually '.')"
        )

    def test_steps_in_correct_order(self):
        """Steps should be ordered: checkout, login, build-push."""
        steps = self.workflow["jobs"]["build"]["steps"]

        checkout_idx = None
        login_idx = None
        build_idx = None

        for i, step in enumerate(steps):
            uses = step.get("uses", "")
            if "actions/checkout" in uses and checkout_idx is None:
                checkout_idx = i
            if "docker/login-action" in uses and login_idx is None:
                login_idx = i
            if "docker/build-push-action" in uses and build_idx is None:
                build_idx = i

        assert all(idx is not None for idx in [checkout_idx, login_idx, build_idx]), (
            "All three steps must be present: checkout, login, build-push"
        )
        assert checkout_idx < login_idx < build_idx, (
            "Steps should be ordered: checkout -> docker login -> build and push"
        )
