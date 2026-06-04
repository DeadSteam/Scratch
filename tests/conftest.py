"""Shared pytest fixtures.

The default profile is "unit" — tests run without real DB/Redis/Tempo.
Integration tests must be marked with ``@pytest.mark.integration`` and
will be wired up to testcontainers in a follow-up step.

Seeding env vars here BEFORE any ``src.*`` import is critical: Settings
is built from os.environ when the first import touches it, so a missing
SECRET_KEY/DATABASE_URL turns into a collection-time crash.
"""

from __future__ import annotations

import os

import pytest


def _seed_test_env() -> None:
    defaults = {
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "SECRET_KEY": "unit-test-secret-key-at-least-32-characters-long",
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
        "USERS_DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5433/test",
        "KNOWLEDGE_DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5434/test",
        "REDIS_URL": "redis://localhost:6379/0",
        "ADMIN_PASSWORD": "test-admin-password",
        "METRICS_USERNAME": "prometheus",
        "METRICS_PASSWORD": "test-metrics-password",
        "CORS_ORIGINS": '["http://test"]',
        # Don't talk to Tempo from unit tests — every test would otherwise
        # log gRPC UNAVAILABLE on teardown.
        "TRACING_ENABLED": "false",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)


_seed_test_env()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def _reset_settings_cache():
    """Tests that mutate env vars need the @lru_cache'd Settings to refresh."""
    from src.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
