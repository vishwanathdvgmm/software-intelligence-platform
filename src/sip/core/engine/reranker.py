"""Reranker Adapter / Mock."""

from sip.core.contracts.rag import Evidence, Query, RetrievalPlan, RetrievalResult

class MockCrossEncoderReranker:
    """Mock Reranker for M2 testing without direct ML SDK dependencies.
    
    LIMITATION: Production reranking (Phase 4 Data Layer) is deferred. 
    This is a test double that simply preserves fused rank order 
    to satisfy the canonical pipeline boundary.
    """

    def __init__(self, model_name: str = "mock-model") -> None:
        """Initialize the mock reranker."""
        self.model_name = model_name

    async def rerank(
        self, query: Query, result: RetrievalResult, plan: RetrievalPlan
    ) -> list[Evidence]:
        """Rerank the fused candidates using mock scores."""
        if not result.candidates:
            return []

        candidates = list(result.candidates)
        reranked = []
        for i, cand in enumerate(candidates[: plan.rerank_top_k]):
            reranked.append(
                Evidence(
                    chunk_id=cand.chunk_id,
                    knowledge_record=cand.knowledge_record,
                    reranker_score=10.0 - i,  # Mock score
                    rank=i + 1,
                    fusion_score=cand.score,
                )
            )
        return reranked
