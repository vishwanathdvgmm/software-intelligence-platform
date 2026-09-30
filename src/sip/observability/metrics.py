"""SIP Metrics Collector — runtime performance counters.

Provides in-process counters and histograms for the key runtime metrics
specified in Phase 9 §9.51:

    requests_total, requests_failed, retrieval_latency, reranker_latency,
    llm_latency, tokens_total, retrieval_hit_rate

This is a lightweight, stdlib-only implementation suitable for the
desktop MVP.  It stores values in memory and exposes them via a simple
``snapshot()`` dict for the API health/metrics endpoint.

Production / enterprise deployments can replace this with a
Prometheus-compatible collector by implementing the same protocol.

Thread safety
-------------
All mutations use a ``threading.Lock`` so counters are safe to update
from any async task or thread (e.g. background ingestion).
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List

from sip.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class _LatencyHistogram:
    """Simple in-memory latency histogram (stores raw values)."""
    values: List[float] = field(default_factory=list)

    def record(self, ms: float) -> None:
        self.values.append(ms)

    @property
    def count(self) -> int:
        return len(self.values)

    @property
    def mean(self) -> float:
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)

    @property
    def p95(self) -> float:
        if not self.values:
            return 0.0
        sorted_v = sorted(self.values)
        idx = int(len(sorted_v) * 0.95)
        return sorted_v[min(idx, len(sorted_v) - 1)]

    @property
    def p99(self) -> float:
        if not self.values:
            return 0.0
        sorted_v = sorted(self.values)
        idx = int(len(sorted_v) * 0.99)
        return sorted_v[min(idx, len(sorted_v) - 1)]

    def to_dict(self) -> Dict[str, float]:
        return {
            "count": self.count,
            "mean_ms": round(self.mean, 2),
            "p95_ms": round(self.p95, 2),
            "p99_ms": round(self.p99, 2),
        }

class MetricsCollector:
    """Singleton-style in-process metrics collector.

    Usage::

        metrics = MetricsCollector()
        metrics.inc_requests()
        metrics.record_retrieval_latency(85.3)
        metrics.record_llm_latency(1200.0)
        metrics.add_tokens(input_tokens=500, output_tokens=120)

        snapshot = metrics.snapshot()
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requests_total: int = 0
        self._requests_failed: int = 0
        self._tokens_input: int = 0
        self._tokens_output: int = 0

        self._retrieval_latency = _LatencyHistogram()
        self._reranker_latency = _LatencyHistogram()
        self._llm_latency = _LatencyHistogram()
        self._total_latency = _LatencyHistogram()

        self._retrieval_hits: int = 0
        self._retrieval_queries: int = 0

        self._started_at: float = time.time()

    # ── Counters ────────────────────────────────────────────────────────────

    def inc_requests(self) -> None:
        with self._lock:
            self._requests_total += 1

    def inc_failures(self) -> None:
        with self._lock:
            self._requests_failed += 1

    def add_tokens(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        with self._lock:
            self._tokens_input += input_tokens
            self._tokens_output += output_tokens

    # ── Latency histograms ──────────────────────────────────────────────────

    def record_retrieval_latency(self, ms: float) -> None:
        with self._lock:
            self._retrieval_latency.record(ms)

    def record_reranker_latency(self, ms: float) -> None:
        with self._lock:
            self._reranker_latency.record(ms)

    def record_llm_latency(self, ms: float) -> None:
        with self._lock:
            self._llm_latency.record(ms)

    def record_total_latency(self, ms: float) -> None:
        with self._lock:
            self._total_latency.record(ms)

    # ── Retrieval hit rate ──────────────────────────────────────────────────

    def record_retrieval_hit(self, hit: bool) -> None:
        """Record whether at least one relevant result was retrieved."""
        with self._lock:
            self._retrieval_queries += 1
            if hit:
                self._retrieval_hits += 1

    # ── Snapshot ────────────────────────────────────────────────────────────

    def snapshot(self) -> Dict[str, object]:
        """Return a point-in-time snapshot of all collected metrics."""
        with self._lock:
            hit_rate = (
                self._retrieval_hits / self._retrieval_queries
                if self._retrieval_queries > 0
                else 0.0
            )
            return {
                "uptime_seconds": round(time.time() - self._started_at, 1),
                "requests_total": self._requests_total,
                "requests_failed": self._requests_failed,
                "tokens_input": self._tokens_input,
                "tokens_output": self._tokens_output,
                "tokens_total": self._tokens_input + self._tokens_output,
                "retrieval_hit_rate": round(hit_rate, 4),
                "latency": {
                    "retrieval": self._retrieval_latency.to_dict(),
                    "reranker": self._reranker_latency.to_dict(),
                    "llm": self._llm_latency.to_dict(),
                    "total": self._total_latency.to_dict(),
                },
            }

    def reset(self) -> None:
        """Reset all counters (useful for tests)."""
        with self._lock:
            self._requests_total = 0
            self._requests_failed = 0
            self._tokens_input = 0
            self._tokens_output = 0
            self._retrieval_latency = _LatencyHistogram()
            self._reranker_latency = _LatencyHistogram()
            self._llm_latency = _LatencyHistogram()
            self._total_latency = _LatencyHistogram()
            self._retrieval_hits = 0
            self._retrieval_queries = 0
            self._started_at = time.time()

# ── Module-level singleton ──────────────────────────────────────────────────

_collector: MetricsCollector | None = None

def get_metrics_collector() -> MetricsCollector:
    """Return the global metrics collector (lazy singleton)."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
