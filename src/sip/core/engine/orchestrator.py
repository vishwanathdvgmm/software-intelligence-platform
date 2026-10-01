"""Adaptive RAG Engine Orchestrator."""

import asyncio
import time
import structlog
from typing import Optional

from sip.core.contracts.rag import (
    Context,
    EvidenceSufficiencyAssessment,
    EvidenceSufficiency,
    Query,
    RetrievalStrategy,
    RetrievalVersionSnapshot,
    RetrievalCandidate,
)

from sip.core.protocols.rag import (
    QueryAnalyzerProtocol,
    RetrievalPlannerProtocol,
    ResultFusionProtocol,
    CandidateDeduplicatorProtocol,
    RerankerProtocol,
    ContextOptimizerProtocol,
    EvidenceEvaluatorProtocol,
    EvidenceGateProtocol,
    MetadataFilterProtocol,
)

from sip.core.protocols.retrieval import LexicalRetriever, SemanticRetriever

logger = structlog.get_logger(__name__)

class AdaptiveRAGEngine:
    """Orchestrates the full Adaptive RAG pipeline.
    
    Implements a bounded adaptive loop.
    """

    def __init__(
        self,
        analyzer: QueryAnalyzerProtocol,
        planner: RetrievalPlannerProtocol,
        semantic_retriever: SemanticRetriever,
        lexical_retriever: LexicalRetriever,
        metadata_filter: MetadataFilterProtocol,
        fusion: ResultFusionProtocol,
        deduplicator: CandidateDeduplicatorProtocol,
        reranker: RerankerProtocol,
        optimizer: ContextOptimizerProtocol,
        evaluator: EvidenceEvaluatorProtocol,
        gate: EvidenceGateProtocol,
        max_iterations: int = 3,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.analyzer = analyzer
        self.planner = planner
        self.semantic_retriever = semantic_retriever
        self.lexical_retriever = lexical_retriever
        self.metadata_filter = metadata_filter
        self.fusion = fusion
        self.deduplicator = deduplicator
        self.reranker = reranker
        self.optimizer = optimizer
        self.evaluator = evaluator
        self.gate = gate
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds

    async def retrieve_context(self, query: Query) -> tuple[Context, EvidenceSufficiencyAssessment]:
        """Execute the adaptive retrieval pipeline."""
        try:
            return await asyncio.wait_for(
                self._adaptive_loop(query),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.warning("rag.pipeline.timeout", query_id=str(query.id))
            raise RuntimeError("RAG Pipeline timed out")
        except asyncio.CancelledError:
            logger.warning("rag.pipeline.cancelled", query_id=str(query.id))
            raise RuntimeError("RAG Pipeline was cancelled")

    async def _adaptive_loop(self, query: Query) -> tuple[Context, EvidenceSufficiencyAssessment]:
        logger.info("rag.pipeline.start", query_id=str(query.id), expert_id=str(query.expert_id))

        # Query analysis happens once (immutable original query)
        analysis = await self.analyzer.analyze(query)
        logger.debug("rag.analyzed", query_type=analysis.query_type)

        iteration = 0
        last_evidence_count = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.info("rag.iteration.start", iteration=iteration)

            # Generate Retrieval Plan (could adapt based on iteration state if the planner supported it)
            plan = await self.planner.plan(analysis)
            logger.debug("rag.planned", strategy=plan.strategy)
            
            # Apply Metadata Filter
            version_filter = self.metadata_filter.build_filter(analysis)
            
            # Update plan with the generated filter
            plan = plan.model_copy(update={"version_filter": version_filter})

            semantic_cands: list[RetrievalCandidate] = []
            lexical_cands: list[RetrievalCandidate] = []

            # Execute Retrieval
            if plan.strategy in (RetrievalStrategy.SEMANTIC, RetrievalStrategy.HYBRID):
                results = await self.semantic_retriever.search(
                    query_text=query.text,
                    expert_id=query.expert_id,
                    version_filter=plan.version_filter,
                    top_k=plan.semantic_top_k,
                )
                
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

            # Fuse & Deduplicate
            fused_result = await self.fusion.fuse(semantic_cands, lexical_cands, plan)
            
            dedup_cands = await self.deduplicator.deduplicate(list(fused_result.candidates))
            fused_result = fused_result.model_copy(update={"candidates": tuple(dedup_cands)})
            logger.debug("rag.fused", total_candidates=len(fused_result.candidates))
            
            # Rerank
            evidence = await self.reranker.rerank(query, fused_result, plan)
            logger.debug("rag.reranked", top_evidence=len(evidence))

            # Optimize Context
            context = await self.optimizer.optimize(query, evidence)
            logger.info("rag.optimized", token_count=context.token_count)

            # Evaluate Evidence
            assessment = await self.evaluator.evaluate(query, evidence)
            logger.info("rag.evaluated", sufficiency=assessment.sufficiency)

            # Evidence Gate
            is_sufficient = await self.gate.enforce(assessment)
            
            if is_sufficient:
                logger.info("rag.pipeline.complete", token_count=context.token_count, iteration=iteration)
                return context, assessment
                
            # No-progress check
            if len(evidence) == last_evidence_count:
                logger.warning("rag.no_progress", iteration=iteration)
                # Terminate early due to no progress
                break
                
            last_evidence_count = len(evidence)
            
        logger.warning("rag.pipeline.max_iterations_reached")
        # Return best effort context and assessment
        return context, assessment # type: ignore
