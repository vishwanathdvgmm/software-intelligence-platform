import asyncio
import os
import glob
from uuid import uuid4
from datetime import datetime
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sip.infrastructure.database.models import (
    Base, SoftwareModel, SourceModel, DocumentModel, 
    DocumentVersionModel, ChunkModel
)
from sip.core.contracts.knowledge import (
    KnowledgeRecord, Chunk, Document, DocumentVersion, 
    Source, Software, DocumentType, SourceType, AuthorityLevel, ChunkType
)

# Constants
QDRANT_URL = "http://localhost:6333"
PG_URL = "postgresql+asyncpg://sip:changeme@localhost:5432/sip"
DOCS_DIR = "docs"
COLLECTION_NAME = "sip_knowledge"

async def init_db(engine: Any) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_qdrant(client: Any) -> None:
    try:
        await client.get_collection(COLLECTION_NAME)
    except Exception:
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=rest.VectorParams(
                size=384,
                distance=rest.Distance.COSINE
            )
        )

def simple_markdown_chunker(text: str) -> list[str]:
    """Splits markdown by headings (##) roughly into sections."""
    sections = text.split("\n## ")
    chunks = []
    for i, sec in enumerate(sections):
        content = sec if i == 0 else "## " + sec
        # Further split if too long (very naive)
        if len(content) > 1500:
            paragraphs = content.split("\n\n")
            current = ""
            for p in paragraphs:
                if len(current) + len(p) > 1000:
                    chunks.append(current.strip())
                    current = p
                else:
                    current += "\n\n" + p
            if current:
                chunks.append(current.strip())
        else:
            if content.strip():
                chunks.append(content.strip())
    return [c for c in chunks if len(c) > 50]

async def main() -> None:
    print("Starting SIP Ingestion Pipeline...")
    
    # Init Models
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Init Qdrant
    print("Connecting to Qdrant...")
    qdrant = AsyncQdrantClient(url=QDRANT_URL)
    await init_qdrant(qdrant)
    
    # Init Postgres
    print("Connecting to Postgres...")
    engine = create_async_engine(PG_URL)
    await init_db(engine)
    SessionLocal = async_sessionmaker(engine)
    
    # Read files
    md_files = glob.glob(f"{DOCS_DIR}/**/*.md", recursive=True)
    print(f"Found {len(md_files)} markdown files in {DOCS_DIR}/")
    
    # Base Entities
    software_id = uuid4()
    expert_id = uuid4()
    source_id = uuid4()
    
    sw_contract = Software.model_construct(id=software_id, name="SIP")
    src_contract = Source.model_construct(
        id=source_id, url="local://docs", 
        source_type=SourceType.OFFICIAL_DOCS
    )

    async with SessionLocal() as session:
        # We can skip PG inserts for simplicity and just populate Qdrant with the serialized records,
        # but to be totally correct we should insert into PG as well.
        # For this demonstration, we'll focus heavily on Qdrant since the Retriever pulls from there!
        points = []
        
        for file_path in md_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            doc_id = uuid4()
            doc_ver_id = uuid4()
            
            doc_contract = Document.model_construct(
                id=doc_id, url=file_path, document_type=DocumentType.OTHER
            )
            doc_ver_contract = DocumentVersion.model_construct(
                id=doc_ver_id, content_hash=str(hash(content))
            )
            
            chunks_text = simple_markdown_chunker(content)
            print(f"Chunked {file_path} into {len(chunks_text)} chunks.")
            
            for idx, text in enumerate(chunks_text):
                chunk_id = uuid4()
                chunk_contract = Chunk.model_construct(
                    id=chunk_id,
                    document_version_id=doc_ver_id,
                    document_id=doc_id,
                    software_id=software_id,
                    source_id=source_id,
                    source_type=SourceType.OFFICIAL_DOCS,
                    authority_level=AuthorityLevel.OFFICIAL,
                    text=text,
                    chunk_type=ChunkType.TEXT,
                    content_hash=str(hash(text)),
                    position_in_section=idx,
                    position_in_document=idx,
                    token_count=len(text.split()) # roughly
                )
                
                record = KnowledgeRecord.model_construct(
                    chunk=chunk_contract,
                    document=doc_contract,
                    document_version=doc_ver_contract,
                    source=src_contract,
                    software=sw_contract
                )
                
                # Embed
                vector = model.encode(text).tolist()
                
                # Qdrant Payload
                payload = {
                    "expert_id": str(expert_id),
                    "knowledge_record_json": record.model_dump_json(),
                    "source_uri": file_path
                }
                
                points.append(
                    rest.PointStruct(
                        id=str(chunk_id),
                        vector=vector,
                        payload=payload
                    )
                )
                
        # Insert into Qdrant
        print(f"Upserting {len(points)} chunks into Qdrant...")
        # Upsert in batches of 50
        batch_size = 50
        for i in range(0, len(points), batch_size):
            await qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=points[i:i+batch_size]
            )
        
        print(f"Ingestion complete! Embedded {len(points)} knowledge chunks.")
        
        # Write expert_id out so we can use it in server.py
        with open("scratch/expert_id.txt", "w") as f:
            f.write(str(expert_id))

if __name__ == "__main__":
    asyncio.run(main())
