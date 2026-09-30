from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .llm import LLMResponse
from .rag import RetrievalVersionSnapshot
from .knowledge import Chunk

@dataclass
class EvaluationTestCase:
    id: str
    question: str
    expected_answer: Optional[str] = None
    expected_sources: List[str] = field(default_factory=list)
    question_type: str = "factoid"

@dataclass
class EvaluationMetrics:
    # Retrieval
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    hit_rate_at_k: float = 0.0
    mrr: float = 0.0
    
    # Context
    context_relevance: float = 0.0
    context_compression_ratio: float = 1.0
    
    # Generation
    answer_correctness: float = 0.0
    faithfulness: float = 0.0
    
    # Performance
    latency_ms: float = 0.0
    total_tokens: int = 0

@dataclass
class EvaluationResult:
    test_case_id: str
    architecture: str  # e.g., "sip_rag" or "baseline_rag"
    metrics: EvaluationMetrics
    generated_answer: str
    retrieved_chunks: List[Chunk] = field(default_factory=list)
    raw_response: Optional[LLMResponse] = None
    error: Optional[str] = None
