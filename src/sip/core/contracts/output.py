"""Output contracts — Citations, Execution Traces, Evaluation Results.

These are the "exit contracts" of the SIP system:
- ``Citation``: links an answer claim to the exact Evidence → Chunk → Source chain.
- ``ExecutionTrace``: full per-request pipeline trace for observability/debugging.
- ``EvaluationResult``: structured metric output from the benchmarking framework.

The ``ExecutionTrace`` is the M0 observability foundation evolved into a
structured model — M9 will add OpenTelemetry spans on top of this.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from sip.core.contracts.base import SIPBaseModel, new_uuid, utc_now
from sip.core.contracts.knowledge import AuthorityLevel, SourceType
from sip.core.contracts.rag import (
    EvidenceSufficiency,
    QueryType,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
)

# ─── Citation ───────────────────────────────────────────────────────────────


class Citation(SIPBaseModel):
    """A verifiable link from an answer claim to its source.

    The full provenance chain:
        Answer claim → Evidence (reranker score) → Chunk → Document → Source
    """

    id: UUID = Field(default_factory=new_uuid)
    # The chunk that supports this citation
    chunk_id: UUID
    document_id: UUID
    source_id: UUID
    # Display metadata
    source_url: str
    document_title: str = Field(default="")
    section_heading: str = Field(default="")
    # The exact text span from the chunk that supports the claim
    supporting_text: str = Field(default="")
    # Authority and source type (for UI display)
    authority_level: AuthorityLevel
    source_type: SourceType
    # Software version this citation is from (for version-aware display)
    software_version_string: str | None = None
    # Reranker score of the evidence item
    relevance_score: float | None = None


# ─── Execution trace ─────────────────────────────────────────────────────────


class RetrievalTraceEntry(SIPBaseModel):
    """Per-retriever trace data within an ExecutionTrace."""

    retriever: str  # "semantic" | "bm25s"
    candidates_returned: int
    latency_ms: float | None = None


class ExecutionTrace(SIPBaseModel):
    """Full per-request trace of the SIP pipeline.

    Captures every stage's inputs, outputs, and timing. This is the
    structured contract underlying M9 observability — M9 will instrument
    this into OpenTelemetry spans.

    Every field here corresponds to a log event or span that should be
    emitted by the corresponding pipeline component (enforced in M2).
    """

    id: UUID = Field(default_factory=new_uuid)
    query_id: UUID
    expert_id: UUID
    request_id: str  # HTTP/API request correlation ID

    # ── Version snapshot ────────────────────────────────────────────────────
    # Full version snapshot for exact retrieval reproducibility (Change 5)
    version_snapshot: RetrievalVersionSnapshot

    # ── Query analysis ──────────────────────────────────────────────────────
    query_type: QueryType | None = None
    query_analysis_latency_ms: float | None = None

    # ── Retrieval ───────────────────────────────────────────────────────────
    strategy_used: RetrievalStrategy | None = None
    retrieval_entries: tuple[RetrievalTraceEntry, ...] = Field(default_factory=tuple)
    fusion_latency_ms: float | None = None
    candidates_before_dedup: int | None = None
    candidates_after_dedup: int | None = None
    reranking_latency_ms: float | None = None
    evidence_count: int | None = None

    # ── Evidence gate ───────────────────────────────────────────────────────
    sufficiency: EvidenceSufficiency | None = None
    sufficiency_confidence: float | None = None
    retry_count: int = 0
    abstained: bool = False

    # ── Context optimization ────────────────────────────────────────────────
    context_token_count: int | None = None
    context_items_removed: int | None = None
    context_truncated: bool = False
    context_optimization_latency_ms: float | None = None

    # ── LLM generation ──────────────────────────────────────────────────────
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_input_tokens: int | None = None
    llm_output_tokens: int | None = None
    llm_latency_ms: float | None = None

    # ── Answer ──────────────────────────────────────────────────────────────
    answer_length_chars: int | None = None
    citation_count: int | None = None

    # ── Overall ─────────────────────────────────────────────────────────────
    total_latency_ms: float | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


# ─── Evaluation ─────────────────────────────────────────────────────────────


class MetricValue(SIPBaseModel):
    """A single named metric with its value and optional metadata."""

    name: str
    value: float
    # Higher is better (True) or lower is better (False)
    higher_is_better: bool = True
    # Threshold for pass/fail classification (optional)
    threshold: float | None = None

    @property
    def passes_threshold(self) -> bool | None:
        if self.threshold is None:
            return None
        if self.higher_is_better:
            return self.value >= self.threshold
        return self.value <= self.threshold


class EvaluationSystem(StrEnum):
    """Which system is being evaluated."""

    SIP = "sip"
    BASELINE = "baseline"


class EvaluationResult(SIPBaseModel):
    """Structured result from a single evaluation run.

    Stores metrics for either SIP or the baseline system, associated with
    a specific dataset, expert, and full version snapshot.

    Note: No assumption is made about which system performs better.
    Results are objective measurements only (Change 1 from updated plan).
    """

    id: UUID = Field(default_factory=new_uuid)
    experiment_id: str = Field(..., min_length=1)
    system: EvaluationSystem
    dataset_name: str = Field(..., min_length=1)
    expert_id: UUID | None = None

    # Full version snapshot — enables exact reproduction of the evaluated run
    version_snapshot: RetrievalVersionSnapshot | None = None

    # ── Retrieval metrics ───────────────────────────────────────────────────
    precision_at_k: MetricValue | None = None
    recall_at_k: MetricValue | None = None
    hit_rate_at_k: MetricValue | None = None
    mrr: MetricValue | None = None
    ndcg: MetricValue | None = None

    # ── Context metrics ─────────────────────────────────────────────────────
    context_relevance: MetricValue | None = None
    context_redundancy: MetricValue | None = None
    compression_ratio: MetricValue | None = None

    # ── Generation metrics ──────────────────────────────────────────────────
    faithfulness: MetricValue | None = None
    groundedness: MetricValue | None = None
    hallucination_rate: MetricValue | None = None
    citation_accuracy: MetricValue | None = None

    # ── Evidence gate metrics ───────────────────────────────────────────────
    gate_precision: MetricValue | None = None
    gate_recall: MetricValue | None = None
    false_accept_rate: MetricValue | None = None
    false_reject_rate: MetricValue | None = None

    # ── Abstention metrics ──────────────────────────────────────────────────
    correct_abstention_rate: MetricValue | None = None
    incorrect_answer_rate: MetricValue | None = None

    # ── Latency ─────────────────────────────────────────────────────────────
    mean_latency_ms: float | None = None
    p95_latency_ms: float | None = None

    evaluated_at: datetime = Field(default_factory=utc_now)
    notes: str = Field(default="")
