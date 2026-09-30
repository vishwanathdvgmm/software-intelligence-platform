"""Evaluation Dataset parser and structures."""

import json
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sip.core.contracts.base import SIPBaseModel, new_uuid

class EvaluationQuestion(SIPBaseModel):
    id: str
    question: str
    expected_answer: str
    expected_sources: List[str]
    question_type: str
    difficulty: Optional[str] = "Medium"


class EvaluationDataset(SIPBaseModel):
    id: UUID
    name: str
    questions: List[EvaluationQuestion]

    @classmethod
    def load_from_file(cls, path: str | Path, name: str) -> "EvaluationDataset":
        """Load an evaluation dataset from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        questions = [EvaluationQuestion(**q) for q in data]
        return cls(id=new_uuid(), name=name, questions=questions)
