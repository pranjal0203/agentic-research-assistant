"""
Integration tests for Tavily web retrieval.

These tests make real Tavily API requests
and therefore require valid API credentials.
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()

from services.web_search import search_web

RUN_TAVILY_TESTS = (
    os.getenv(
        "RUN_TAVILY_TESTS",
        "",
    ).lower()
    == "true"
)

pytestmark = pytest.mark.skipif(
    not RUN_TAVILY_TESTS,
    reason="Tavily integration tests are disabled.",
)


def test_tavily_returns_results() -> None:
    """
    Verify Tavily returns web results
    for a valid search query.
    """

    results = search_web(
        "Who is the CEO of OpenAI?",
    )

    assert results
    assert len(results) > 0


def test_tavily_result_structure() -> None:
    """
    Verify Tavily results contain
    the expected structured fields.
    """

    results = search_web(
        "Who is the CEO of OpenAI?",
    )

    assert results

    result = results[0]

    assert result.title
    assert result.url
    assert result.content
    assert isinstance(
        result.score,
        float,
    )


def test_tavily_returns_relevant_results() -> None:
    """
    Verify Tavily returns relevant evidence
    for a known search query.
    """

    results = search_web(
        "Who is the CEO of OpenAI?",
    )

    assert results

    combined_content = " ".join(
        (f"{result.title} " f"{result.content}").lower() for result in results
    )

    assert "openai" in combined_content
