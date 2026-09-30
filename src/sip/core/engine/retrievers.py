"""Retriever Implementations for M2."""

from uuid import UUID

try:
    import bm25s  # type: ignore

    HAS_BM25S = True
except ImportError:
    HAS_BM25S = False

from sip.core.contracts.knowledge import KnowledgeRecord
from sip.core.protocols.retrieval import LexicalRetriever, SemanticRetriever

class MockSemanticRetriever(SemanticRetriever):
    """In-memory vector similarity for testing."""

    def __init__(self, data: list[KnowledgeRecord]) -> None:
        """Initialize with some mock data."""
        self.data = data

    async def search(
        self,
        query_vector: list[float],
        expert_id: UUID,
        version_filter: dict[str, str | list[str]],
        top_k: int,
    ) -> list[tuple[KnowledgeRecord, float]]:
        """Mock search returning random/top records."""
        # Just return up to top_k records with mock scores
        results = []
        for i, record in enumerate(self.data[:top_k]):
            # Mock score: 1.0 - 0.1 * i
            results.append((record, max(0.1, 1.0 - (0.1 * i))))
        return results

class BM25SRetriever(LexicalRetriever):
    """BM25S library integration."""

    def __init__(self, data: list[KnowledgeRecord], mock: bool = False) -> None:
        """Initialize the BM25S index with data."""
        self.data = data
        self.mock = mock or not HAS_BM25S

        if not self.mock:
            self.retriever = bm25s.BM25()
            if data:
                # Tokenize chunk contents
                corpus = [record.chunk.text for record in data]
                corpus_tokens = bm25s.tokenize(corpus)
                self.retriever.index(corpus_tokens)

    async def search(
        self,
        query_text: str,
        expert_id: UUID,
        version_filter: dict[str, str | list[str]],
        top_k: int,
    ) -> list[tuple[KnowledgeRecord, float]]:
        """Search the BM25S index."""
        if not self.data:
            return []

        if self.mock:
            # Mock keyword search: just return random/top items based on a heuristic
            results = []
            for i, record in enumerate(self.data[:top_k]):
                # Give a mock BM25 score <= 1.0
                results.append((record, max(0.1, 1.0 - (0.1 * i))))
            return results

        query_tokens = bm25s.tokenize(query_text)
        results, scores = self.retriever.retrieve(query_tokens, corpus=self.data, k=top_k)

        # Format results
        output = []
        # BM25S retrieve returns results and scores as numpy arrays of shape (1, k)
        for i in range(len(results[0])):
            record = results[0][i]
            score = float(scores[0][i])
            output.append((record, score))

        return output
