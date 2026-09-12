"""
Knowledge models.
"""

from dataclasses import dataclass

from langchain_core.documents import Document

from models.retrieval_candidate import RetrievalCandidate
from models.web_result import WebResult


@dataclass(slots=True, frozen=True)
class PDFKnowledge:
    """
    Knowledge retrieved from
    the local knowledge base.
    """

    retrieved_documents: list[tuple[Document, float]]

    candidates: list[RetrievalCandidate]


@dataclass(slots=True, frozen=True)
class WebKnowledge:
    """
    Knowledge retrieved from
    the web.
    """

    results: list[WebResult]

    candidates: list[RetrievalCandidate]


Knowledge = PDFKnowledge | WebKnowledge
