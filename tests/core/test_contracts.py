"""Tests for M1 Core Data Contracts.

Verifies validation, immutability, enum values, and nested structures.
"""

from uuid import UUID

import pytest
from pydantic import ValidationError

from sip.core.contracts import (
    AuthorityLevel,
    Chunk,
    ChunkType,
    Document,
    DocumentVersion,
    Expert,
    ExpertConfig,
    ExpertStatus,
    KnowledgeRecord,
    LLMRequest,
    Message,
    MessageRole,
    ModelProfile,
    RetrievalCandidate,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
    Software,
    Source,
    SourceType,
    Tool,
    ToolPermission,
)


class TestBaseModel:
    def test_immutability(self) -> None:
        software = Software(name="Docker", slug="docker")
        with pytest.raises(ValidationError, match="Instance is frozen"):
            software.name = "Docker Edited"  # type: ignore[misc]

    def test_json_serialization(self) -> None:
        software = Software(name="Docker", slug="docker", description="A platform")
        data = software.model_dump(mode="json")
        assert isinstance(data["id"], str)
        assert data["name"] == "Docker"
        assert isinstance(data["created_at"], str)


class TestKnowledgeContracts:
    def test_software_slug_lowercase(self) -> None:
        software = Software(name="Docker Engine", slug="Docker-Engine")
        assert software.slug == "docker-engine"

    def test_software_slug_invalid_chars(self) -> None:
        with pytest.raises(ValidationError):
            Software(name="Docker", slug="docker_engine!")

    def test_authority_level_weights(self) -> None:
        assert AuthorityLevel.OFFICIAL.weight == 1.0
        assert AuthorityLevel.COMMUNITY.weight == 0.5
        assert AuthorityLevel.AUTO_GENERATED.weight == 0.3

    def test_chunk_validation(self) -> None:
        # Missing required fields
        with pytest.raises(ValidationError):
            Chunk(text="some text")  # type: ignore[call-arg]

        # Valid chunk
        software = Software(name="Docker", slug="docker")
        source = Source(
            software_id=software.id,
            url="https://docs.docker.com",
            source_type=SourceType.OFFICIAL_DOCS,
        )
        doc = Document(
            source_id=source.id,
            software_id=software.id,
            url="https://docs.docker.com/engine",
        )
        doc_ver = DocumentVersion(
            document_id=doc.id,
            content_hash="a" * 64,
            version_number=1,
        )
        chunk = Chunk(
            document_version_id=doc_ver.id,
            document_id=doc.id,
            software_id=software.id,
            source_id=source.id,
            source_type=source.source_type,
            authority_level=source.authority_level,
            text="Docker is a platform.",
            content_hash="b" * 64,
            position_in_section=0,
            position_in_document=0,
        )
        assert chunk.chunk_type == ChunkType.TEXT
        assert chunk.authority_level == AuthorityLevel.OFFICIAL

        record = KnowledgeRecord(
            chunk=chunk,
            document=doc,
            document_version=doc_ver,
            source=source,
            software=software,
        )
        assert record.chunk.id == chunk.id


class TestRAGContracts:
    def test_retrieval_version_snapshot(self) -> None:
        snapshot = RetrievalVersionSnapshot(
            expert_id=UUID("00000000-0000-0000-0000-000000000000"),
            expert_version="1",
            embedding_model="test-model",
            embedding_model_version="1",
            embedding_dimension=384,
            reranker_model="test-reranker",
            reranker_model_version="1",
            semantic_top_k=20,
            lexical_top_k=20,
            rerank_top_k=10,
            strategy=RetrievalStrategy.HYBRID,
        )
        assert snapshot.rrf_k == 60
        assert snapshot.captured_at is not None

    def test_retrieval_candidate_score_bounds(self) -> None:
        software = Software(name="x", slug="x")
        source = Source(software_id=software.id, url="http://x", source_type=SourceType.OTHER)
        doc = Document(source_id=source.id, software_id=software.id, url="http://x")
        doc_ver = DocumentVersion(document_id=doc.id, content_hash="a" * 64, version_number=1)
        chunk = Chunk(
            document_version_id=doc_ver.id,
            document_id=doc.id,
            software_id=software.id,
            source_id=source.id,
            source_type=source.source_type,
            authority_level=source.authority_level,
            text="x",
            content_hash="b" * 64,
            position_in_section=0,
            position_in_document=0,
        )
        record = KnowledgeRecord(
            chunk=chunk, document=doc, document_version=doc_ver, source=source, software=software
        )

        with pytest.raises(ValidationError, match="less than or equal to 1"):
            RetrievalCandidate(
                chunk_id=chunk.id,
                knowledge_record=record,
                score=1.5,
                retriever="semantic",
                rank=1,
            )

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            RetrievalCandidate(
                chunk_id=chunk.id,
                knowledge_record=record,
                score=-0.1,
                retriever="semantic",
                rank=1,
            )


class TestExpertContracts:
    def test_expert_slug_lowercase(self) -> None:
        expert = Expert(name="Docker Expert", slug="Docker-Expert")
        assert expert.slug == "docker-expert"

    def test_expert_config_defaults(self) -> None:
        config = ExpertConfig()
        assert config.retrieval.strategy == RetrievalStrategy.HYBRID
        assert config.evidence.enable_abstention is True

    def test_expert_status_is_queryable(self) -> None:
        draft = Expert(name="A", slug="a", status=ExpertStatus.DRAFT)
        active = Expert(name="B", slug="b", status=ExpertStatus.ACTIVE)
        assert draft.is_queryable() is False
        assert active.is_queryable() is True


class TestLLMContracts:
    def test_llm_request(self) -> None:
        profile = ModelProfile(
            provider="ollama",
            model_id="qwen",
            context_window=8192,
        )
        msg = Message(role=MessageRole.USER, content="Hello")
        req = LLMRequest(model_profile=profile, messages=(msg,))
        assert req.temperature == 0.1
        assert req.max_output_tokens == 2048


class TestToolContracts:
    def test_tool_permissions(self) -> None:
        tool = Tool(
            id="read_knowledge",
            name="Read Knowledge",
            description="Reads from DB",
            required_permissions=frozenset([ToolPermission.KNOWLEDGE_READ]),
        )
        assert ToolPermission.KNOWLEDGE_READ in tool.required_permissions
        assert ToolPermission.EXPERT_WRITE not in tool.required_permissions
