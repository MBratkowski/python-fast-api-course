"""
Exercise 1: Write a Basic GitHub Actions Workflow

In this exercise, you'll define a GitHub Actions CI workflow as a Python dictionary.
The tests validate that your workflow has the correct structure, triggers, jobs, and steps.

Mobile analogy: This is like defining your Bitrise or Xcode Cloud pipeline steps,
but instead of clicking through a GUI, you express it as a data structure (YAML in
real life, dict here for testability).

Instructions:
1. Implement the create_ci_workflow() function
2. Return a dict representing a valid GitHub Actions workflow
3. Run the tests to verify your workflow is correct

Run: pytest 018-ci-cd-deployment/exercises/01_workflow_file.py -v
"""


# ============= TODO: Implement this function =============
# Create a GitHub Actions workflow dict with these requirements:
# - Workflow name: "CI"
# - Triggers: push to main, pull_request to main
# - One job called "test" running on ubuntu-latest
# - Steps:
#   1. Checkout code (uses: actions/checkout@v4)
#   2. Setup Python 3.12 (uses: actions/setup-python@v5, with python-version "3.12")
#   3. Install dependencies (run: pip install -r requirements.txt)
#   4. Run tests (run: pytest -v)
#
# Hints:
# - The "on" key defines triggers
# - Each step is a dict with either "uses" or "run"
# - The "with" key passes parameters to an action
# - Look at .github/workflows/ examples in the theory files

def create_ci_workflow() -> dict:
    """Return a dict representing a GitHub Actions CI workflow."""
    # TODO: Replace with your workflow definition
    return {}


# ============= TESTS (do not modify below) =============


class TestCIWorkflow:
    """Tests that validate your GitHub Actions workflow structure."""

    def setup_method(self):
        self.workflow = create_ci_workflow()

    def test_has_name(self):
        """Workflow should have a name field set to 'CI'."""
        assert "name" in self.workflow, "Workflow must have a 'name' field"
        assert self.workflow["name"] == "CI", (
            f"Workflow name should be 'CI', got: {self.workflow['name']}"
        )

    def test_has_triggers(self):
        """Workflow should have 'on' triggers defined."""
        # GitHub Actions uses 'on' but in Python dicts we accept both
        triggers = self.workflow.get("on") or self.workflow.get(True)
        assert triggers is not None, (
            "Workflow must have triggers defined under 'on' key"
        )

    def test_triggers_on_push_to_main(self):
        """Should trigger on push to main branch."""
        triggers = self.workflow.get("on") or self.workflow.get(True)
        assert "push" in triggers, "Should have a 'push' trigger"
        push_config = triggers["push"]
        assert "branches" in push_config, "Push trigger should specify branches"
        assert "main" in push_config["branches"], (
            "Push trigger should include 'main' branch"
        )

    def test_triggers_on_pull_request_to_main(self):
        """Should trigger on pull requests targeting main."""
        triggers = self.workflow.get("on") or self.workflow.get(True)
        assert "pull_request" in triggers, "Should have a 'pull_request' trigger"
        pr_config = triggers["pull_request"]
        assert "branches" in pr_config, "PR trigger should specify branches"
        assert "main" in pr_config["branches"], (
            "PR trigger should include 'main' branch"
        )

    def test_has_test_job(self):
        """Should have a 'test' job defined."""
        assert "jobs" in self.workflow, "Workflow must have a 'jobs' section"
        assert "test" in self.workflow["jobs"], (
            "Should have a job named 'test'"
        )

    def test_job_runs_on_ubuntu(self):
        """Test job should run on ubuntu-latest."""
        job = self.workflow["jobs"]["test"]
        assert "runs-on" in job, "Job must specify 'runs-on'"
        assert job["runs-on"] == "ubuntu-latest", (
            f"Job should run on 'ubuntu-latest', got: {job['runs-on']}"
        )

    def test_has_checkout_step(self):
        """Should have a checkout step using actions/checkout@v4."""
        steps = self.workflow["jobs"]["test"]["steps"]
        checkout_steps = [
            s for s in steps if s.get("uses", "").startswith("actions/checkout")
        ]
        assert len(checkout_steps) >= 1, (
            "Should have a step using actions/checkout@v4"
        )

    def test_has_setup_python_step(self):
        """Should have a setup-python step with version 3.12."""
        steps = self.workflow["jobs"]["test"]["steps"]
        python_steps = [
            s for s in steps
            if s.get("uses", "").startswith("actions/setup-python")
        ]
        assert len(python_steps) >= 1, (
            "Should have a step using actions/setup-python@v5"
        )
        python_step = python_steps[0]
        assert "with" in python_step, (
            "setup-python step should have a 'with' section"
        )
        python_version = str(python_step["with"].get("python-version", ""))
        assert "3.12" in python_version, (
            f"Python version should be '3.12', got: {python_version}"
        )

    def test_has_install_step(self):
        """Should have a step that installs dependencies."""
        steps = self.workflow["jobs"]["test"]["steps"]
        install_steps = [
            s for s in steps
            if "pip install" in s.get("run", "")
            and "requirements" in s.get("run", "")
        ]
        assert len(install_steps) >= 1, (
            "Should have a step that runs 'pip install -r requirements.txt'"
        )

    def test_has_test_step(self):
        """Should have a step that runs pytest."""
        steps = self.workflow["jobs"]["test"]["steps"]
        test_steps = [
            s for s in steps if "pytest" in s.get("run", "")
        ]
        assert len(test_steps) >= 1, (
            "Should have a step that runs pytest"
        )

    def test_steps_in_correct_order(self):
        """Steps should be in logical order: checkout, setup, install, test."""
        steps = self.workflow["jobs"]["test"]["steps"]

        checkout_idx = None
        setup_idx = None
        install_idx = None
        test_idx = None

        for i, step in enumerate(steps):
            uses = step.get("uses", "")
            run = step.get("run", "")
            if "actions/checkout" in uses and checkout_idx is None:
                checkout_idx = i
            if "actions/setup-python" in uses and setup_idx is None:
                setup_idx = i
            if "pip install" in run and install_idx is None:
                install_idx = i
            if "pytest" in run and test_idx is None:
                test_idx = i

        assert all(idx is not None for idx in [checkout_idx, setup_idx, install_idx, test_idx]), (
            "All four step types must be present"
        )
        assert checkout_idx < setup_idx < install_idx < test_idx, (
            "Steps should be ordered: checkout -> setup-python -> install -> pytest"
        )
