"""SIP Pipeline Tracer — per-request lifecycle tracing.

Captures timing and metadata for every stage of the RAG pipeline,
producing an ``ExecutionTrace`` at the end of the request.

The tracer is designed to be instantiated once per request and passed
through the pipeline. Each stage calls the corresponding ``record_*``
method.  At the end, ``build_trace()`` produces the final immutable
``ExecutionTrace`` contract.

Usage
-----
    tracer = PipelineTracer(query_id=q.id, expert_id=expert.id, request_id="req-abc")
    tracer.record_query_analysis(query_type=QueryType.FACTOID, latency_ms=12.3)
    tracer.record_retrieval("semantic", candidates=15, latency_ms=85.0)
    ...
    trace = tracer.build_trace(version_snapshot=snapshot)

Security note
-------------
The tracer MUST NOT store raw query text, LLM prompts, or retrieved
document contents.  Only metadata (counts, types, IDs, timings) are
recorded.  This is enforced by the API — there is no ``content`` field
on any recording method.
"""

from __future__ import annotations

import time
from typing import Optional
from uuid import UUID

from sip.core.contracts.base import new_uuid
from sip.core.contracts.output import (
    ExecutionTrace,
    RetrievalTraceEntry,
)
from sip.core.contracts.rag import (
    EvidenceSufficiency,
    QueryType,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
)
from sip.core.logging import get_logger

logger = get_logger(__name__)


class PipelineTracer:
    """Mutable builder for a single request's ``ExecutionTrace``.

    Create one at the start of a request, call ``record_*`` methods as
    the pipeline progresses, then call ``build_trace()`` to produce the
    immutable Pydantic model.
    """

    def __init__(
        self,
        query_id: UUID,
        expert_id: UUID,
        request_id: str,
    ) -> None:
        self._query_id = query_id
        self._expert_id = expert_id
        self._request_id = request_id
        self._start_ns = time.perf_counter_ns()

        # ── Query analysis ──────────────────────────────────────────────
        self._query_type: QueryType | None = None
        self._query_analysis_latency_ms: float | None = None

        # ── Retrieval ───────────────────────────────────────────────────
        self._strategy: RetrievalStrategy | None = None
        self._retrieval_entries: list[RetrievalTraceEntry] = []
        self._fusion_latency_ms: float | None = None
        self._candidates_before_dedup: int | None = None
        self._candidates_after_dedup: int | None = None
        self._reranking_latency_ms: float | None = None
        self._evidence_count: int | None = None

        # ── Evidence gate ───────────────────────────────────────────────
        self._sufficiency: EvidenceSufficiency | None = None
        self._sufficiency_confidence: float | None = None
        self._retry_count: int = 0
        self._abstained: bool = False

        # ── Context optimization ────────────────────────────────────────
        self._context_token_count: int | None = None
        self._context_items_removed: int | None = None
        self._context_truncated: bool = False
        self._context_optimization_latency_ms: float | None = None

        # ── LLM generation ──────────────────────────────────────────────
        self._llm_provider: str | None = None
        self._llm_model: str | None = None
        self._llm_input_tokens: int | None = None
        self._llm_output_tokens: int | None = None
        self._llm_latency_ms: float | None = None

        # ── Answer ──────────────────────────────────────────────────────
        self._answer_length_chars: int | None = None
        self._citation_count: int | None = None

        # ── Error ───────────────────────────────────────────────────────
        self._error: str | None = None

    # ─── Recording methods ──────────────────────────────────────────────────

    def record_query_analysis(
        self,
        query_type: QueryType,
        latency_ms: float,
    ) -> None:
        """Record query analysis stage completion."""
        self._query_type = query_type
        self._query_analysis_latency_ms = latency_ms
        logger.info(
            "trace.query_analysis",
            query_id=str(self._query_id),
            query_type=query_type.value,
            latency_ms=round(latency_ms, 2),
        )

    def record_retrieval(
        self,
        retriever: str,
        candidates: int,
        latency_ms: float,
    ) -> None:
        """Record a single retriever's results (semantic / bm25s)."""
        entry = RetrievalTraceEntry(
            retriever=retriever,
            candidates_returned=candidates,
            latency_ms=latency_ms,
        )
        self._retrieval_entries.append(entry)
        logger.info(
            "trace.retrieval",
            query_id=str(self._query_id),
            retriever=retriever,
            candidates=candidates,
            latency_ms=round(latency_ms, 2),
        )

    def record_strategy(self, strategy: RetrievalStrategy) -> None:
        """Record which retrieval strategy was selected."""
        self._strategy = strategy
        logger.info(
            "trace.strategy_selected",
            query_id=str(self._query_id),
            strategy=strategy.value,
        )

    def record_fusion(
        self,
        before_dedup: int,
        after_dedup: int,
        latency_ms: float,
    ) -> None:
        """Record fusion/deduplication stage."""
        self._candidates_before_dedup = before_dedup
        self._candidates_after_dedup = after_dedup
        self._fusion_latency_ms = latency_ms
        logger.info(
            "trace.fusion",
            query_id=str(self._query_id),
            before_dedup=before_dedup,
            after_dedup=after_dedup,
            latency_ms=round(latency_ms, 2),
        )

    def record_reranking(
        self,
        evidence_count: int,
        latency_ms: float,
    ) -> None:
        """Record reranking stage completion."""
        self._evidence_count = evidence_count
        self._reranking_latency_ms = latency_ms
        logger.info(
            "trace.reranking",
            query_id=str(self._query_id),
            evidence_count=evidence_count,
            latency_ms=round(latency_ms, 2),
        )

    def record_evidence_gate(
        self,
        sufficiency: EvidenceSufficiency,
        confidence: float,
        retry_count: int = 0,
        abstained: bool = False,
    ) -> None:
        """Record evidence gate decision."""
        self._sufficiency = sufficiency
        self._sufficiency_confidence = confidence
        self._retry_count = retry_count
        self._abstained = abstained
        logger.info(
            "trace.evidence_gate",
            query_id=str(self._query_id),
            sufficiency=sufficiency.value,
            confidence=round(confidence, 3),
            retry_count=retry_count,
            abstained=abstained,
        )

    def record_context_optimization(
        self,
        token_count: int,
        items_removed: int,
        truncated: bool,
        latency_ms: float,
    ) -> None:
        """Record context optimization stage."""
        self._context_token_count = token_count
        self._context_items_removed = items_removed
        self._context_truncated = truncated
        self._context_optimization_latency_ms = latency_ms
        logger.info(
            "trace.context_optimization",
            query_id=str(self._query_id),
            token_count=token_count,
            items_removed=items_removed,
            truncated=truncated,
            latency_ms=round(latency_ms, 2),
        )

    def record_llm_generation(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
    ) -> None:
        """Record LLM generation stage."""
        self._llm_provider = provider
        self._llm_model = model
        self._llm_input_tokens = input_tokens
        self._llm_output_tokens = output_tokens
        self._llm_latency_ms = latency_ms
        logger.info(
            "trace.llm_generation",
            query_id=str(self._query_id),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=round(latency_ms, 2),
        )

    def record_answer(
        self,
        answer_length_chars: int,
        citation_count: int,
    ) -> None:
        """Record answer generation metadata."""
        self._answer_length_chars = answer_length_chars
        self._citation_count = citation_count
        logger.info(
            "trace.answer",
            query_id=str(self._query_id),
            answer_length_chars=answer_length_chars,
            citation_count=citation_count,
        )

    def record_error(self, error: str) -> None:
        """Record a pipeline error."""
        self._error = error
        logger.error(
            "trace.error",
            query_id=str(self._query_id),
            error=error,
        )

    # ─── Build the final trace ──────────────────────────────────────────────

    def build_trace(
        self,
        version_snapshot: RetrievalVersionSnapshot,
    ) -> ExecutionTrace:
        """Produce the immutable ``ExecutionTrace`` from all recorded data."""
        elapsed_ns = time.perf_counter_ns() - self._start_ns
        total_latency_ms = elapsed_ns / 1_000_000

        trace = ExecutionTrace(
            query_id=self._query_id,
            expert_id=self._expert_id,
            request_id=self._request_id,
            version_snapshot=version_snapshot,
            # Query analysis
            query_type=self._query_type,
            query_analysis_latency_ms=self._query_analysis_latency_ms,
            # Retrieval
            strategy_used=self._strategy,
            retrieval_entries=tuple(self._retrieval_entries),
            fusion_latency_ms=self._fusion_latency_ms,
            candidates_before_dedup=self._candidates_before_dedup,
            candidates_after_dedup=self._candidates_after_dedup,
            reranking_latency_ms=self._reranking_latency_ms,
            evidence_count=self._evidence_count,
            # Evidence gate
            sufficiency=self._sufficiency,
            sufficiency_confidence=self._sufficiency_confidence,
            retry_count=self._retry_count,
            abstained=self._abstained,
            # Context optimization
            context_token_count=self._context_token_count,
            context_items_removed=self._context_items_removed,
            context_truncated=self._context_truncated,
            context_optimization_latency_ms=self._context_optimization_latency_ms,
            # LLM generation
            llm_provider=self._llm_provider,
            llm_model=self._llm_model,
            llm_input_tokens=self._llm_input_tokens,
            llm_output_tokens=self._llm_output_tokens,
            llm_latency_ms=self._llm_latency_ms,
            # Answer
            answer_length_chars=self._answer_length_chars,
            citation_count=self._citation_count,
            # Overall
            total_latency_ms=total_latency_ms,
            error=self._error,
        )

        logger.info(
            "trace.complete",
            query_id=str(self._query_id),
            total_latency_ms=round(total_latency_ms, 2),
            error=self._error is not None,
        )

        return trace
