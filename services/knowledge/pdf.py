"""
PDF knowledge service.

This module searches the local
knowledge base.
"""

from langchain_chroma import Chroma

from models.knowledge import PDFKnowledge
from services.candidate_builder import (
    build_pdf_candidates,
)
from services.retriever import (
    retrieve_documents,
)


def search_pdf_knowledge(
    vector_store: Chroma,
    question: str,
) -> PDFKnowledge:
    """
    Search the local knowledge base.

    Args:
        vector_store:
            Initialized Chroma vector
            database.

        question:
            User question.

    Returns:
        Retrieved PDF knowledge containing
        source documents and retrieval
        candidates.
    """

    retrieved_documents = retrieve_documents(
        vector_store,
        question,
    )

    return PDFKnowledge(
        retrieved_documents=retrieved_documents,
        candidates=build_pdf_candidates(
            retrieved_documents,
        ),
    )
