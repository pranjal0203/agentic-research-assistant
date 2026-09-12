"""
Retrieval evaluation service.

This module evaluates retrieval quality
before answer generation.
"""

from config.settings import (
    PDF_CONFIDENCE_HIGH,
    PDF_CONFIDENCE_VERY_HIGH,
    PDF_RETRIEVAL_THRESHOLD,
    WEB_CONFIDENCE_HIGH,
    WEB_CONFIDENCE_VERY_HIGH,
    WEB_RETRIEVAL_THRESHOLD,
)
from models.confidence import Confidence
from models.retrieval_evaluation import RetrievalEvaluation
from models.web_result import WebResult


def evaluate_pdf_retrieval(
    retrieved_documents: list[tuple],
    threshold: float = PDF_RETRIEVAL_THRESHOLD,
) -> RetrievalEvaluation:
    """
    Evaluate the quality of retrieved
    PDF documents.

    Args:
        retrieved_documents:
            Retrieved (Document, distance) pairs.

        threshold:
            Maximum acceptable retrieval distance.

    Returns:
        Retrieval evaluation result.
    """

    if not retrieved_documents:
        return RetrievalEvaluation(
            passed=False,
            confidence=Confidence.NONE,
            score=float("inf"),
        )

    valid_distances = [
        distance
        for _, distance in retrieved_documents
        if isinstance(distance, (int, float))
    ]

    if not valid_distances:
        return RetrievalEvaluation(
            passed=False,
            confidence=Confidence.NONE,
            score=float("inf"),
        )

    best_distance = min(
        valid_distances,
    )

    if best_distance <= PDF_CONFIDENCE_VERY_HIGH:
        confidence = Confidence.VERY_HIGH

    elif best_distance <= PDF_CONFIDENCE_HIGH:
        confidence = Confidence.HIGH

    elif best_distance <= threshold:
        confidence = Confidence.MEDIUM

    else:
        confidence = Confidence.LOW

    return RetrievalEvaluation(
        passed=best_distance <= threshold,
        confidence=confidence,
        score=best_distance,
    )


def evaluate_web_retrieval(
    results: list[WebResult],
    threshold: float = WEB_RETRIEVAL_THRESHOLD,
) -> RetrievalEvaluation:
    """
    Evaluate the quality of retrieved
    web search results.

    Args:
        results:
            Retrieved web search results.

        threshold:
            Minimum acceptable relevance score.

    Returns:
        Retrieval evaluation result.
    """

    if not results:
        return RetrievalEvaluation(
            passed=False,
            confidence=Confidence.NONE,
            score=0.0,
        )

    valid_scores = [
        result.score
        for result in results
        if isinstance(
            result.score,
            (int, float),
        )
    ]

    if not valid_scores:
        return RetrievalEvaluation(
            passed=False,
            confidence=Confidence.NONE,
            score=0.0,
        )

    best_score = max(
        valid_scores,
    )

    if best_score >= WEB_CONFIDENCE_VERY_HIGH:
        confidence = Confidence.VERY_HIGH

    elif best_score >= WEB_CONFIDENCE_HIGH:
        confidence = Confidence.HIGH

    elif best_score >= threshold:
        confidence = Confidence.MEDIUM

    else:
        confidence = Confidence.LOW

    return RetrievalEvaluation(
        passed=best_score >= threshold,
        confidence=confidence,
        score=best_score,
    )


def combine_confidence(
    pdf_confidence: Confidence,
    web_confidence: Confidence,
) -> Confidence:
    """
    Combine PDF and web retrieval confidence
    into a final hybrid confidence level.

    Hybrid confidence is intentionally conservative.

    The final confidence cannot be higher than
    the weaker retrieval source because a hybrid
    answer should not claim strong confidence when
    one required source is weak.

    Args:
        pdf_confidence:
            Confidence from PDF retrieval.

        web_confidence:
            Confidence from web retrieval.

    Returns:
        Combined hybrid confidence.
    """

    confidence_rank = {
        Confidence.NONE: 0,
        Confidence.LOW: 1,
        Confidence.MEDIUM: 2,
        Confidence.HIGH: 3,
        Confidence.VERY_HIGH: 4,
    }

    return min(
        (
            pdf_confidence,
            web_confidence,
        ),
        key=lambda c: confidence_rank[c],
    )
