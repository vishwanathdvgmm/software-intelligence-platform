"""Tests for sip.core.logging — structured logging setup."""

from __future__ import annotations

import logging
from typing import ClassVar

import structlog

from sip.core.logging import (
    bind_request_context,
    clear_request_context,
    configure_logging,
    get_logger,
    unbind_request_context,
)

class TestConfigureLogging:
    def test_configure_is_idempotent(self) -> None:
        configure_logging(force=True)
        configure_logging()  # Second call should be a no-op
        configure_logging()  # Third call — still a no-op

    def test_configure_with_force(self) -> None:
        configure_logging(force=True)
        configure_logging(force=True)  # Force=True always reconfigures

    def test_root_handler_is_set(self) -> None:
        configure_logging(force=True)
        root = logging.getLogger()
        assert len(root.handlers) >= 1

class TestGetLogger:
    def test_returns_bound_logger(self) -> None:
        logger = get_logger("sip.test")
        # structlog bound loggers have info/error/debug/warning methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")

    def test_different_names_return_loggers(self) -> None:
        logger_a = get_logger("sip.rag")
        logger_b = get_logger("sip.ingestion")
        # Both are valid logger objects
        assert logger_a is not None
        assert logger_b is not None

    def test_logger_can_emit_info(self) -> None:
        logger = get_logger("sip.test.emit")
        # Should not raise
        logger.info("test.event", key="value", number=42)

    def test_logger_can_emit_error(self) -> None:
        logger = get_logger("sip.test.emit")
        logger.error("test.error", error="something went wrong")

    def test_logger_can_emit_debug(self) -> None:
        logger = get_logger("sip.test.emit")
        logger.debug("test.debug", detail="verbose info")

class TestContextVariables:
    def test_bind_and_clear(self) -> None:
        bind_request_context(request_id="req-001", expert_id="docker")
        ctx = structlog.contextvars.get_contextvars()
        assert ctx.get("request_id") == "req-001"
        assert ctx.get("expert_id") == "docker"
        clear_request_context()
        ctx_after = structlog.contextvars.get_contextvars()
        assert "request_id" not in ctx_after

    def test_unbind_specific_keys(self) -> None:
        bind_request_context(request_id="req-002", expert_id="python", operation="search")
        unbind_request_context("operation")
        ctx = structlog.contextvars.get_contextvars()
        assert "request_id" in ctx
        assert "expert_id" in ctx
        assert "operation" not in ctx

    def test_clear_removes_all_context(self) -> None:
        bind_request_context(request_id="r1", expert_id="e1", op="search", extra="foo")
        clear_request_context()
        ctx = structlog.contextvars.get_contextvars()
        assert len(ctx) == 0

    def test_bind_overwrites_existing_key(self) -> None:
        bind_request_context(request_id="old")
        bind_request_context(request_id="new")
        ctx = structlog.contextvars.get_contextvars()
        assert ctx["request_id"] == "new"

    def test_bind_multiple_calls_accumulate(self) -> None:
        bind_request_context(request_id="r1")
        bind_request_context(expert_id="e1")
        ctx = structlog.contextvars.get_contextvars()
        assert ctx["request_id"] == "r1"
        assert ctx["expert_id"] == "e1"

class TestObservabilityContract:
    """Verify that the logging module supports the key SIP observability fields.

    These fields must be bindable from M0 onwards.  M9 will add OpenTelemetry
    spans and the full ExecutionTrace model on top of this base.
    """

    REQUIRED_CONTEXT_FIELDS: ClassVar[list[str]] = [
        "request_id",
        "expert_id",
        "operation",
        "duration_ms",
    ]

    def test_all_required_fields_bindable(self) -> None:
        """All standard SIP observability context fields can be bound."""
        bind_request_context(
            request_id="req-obs-test",
            expert_id="docker-expert",
            operation="retrieval.hybrid",
            duration_ms=150,
        )
        ctx = structlog.contextvars.get_contextvars()
        for field in self.REQUIRED_CONTEXT_FIELDS:
            assert field in ctx, f"Required context field '{field}' not found"
