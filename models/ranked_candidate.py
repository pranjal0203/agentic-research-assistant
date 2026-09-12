"""
Ranked retrieval candidate model.

This module defines a retrieval candidate
after cross-source relevance ranking.
"""

from dataclasses import dataclass

from models.retrieval_candidate import RetrievalCandidate


@dataclass(slots=True)
class RankedCandidate:
    """
    A retrieval candidate with a normalized
    cross-source relevance score.

    Attributes:
        candidate:
            The original retrieval candidate.

        relevance_score:
            Cross-source relevance score produced
            by the reranking process.

            Higher scores indicate greater
            relevance to the user's question.
    """

    candidate: RetrievalCandidate
    relevance_score: float
