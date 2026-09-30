"""Evaluation Runner for SIP.

Coordinates the evaluation of a dataset against Baseline RAG and SIP RAG.
"""
import time
from typing import List, Dict, Optional, Any
from uuid import UUID

from sip.core.contracts import EvaluationResult, EvaluationSystem, MetricValue
from sip.evaluation.dataset import EvaluationDataset
from sip.evaluation.baseline import BaselineRAG
from sip.evaluation.metrics import MetricEngine

# Assuming we have a SIPRAG interface. We'll use a protocol for testing.
class Evaluator:
    def __init__(self, baseline_rag: BaselineRAG, sip_rag: Any) -> None:
        self.baseline_rag = baseline_rag
        self.sip_rag = sip_rag
        
    async def evaluate_dataset(
        self, 
        dataset: EvaluationDataset, 
        system: EvaluationSystem = EvaluationSystem.BASELINE,
        experiment_id: str = "exp_01"
    ) -> List[EvaluationResult]:
        
        results: List[EvaluationResult] = []
        for question in dataset.questions:
            start_time = time.time()
            
            # TODO: Extract retrieved sources correctly depending on the system
            # For this MVP, we will mock the retrieved sources based on actual runtime logs
            try:
                if system == EvaluationSystem.BASELINE:
                    answer = await self.baseline_rag.execute(question.question)
                    retrieved_sources: List[str] = [] # MOCK: Fetch from Baseline Trace
                else:
                    answer = await self.sip_rag.execute(question.question)
                    retrieved_sources: List[str] = [] # MOCK: Fetch from SIP Trace
                
                latency = (time.time() - start_time) * 1000
                
                # Metrics
                retrieval_metrics = MetricEngine.evaluate_retrieval(
                    retrieved=retrieved_sources,
                    expected=question.expected_sources
                )

                
                result = EvaluationResult(
                    experiment_id=experiment_id,
                    system=system,
                    dataset_name=dataset.name,
                    precision_at_k=retrieval_metrics["precision_at_k"],
                    recall_at_k=retrieval_metrics["recall_at_k"],
                    hit_rate_at_k=retrieval_metrics["hit_rate_at_k"],
                    mrr=retrieval_metrics["mrr"],
                    mean_latency_ms=latency
                )
                results.append(result)
                
            except Exception as e:
                # Capture failed executions
                results.append(EvaluationResult(
                    experiment_id=experiment_id,
                    system=system,
                    dataset_name=dataset.name,
                    error=str(e)
                ))

        return results
