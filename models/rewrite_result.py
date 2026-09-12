"""
Question rewrite result model.

This module represents the result of
context-aware question rewriting.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RewriteResult:
    """
    Represent the result of resolving
    a conversational question.

    Attributes:
        question:
            Standalone question suitable
            for retrieval.

        resolved:
            Whether the question contains
            enough context for retrieval.
    """

    question: str
    resolved: bool
