"""RRF Fusion."""

import time
from uuid import UUID

from sip.core.contracts.rag import RetrievalCandidate, RetrievalPlan, RetrievalResult

class RRFFusion:
    """Reciprocal Rank Fusion."""

    async def fuse(
        self,
        semantic_candidates: list[RetrievalCandidate],
        lexical_candidates: list[RetrievalCandidate],
        plan: RetrievalPlan,
    ) -> RetrievalResult:
        """Fuse candidates using RRF."""
        start_time = time.perf_counter()

        fused: dict[UUID, tuple[RetrievalCandidate, float]] = {}

        def add_candidates(candidates: list[RetrievalCandidate]) -> None:
            for idx, candidate in enumerate(candidates):
                rank = candidate.rank if candidate.rank > 0 else idx + 1
                score = 1.0 / (plan.rrf_k + rank)

                if candidate.chunk_id in fused:
                    existing_cand, existing_score = fused[candidate.chunk_id]
                    fused[candidate.chunk_id] = (existing_cand, existing_score + score)
                else:
                    fused[candidate.chunk_id] = (candidate, score)

        add_candidates(semantic_candidates)
        add_candidates(lexical_candidates)

        sorted_fused = sorted(fused.values(), key=lambda x: x[1], reverse=True)

        final_candidates = []
        for i, (candidate, rrf_score) in enumerate(sorted_fused):
            final_candidates.append(
                RetrievalCandidate(
                    chunk_id=candidate.chunk_id,
                    knowledge_record=candidate.knowledge_record,
                    score=rrf_score,
                    retriever="fusion",
                    rank=i + 1,
                )
            )

        latency = (time.perf_counter() - start_time) * 1000

        return RetrievalResult(
            query_id=plan.query_id,
            candidates=tuple(final_candidates),
            semantic_count=len(semantic_candidates),
            lexical_count=len(lexical_candidates),
            duplicates_removed=0, # handled by deduplicator
            fusion_latency_ms=latency,
        )
