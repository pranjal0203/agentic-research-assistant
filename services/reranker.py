"""
Cross-source reranking service.

This module reranks retrieval candidates
using a common embedding space.

PDF and Web retrieval scores may use
different scoring systems, so the original
retrieval score is not used directly for
cross-source comparison.

Instead, every candidate is compared against
the user's question using the same embedding
model.

Important:
The reranker does NOT aggressively discard
candidates based only on embedding similarity.
The final top-k selection is handled by the
response builder.
"""

import math

from models.ranked_candidate import RankedCandidate
from models.retrieval_candidate import RetrievalCandidate
from services.embeddings import embeddings


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between
    two embedding vectors.

    Args:
        vector_a:
            First embedding vector.

        vector_b:
            Second embedding vector.

    Returns:
        Cosine similarity between the vectors.

    Raises:
        ValueError:
            If the vectors have different
            dimensions.
    """

    if len(vector_a) != len(vector_b):
        raise ValueError("Embedding vectors must have " "the same dimensionality.")

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
            strict=True,
        )
    )

    magnitude_a = math.sqrt(sum(value * value for value in vector_a))

    magnitude_b = math.sqrt(sum(value * value for value in vector_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def _clean_candidates(
    candidates: list[RetrievalCandidate],
) -> list[RetrievalCandidate]:
    """
    Remove candidates that cannot contribute
    useful textual evidence.

    Duplicate content is removed so identical
    evidence is not repeatedly passed to the
    response generator.
    """

    cleaned: list[RetrievalCandidate] = []

    seen_content: set[str] = set()

    for candidate in candidates:
        content = candidate.content.strip()

        if not content:
            continue

        normalized_content = content.casefold()

        if normalized_content in seen_content:
            continue

        seen_content.add(
            normalized_content,
        )

        cleaned.append(candidate)

    return cleaned


def rerank_candidates(
    question: str,
    candidates: list[RetrievalCandidate],
) -> list[RankedCandidate]:
    """
    Rerank retrieval candidates against
    the user's question.

    All candidates are embedded using the
    same embedding model so PDF and Web
    content can be compared in a common
    semantic space.

    Candidates are NOT removed solely because
    their semantic score is below an arbitrary
    threshold. This is important because
    useful evidence can have relatively low
    cosine similarity while still being directly
    relevant.

    Args:
        question:
            The user's question.

        candidates:
            Retrieval candidates from one
            or more knowledge sources.

    Returns:
        Candidates ordered from most to
        least semantically relevant.
    """

    question = question.strip()

    if not question:
        return []

    candidates = _clean_candidates(
        candidates,
    )

    if not candidates:
        return []

    question_embedding = embeddings.embed_query(
        question,
    )

    candidate_embeddings = embeddings.embed_documents(
        [candidate.content for candidate in candidates],
    )

    ranked_candidates: list[RankedCandidate] = []

    for candidate, candidate_embedding in zip(
        candidates,
        candidate_embeddings,
        strict=True,
    ):
        relevance_score = cosine_similarity(
            question_embedding,
            candidate_embedding,
        )

        ranked_candidates.append(
            RankedCandidate(
                candidate=candidate,
                relevance_score=relevance_score,
            )
        )

    return sorted(
        ranked_candidates,
        key=lambda candidate: candidate.relevance_score,
        reverse=True,
    )
