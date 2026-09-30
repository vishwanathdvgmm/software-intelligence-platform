"""Knowledge domain contracts — Phase 4.

Represents the storage-agnostic data model for the knowledge layer.
These models define the shape of knowledge but are not tied to any
database schema (PostgreSQL, Qdrant, etc.).

Hierarchy:
    Software
      └── SoftwareVersion (many)
            └── Source (many)
                  └── Document (many)
                        └── DocumentVersion (many)
                              └── Section (many)
                                    └── Chunk (many)  ← retrievable atom

``KnowledgeRecord`` is a flattened provenance bundle used by the RAG
retrieval layer — it carries a Chunk together with the full chain of
metadata needed to produce a Citation.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field, field_validator

from sip.core.contracts.base import SIPBaseModel, new_uuid, utc_now

# ─── Enumerations ──────────────────────────────────────────────────────────

class SourceType(StrEnum):
    """Where a knowledge source originates."""

    OFFICIAL_DOCS = "official_docs"
    GITHUB_REPO = "github_repo"
    GITHUB_ISSUES = "github_issues"
    STACK_OVERFLOW = "stack_overflow"
    YOUTUBE = "youtube"
    COMMUNITY_DOCS = "community_docs"
    BLOG = "blog"
    RFC = "rfc"
    OTHER = "other"

class AuthorityLevel(StrEnum):
    """Trust / authority of a source.

    Used to weight retrieval results and guide evidence evaluation.
    """

    OFFICIAL = "official"  # e.g. docs.docker.com — highest trust
    COMMUNITY = "community"  # e.g. Stack Overflow answers — medium trust
    AUTO_GENERATED = "auto_generated"  # e.g. generated reference — lower trust

    @property
    def weight(self) -> float:
        """Numeric retrieval weight for RRF score adjustment."""
        return {
            AuthorityLevel.OFFICIAL: 1.0,
            AuthorityLevel.COMMUNITY: 0.5,
            AuthorityLevel.AUTO_GENERATED: 0.3,
        }[self]

class DocumentType(StrEnum):
    """Semantic type of a document."""

    GUIDE = "guide"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    CHANGELOG = "changelog"
    API_DOCS = "api_docs"
    ISSUE = "issue"
    DISCUSSION = "discussion"
    OTHER = "other"

class ChunkType(StrEnum):
    """Content type of a chunk."""

    TEXT = "text"
    CODE = "code"
    TABLE = "table"
    HEADING = "heading"
    MIXED = "mixed"

class IngestionStatus(StrEnum):
    """Status of an ingestion run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

# ─── Knowledge entities ─────────────────────────────────────────────────────

class Software(SIPBaseModel):
    """A software product that an Expert can be trained on.

    Examples: Docker, Kubernetes, Python, React.
    """

    id: UUID = Field(default_factory=new_uuid)
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9\-]+$")
    description: str = Field(default="")
    homepage_url: str | None = None
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("slug", mode="before")
    @classmethod
    def slug_lowercase(cls, v: str) -> str:
        return v.lower()

class SoftwareVersion(SIPBaseModel):
    """A specific version of a Software product.

    Retrieval is always version-aware — chunks are associated with one or
    more SoftwareVersions so that a query for "docker 25.0" does not surface
    results from "docker 20.10".
    """

    id: UUID = Field(default_factory=new_uuid)
    software_id: UUID
    version_string: str = Field(..., min_length=1, max_length=100)
    # Semver components for range queries (nullable if non-semver)
    major: int | None = None
    minor: int | None = None
    patch: int | None = None
    is_latest: bool = False
    release_date: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)

class Source(SIPBaseModel):
    """A knowledge source — a URL root or repository that can be crawled.

    Examples:
        - https://docs.docker.com/  (OFFICIAL_DOCS)
        - https://github.com/moby/moby  (GITHUB_REPO)
        - https://stackoverflow.com/questions/tagged/docker  (STACK_OVERFLOW)
    """

    id: UUID = Field(default_factory=new_uuid)
    software_id: UUID
    url: str = Field(..., min_length=1)
    source_type: SourceType
    authority_level: AuthorityLevel = AuthorityLevel.OFFICIAL
    name: str = Field(default="")
    # Which software versions this source covers (empty = all versions)
    version_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    is_active: bool = True
    crawl_frequency_hours: int = Field(default=24, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    last_crawled_at: datetime | None = None

class Document(SIPBaseModel):
    """A logical document within a Source.

    A Document is the stable identity for a URL/file over time. Each crawl
    that detects a change creates a new DocumentVersion — the Document ID
    remains stable so history is preserved.
    """

    id: UUID = Field(default_factory=new_uuid)
    source_id: UUID
    software_id: UUID
    url: str = Field(..., min_length=1)
    document_type: DocumentType = DocumentType.OTHER
    title: str = Field(default="")
    language: str = Field(default="en")
    created_at: datetime = Field(default_factory=utc_now)

class DocumentVersion(SIPBaseModel):
    """A snapshot of a Document's content at a point in time.

    ``content_hash`` (SHA-256 of normalized content) drives change detection:
    if hash is unchanged, no re-ingestion is needed.
    """

    id: UUID = Field(default_factory=new_uuid)
    document_id: UUID
    # SHA-256 hex digest of the normalized document content
    content_hash: str = Field(..., min_length=64, max_length=64)
    version_number: int = Field(..., ge=1)
    fetched_at: datetime = Field(default_factory=utc_now)
    # Raw byte size of the source document
    raw_size_bytes: int | None = None
    is_current: bool = True
    ingestion_run_id: UUID | None = None

class Section(SIPBaseModel):
    """A structural section within a DocumentVersion.

    Sections represent the heading hierarchy (h1 → h2 → h3 …) and are used
    to preserve document structure during chunking.
    """

    id: UUID = Field(default_factory=new_uuid)
    document_version_id: UUID
    parent_section_id: UUID | None = None
    heading: str = Field(default="")
    heading_level: int = Field(default=1, ge=1, le=6)
    # Position within the document (0-indexed)
    position: int = Field(..., ge=0)

class Chunk(SIPBaseModel):
    """The atomic unit of retrieval in the RAG pipeline.

    A Chunk is stored in both PostgreSQL (metadata) and Qdrant (vector).
    The ``chunk_id`` is stable across re-ingestions as long as content is
    unchanged — this is critical for BM25S index consistency.

    All Qdrant payload fields required for version-aware filtered retrieval
    are present here (Phase 4.21 compliance).
    """

    id: UUID = Field(default_factory=new_uuid)
    document_version_id: UUID
    document_id: UUID
    section_id: UUID | None = None
    software_id: UUID
    # Which software versions this chunk is relevant to
    software_version_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    source_id: UUID
    source_type: SourceType
    authority_level: AuthorityLevel

    # Content
    text: str = Field(..., min_length=1)
    chunk_type: ChunkType = ChunkType.TEXT
    # SHA-256 of the chunk text — used for deduplication
    content_hash: str = Field(..., min_length=64, max_length=64)

    # Position metadata
    position_in_section: int = Field(..., ge=0)
    position_in_document: int = Field(..., ge=0)

    # Token budget tracking
    token_count: int | None = None

    # Embedding metadata (populated after embedding is generated)
    embedding_model: str | None = None
    embedding_model_version: str | None = None

    document_type: DocumentType = DocumentType.OTHER
    language: str = Field(default="en")
    created_at: datetime = Field(default_factory=utc_now)

class KnowledgeRecord(SIPBaseModel):
    """Flattened provenance bundle for a single retrieved Chunk.

    Carries the Chunk together with all parent metadata needed to produce
    a complete Citation. Created by the retrieval layer — never persisted.
    """

    chunk: Chunk
    document: Document
    document_version: DocumentVersion
    source: Source
    software: Software
    # The specific version this record is associated with (if determinable)
    software_version: SoftwareVersion | None = None
