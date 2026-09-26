"""RAG pipeline contracts — Phase 3.

Defines the data flowing through each stage of the Adaptive RAG engine:

    Query
      → QueryAnalysis (QueryAnalyzer output)
      → RetrievalPlan (RetrievalPlanner output)
      → RetrievalCandidate[] (Retriever output, per source)
      → RetrievalResult (RRF Fusion + Dedup output)
      → Evidence[] (CrossEncoderReranker output)
      → EvidenceSufficiencyAssessment (EvidenceEvaluator output)
      → Context (ContextOptimizer output)

``RetrievalVersionSnapshot`` captures all version metadata required for
retrieval reproducibility — attached to RetrievalPlan and ExecutionTrace.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from sip.core.contracts.base import SIPBaseModel, new_uuid, utc_now
from sip.core.contracts.knowledge import KnowledgeRecord

# ─── Enumerations ──────────────────────────────────────────────────────────


class QueryType(StrEnum):
    """Semantic type of a user query."""

    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    TROUBLESHOOTING = "troubleshooting"
    COMPARISON = "comparison"
    VERSION_SPECIFIC = "version_specific"
    MULTI_HOP = "multi_hop"
    EXPLORATORY = "exploratory"


class QueryComplexity(StrEnum):
    """Estimated complexity of a query."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class RetrievalStrategy(StrEnum):
    """Which retrieval paths the planner selected."""

    SEMANTIC = "semantic"
    LEXICAL = "lexical"
    HYBRID = "hybrid"


class EvidenceSufficiency(StrEnum):
    """Outcome of the Evidence Gate evaluation.

    - SUFFICIENT: Evidence is adequate to answer confidently.
    - INSUFFICIENT: Not enough relevant evidence found.
    - AMBIGUOUS: Evidence is present but unclear or conflicting.
    - CONTRADICTORY: Evidence sources contradict each other.
    - STALE: Evidence exists but is outdated for the query context.
    - VERSION_MISMATCH: Evidence is for a different software version.
    """

    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    AMBIGUOUS = "ambiguous"
    CONTRADICTORY = "contradictory"
    STALE = "stale"
    VERSION_MISMATCH = "version_mismatch"


# ─── Retrieval reproducibility ─────────────────────────────────────────────


class RetrievalVersionSnapshot(SIPBaseModel):
    """Snapshot of all component versions at retrieval time.

    Attached to every RetrievalPlan and ExecutionTrace so that any retrieval
    can be exactly reproduced by replaying it with the same versions.

    This directly addresses Change 5 from the updated implementation plan.
    """

    # Expert and knowledge state
    expert_id: UUID
    expert_version: str
    knowledge_version: str | None = None  # version tag of the knowledge index

    # Embedding model — changing this invalidates all Qdrant vectors
    embedding_model: str
    embedding_model_version: str
    embedding_dimension: int

    # BM25S index — keyed by expert_id + knowledge version
    bm25s_index_version: str | None = None

    # Reranker model
    reranker_model: str
    reranker_model_version: str

    # Retrieval configuration snapshot
    semantic_top_k: int
    lexical_top_k: int
    rerank_top_k: int
    rrf_k: int = 60  # RRF constant
    strategy: RetrievalStrategy

    captured_at: datetime = Field(default_factory=utc_now)


# ─── Query pipeline ─────────────────────────────────────────────────────────


class Query(SIPBaseModel):
    """Raw user query entering the RAG pipeline."""

    id: UUID = Field(default_factory=new_uuid)
    expert_id: UUID
    text: str = Field(..., min_length=1, max_length=4096)
    # Optional conversation context (previous turns)
    conversation_id: UUID | None = None
    # Explicit version filter from the user (e.g. "docker 25.0")
    requested_version: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class QueryAnalysis(SIPBaseModel):
    """Output of the QueryAnalyzer stage.

    Extracts structured information from the raw query text.
    """

    query_id: UUID
    query_type: QueryType
    complexity: QueryComplexity
    # Named entities extracted from the query (software names, versions, etc.)
    entities: tuple[str, ...] = Field(default_factory=tuple)
    # Detected software version constraints (e.g. ">=25.0")
    version_constraints: tuple[str, ...] = Field(default_factory=tuple)
    # Whether the query appears to require multi-document reasoning
    requires_multi_hop: bool = False
    # Sub-questions decomposed from the original (for multi-hop)
    sub_questions: tuple[str, ...] = Field(default_factory=tuple)


class RetrievalPlan(SIPBaseModel):
    """Output of the RetrievalPlanner stage.

    Encodes the retrieval strategy and parameters for this query.
    Carries a ``version_snapshot`` for full reproducibility.
    """

    query_id: UUID
    strategy: RetrievalStrategy
    semantic_top_k: int = Field(default=20, ge=1, le=200)
    lexical_top_k: int = Field(default=20, ge=1, le=200)
    rerank_top_k: int = Field(default=10, ge=1, le=100)
    # RRF constant — higher = less emphasis on individual rank positions
    rrf_k: int = Field(default=60, ge=1)
    # Qdrant filter payload — version-aware filtering applied at retrieval
    version_filter: dict[str, str | list[str]] = Field(default_factory=dict)
    # Rationale for strategy selection (for trace/debug)
    rationale: str = Field(default="")
    # Full version snapshot — enables exact reproduction of this retrieval
    version_snapshot: RetrievalVersionSnapshot


class RetrievalCandidate(SIPBaseModel):
    """A single candidate result from one retrieval source (semantic or lexical).

    Scores are normalized to [0, 1] within each retriever before fusion.
    """

    chunk_id: UUID
    knowledge_record: KnowledgeRecord
    # Normalized score from the retriever (semantic cosine sim or BM25S score)
    score: float = Field(..., ge=0.0, le=1.0)
    # Which retriever produced this candidate
    retriever: str  # e.g. "semantic", "bm25s"
    # Rank within the retriever's result set (1-indexed)
    rank: int = Field(..., ge=1)


class RetrievalResult(SIPBaseModel):
    """Output of RRF Fusion + Deduplication.

    The unified, deduplicated candidate set ready for reranking.
    """

    query_id: UUID
    candidates: tuple[RetrievalCandidate, ...]
    # Per-retriever candidate counts before fusion
    semantic_count: int = 0
    lexical_count: int = 0
    # Duplicates removed (same chunk_id from multiple retrievers)
    duplicates_removed: int = 0
    fusion_latency_ms: float | None = None


class Evidence(SIPBaseModel):
    """A single piece of evidence after Cross-Encoder reranking.

    Carries the full KnowledgeRecord (for provenance/citation) plus
    the reranker score.
    """

    chunk_id: UUID
    knowledge_record: KnowledgeRecord
    # Raw cross-encoder score (not normalized, can be negative)
    reranker_score: float
    # Final rank in the reranked list (1-indexed)
    rank: int = Field(..., ge=1)
    # RRF fused score (carried forward for transparency)
    fusion_score: float | None = None


class EvidenceSufficiencyAssessment(SIPBaseModel):
    """Output of the EvidenceEvaluator (Evidence Gate).

    Determines whether the retrieved evidence is adequate for generation,
    and whether the pipeline should retry, reformulate, or abstain.
    """

    query_id: UUID
    sufficiency: EvidenceSufficiency
    # Confidence in the sufficiency determination [0, 1]
    confidence: float = Field(..., ge=0.0, le=1.0)
    # Human-readable rationale for the decision
    rationale: str = Field(default="")
    # Which attempt this is (1 = first, >1 = after retry)
    attempt_number: int = Field(default=1, ge=1)
    # Whether the pipeline should attempt another retrieval cycle
    should_retry: bool = False
    # Suggested reformulation for retry (if applicable)
    reformulated_query: str | None = None


class Context(SIPBaseModel):
    """Final optimized context delivered to the LLM.

    Output of the ContextOptimizer — evidence has been filtered, deduplicated,
    possibly compressed, ordered, and trimmed to fit the token budget.
    """

    query_id: UUID
    # Ordered evidence items (most relevant first)
    evidence_items: tuple[Evidence, ...]
    # Rendered text handed to the LLM
    rendered_text: str
    # Token count of the rendered context
    token_count: int = Field(..., ge=0)
    # Whether any evidence was dropped to meet the token budget
    truncated: bool = False
    # Items removed during optimization
    items_removed: int = 0
    optimization_latency_ms: float | None = None
