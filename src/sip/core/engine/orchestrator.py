"""Adaptive RAG Engine Orchestrator."""

import structlog

from sip.core.contracts.rag import (
    Context,
    EvidenceSufficiencyAssessment,
    Query,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
)
from sip.core.engine.analyzer import QueryAnalyzer, QueryTransformer
from sip.core.engine.context import ContextOptimizer
from sip.core.engine.evaluator import EvidenceEvaluator
from sip.core.engine.fusion import RRFFusion
from sip.core.engine.planner import RetrievalPlanner
from sip.core.engine.reranker import CrossEncoderReranker
from sip.core.protocols.retrieval import LexicalRetriever, SemanticRetriever

logger = structlog.get_logger(__name__)

class AdaptiveRAGEngine:
    """Orchestrates the full Adaptive RAG pipeline."""

    def __init__(
        self,
        semantic_retriever: SemanticRetriever,
        lexical_retriever: LexicalRetriever,
        version_snapshot: RetrievalVersionSnapshot,
    ) -> None:
        """Initialize the pipeline components."""
        self.semantic_retriever = semantic_retriever
        self.lexical_retriever = lexical_retriever

        # Initialize pipeline stages
        self.analyzer = QueryAnalyzer()
        self.transformer = QueryTransformer()
        self.planner = RetrievalPlanner(version_snapshot)
        self.fusion = RRFFusion()
        self.reranker = CrossEncoderReranker(mock=True)  # Using mock for M2
        self.optimizer = ContextOptimizer()
        self.evaluator = EvidenceEvaluator()

    async def retrieve_context(self, query: Query) -> tuple[Context, EvidenceSufficiencyAssessment]:
        """Execute the retrieval pipeline to produce an optimized context."""
        logger.info("rag.pipeline.start", query_id=str(query.id), expert_id=str(query.expert_id))

        # 1. Analyze
        analysis = await self.analyzer.analyze(query)
        logger.debug("rag.analyzed", query_type=analysis.query_type)

        # 2. Plan
        plan = await self.planner.plan(analysis)
        logger.debug("rag.planned", strategy=plan.strategy)

        # 3. Retrieve
        # In a real system, the QueryTransformer might generate sub-queries here,
        # and we would retrieve for all of them concurrently.

        from sip.core.contracts.rag import RetrievalCandidate

        semantic_cands: list[RetrievalCandidate] = []
        lexical_cands: list[RetrievalCandidate] = []

        query_vector = [0.0] * 384
        try:
            # Generate real embeddings if installed
            from sentence_transformers import SentenceTransformer
            if not hasattr(self, '_embedding_model'):
                logger.info("Loading AI embedding model into memory for the first time... this may take 30-40s")
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            query_vector = self._embedding_model.encode(query.text).tolist()
        except ImportError:
            pass

        if plan.strategy in (RetrievalStrategy.SEMANTIC, RetrievalStrategy.HYBRID):
            results = await self.semantic_retriever.search(
                query_vector=query_vector,
                expert_id=query.expert_id,
                version_filter=plan.version_filter,
                top_k=plan.semantic_top_k,
            )
            # Convert to candidates (note: we don't have chunk_id directly here,
            # but we assume KnowledgeRecord has chunk_id via record.chunk.id)
            from sip.core.contracts.rag import RetrievalCandidate

            semantic_cands = [
                RetrievalCandidate(
                    chunk_id=rec.chunk.id,
                    knowledge_record=rec,
                    score=score,
                    retriever="semantic",
                    rank=i + 1,
                )
                for i, (rec, score) in enumerate(results)
            ]

        if plan.strategy in (RetrievalStrategy.LEXICAL, RetrievalStrategy.HYBRID):
            results = await self.lexical_retriever.search(
                query_text=query.text,
                expert_id=query.expert_id,
                version_filter=plan.version_filter,
                top_k=plan.lexical_top_k,
            )
            lexical_cands = [
                RetrievalCandidate(
                    chunk_id=rec.chunk.id,
                    knowledge_record=rec,
                    score=score,
                    retriever="bm25s",
                    rank=i + 1,
                )
                for i, (rec, score) in enumerate(results)
            ]

        # 4. Fuse & Deduplicate
        result = await self.fusion.fuse(semantic_cands, lexical_cands, plan)
        logger.debug("rag.fused", total_candidates=len(result.candidates))

        # 5. Rerank
        evidence = await self.reranker.rerank(query, result, plan)
        logger.debug("rag.reranked", top_evidence=len(evidence))

        # 6. Evaluate
        assessment = await self.evaluator.evaluate(query, evidence)
        logger.info("rag.evaluated", sufficiency=assessment.sufficiency)

        # 7. Optimize Context
        context = await self.optimizer.optimize(query, evidence)
        logger.info("rag.pipeline.complete", token_count=context.token_count)

        return context, assessment
