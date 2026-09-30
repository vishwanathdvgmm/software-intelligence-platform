"""RRF Fusion and Deduplication."""

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
        """Fuse candidates using RRF and deduplicate."""
        start_time = time.perf_counter()

        # Dictionary to accumulate RRF scores by chunk_id
        # chunk_id -> (merged_candidate, rrf_score)
        fused: dict[UUID, tuple[RetrievalCandidate, float]] = {}

        def add_candidates(candidates: list[RetrievalCandidate]) -> None:
            for idx, candidate in enumerate(candidates):
                # RRF score = 1 / (k + rank)
                # We use idx + 1 as rank if candidate.rank is not set or to be safe
                rank = candidate.rank if candidate.rank > 0 else idx + 1
                score = 1.0 / (plan.rrf_k + rank)

                if candidate.chunk_id in fused:
                    existing_cand, existing_score = fused[candidate.chunk_id]
                    # Accumulate score
                    fused[candidate.chunk_id] = (existing_cand, existing_score + score)
                else:
                    fused[candidate.chunk_id] = (candidate, score)

        add_candidates(semantic_candidates)
        add_candidates(lexical_candidates)

        # Sort by accumulated RRF score descending
        sorted_fused = sorted(fused.values(), key=lambda x: x[1], reverse=True)

        # Rebuild candidates with updated scores and ranks
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

        duplicates_removed = (len(semantic_candidates) + len(lexical_candidates)) - len(
            final_candidates
        )
        latency = (time.perf_counter() - start_time) * 1000

        return RetrievalResult(
            query_id=plan.query_id,
            candidates=tuple(final_candidates),
            semantic_count=len(semantic_candidates),
            lexical_count=len(lexical_candidates),
            duplicates_removed=duplicates_removed,
            fusion_latency_ms=latency,
        )
