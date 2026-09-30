"""Storage-agnostic retrieval protocols — M2 requirement.

The entire Adaptive RAG Engine (Phase 3) must depend ONLY on these protocols.
It must not import Qdrant, BM25S, or PostgreSQL clients. This guarantees that
the RAG core is fully decoupled from the storage implementation (Change 2).
"""

from typing import Protocol
from uuid import UUID

from sip.core.contracts import Chunk, KnowledgeRecord


class SemanticRetriever(Protocol):
    """Protocol for semantic vector retrieval (e.g. Qdrant)."""

    async def search(
        self,
        query_vector: list[float],
        expert_id: UUID,
        version_filter: dict[str, str | list[str]],
        top_k: int,
    ) -> list[tuple[KnowledgeRecord, float]]:
        """Search for semantically similar chunks.

        Args:
            query_vector: The embedded query.
            expert_id: Scopes retrieval to sources associated with this Expert.
            version_filter: Explicit software version requirements.
            top_k: Maximum number of results to return.

        Returns:
            List of (KnowledgeRecord, similarity_score) tuples, sorted by score descending.
        """
        ...


class LexicalRetriever(Protocol):
    """Protocol for lexical keyword retrieval (e.g. BM25S)."""

    async def search(
        self,
        query_text: str,
        expert_id: UUID,
        version_filter: dict[str, str | list[str]],
        top_k: int,
    ) -> list[tuple[KnowledgeRecord, float]]:
        """Search for keyword-matching chunks.

        Args:
            query_text: The raw user query or transformed query.
            expert_id: Scopes retrieval to sources associated with this Expert.
            version_filter: Explicit software version requirements.
            top_k: Maximum number of results to return.

        Returns:
            List of (KnowledgeRecord, bm25_score) tuples, sorted by score descending.
        """
        ...


class ChunkRepository(Protocol):
    """Protocol for retrieving chunks by ID (used for deduplication/hydration)."""

    async def get_by_ids(self, chunk_ids: list[UUID]) -> dict[UUID, Chunk]:
        """Fetch chunks by their IDs.

        Returns:
            Dictionary mapping chunk_id to Chunk. Missing IDs are omitted.
        """
        ...

    async def get_records_by_chunk_ids(self, chunk_ids: list[UUID]) -> dict[UUID, KnowledgeRecord]:
        """Fetch full KnowledgeRecords for the given chunk IDs.

        Returns:
            Dictionary mapping chunk_id to KnowledgeRecord. Missing IDs are omitted.
        """
        ...
