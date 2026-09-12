"""
Integration tests for context-aware
question rewriting.

These tests call the configured language model
and therefore require valid API credentials.
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()

from models.conversation_message import (
    ConversationMessage,
    MessageRole,
)
from services.question_rewriter import rewrite_question

RUN_LLM_TESTS = (
    os.getenv(
        "RUN_LLM_TESTS",
        "",
    ).lower()
    == "true"
)

pytestmark = pytest.mark.skipif(
    not RUN_LLM_TESTS,
    reason="LLM integration tests are disabled.",
)


@pytest.fixture
def self_attention_history() -> list[ConversationMessage]:
    """
    Return conversation history about
    self-attention.
    """

    return [
        ConversationMessage(
            role=MessageRole.USER,
            content="What is self-attention?",
        ),
        ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=(
                "Self-attention is an attention mechanism "
                "that relates positions within a sequence."
            ),
        ),
    ]


@pytest.fixture
def openai_history() -> list[ConversationMessage]:
    """
    Return conversation history about
    OpenAI leadership.
    """

    return [
        ConversationMessage(
            role=MessageRole.USER,
            content="Who is the CEO of OpenAI?",
        ),
        ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="Sam Altman is the CEO of OpenAI.",
        ),
    ]


def test_standalone_question_without_history() -> None:
    """
    Verify a standalone question is
    considered resolved.
    """

    result = rewrite_question(
        "Who is the CEO of OpenAI?",
        [],
    )

    assert result.resolved is True
    assert result.question


def test_unresolved_question_without_history() -> None:
    """
    Verify a context-dependent question
    without history is unresolved.
    """

    question = "What company does he lead?"

    result = rewrite_question(
        question,
        [],
    )

    assert result.resolved is False
    assert result.question == question


def test_standalone_question_with_history(
    self_attention_history: list[ConversationMessage],
) -> None:
    """
    Verify unrelated history does not make
    a standalone question unresolved.
    """

    result = rewrite_question(
        "What is positional encoding?",
        self_attention_history,
    )

    assert result.resolved is True
    assert result.question


def test_pronoun_follow_up(
    self_attention_history: list[ConversationMessage],
) -> None:
    """
    Verify a pronoun-based follow-up can
    be resolved using conversation history.
    """

    result = rewrite_question(
        "Why is it useful?",
        self_attention_history,
    )

    assert result.resolved is True
    assert "self-attention" in result.question.lower()


def test_contextual_follow_up(
    self_attention_history: list[ConversationMessage],
) -> None:
    """
    Verify a contextual follow-up can
    be rewritten as a standalone question.
    """

    result = rewrite_question(
        "How does it work?",
        self_attention_history,
    )

    assert result.resolved is True
    assert "self-attention" in result.question.lower()


def test_comparison_follow_up(
    self_attention_history: list[ConversationMessage],
) -> None:
    """
    Verify comparison context is preserved
    during rewriting.
    """

    result = rewrite_question(
        "How does that compare with multi-head attention?",
        self_attention_history,
    )

    rewritten = result.question.lower()

    assert result.resolved is True
    assert "self-attention" in rewritten
    assert "multi-head attention" in rewritten


def test_person_reference_follow_up(
    openai_history: list[ConversationMessage],
) -> None:
    """
    Verify a person reference can be
    resolved from conversation history.
    """

    result = rewrite_question(
        "What company does he lead?",
        openai_history,
    )

    assert result.resolved is True
    assert "sam altman" in result.question.lower()
