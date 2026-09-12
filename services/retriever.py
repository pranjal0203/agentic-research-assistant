"""
Document retrieval service.

This module retrieves relevant document chunks
from the vector database.

The retrieval layer intentionally returns a broader
candidate pool than the final answer context requires.

A downstream reranker is responsible for selecting
the strongest final evidence.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config.settings import (
    RETRIEVAL_CANDIDATE_MULTIPLIER,
    TOP_K,
)


def retrieve_documents(
    vector_store: Chroma,
    question: str,
) -> list[tuple[Document, float]]:
    """
    Retrieve a broad candidate set of document chunks
    together with their vector distances.

    The candidate pool is intentionally larger than
    TOP_K because downstream reranking performs the
    final evidence selection.

    Args:
        vector_store:
            Chroma vector store containing indexed
            document chunks.

        question:
            User's retrieval question.

    Returns:
        Document/distance pairs ordered by the
        vector store's initial similarity ranking.
    """

    if not question.strip():
        return []

    if TOP_K <= 0:
        return []

    if RETRIEVAL_CANDIDATE_MULTIPLIER <= 0:
        return []

    candidate_k = TOP_K * RETRIEVAL_CANDIDATE_MULTIPLIER

    return vector_store.similarity_search_with_score(
        query=question,
        k=candidate_k,
    )
