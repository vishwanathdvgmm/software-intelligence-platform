"""Evaluation Metrics calculation engine.

Calculates Retrieval, Context, and Generation metrics.
"""

from typing import List, Dict, Any, Optional
from sip.core.contracts import MetricValue

class MetricEngine:
    
    @staticmethod
    def calculate_precision_at_k(retrieved_sources: List[str], expected_sources: List[str], k: int) -> float:
        """Precision@K = Relevant Retrieved Results / K"""
        if k <= 0:
            return 0.0
        
        top_k = retrieved_sources[:k]
        relevant_retrieved = sum(1 for source in top_k if source in expected_sources)
        return relevant_retrieved / k

    @staticmethod
    def calculate_recall_at_k(retrieved_sources: List[str], expected_sources: List[str], k: int) -> float:
        """Recall@K = Relevant Retrieved Results / Total Relevant Results"""
        if not expected_sources:
            return 1.0  # If nothing is expected, recall is perfect if we found nothing, but usually dataset guarantees > 0
        
        top_k = retrieved_sources[:k]
        relevant_retrieved = sum(1 for source in top_k if source in expected_sources)
        return relevant_retrieved / len(expected_sources)

    @staticmethod
    def calculate_hit_rate_at_k(retrieved_sources: List[str], expected_sources: List[str], k: int) -> float:
        """Hit@K = 1 if at least one relevant result exists, 0 otherwise"""
        top_k = retrieved_sources[:k]
        for source in top_k:
            if source in expected_sources:
                return 1.0
        return 0.0
        
    @staticmethod
    def calculate_mrr(retrieved_sources: List[str], expected_sources: List[str]) -> float:
        """Mean Reciprocal Rank"""
        for i, source in enumerate(retrieved_sources):
            if source in expected_sources:
                return 1.0 / (i + 1)
        return 0.0

    @classmethod
    def evaluate_retrieval(cls, retrieved: List[str], expected: List[str], k: int = 5) -> Dict[str, MetricValue]:
        return {
            "precision_at_k": MetricValue(name=f"Precision@{k}", value=cls.calculate_precision_at_k(retrieved, expected, k), threshold=0.6),
            "recall_at_k": MetricValue(name=f"Recall@{k}", value=cls.calculate_recall_at_k(retrieved, expected, k), threshold=0.7),
            "hit_rate_at_k": MetricValue(name=f"Hit Rate@{k}", value=cls.calculate_hit_rate_at_k(retrieved, expected, k), threshold=1.0),
            "mrr": MetricValue(name="MRR", value=cls.calculate_mrr(retrieved, expected), threshold=0.5),
        }
