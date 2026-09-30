"""Test script for the ingestion pipeline."""

import asyncio
import logging
from uuid import uuid4

from sip.core.contracts import Chunk, DocumentType, Source, SourceType, AuthorityLevel
from sip.core.protocols.ingestion import Embedder, Indexer
from sip.ingestion.chunker import MarkdownChunker
from sip.ingestion.fetcher import HttpxFetcher
from sip.ingestion.parser import HtmlParser
from sip.ingestion.pipeline import BasicSourceAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class MockEmbedder(Embedder):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Return dummy embeddings of dimension 3
        return [[0.1, 0.2, 0.3] for _ in texts]


class MockIndexer(Indexer):
    async def index(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        print(f"\n--- MockIndexer: Indexed {len(chunks)} chunks! ---")
        for i, chunk in enumerate(chunks[:2]):
            print(f"Chunk {i+1}:")
            print(f"  ID: {chunk.id}")
            print(f"  Length: {len(chunk.text)} chars")
            print(f"  Hash: {chunk.content_hash}")
            print(f"  Content Preview: {chunk.text[:100]}...\n")
        if len(chunks) > 2:
            print(f"... and {len(chunks) - 2} more chunks.\n")


async def main() -> None:
    print("Initializing components...")
    fetcher = HttpxFetcher()
    parser = HtmlParser()
    chunker = MarkdownChunker(max_chunk_size=500)
    embedder = MockEmbedder()
    indexer = MockIndexer()

    adapter = BasicSourceAdapter(
        fetcher=fetcher,
        parser=parser,
        chunker=chunker,
        embedder=embedder,
        indexer=indexer,
    )

    # Create a mock Source
    software_id = uuid4()
    source = Source(
        id=uuid4(),
        software_id=software_id,
        url="https://example.com",
        source_type=SourceType.OFFICIAL_DOCS,
        authority_level=AuthorityLevel.OFFICIAL,
        name="Example Domain",
    )

    print(f"\nStarting ingestion for: {source.url}")
    
    async for doc in adapter.run(source):
        print(f"Ingested Document: {doc.title} (URL: {doc.url})")

    await fetcher.close()
    print("\nIngestion test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
