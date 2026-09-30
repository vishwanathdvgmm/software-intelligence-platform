"""Interactive test script for the ingestion pipeline components."""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4
import hashlib

from sip.core.contracts import Document, DocumentType, DocumentVersion, Source, SourceType, AuthorityLevel
from sip.ingestion.chunker import MarkdownChunker
from sip.ingestion.fetcher import HttpxFetcher
from sip.ingestion.parser import HtmlParser

async def main() -> None:
    print("="*60)
    print("SIP Ingestion Pipeline - Interactive Component Test")
    print("="*60)
    
    url = input("\n🌐 Enter a URL to test (default: https://example.com): ").strip()
    if not url:
        url = "https://example.com"
        
    print(f"\n[STEP 1: FETCHER]")
    print(f"Initializing HttpxFetcher and fetching {url}...")
    fetcher = HttpxFetcher()
    
    artifact = await fetcher.fetch(url)
    print(f"✅ Success! Received artifact with status {artifact.status_code}")
    print(f"Content Type: {artifact.content_type}")
    print(f"Raw Bytes (first 200 chars): {artifact.content[:200]!r}...\n")
    
    input("Press Enter to continue to Parsing...")
    
    print(f"\n[STEP 2: PARSER]")
    print("Initializing HtmlParser...")
    parser = HtmlParser()
    
    parsed_text = await parser.parse(artifact)
    print(f"✅ Success! Extracted plain text.")
    print(f"Extracted Length: {len(parsed_text)} characters")
    print(f"--- Parsed Text Preview ---")
    print(f"{parsed_text[:300]}")
    print(f"---------------------------\n")
    
    input("Press Enter to continue to Chunking...")
    
    print(f"\n[STEP 3: CHUNKER]")
    print("Initializing MarkdownChunker (Max Size: 500 chars)...")
    chunker = MarkdownChunker(max_chunk_size=500)
    
    # Setup dummy models for chunker
    software_id = uuid4()
    source = Source(
        id=uuid4(),
        software_id=software_id,
        url=url,
        source_type=SourceType.OFFICIAL_DOCS,
        authority_level=AuthorityLevel.OFFICIAL,
        name="Interactive Test",
    )
    
    doc = Document(
        id=uuid4(),
        source_id=source.id,
        software_id=source.software_id,
        url=source.url,
        document_type=DocumentType.OTHER,
        title="Interactive Document",
        language="en",
        created_at=datetime.now(UTC),
    )

    doc_version = DocumentVersion(
        id=uuid4(),
        document_id=doc.id,
        content_hash=hashlib.sha256(parsed_text.encode()).hexdigest(),
        version_number=1,
        fetched_at=datetime.now(UTC),
    )
    
    chunks = chunker.chunk(parsed_text, doc_version, doc, source)
    
    print(f"✅ Success! Generated {len(chunks)} chunks.")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(f"ID: {chunk.id}")
        print(f"Hash: {chunk.content_hash}")
        print(f"Position: {chunk.position_in_document}")
        print(f"Length: {len(chunk.text)} chars")
        print(f"Content:\n{chunk.text}")
        print("-" * 15)
        
    if len(chunks) > 3:
        print(f"\n... and {len(chunks) - 3} more chunks.")
        
    print("\n[PIPELINE COMPLETE]")
    await fetcher.close()

if __name__ == "__main__":
    asyncio.run(main())
