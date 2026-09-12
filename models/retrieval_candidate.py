"""
Retrieval candidate model.

This module defines the normalized representation
of retrieved information from different sources.
"""

from dataclasses import dataclass

from models.citation import Citation
from models.source import Source


@dataclass(slots=True)
class RetrievalCandidate:
    """
    A normalized piece of retrieved information.

    Retrieval candidates provide a common representation
    for information retrieved from different sources,
    such as PDF documents and web search results.

    Attributes:
        content:
            Retrieved textual content.

        source:
            Source from which the content was retrieved.

        score:
            Retrieval relevance score.

        citation:
            Citation describing the origin of the content.
    """

    content: str
    source: Source
    score: float
    citation: Citation
