"""
Response builder service.

This module builds structured responses
from agent tool results.

The response builder is responsible for:

- extracting normalized retrieval candidates
- improving cross-source evidence ranking
- preserving source diversity
- estimating confidence from final evidence
- building grounded generation context
- producing citations

Important:
The response builder does not treat retrieval existence
as proof that the question has been answered. It focuses
on selecting the strongest evidence available to the
generator.
"""

import re
from collections import defaultdict
from itertools import pairwise

from config.settings import HYBRID_TOP_K, MIN_SOURCE_RELEVANCE
from models.confidence import Confidence
from models.ranked_candidate import RankedCandidate
from models.response import Response
from models.retrieval_candidate import RetrievalCandidate
from models.source import Source
from models.tool_result import ToolResult
from services.context_fusion import (
    build_citations,
    fuse_context,
)
from services.evaluator import (
    evaluate_pdf_retrieval,
    evaluate_web_retrieval,
)
from services.generator import generate_answer
from services.reranker import rerank_candidates

# ---------------------------------------------------------------------------
# Lexical relevance
# ---------------------------------------------------------------------------

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/+-]*")

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "by",
    "can",
    "compare",
    "comparison",
    "compared",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "use",
    "used",
    "using",
    "was",
    "what",
    "when",
    "which",
    "who",
    "why",
    "with",
}


def _tokenize(
    text: str,
) -> list[str]:
    """
    Tokenize text into normalized lexical units.

    Technical tokens such as:

        BERTBASE
        BERTLARGE
        110M
        self-attention
        pre-training

    are intentionally preserved as much as possible.
    """

    return [token.casefold() for token in _TOKEN_PATTERN.findall(text)]


def _content_tokens(
    text: str,
) -> list[str]:
    """
    Return meaningful content tokens after removing
    common question-language stopwords.
    """

    return [token for token in _tokenize(text) if token not in _STOPWORDS]


def _lexical_relevance(
    question: str,
    content: str,
) -> float:
    """
    Estimate lexical relevance between a question
    and a retrieved candidate.

    The score combines:

    1. Individual content-token coverage.
    2. Exact phrase overlap.
    3. Repeated-token protection.

    The result is normalized to [0, 1].

    This is deliberately conservative. Lexical matching
    supplements semantic similarity; it does not replace it.
    """

    question_tokens = _content_tokens(
        question,
    )

    content_tokens = _content_tokens(
        content,
    )

    if not question_tokens or not content_tokens:
        return 0.0

    content_token_set = set(
        content_tokens,
    )

    matched_tokens = sum(
        1 for token in set(question_tokens) if token in content_token_set
    )

    token_coverage = matched_tokens / len(set(question_tokens))

    normalized_question = " ".join(
        question_tokens,
    )

    normalized_content = " ".join(
        content_tokens,
    )

    phrase_score = 0.0

    # Exact full-question phrase match is a strong signal.
    if normalized_question and normalized_question in normalized_content:
        phrase_score = 1.0

    # For multi-token technical queries, reward
    # contiguous phrases.
    elif len(question_tokens) >= 2:
        bigrams = list(pairwise(question_tokens))

        if bigrams:
            content_bigrams = set(pairwise(content_tokens))

            matched_bigrams = sum(1 for bigram in bigrams if bigram in content_bigrams)

            phrase_score = matched_bigrams / len(bigrams)

    return min(
        1.0,
        (0.75 * token_coverage) + (0.25 * phrase_score),
    )


def _combine_relevance_scores(
    question: str,
    ranked_candidates: list[RankedCandidate],
) -> list[RankedCandidate]:
    """
    Combine semantic and lexical relevance.

    The existing reranker provides semantic relevance.
    This function adds a bounded lexical bonus for
    exact technical terminology.

    Semantic relevance remains dominant.

    Final score:

        0.80 * semantic relevance
        0.20 * lexical relevance

    This is intentionally simple and deterministic so
    retrieval behavior can be evaluated and tuned later.
    """

    rescored: list[RankedCandidate] = []

    for ranked_candidate in ranked_candidates:
        lexical_score = _lexical_relevance(
            question,
            ranked_candidate.candidate.content,
        )

        semantic_score = ranked_candidate.relevance_score

        combined_score = 0.80 * semantic_score + 0.20 * lexical_score

        rescored.append(
            RankedCandidate(
                candidate=ranked_candidate.candidate,
                relevance_score=combined_score,
            )
        )

    return sorted(
        rescored,
        key=lambda candidate: candidate.relevance_score,
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Candidate selection
# ---------------------------------------------------------------------------


def _rank_candidates(
    question: str,
    candidates: list[RetrievalCandidate],
) -> list[RankedCandidate]:
    """
    Rerank retrieval candidates and retain
    the strongest evidence.

    Ranking consists of:

    1. Common embedding-based semantic relevance.
    2. Exact lexical/phrase relevance.
    3. Source representation when multiple
       retrieval sources contributed evidence.

    When multiple retrieval sources contribute candidates,
    ensure that each contributing source receives
    representation in the final evidence set before filling
    remaining slots by relevance.

    The reranker itself remains source-agnostic.
    """

    ranked_candidates = rerank_candidates(
        question,
        candidates,
    )

    if not ranked_candidates:
        return []

    ranked_candidates = _combine_relevance_scores(
        question,
        ranked_candidates,
    )

    if HYBRID_TOP_K <= 0:
        return []

    candidates_by_doc: dict[
        str,
        list[RankedCandidate],
    ] = defaultdict(list)

    for candidate in ranked_candidates:
        doc_key = candidate.candidate.citation.title
        candidates_by_doc[doc_key].append(candidate)

    if len(candidates_by_doc) <= 1:
        return ranked_candidates[:HYBRID_TOP_K]

    diverse_representatives: list[RankedCandidate] = []

    for doc_candidates in candidates_by_doc.values():
        top_candidate = doc_candidates[0]
        if top_candidate.relevance_score >= MIN_SOURCE_RELEVANCE:
            diverse_representatives.append(top_candidate)

    # Sort diverse representative candidates by score descending
    diverse_representatives.sort(key=lambda c: c.relevance_score, reverse=True)

    selected_ids = {id(candidate) for candidate in diverse_representatives}
    remaining_candidates: list[RankedCandidate] = []

    for candidate in ranked_candidates:
        if id(candidate) in selected_ids:
            continue
        remaining_candidates.append(candidate)

    # Sort remaining candidates by score descending
    remaining_candidates.sort(key=lambda c: c.relevance_score, reverse=True)

    # Place diverse representatives at the front to guarantee top-k representation
    final_candidates = diverse_representatives + remaining_candidates

    return final_candidates[:HYBRID_TOP_K]


def _extract_candidates(
    tool_results: tuple[ToolResult, ...],
) -> list[RetrievalCandidate]:
    """
    Extract retrieval candidates from
    successful tool results that produced
    usable content.
    """

    candidates: list[RetrievalCandidate] = []

    for result in tool_results:
        if not result.has_relevant_content:
            continue

        if result.knowledge is None:
            continue

        candidates.extend(
            result.knowledge.candidates,
        )

    return candidates


def _determine_source(
    ranked_candidates: list[RankedCandidate],
) -> Source | None:
    """
    Determine the response source from
    candidates that actually survived
    cross-source reranking.
    """

    sources = {
        ranked_candidate.candidate.source for ranked_candidate in ranked_candidates
    }

    if sources == {Source.PDF}:
        return Source.PDF

    if sources == {Source.WEB}:
        return Source.WEB

    if Source.PDF in sources and Source.WEB in sources:
        return Source.HYBRID

    return None


def _confidence_rank(
    confidence: Confidence,
) -> int:
    """
    Return the relative strength of a
    confidence level.
    """

    ranks = {
        Confidence.NONE: 0,
        Confidence.LOW: 1,
        Confidence.MEDIUM: 2,
        Confidence.HIGH: 3,
        Confidence.VERY_HIGH: 4,
    }

    return ranks[confidence]


def _confidence_from_ranked_candidates(
    ranked_candidates: list[RankedCandidate],
) -> Confidence:
    """
    Estimate confidence from the evidence
    that actually survived reranking.

    Confidence is based on:

    - strongest final evidence
    - average quality of the strongest evidence
    - number of strong supporting candidates

    This is deliberately conservative.

    These thresholds are still heuristics and will be
    calibrated later against a real evaluation dataset.
    """

    if not ranked_candidates:
        return Confidence.NONE

    scores = [candidate.relevance_score for candidate in ranked_candidates]

    best_score = max(scores)

    strongest_scores = scores[: min(3, len(scores))]

    average_top_score = sum(strongest_scores) / len(strongest_scores)

    strong_candidate_count = sum(score >= 0.45 for score in scores)

    if best_score >= 0.60 and average_top_score >= 0.52 and strong_candidate_count >= 2:
        return Confidence.VERY_HIGH

    if best_score >= 0.48 and average_top_score >= 0.42:
        return Confidence.HIGH

    if best_score >= 0.38 and average_top_score >= 0.32:
        return Confidence.MEDIUM

    return Confidence.LOW


def _evaluate_source_confidence(
    tool_results: tuple[ToolResult, ...],
    ranked_candidates: list[RankedCandidate],
) -> Confidence:
    """
    Evaluate retrieval confidence using only
    sources that contributed final ranked evidence.

    Source-specific retrieval evaluation remains
    supporting evidence, but final confidence is
    constrained by the actual candidates that
    survived cross-source reranking.
    """

    ranked_sources = {candidate.candidate.source for candidate in ranked_candidates}

    pdf_confidence: Confidence | None = None
    web_confidence: Confidence | None = None

    if Source.PDF in ranked_sources:
        for result in tool_results:
            if not result.has_relevant_content:
                continue

            if result.knowledge is None:
                continue

            if not hasattr(
                result.knowledge,
                "retrieved_documents",
            ):
                continue

            evaluation = evaluate_pdf_retrieval(
                result.knowledge.retrieved_documents,
            )

            if pdf_confidence is None or _confidence_rank(
                evaluation.confidence,
            ) > _confidence_rank(
                pdf_confidence,
            ):
                pdf_confidence = evaluation.confidence

    if Source.WEB in ranked_sources:
        for result in tool_results:
            if not result.has_relevant_content:
                continue

            if result.knowledge is None:
                continue

            if not hasattr(
                result.knowledge,
                "results",
            ):
                continue

            evaluation = evaluate_web_retrieval(
                result.knowledge.results,
            )

            if web_confidence is None or _confidence_rank(
                evaluation.confidence,
            ) > _confidence_rank(
                web_confidence,
            ):
                web_confidence = evaluation.confidence

    semantic_confidence = _confidence_from_ranked_candidates(
        ranked_candidates,
    )

    if pdf_confidence is not None and web_confidence is not None:
        source_confidence = min(
            (
                pdf_confidence,
                web_confidence,
            ),
            key=_confidence_rank,
        )

    elif pdf_confidence is not None:
        source_confidence = pdf_confidence

    elif web_confidence is not None:
        source_confidence = web_confidence

    else:
        source_confidence = Confidence.NONE

    return min(
        (
            source_confidence,
            semantic_confidence,
        ),
        key=_confidence_rank,
    )


def _evaluate_confidence(
    tool_results: tuple[ToolResult, ...],
    ranked_candidates: list[RankedCandidate],
) -> Confidence:
    """
    Evaluate final confidence using:

    1. Source-specific retrieval quality.
    2. Final cross-source semantic + lexical relevance.

    The weaker signal determines the final
    confidence so weak evidence cannot produce
    artificially high confidence.
    """

    return _evaluate_source_confidence(
        tool_results,
        ranked_candidates,
    )


def build_response(
    question: str,
    tool_results: tuple[ToolResult, ...],
) -> Response:
    """
    Build the final structured response
    directly from agent tool results.

    Only evidence that survives cross-source
    reranking is used for:

    - answer generation
    - source determination
    - confidence calculation
    - citations

    Args:
        question:
            Original user question.

        tool_results:
            Results produced by the agent's
            executed tools.

    Returns:
        Final structured response.
    """

    candidates = _extract_candidates(
        tool_results,
    )

    if not candidates:
        return Response.empty()

    ranked_candidates = _rank_candidates(
        question,
        candidates,
    )

    if not ranked_candidates:
        return Response.empty()

    context = fuse_context(
        ranked_candidates,
    )

    source = _determine_source(
        ranked_candidates,
    )

    if source is None:
        return Response.empty()

    confidence = _evaluate_confidence(
        tool_results,
        ranked_candidates,
    )

    answer = generate_answer(
        context,
        question,
    )

    from models.response import NOT_FOUND_MESSAGE

    if answer == NOT_FOUND_MESSAGE or "rate limit has been reached" in answer:
        return Response(
            answer=answer,
            source=Source.NONE,
            confidence=Confidence.NONE,
            citations=[],
        )

    return Response(
        answer=answer,
        source=source,
        confidence=confidence,
        citations=build_citations(
            ranked_candidates,
        ),
    )
