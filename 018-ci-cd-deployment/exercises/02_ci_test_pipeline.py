"""
Exercise 2: Create a CI Pipeline with PostgreSQL Service Container

In this exercise, you'll define a GitHub Actions workflow that runs tests against
a real PostgreSQL database using a service container.

Mobile analogy: On iOS, you configure a test scheme to use a specific simulator.
Here, you configure a CI job to spin up a real PostgreSQL database alongside your
test runner. It's the backend equivalent of choosing "iPhone 16 Pro, iOS 18" as
your test destination -- except instead of a simulator, you get a real database.

Instructions:
1. Implement the create_test_pipeline_with_db() function
2. Return a dict representing a workflow with PostgreSQL service container
3. Run the tests to verify your pipeline is correct

Run: pytest 018-ci-cd-deployment/exercises/02_ci_test_pipeline.py -v
"""


# ============= TODO: Implement this function =============
# Create a GitHub Actions workflow dict with these requirements:
# - Workflow name: "CI Tests"
# - Triggers: push to main, pull_request to main
# - One job called "test" running on ubuntu-latest
# - Services: PostgreSQL 16 with:
#   - Image: postgres:16
#   - Environment: POSTGRES_PASSWORD=testpass, POSTGRES_DB=testdb
#   - Ports: 5432:5432
#   - Health check options: --health-cmd pg_isready, --health-interval 10s,
#     --health-timeout 5s, --health-retries 5
# - Steps: checkout, setup-python 3.12, install deps, run pytest
# - The pytest step should have a DATABASE_URL env var pointing to:
#   postgresql://postgres:testpass@localhost:5432/testdb
#
# Hints:
# - Services are defined at the job level, not the step level
# - The "options" field is a string with Docker health check flags
# - Ports are strings like "5432:5432"
# - Step-level "env" sets environment variables for that step only

def create_test_pipeline_with_db() -> dict:
    """Return a dict representing a CI workflow with PostgreSQL service."""
    # TODO: Replace with your workflow definition
    return {}


# ============= TESTS (do not modify below) =============


class TestCITestPipeline:
    """Tests that validate your CI pipeline with PostgreSQL."""

    def setup_method(self):
        self.workflow = create_test_pipeline_with_db()

    def test_has_name(self):
        """Workflow should have a name."""
        assert "name" in self.workflow, "Workflow must have a 'name' field"

    def test_has_test_job(self):
        """Should have a 'test' job."""
        assert "jobs" in self.workflow, "Workflow must have 'jobs'"
        assert "test" in self.workflow["jobs"], "Should have a 'test' job"

    def test_has_services_block(self):
        """Test job should have a services block for containers."""
        job = self.workflow["jobs"]["test"]
        assert "services" in job, (
            "Test job should have a 'services' section for database containers"
        )

    def test_has_postgres_service(self):
        """Should define a PostgreSQL service container."""
        services = self.workflow["jobs"]["test"]["services"]
        assert "postgres" in services, (
            "Should have a service named 'postgres'"
        )

    def test_postgres_image(self):
        """PostgreSQL service should use postgres:16 image."""
        postgres = self.workflow["jobs"]["test"]["services"]["postgres"]
        assert "image" in postgres, "Postgres service must specify an image"
        assert "postgres" in postgres["image"], (
            f"Should use a postgres image, got: {postgres['image']}"
        )

    def test_postgres_environment(self):
        """PostgreSQL should have password and database configured."""
        postgres = self.workflow["jobs"]["test"]["services"]["postgres"]
        env = postgres.get("env", {})
        assert "POSTGRES_PASSWORD" in env, (
            "PostgreSQL service needs POSTGRES_PASSWORD in env"
        )
        assert "POSTGRES_DB" in env, (
            "PostgreSQL service needs POSTGRES_DB in env"
        )

    def test_postgres_port_mapping(self):
        """PostgreSQL should map port 5432."""
        postgres = self.workflow["jobs"]["test"]["services"]["postgres"]
        assert "ports" in postgres, "PostgreSQL service should map ports"
        ports = postgres["ports"]
        port_strings = [str(p) for p in ports]
        has_5432 = any("5432" in p for p in port_strings)
        assert has_5432, (
            f"Should map port 5432, got ports: {ports}"
        )

    def test_postgres_health_check(self):
        """PostgreSQL should have health check options."""
        postgres = self.workflow["jobs"]["test"]["services"]["postgres"]
        assert "options" in postgres, (
            "PostgreSQL service should have health check 'options'"
        )
        options = postgres["options"]
        assert "health-cmd" in options, (
            "Health check options should include --health-cmd"
        )
        assert "pg_isready" in options, (
            "Health check command should be pg_isready"
        )

    def test_has_database_url_env(self):
        """Test step should have DATABASE_URL environment variable."""
        steps = self.workflow["jobs"]["test"]["steps"]
        db_url_found = False
        for step in steps:
            env = step.get("env", {})
            if "DATABASE_URL" in env:
                db_url_found = True
                url = env["DATABASE_URL"]
                assert "postgresql" in url, (
                    f"DATABASE_URL should be a PostgreSQL URL, got: {url}"
                )
                assert "localhost" in url or "postgres" in url, (
                    f"DATABASE_URL should connect to localhost or postgres host, got: {url}"
                )
                assert "5432" in url, (
                    f"DATABASE_URL should use port 5432, got: {url}"
                )
                break

        assert db_url_found, (
            "At least one step should have a DATABASE_URL environment variable"
        )

    def test_has_pytest_step(self):
        """Should have a step that runs pytest."""
        steps = self.workflow["jobs"]["test"]["steps"]
        test_steps = [
            s for s in steps if "pytest" in s.get("run", "")
        ]
        assert len(test_steps) >= 1, (
            "Should have a step that runs pytest"
        )

    def test_has_checkout_step(self):
        """Should have a checkout step."""
        steps = self.workflow["jobs"]["test"]["steps"]
        checkout_steps = [
            s for s in steps
            if s.get("uses", "").startswith("actions/checkout")
        ]
        assert len(checkout_steps) >= 1, (
            "Should have a step using actions/checkout"
        )

    def test_health_check_has_retries(self):
        """Health check should have retry configuration."""
        postgres = self.workflow["jobs"]["test"]["services"]["postgres"]
        options = postgres.get("options", "")
        assert "health-retries" in options, (
            "Health check should include --health-retries to avoid flaky CI"
        )
        assert "health-interval" in options, (
            "Health check should include --health-interval"
        )
