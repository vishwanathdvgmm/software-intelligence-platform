"""Observability — tracing, metrics, and request middleware (Phase 9).

Three pillars:

1. **Logs** — Structured logging via ``sip.core.logging`` (structlog).
   Already established in M0; bound context variables carry ``request_id``,
   ``expert_id``, etc. through every event.

2. **Metrics** — In-process counters and latency histograms via
   ``MetricsCollector``.  Exposed through the ``/api/metrics`` endpoint.

3. **Traces** — Per-request pipeline traces via ``PipelineTracer``,
   producing ``ExecutionTrace`` contracts for debugging and evaluation.

The ``ObservabilityMiddleware`` ties these together: it generates
correlation IDs, binds them to the log context, and records request-level
latency in the metrics collector.
"""

from sip.observability.metrics import MetricsCollector, get_metrics_collector
from sip.observability.middleware import ObservabilityMiddleware
from sip.observability.tracer import PipelineTracer

__all__ = [
    "MetricsCollector",
    "ObservabilityMiddleware",
    "PipelineTracer",
    "get_metrics_collector",
]
