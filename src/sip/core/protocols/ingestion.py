"""Storage-agnostic ingestion protocols — M4 requirements."""

from collections.abc import AsyncGenerator
from typing import Protocol

from sip.core.contracts import Chunk, Document, DocumentVersion, Source


class RawArtifact(Protocol):
    """Raw artifact retrieved from a Source."""

    url: str
    content: bytes
    content_type: str
    status_code: int


class Fetcher(Protocol):
    """Protocol for fetching resources from the web or APIs."""

    async def fetch(self, url: str) -> RawArtifact:
        """Fetch a single URL."""
        ...


class Parser(Protocol):
    """Protocol for parsing RawArtifacts into clean text/structure."""

    async def parse(self, artifact: RawArtifact) -> str:
        """Parse raw content into normalized text/Markdown."""
        ...


class Chunker(Protocol):
    """Protocol for chunking normalized text."""

    def chunk(
        self, text: str, document_version: DocumentVersion, document: Document, source: Source
    ) -> list[Chunk]:
        """Split text into semantic Chunks."""
        ...


class Embedder(Protocol):
    """Protocol for embedding text."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of strings into vectors."""
        ...


class Indexer(Protocol):
    """Protocol for persisting Chunks and their embeddings."""

    async def index(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """Store chunks in PostgreSQL and Qdrant."""
        ...


class SourceAdapter(Protocol):
    """Protocol for orchestrating ingestion for a specific Source."""

    def run(self, source: Source) -> AsyncGenerator[Document, None]:
        """Crawl, fetch, parse, and yield documents for a source."""
        ...
