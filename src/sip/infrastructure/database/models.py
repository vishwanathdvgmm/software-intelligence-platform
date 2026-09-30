"""SQLAlchemy models for PostgreSQL storage."""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from sip.core.contracts.knowledge import AuthorityLevel, ChunkType, DocumentType, SourceType

class Base(DeclarativeBase):
    """Base for all SQLAlchemy models."""

    pass

class SoftwareModel(Base):
    __tablename__ = "software"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    homepage_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    versions: Mapped[list["SoftwareVersionModel"]] = relationship(back_populates="software")
    sources: Mapped[list["SourceModel"]] = relationship(back_populates="software")

class SoftwareVersionModel(Base):
    __tablename__ = "software_versions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    software_id: Mapped[UUID] = mapped_column(ForeignKey("software.id"), nullable=False)
    version_string: Mapped[str] = mapped_column(String(100), nullable=False)
    major: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    patch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    release_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    software: Mapped["SoftwareModel"] = relationship(back_populates="versions")

# Association table for Source to SoftwareVersion
source_version_assoc = Table(
    "source_software_versions",
    Base.metadata,
    Column("source_id", PG_UUID(as_uuid=True), ForeignKey("sources.id"), primary_key=True),
    Column(
        "software_version_id",
        PG_UUID(as_uuid=True),
        ForeignKey("software_versions.id"),
        primary_key=True,
    ),
)

class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    software_id: Mapped[UUID] = mapped_column(ForeignKey("software.id"), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    authority_level: Mapped[AuthorityLevel] = mapped_column(
        Enum(AuthorityLevel), default=AuthorityLevel.OFFICIAL
    )
    name: Mapped[str] = mapped_column(String, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    crawl_frequency_hours: Mapped[int] = mapped_column(Integer, default=24)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    software: Mapped["SoftwareModel"] = relationship(back_populates="sources")
    versions: Mapped[list["SoftwareVersionModel"]] = relationship(secondary=source_version_assoc)
    documents: Mapped[list["DocumentModel"]] = relationship(back_populates="source")

class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    software_id: Mapped[UUID] = mapped_column(ForeignKey("software.id"), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), default=DocumentType.OTHER
    )
    title: Mapped[str] = mapped_column(String, default="")
    language: Mapped[str] = mapped_column(String, default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["SourceModel"] = relationship(back_populates="documents")
    versions: Mapped[list["DocumentVersionModel"]] = relationship(back_populates="document")

class DocumentVersionModel(Base):
    __tablename__ = "document_versions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    raw_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    ingestion_run_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    document: Mapped["DocumentModel"] = relationship(back_populates="versions")
    sections: Mapped[list["SectionModel"]] = relationship(back_populates="document_version")
    chunks: Mapped[list["ChunkModel"]] = relationship(back_populates="document_version")

class SectionModel(Base):
    __tablename__ = "sections"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id"), nullable=False
    )
    parent_section_id: Mapped[UUID | None] = mapped_column(ForeignKey("sections.id"), nullable=True)
    heading: Mapped[str] = mapped_column(String, default="")
    heading_level: Mapped[int] = mapped_column(Integer, default=1)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    document_version: Mapped["DocumentVersionModel"] = relationship(back_populates="sections")

# Association table for Chunk to SoftwareVersion
chunk_version_assoc = Table(
    "chunk_software_versions",
    Base.metadata,
    Column("chunk_id", PG_UUID(as_uuid=True), ForeignKey("chunks.id"), primary_key=True),
    Column(
        "software_version_id",
        PG_UUID(as_uuid=True),
        ForeignKey("software_versions.id"),
        primary_key=True,
    ),
)

class ChunkModel(Base):
    __tablename__ = "chunks"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id"), nullable=False
    )
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    section_id: Mapped[UUID | None] = mapped_column(ForeignKey("sections.id"), nullable=True)
    software_id: Mapped[UUID] = mapped_column(ForeignKey("software.id"), nullable=False)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    authority_level: Mapped[AuthorityLevel] = mapped_column(Enum(AuthorityLevel), nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_type: Mapped[ChunkType] = mapped_column(Enum(ChunkType), default=ChunkType.TEXT)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    position_in_section: Mapped[int] = mapped_column(Integer, nullable=False)
    position_in_document: Mapped[int] = mapped_column(Integer, nullable=False)

    document_version: Mapped["DocumentVersionModel"] = relationship(back_populates="chunks")
    software_versions: Mapped[list["SoftwareVersionModel"]] = relationship(
        secondary=chunk_version_assoc
    )

class ExpertModel(Base):
    __tablename__ = "experts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    config_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class ExpertVersionModel(Base):
    __tablename__ = "expert_versions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    expert_id: Mapped[UUID] = mapped_column(ForeignKey("experts.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    config_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    change_reason: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[str] = mapped_column(String, default="system")
