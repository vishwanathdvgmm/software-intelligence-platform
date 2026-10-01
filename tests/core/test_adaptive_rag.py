"""Tests for Adaptive RAG Pipeline."""

import asyncio
import pytest
from typing import List, Dict, Union, Any, Tuple
from uuid import UUID, uuid4
from sip.core.contracts.rag import (
    Query, QueryType, QueryComplexity, QueryAnalysis, 
    RetrievalStrategy, RetrievalVersionSnapshot, RetrievalPlan,
    RetrievalCandidate, RetrievalResult, Evidence, 
    EvidenceSufficiencyAssessment, EvidenceSufficiency, Context
)
from sip.core.contracts.knowledge import (
    KnowledgeRecord, Chunk, ChunkType, Source, SourceType, Software, SoftwareVersion, AuthorityLevel
)
from sip.core.engine.orchestrator import AdaptiveRAGEngine

class FakeQueryAnalyzer:
    async def analyze(self, query: Query) -> QueryAnalysis:
        return QueryAnalysis(
            query_id=query.id, query_type=QueryType.FACTUAL, complexity=QueryComplexity.SIMPLE
        )

class FakeRetrievalPlanner:
    async def plan(self, analysis: QueryAnalysis) -> RetrievalPlan:
        snap = RetrievalVersionSnapshot(
            expert_id=uuid4(), expert_version="1", embedding_model="m",
            embedding_model_version="1", embedding_dimension=384,
            reranker_model="r", reranker_model_version="1",
            semantic_top_k=5, lexical_top_k=5, rerank_top_k=5, strategy=RetrievalStrategy.HYBRID
        )
        return RetrievalPlan(
            query_id=analysis.query_id, strategy=RetrievalStrategy.HYBRID,
            version_snapshot=snap, semantic_top_k=5, lexical_top_k=5, rerank_top_k=5, rrf_k=60
        )

class FakeSemanticRetriever:
    async def search(
        self, query_text: str, expert_id: UUID, version_filter: Dict[str, Union[str, List[str]]], top_k: int
    ) -> List[Tuple[KnowledgeRecord, float]]:
        return []

class FakeLexicalRetriever:
    async def search(
        self, query_text: str, expert_id: UUID, version_filter: Dict[str, Union[str, List[str]]], top_k: int
    ) -> List[Tuple[KnowledgeRecord, float]]:
        return []

class FakeMetadataFilter:
    def build_filter(self, analysis: QueryAnalysis) -> Dict[str, Union[str, List[str]]]:
        return {}

class FakeFusion:
    async def fuse(
        self, semantic_cands: List[RetrievalCandidate], lexical_cands: List[RetrievalCandidate], plan: RetrievalPlan
    ) -> RetrievalResult:
        return RetrievalResult(query_id=plan.query_id, candidates=tuple())

class FakeDeduplicator:
    async def deduplicate(self, candidates: List[RetrievalCandidate]) -> List[RetrievalCandidate]:
        return candidates

class FakeReranker:
    async def rerank(self, query: Query, result: RetrievalResult, plan: RetrievalPlan) -> List[Evidence]:
        return []

class FakeContextOptimizer:
    async def optimize(self, query: Query, evidence: List[Evidence]) -> Context:
        return Context(query_id=query.id, evidence_items=tuple(), rendered_text="", token_count=0)

class FakeEvidenceEvaluator:
    async def evaluate(self, query: Query, evidence: List[Evidence]) -> EvidenceSufficiencyAssessment:
        return EvidenceSufficiencyAssessment(
            query_id=query.id, sufficiency=EvidenceSufficiency.SUFFICIENT,
            confidence=1.0, attempt_number=1
        )

class FakeEvidenceGate:
    async def enforce(self, assessment: EvidenceSufficiencyAssessment) -> bool:
        return assessment.sufficiency == EvidenceSufficiency.SUFFICIENT


@pytest.mark.asyncio
async def test_adaptive_rag_pipeline_success() -> None:
    engine = AdaptiveRAGEngine(
        analyzer=FakeQueryAnalyzer(),
        planner=FakeRetrievalPlanner(),
        semantic_retriever=FakeSemanticRetriever(),
        lexical_retriever=FakeLexicalRetriever(),
        metadata_filter=FakeMetadataFilter(),
        fusion=FakeFusion(),
        deduplicator=FakeDeduplicator(),
        reranker=FakeReranker(),
        optimizer=FakeContextOptimizer(),
        evaluator=FakeEvidenceEvaluator(),
        gate=FakeEvidenceGate(),
    )
    
    query = Query(expert_id=uuid4(), text="How to use SIP?")
    context, assessment = await engine.retrieve_context(query)
    
    assert context is not None
    assert assessment.sufficiency == EvidenceSufficiency.SUFFICIENT

@pytest.mark.asyncio
async def test_adaptive_rag_pipeline_timeout() -> None:
    class SlowEvaluator(FakeEvidenceEvaluator):
        async def evaluate(self, query: Query, evidence: List[Evidence]) -> EvidenceSufficiencyAssessment:
            await asyncio.sleep(0.5)
            return await super().evaluate(query, evidence)

    engine = AdaptiveRAGEngine(
        analyzer=FakeQueryAnalyzer(),
        planner=FakeRetrievalPlanner(),
        semantic_retriever=FakeSemanticRetriever(),
        lexical_retriever=FakeLexicalRetriever(),
        metadata_filter=FakeMetadataFilter(),
        fusion=FakeFusion(),
        deduplicator=FakeDeduplicator(),
        reranker=FakeReranker(),
        optimizer=FakeContextOptimizer(),
        evaluator=SlowEvaluator(),
        gate=FakeEvidenceGate(),
        timeout_seconds=0.1
    )
    
    query = Query(expert_id=uuid4(), text="Timeout test")
    
    with pytest.raises(RuntimeError, match="timed out"):
        await engine.retrieve_context(query)

@pytest.mark.asyncio
async def test_adaptive_rag_pipeline_max_iterations() -> None:
    class AlwaysInsufficientEvaluator(FakeEvidenceEvaluator):
        async def evaluate(self, query: Query, evidence: List[Evidence]) -> EvidenceSufficiencyAssessment:
            return EvidenceSufficiencyAssessment(
                query_id=query.id, sufficiency=EvidenceSufficiency.INSUFFICIENT,
                confidence=1.0, attempt_number=1
            )
            
    class ProgressReranker(FakeReranker):
        def __init__(self) -> None:
            self.count = 0
            
        async def rerank(self, query: Query, result: RetrievalResult, plan: RetrievalPlan) -> List[Evidence]:
            self.count += 1
            doc_id = uuid4()
            doc_ver_id = uuid4()
            soft_id = uuid4()
            src_id = uuid4()
            
            from sip.core.contracts.knowledge import Document, DocumentVersion, DocumentType
            doc = Document(software_id=soft_id, source_id=src_id, document_type=DocumentType.OTHER, url="a") # type: ignore
            doc_v = DocumentVersion(document_id=doc_id, content_hash="a" * 64, version_number=1)
            kr = KnowledgeRecord(
                software=Software(slug="sip", name="sip", description=""),
                software_version=SoftwareVersion(software_id=soft_id, version_name="1", version_string="1"),
                source=Source(software_id=soft_id, source_type=SourceType.OFFICIAL_DOCS, url="a", uri="a"), # type: ignore
                document=doc,
                document_version=doc_v,
                chunk=Chunk(source_id=src_id, chunk_type=ChunkType.TEXT, text="a", token_count=1,
                            document_id=doc_id, document_version_id=doc_ver_id, software_id=soft_id,
                            source_type=SourceType.OFFICIAL_DOCS, authority_level=AuthorityLevel.OFFICIAL,
                            content_hash="a" * 64, position_in_section=1, position_in_document=1)
            )
            return [
                Evidence(chunk_id=uuid4(), knowledge_record=kr, reranker_score=1.0, rank=1)
                for _ in range(self.count)
            ]

    engine = AdaptiveRAGEngine(
        analyzer=FakeQueryAnalyzer(),
        planner=FakeRetrievalPlanner(),
        semantic_retriever=FakeSemanticRetriever(),
        lexical_retriever=FakeLexicalRetriever(),
        metadata_filter=FakeMetadataFilter(),
        fusion=FakeFusion(),
        deduplicator=FakeDeduplicator(),
        reranker=ProgressReranker(),
        optimizer=FakeContextOptimizer(),
        evaluator=AlwaysInsufficientEvaluator(),
        gate=FakeEvidenceGate(),
        max_iterations=2
    )
    
    query = Query(expert_id=uuid4(), text="Iteration test")
    
    context, assessment = await engine.retrieve_context(query)
    assert assessment.sufficiency == EvidenceSufficiency.INSUFFICIENT
