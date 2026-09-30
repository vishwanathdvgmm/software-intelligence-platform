"""Tests for the Adaptive RAG Engine."""

from uuid import uuid4

import pytest

from sip.core.contracts.knowledge import (
    AuthorityLevel,
    Chunk,
    Document,
    DocumentVersion,
    KnowledgeRecord,
    Software,
    Source,
    SourceType,
)
from sip.core.contracts.rag import Query, RetrievalStrategy, RetrievalVersionSnapshot
from sip.core.engine.orchestrator import AdaptiveRAGEngine
from sip.core.engine.retrievers import BM25SRetriever, MockSemanticRetriever

@pytest.fixture
def mock_knowledge() -> list[KnowledgeRecord]:
    """Create some mock knowledge records."""
    records = []

    # Create common parents
    sw = Software(id=uuid4(), name="Docker", slug="docker")
    src = Source(
        id=uuid4(),
        software_id=sw.id,
        url="https://docs.docker.com",
        source_type=SourceType.OFFICIAL_DOCS,
        authority_level=AuthorityLevel.OFFICIAL,
    )
    doc = Document(
        id=uuid4(), source_id=src.id, software_id=sw.id, url="https://docs.docker.com/network"
    )
    doc_v = DocumentVersion(id=uuid4(), document_id=doc.id, content_hash="b" * 64, version_number=1)

    for i in range(5):
        chunk = Chunk(
            id=uuid4(),
            document_id=doc.id,
            document_version_id=doc_v.id,
            software_id=sw.id,
            source_id=src.id,
            source_type=SourceType.OFFICIAL_DOCS,
            authority_level=AuthorityLevel.OFFICIAL,
            text=f"This is mock knowledge chunk {i} about Docker networking.",
            content_hash="a" * 64,
            position_in_section=i,
            position_in_document=i,
        )
        record = KnowledgeRecord(
            chunk=chunk, document=doc, document_version=doc_v, source=src, software=sw
        )
        records.append(record)
    return records

@pytest.mark.asyncio
async def test_adaptive_rag_engine_end_to_end(mock_knowledge: list[KnowledgeRecord]) -> None:
    """Test the full pipeline end-to-end with mock data."""
    expert_id = uuid4()

    # 1. Setup mock components
    semantic_retriever = MockSemanticRetriever(data=mock_knowledge)
    lexical_retriever = BM25SRetriever(data=mock_knowledge, mock=True)

    snapshot = RetrievalVersionSnapshot(
        expert_id=expert_id,
        expert_version="v1",
        embedding_model="mock-embed-v1",
        embedding_model_version="1.0",
        embedding_dimension=384,
        reranker_model="mock-rerank-v1",
        reranker_model_version="1.0",
        semantic_top_k=20,
        lexical_top_k=20,
        rerank_top_k=10,
        strategy=RetrievalStrategy.HYBRID,
    )

    # 2. Initialize Engine
    engine = AdaptiveRAGEngine(
        semantic_retriever=semantic_retriever,
        lexical_retriever=lexical_retriever,
        version_snapshot=snapshot,
    )

    # 3. Create query
    query = Query(
        expert_id=expert_id, text="How do I configure Docker networking to avoid IP conflicts?"
    )

    # 4. Execute pipeline
    context, assessment = await engine.retrieve_context(query)

    # 5. Assertions
    assert context.query_id == query.id
    assert assessment.query_id == query.id

    # We expect some evidence items in the context
    assert len(context.evidence_items) > 0
    assert "Docker networking" in context.rendered_text

    # Check that rank and scores are present
    assert context.evidence_items[0].rank == 1
    assert context.evidence_items[0].reranker_score is not None
