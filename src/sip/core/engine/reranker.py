"""Cross-Encoder Reranker."""

from sip.core.contracts.rag import Evidence, Query, RetrievalPlan, RetrievalResult

class CrossEncoderReranker:
    """Reranks candidates using a sentence-transformers CrossEncoder."""

    def __init__(
        self, model_name: str = "cross-encoder/ms-marco-TinyBERT-L-2-v2", mock: bool = False
    ) -> None:
        """Initialize the reranker."""
        self.model_name = model_name
        self.mock = mock
        if not mock:
            from sentence_transformers import CrossEncoder  # type: ignore

            self.model = CrossEncoder(model_name)

    async def rerank(
        self, query: Query, result: RetrievalResult, plan: RetrievalPlan
    ) -> list[Evidence]:
        """Rerank the fused candidates."""
        if not result.candidates:
            return []

        candidates = list(result.candidates)

        if self.mock:
            # Just keep original RRF order and mock the scores
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

        # Real cross-encoder scoring
        query_text = query.text
        pairs = [(query_text, cand.knowledge_record.chunk.text) for cand in candidates]

        scores = self.model.predict(pairs)

        # Combine candidates with scores
        scored_candidates = list(zip(candidates, scores, strict=False))
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        evidence_list = []
        for i, (cand, score) in enumerate(scored_candidates[: plan.rerank_top_k]):
            evidence_list.append(
                Evidence(
                    chunk_id=cand.chunk_id,
                    knowledge_record=cand.knowledge_record,
                    reranker_score=float(score),
                    rank=i + 1,
                    fusion_score=cand.score,
                )
            )

        return evidence_list
