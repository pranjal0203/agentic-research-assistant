"""
Web search result model.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class WebResult:
    """
    Represents a single web search result.
    """

    title: str
    url: str
    content: str
    score: float
