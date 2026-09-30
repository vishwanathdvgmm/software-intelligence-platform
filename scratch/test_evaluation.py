"""Test script for the SIP Evaluation Architecture."""

import asyncio
from sip.evaluation.dataset import EvaluationDataset, EvaluationQuestion
from sip.core.contracts import new_uuid
from sip.evaluation.metrics import MetricEngine
from sip.core.contracts import EvaluationSystem

async def main() -> None:
    print("Testing Evaluation Dataset & Metrics...")
    
    # 1. Create a dummy dataset
    dataset = EvaluationDataset(
        id=new_uuid(),
        name="SIP_MVP_Benchmark",
        questions=[
            EvaluationQuestion(
                id="Q-1",
                question="Why use semantic routing?",
                expected_answer="To dynamically select the best knowledge base based on the query.",
                expected_sources=["routing.md"],
                question_type="factoid"
            )
        ]
    )
    
    print(f"Loaded dataset '{dataset.name}' with {len(dataset.questions)} question(s).")
    
    # 2. Test metrics directly
    print("\n--- Testing Retrieval Metrics ---")
    retrieved_mock = ["routing.md", "rag_architecture.md"]
    expected = dataset.questions[0].expected_sources
    
    metrics = MetricEngine.evaluate_retrieval(retrieved_mock, expected, k=5)
    
    for k, v in metrics.items():
        print(f"{v.name}: {v.value} (Passes threshold: {v.passes_threshold})")
        
    print("\nEvaluation architecture foundation is ready!")

if __name__ == "__main__":
    asyncio.run(main())
