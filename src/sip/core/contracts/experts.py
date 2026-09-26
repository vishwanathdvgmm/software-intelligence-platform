"""Expert system contracts — Phase 6.

Defines the Expert entity and its full lifecycle state machine.

Lifecycle states:
    DRAFT → CONFIGURING → BUILDING → VALIDATING → READY → ACTIVE
                                                            ↓
                                            UPDATING / DISABLED / ARCHIVED

An Expert is the core product entity of SIP — it encapsulates:
- Which software and versions it covers (knowledge scope)
- How to retrieve (retrieval config)
- How to generate (generation config)
- When evidence is sufficient (evidence gate config)
- How to handle versioning (version policy)
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field, field_validator

from sip.core.contracts.base import SIPBaseModel, new_uuid, utc_now
from sip.core.contracts.rag import RetrievalStrategy

# ─── Enumerations ──────────────────────────────────────────────────────────


class ExpertStatus(StrEnum):
    """Full lifecycle state of an Expert.

    Valid transitions:
        DRAFT         → CONFIGURING
        CONFIGURING   → BUILDING | DRAFT (reset)
        BUILDING      → VALIDATING | CONFIGURING (on failure)
        VALIDATING    → READY | BUILDING (on validation failure)
        READY         → ACTIVE
        ACTIVE        → UPDATING | DISABLED
        UPDATING      → ACTIVE | DISABLED
        DISABLED      → ACTIVE | ARCHIVED
        ARCHIVED      → (terminal)
    """

    DRAFT = "draft"
    CONFIGURING = "configuring"
    BUILDING = "building"
    VALIDATING = "validating"
    READY = "ready"
    ACTIVE = "active"
    UPDATING = "updating"
    DISABLED = "disabled"
    ARCHIVED = "archived"


# Valid state transitions (enforced by the Expert service, not the model)
EXPERT_VALID_TRANSITIONS: dict[ExpertStatus, frozenset[ExpertStatus]] = {
    ExpertStatus.DRAFT: frozenset({ExpertStatus.CONFIGURING}),
    ExpertStatus.CONFIGURING: frozenset({ExpertStatus.BUILDING, ExpertStatus.DRAFT}),
    ExpertStatus.BUILDING: frozenset({ExpertStatus.VALIDATING, ExpertStatus.CONFIGURING}),
    ExpertStatus.VALIDATING: frozenset({ExpertStatus.READY, ExpertStatus.BUILDING}),
    ExpertStatus.READY: frozenset({ExpertStatus.ACTIVE}),
    ExpertStatus.ACTIVE: frozenset({ExpertStatus.UPDATING, ExpertStatus.DISABLED}),
    ExpertStatus.UPDATING: frozenset({ExpertStatus.ACTIVE, ExpertStatus.DISABLED}),
    ExpertStatus.DISABLED: frozenset({ExpertStatus.ACTIVE, ExpertStatus.ARCHIVED}),
    ExpertStatus.ARCHIVED: frozenset(),  # terminal
}


class VersionPolicy(StrEnum):
    """How the Expert handles software version scope."""

    LATEST_ONLY = "latest_only"       # Only retrieve from the latest version
    PINNED = "pinned"                 # Retrieve from a specific pinned version
    RANGE = "range"                   # Retrieve from a version range
    ALL_VERSIONS = "all_versions"     # Retrieve across all versions (with metadata)


# ─── Expert sub-configs ─────────────────────────────────────────────────────


class RetrievalConfig(SIPBaseModel):
    """Retrieval parameters for an Expert.

    Controls how the RAG pipeline retrieves and ranks evidence for this Expert.
    All model references here are configurable defaults — not lock-ins.
    """

    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    semantic_top_k: int = Field(default=20, ge=1, le=200)
    lexical_top_k: int = Field(default=20, ge=1, le=200)
    rerank_top_k: int = Field(default=10, ge=1, le=100)
    rrf_k: int = Field(default=60, ge=1)
    # Configurable model overrides (if None, system defaults from config.py are used)
    embedding_model: str | None = None
    embedding_model_version: str | None = None
    reranker_model: str | None = None
    reranker_model_version: str | None = None


class GenerationConfig(SIPBaseModel):
    """LLM generation parameters for an Expert.

    All model references are configurable defaults.
    """

    # If None, system default from config.py is used
    llm_provider: str | None = None
    llm_model: str | None = None
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=2048, ge=1)
    # System prompt template for this expert (supports {expert_name} interpolation)
    system_prompt_template: str = Field(default="")


class EvidenceConfig(SIPBaseModel):
    """Evidence Gate configuration for an Expert.

    Controls when the gate considers evidence sufficient, and what to do
    when it is not.
    """

    # Minimum reranker score to consider a piece of evidence relevant
    min_evidence_score: float = Field(default=0.3, ge=0.0, le=1.0)
    # Minimum number of evidence items required for SUFFICIENT verdict
    min_evidence_count: int = Field(default=1, ge=1)
    # Maximum number of retry attempts on INSUFFICIENT verdict
    max_retry_attempts: int = Field(default=2, ge=0, le=5)
    # Whether to abstain (return no answer) rather than hallucinate
    enable_abstention: bool = True
    # Whether to flag VERSION_MISMATCH when evidence is from wrong version
    enable_version_mismatch_detection: bool = True


class ExpertConfig(SIPBaseModel):
    """Complete configuration for an Expert.

    Snapshot-able — whenever config changes, a new ExpertVersion is created.
    """

    # IDs of Software entities this Expert covers
    software_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    # Version policy for retrieval scoping
    version_policy: VersionPolicy = VersionPolicy.LATEST_ONLY
    # Pinned version string (used when version_policy = PINNED)
    pinned_version: str | None = None

    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    evidence: EvidenceConfig = Field(default_factory=EvidenceConfig)

    @field_validator("pinned_version")
    @classmethod
    def pinned_version_requires_policy(cls, v: str | None) -> str | None:
        # Cross-field validation is done in the Expert service, not here,
        # since frozen models cannot access other fields in validators cleanly.
        return v


# ─── Expert entity ──────────────────────────────────────────────────────────


class Expert(SIPBaseModel):
    """An Expert entity — the core product unit of SIP.

    An Expert is a configured RAG agent specializing in one or more software
    products. It encapsulates knowledge scope, retrieval strategy, generation
    parameters, and evidence gate settings.
    """

    id: UUID = Field(default_factory=new_uuid)
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9\-]+$")
    description: str = Field(default="")
    status: ExpertStatus = ExpertStatus.DRAFT
    config: ExpertConfig = Field(default_factory=ExpertConfig)
    # Current config version number (bumped on each config change)
    config_version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    activated_at: datetime | None = None

    @field_validator("slug", mode="before")
    @classmethod
    def slug_lowercase(cls, v: str) -> str:
        return v.lower()

    def is_queryable(self) -> bool:
        """Return True if this Expert can accept queries."""
        return self.status == ExpertStatus.ACTIVE


class ExpertVersion(SIPBaseModel):
    """Immutable snapshot of an Expert's config at a point in time.

    Created whenever ExpertConfig changes so that retrieval runs referencing
    an older version can still be reproduced exactly.
    """

    id: UUID = Field(default_factory=new_uuid)
    expert_id: UUID
    version_number: int = Field(..., ge=1)
    config_snapshot: ExpertConfig
    # Reason for the config change
    change_reason: str = Field(default="")
    created_at: datetime = Field(default_factory=utc_now)
    created_by: str = Field(default="system")
