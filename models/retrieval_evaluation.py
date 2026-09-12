"""
Retrieval evaluation model.
"""

from dataclasses import dataclass

from models.confidence import Confidence


@dataclass(slots=True)
class RetrievalEvaluation:
    """
    Retrieval evaluation result.
    """

    passed: bool
    confidence: Confidence
    score: float
