"""Ingestion Pipeline orchestration."""

import logging
from collections.abc import AsyncGenerator
from datetime import UTC

from sip.core.contracts import Document, DocumentVersion, Source
from sip.core.protocols.ingestion import (
    Chunker,
    Embedder,
    Fetcher,
    Indexer,
    Parser,
    SourceAdapter,
)

logger = logging.getLogger(__name__)


class BasicSourceAdapter(SourceAdapter):
    """A basic generic source adapter that fetches and indexes a single URL as a Document."""

    def __init__(
        self,
        fetcher: Fetcher,
        parser: Parser,
        chunker: Chunker,
        embedder: Embedder,
        indexer: Indexer,
    ) -> None:
        self.fetcher = fetcher
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.indexer = indexer

    async def run(self, source: Source) -> AsyncGenerator[Document, None]:
        """Crawl the source URL."""
        logger.info(f"Starting crawl for {source.url}")

        # 1. Fetch
        artifact = await self.fetcher.fetch(source.url)

        # 2. Parse
        content = await self.parser.parse(artifact)

        # In a real system, we'd detect Document/Version from DB. For now:
        from datetime import datetime
        from uuid import uuid4

        from sip.core.contracts import DocumentType

        doc = Document(
            id=uuid4(),
            source_id=source.id,
            software_id=source.software_id,
            url=source.url,
            document_type=DocumentType.OTHER,
            title="Generated Document",
            language="en",
            created_at=datetime.now(UTC),
        )

        import hashlib

        doc_version = DocumentVersion(
            id=uuid4(),
            document_id=doc.id,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            version_number=1,
            fetched_at=datetime.now(UTC),
        )

        # 3. Chunk
        chunks = self.chunker.chunk(content, doc_version, doc, source)

        if not chunks:
            logger.warning("No chunks generated.")
            return

        # 4. Embed
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedder.embed(texts)

        # 5. Index
        await self.indexer.index(chunks, embeddings)

        logger.info(f"Indexed {len(chunks)} chunks for {source.url}")
        yield doc
