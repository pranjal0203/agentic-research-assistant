"""
Web knowledge service.

This module searches the web
for relevant information.
"""

from models.knowledge import WebKnowledge
from services.candidate_builder import build_web_candidates
from services.web_search import search_web


def search_web_knowledge(
    question: str,
) -> WebKnowledge:
    """
    Search the web and normalize
    the results into WebKnowledge.
    """

    results = search_web(
        question,
    )

    return WebKnowledge(
        results=results,
        candidates=build_web_candidates(
            results,
        ),
    )
