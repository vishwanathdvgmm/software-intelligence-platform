"""SIP Request Middleware — correlation IDs and request-level observability.

Provides a FastAPI middleware that:
1. Generates or extracts a ``request_id`` for every incoming request.
2. Binds it to the structlog context so all downstream log events carry it.
3. Records total request latency in the MetricsCollector.
4. Clears the context at the end of the request.

This is the glue between the Logs, Metrics, and Traces pillars.
"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from sip.core.logging import bind_request_context, clear_request_context, get_logger
from sip.observability.metrics import get_metrics_collector

logger = get_logger(__name__)

_REQUEST_ID_HEADER = "X-Request-Id"

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for per-request observability."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 1. Extract or generate correlation ID
        request_id = request.headers.get(_REQUEST_ID_HEADER) or str(uuid.uuid4())

        # 2. Bind to structlog context (all downstream logs will carry this)
        bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        metrics = get_metrics_collector()
        metrics.inc_requests()
        start_ns = time.perf_counter_ns()

        logger.info(
            "request.started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
            response.headers[_REQUEST_ID_HEADER] = request_id
            return response

        except Exception:
            metrics.inc_failures()
            logger.exception(
                "request.failed",
                request_id=request_id,
            )
            raise

        finally:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            metrics.record_total_latency(elapsed_ms)
            logger.info(
                "request.completed",
                request_id=request_id,
                latency_ms=round(elapsed_ms, 2),
            )
            clear_request_context()
