"""Basic text chunker for ingestion."""

import re
from uuid import uuid4

from sip.core.contracts import Chunk, Document, DocumentVersion, Source
from sip.core.protocols.ingestion import Chunker


class MarkdownChunker(Chunker):
    """Splits markdown/text into chunks based on headers or paragraphs."""

    def __init__(self, max_chunk_size: int = 1000) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk(
        self, text: str, document_version: DocumentVersion, document: Document, source: Source
    ) -> list[Chunk]:
        """Split text into chunks."""
        # Simple paragraph splitting for now
        paragraphs = re.split(r"\n\s*\n", text)

        chunks = []
        current_text = ""
        position = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            if len(current_text) + len(p) > self.max_chunk_size and current_text:
                chunks.append(
                    self._create_chunk(current_text, document_version, document, source, position)
                )
                current_text = p
                position += 1
            else:
                if current_text:
                    current_text += "\n\n" + p
                else:
                    current_text = p

        if current_text:
            chunks.append(
                self._create_chunk(current_text, document_version, document, source, position)
            )

        return chunks

    def _create_chunk(
        self,
        content: str,
        doc_version: DocumentVersion,
        document: Document,
        source: Source,
        position: int,
    ) -> Chunk:
        import hashlib

        return Chunk(
            id=uuid4(),
            document_version_id=doc_version.id,
            document_id=doc_version.document_id,
            section_id=None,
            software_id=document.software_id,
            software_version_ids=source.version_ids,
            source_id=source.id,
            source_type=source.source_type,
            authority_level=source.authority_level,
            text=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            position_in_section=position,
            position_in_document=position,
        )
