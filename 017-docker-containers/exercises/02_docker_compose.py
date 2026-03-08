"""
Exercise 2: Write a Docker Compose Configuration

In this exercise, you'll define a docker-compose.yml as a Python string.
The tests validate that your configuration properly sets up:
- Three services: api, db (PostgreSQL), and redis
- PostgreSQL healthcheck
- Proper depends_on with health conditions
- Environment variables
- Named volumes for data persistence

Instructions:
1. Fill in the COMPOSE_CONTENT string with valid docker-compose.yml content
2. Run the tests to verify your configuration

Run: pytest 017-docker-containers/exercises/02_docker_compose.py -v
"""

import yaml


# ============= TODO: Write your docker-compose.yml =============
# Replace the empty string with a complete docker-compose.yml that defines:
# - An "api" service that builds from . and maps port 8000
# - A "db" service using postgres:16-alpine with a healthcheck
# - A "redis" service using redis:7-alpine
# - The api should depend on db (service_healthy) and redis (service_started)
# - Environment variables: DATABASE_URL, REDIS_URL for the api service
# - PostgreSQL environment: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
# - Named volume "postgres_data" for PostgreSQL data persistence
#
# Use Docker Compose v2 syntax (no "version:" key needed).
#
# Hints:
# - PostgreSQL healthcheck: pg_isready -U <user> -d <dbname>
# - Service names become hostnames: db:5432, redis:6379
# - depends_on with condition requires the nested syntax

COMPOSE_CONTENT = """\
# TODO: Write your docker-compose.yml here
services: {}
"""


# ============= TESTS (do not modify below) =============


def _parse_compose(content: str) -> dict:
    """Parse docker-compose.yml content."""
    return yaml.safe_load(content)


class TestDockerCompose:
    """Tests that validate your docker-compose.yml content."""

    def test_has_services(self):
        """Should define a services section."""
        config = _parse_compose(COMPOSE_CONTENT)
        assert config is not None, "YAML content should not be empty"
        assert "services" in config, "Must have a 'services' section"
        assert isinstance(config["services"], dict), "services should be a mapping"

    def test_has_three_services(self):
        """Should define exactly three services: api, db, redis."""
        config = _parse_compose(COMPOSE_CONTENT)
        services = config.get("services", {})
        assert "api" in services, "Must have an 'api' service"
        assert "db" in services, "Must have a 'db' service"
        assert "redis" in services, "Must have a 'redis' service"

    def test_api_builds_from_dockerfile(self):
        """API service should build from current directory."""
        config = _parse_compose(COMPOSE_CONTENT)
        api = config["services"]["api"]
        assert "build" in api, (
            "API service should have a 'build' key (e.g., build: .)"
        )

    def test_api_maps_port_8000(self):
        """API service should map port 8000."""
        config = _parse_compose(COMPOSE_CONTENT)
        api = config["services"]["api"]
        assert "ports" in api, "API service should have 'ports'"
        ports = api["ports"]
        port_strings = [str(p) for p in ports]
        has_8000 = any("8000" in p for p in port_strings)
        assert has_8000, (
            f"API should map port 8000. Got ports: {port_strings}"
        )

    def test_db_uses_postgres_image(self):
        """DB service should use a PostgreSQL image."""
        config = _parse_compose(COMPOSE_CONTENT)
        db = config["services"]["db"]
        assert "image" in db, "DB service should specify an image"
        assert "postgres" in db["image"].lower(), (
            f"DB should use a postgres image, got: {db['image']}"
        )

    def test_db_has_healthcheck(self):
        """PostgreSQL service should have a healthcheck."""
        config = _parse_compose(COMPOSE_CONTENT)
        db = config["services"]["db"]
        assert "healthcheck" in db, (
            "DB service must have a healthcheck so the API can wait for it. "
            "Use pg_isready for PostgreSQL health checking."
        )
        hc = db["healthcheck"]
        assert "test" in hc, "Healthcheck must have a 'test' command"
        # Check that pg_isready is used
        test_cmd = str(hc["test"])
        assert "pg_isready" in test_cmd, (
            f"Healthcheck should use pg_isready, got: {test_cmd}"
        )

    def test_db_has_postgres_env(self):
        """PostgreSQL should have POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB."""
        config = _parse_compose(COMPOSE_CONTENT)
        db = config["services"]["db"]
        assert "environment" in db, "DB service should have environment variables"

        env = db["environment"]
        # Handle both list and dict formats
        if isinstance(env, list):
            env_str = " ".join(env)
        else:
            env_str = " ".join(str(k) for k in env.keys())

        assert "POSTGRES_USER" in env_str, "Must set POSTGRES_USER"
        assert "POSTGRES_PASSWORD" in env_str, "Must set POSTGRES_PASSWORD"
        assert "POSTGRES_DB" in env_str, "Must set POSTGRES_DB"

    def test_redis_uses_redis_image(self):
        """Redis service should use a Redis image."""
        config = _parse_compose(COMPOSE_CONTENT)
        redis_svc = config["services"]["redis"]
        assert "image" in redis_svc, "Redis service should specify an image"
        assert "redis" in redis_svc["image"].lower(), (
            f"Redis should use a redis image, got: {redis_svc['image']}"
        )

    def test_api_depends_on_db(self):
        """API should depend on db with service_healthy condition."""
        config = _parse_compose(COMPOSE_CONTENT)
        api = config["services"]["api"]
        assert "depends_on" in api, "API should have depends_on"

        depends = api["depends_on"]
        assert "db" in depends, "API should depend on 'db'"

        # Check for condition: service_healthy
        if isinstance(depends["db"], dict):
            condition = depends["db"].get("condition", "")
            assert condition == "service_healthy", (
                f"API should depend on db with condition: service_healthy, "
                f"got: {condition}"
            )
        else:
            raise AssertionError(
                "depends_on.db should use the extended syntax with "
                "'condition: service_healthy'"
            )

    def test_has_named_volumes(self):
        """Should declare named volumes for data persistence."""
        config = _parse_compose(COMPOSE_CONTENT)
        assert "volumes" in config, (
            "Must have a top-level 'volumes' section for named volumes"
        )
        volumes = config["volumes"]
        assert volumes is not None, "Volumes section should not be empty"
        # Check that postgres data volume exists
        volume_names = list(volumes.keys()) if isinstance(volumes, dict) else []
        has_postgres_vol = any("postgres" in v.lower() for v in volume_names)
        assert has_postgres_vol, (
            f"Should have a postgres data volume. Got volumes: {volume_names}"
        )

    def test_api_has_database_url(self):
        """API service should have DATABASE_URL environment variable."""
        config = _parse_compose(COMPOSE_CONTENT)
        api = config["services"]["api"]
        assert "environment" in api, "API should have environment variables"

        env = api["environment"]
        if isinstance(env, list):
            env_str = " ".join(env)
        else:
            env_str = " ".join(str(k) for k in env.keys())

        assert "DATABASE_URL" in env_str, (
            "API should have DATABASE_URL environment variable"
        )

    def test_no_version_key(self):
        """Should use Compose v2 syntax (no 'version' key needed)."""
        config = _parse_compose(COMPOSE_CONTENT)
        if "version" in config:
            # Not a hard failure, just a warning
            pass  # Compose v2 ignores the version key
