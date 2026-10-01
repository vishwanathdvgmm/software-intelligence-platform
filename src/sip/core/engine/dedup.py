"""Candidate Deduplication."""

from typing import List
from uuid import UUID

from sip.core.contracts.rag import RetrievalCandidate

class CandidateDeduplicator:
    """Removes duplicate candidates based on canonical identity."""

    async def deduplicate(self, candidates: List[RetrievalCandidate]) -> List[RetrievalCandidate]:
        """Deduplicate candidates by chunk_id."""
        seen: set[UUID] = set()
        unique = []
        for cand in candidates:
            if cand.chunk_id not in seen:
                seen.add(cand.chunk_id)
                unique.append(cand)
        return unique
