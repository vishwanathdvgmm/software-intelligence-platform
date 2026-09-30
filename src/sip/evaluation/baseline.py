"""Baseline RAG implementation for comparison against SIP.

This is intentionally simple to represent a traditional RAG approach:
User Query -> Embedding -> Vector Search -> Top-K -> LLM -> Answer

It does NOT use advanced routing, evidence gating, or reranking.
"""

from typing import List, Dict, Any, Optional, Protocol
from uuid import UUID

from sip.core.contracts import (
    Query,
    RetrievalCandidate,
    Context,
    Evidence,
    LLMRequest,
    Message,
    MessageRole,
    ModelProfile,
    Chunk
)
from sip.core.contracts.llm import LLMProvider
from sip.core.protocols.llm import LLMGateway

class VectorStoreProtocol(Protocol):
    async def search(self, query: str, k: int) -> List[Chunk]:
        ...

class BaselineRAG:
    """Traditional RAG pipeline for evaluation baseline."""
    
    def __init__(self, vector_store: VectorStoreProtocol, llm_gateway: LLMGateway) -> None:
        self.vector_store = vector_store
        self.llm_gateway = llm_gateway

    async def execute(self, query: str, top_k: int = 5) -> str:
        """Execute a simple retrieve-and-generate pipeline."""
        
        candidates = await self.vector_store.search(
            query=query,
            k=top_k
        )
        
        context_text = ""
        for i, doc in enumerate(candidates):
            context_text += f"\n--- Document {i+1} ---\n{doc.text}\n"

        prompt = f"""Answer the question based only on the following context.
        
Context:
{context_text}

Question:
{query}
"""
        request = LLMRequest(
            messages=(Message(role=MessageRole.USER, content=prompt),),
            model_profile=ModelProfile(
                provider=LLMProvider.OLLAMA, 
                model_id="default", 
                context_window=4096,
                max_output_tokens=1024
            )
        )
        
        response = await self.llm_gateway.generate(request)
        return response.content
