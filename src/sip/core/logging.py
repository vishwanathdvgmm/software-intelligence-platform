"""SIP structured logging.

Provides a consistent logging setup across all subsystems using ``structlog``.
Structured events carry context variables (request_id, expert_id, operation,
etc.) automatically once bound to the logger.

Usage
-----
    from sip.core.logging import get_logger, bind_request_context

    logger = get_logger(__name__)

    # Bind per-request context (call once at request entry point):
    bind_request_context(request_id="req-abc123", expert_id="docker-expert")

    # Emit structured events with key=value pairs:
    logger.info("retrieval.started", query_length=42, strategy="hybrid")
    logger.error("retrieval.failed", error=str(exc), duration_ms=150)

Format
------
- ``console`` (development): human-readable coloured output via structlog's
  ConsoleRenderer.
- ``json`` (production / CI): machine-readable JSON — one event per line.

The format is driven by ``settings.logging.format``.

Observability note
------------------
M0 establishes the logging foundation.  M9 will add OpenTelemetry spans,
metrics, and the full ExecutionTrace model on top of this base.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, cast

import structlog

from sip.core.config import LogFormat, get_settings

# Module-level flag so configure() is idempotent.
_configured: bool = False

def configure_logging(*, force: bool = False) -> None:
    """Configure structlog and stdlib logging.

    Safe to call multiple times — subsequent calls are no-ops unless
    ``force=True`` (useful in tests).

    Should be called once at application startup.
    """
    global _configured
    if _configured and not force:
        return

    settings = get_settings()
    log_level = settings.logging.level.upper()
    use_json = settings.logging.format == LogFormat.JSON

    # ── Shared processors (always applied) ────────────────────────────────
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if use_json:
        # Production: JSON, one event per line.
        shared_processors.append(structlog.processors.dict_tracebacks)
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        # Development: coloured, human-readable.
        shared_processors.append(structlog.dev.set_exc_info)
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelNamesMapping()[log_level]
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # Silence overly verbose third-party loggers in development.
    for noisy in ("httpx", "httpcore", "asyncio", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog bound logger for the given module name.

    Calling ``configure_logging()`` is not required before this — it will
    be called automatically on first use if not already done.
    """
    if not _configured:
        configure_logging()
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))

# ─── Context variable helpers ───────────────────────────────────────────────

def bind_request_context(**kwargs: object) -> None:
    """Bind key-value pairs to the current async context.

    All subsequent log events in the same async task will automatically
    include these values.  Typical usage at request entry points:

        bind_request_context(
            request_id="req-abc",
            expert_id="docker-expert",
        )
    """
    structlog.contextvars.bind_contextvars(**kwargs)

def clear_request_context() -> None:
    """Clear all context variables for the current async task.

    Call at the end of a request or in test teardown.
    """
    structlog.contextvars.clear_contextvars()

def unbind_request_context(*keys: str) -> None:
    """Remove specific keys from the current async context."""
    structlog.contextvars.unbind_contextvars(*keys)
