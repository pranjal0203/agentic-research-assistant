"""
Context fusion service.

This module combines ranked retrieval
candidates into bounded LLM context while
preserving citation information.

The context budget is controlled through
configuration rather than source-specific
or domain-specific rules.
"""

from config.settings import (
    GENERATION_CONTEXT_MAX_CHARS,
    GENERATION_CONTEXT_TOP_K,
)
from models.citation import Citation
from models.ranked_candidate import RankedCandidate


def _truncate_content(
    content: str,
    max_chars: int,
) -> str:
    """
    Bound the amount of candidate text exposed
    to the answer-generation model.

    Truncation occurs only at the context
    presentation layer. The original candidate
    remains unchanged.
    """

    content = content.strip()

    if len(content) <= max_chars:
        return content

    return content[:max_chars].rstrip() + "\n[Evidence truncated for context budget.]"


def fuse_context(
    ranked_candidates: list[RankedCandidate],
) -> str:
    """
    Combine the strongest ranked candidates into
    a bounded structured context string.

    Candidates are already ordered by relevance
    before reaching this function.

    Citation metadata remains attached to each
    evidence block.
    """

    context_blocks: list[str] = []

    for ranked_candidate in ranked_candidates[:GENERATION_CONTEXT_TOP_K]:
        candidate = ranked_candidate.candidate
        citation = candidate.citation

        content = _truncate_content(
            candidate.content,
            GENERATION_CONTEXT_MAX_CHARS,
        )

        if not content:
            continue

        header = " | ".join(
            part
            for part in (
                candidate.source.value,
                citation.title,
                citation.location,
            )
            if part
        )

        context_blocks.append(f"[{header}]\n{content}")

    return "\n\n".join(
        context_blocks,
    )


def build_citations(
    ranked_candidates: list[RankedCandidate],
) -> list[Citation]:
    """
    Build unique citations in relevance order.

    Only candidates that are actually exposed
    to the final generation context contribute
    citations.
    """

    citations: list[Citation] = []

    seen: set[tuple[str, str, str | None]] = set()

    for ranked_candidate in ranked_candidates[:GENERATION_CONTEXT_TOP_K]:
        citation = ranked_candidate.candidate.citation

        key = (
            citation.title,
            citation.location,
            citation.url,
        )

        if key in seen:
            continue

        seen.add(key)
        citations.append(
            citation,
        )

    return citations
