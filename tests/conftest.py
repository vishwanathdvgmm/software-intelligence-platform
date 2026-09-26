"""Pytest configuration and shared fixtures for the SIP test suite."""

from __future__ import annotations

import os

import pytest

from sip.core.config import get_settings
from sip.core.logging import clear_request_context, configure_logging

# ─── Session-level setup ───────────────────────────────────────────────────


def pytest_configure(config: pytest.Config) -> None:
    """Set the environment to testing before any test runs."""
    os.environ.setdefault("SIP_ENV", "testing")
    os.environ.setdefault("SIP_LOG_FORMAT", "console")
    os.environ.setdefault("SIP_LOG_LEVEL", "DEBUG")


# ─── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_settings_cache() -> None:  # type: ignore[return]
    """Clear the settings singleton cache before each test.

    This ensures that env-var overrides applied inside a test (via
    ``monkeypatch.setenv``) result in a fresh Settings read.
    """
    get_settings.cache_clear()
    yield  # type: ignore[misc]
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def reset_logging_context() -> None:  # type: ignore[return]
    """Clear structlog context variables between tests."""
    clear_request_context()
    yield  # type: ignore[misc]
    clear_request_context()


@pytest.fixture(scope="session", autouse=True)
def configure_test_logging() -> None:
    """Configure logging once for the entire test session."""
    configure_logging(force=True)
