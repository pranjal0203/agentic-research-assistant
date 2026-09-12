"""
Unit tests for bounded conversation memory.
"""

import pytest

from models.conversation_message import (
    MessageRole,
)
from services.conversation_memory import ConversationMemory


def test_add_messages() -> None:
    """
    Verify user and assistant messages
    are stored correctly.
    """

    memory = ConversationMemory(
        max_messages=4,
    )

    memory.add_user_message(
        "Hello",
    )
    memory.add_assistant_message(
        "Hi",
    )

    messages = memory.messages

    assert len(messages) == 2

    assert messages[0].role is MessageRole.USER
    assert messages[0].content == "Hello"

    assert messages[1].role is MessageRole.ASSISTANT
    assert messages[1].content == "Hi"


def test_memory_removes_oldest_messages() -> None:
    """
    Verify the oldest messages are removed
    when memory exceeds its configured limit.
    """

    memory = ConversationMemory(
        max_messages=4,
    )

    memory.add_user_message(
        "Question 1",
    )
    memory.add_assistant_message(
        "Answer 1",
    )
    memory.add_user_message(
        "Question 2",
    )
    memory.add_assistant_message(
        "Answer 2",
    )
    memory.add_user_message(
        "Question 3",
    )
    memory.add_assistant_message(
        "Answer 3",
    )

    messages = memory.messages

    assert len(messages) == 4

    assert messages[0].content == "Question 2"
    assert messages[1].content == "Answer 2"
    assert messages[2].content == "Question 3"
    assert messages[3].content == "Answer 3"


def test_clear_memory() -> None:
    """
    Verify conversation history can
    be completely cleared.
    """

    memory = ConversationMemory(
        max_messages=4,
    )

    memory.add_user_message(
        "Hello",
    )
    memory.add_assistant_message(
        "Hi",
    )

    memory.clear()

    assert memory.messages == []


def test_messages_returns_copy() -> None:
    """
    Verify callers cannot mutate the
    internal conversation history.
    """

    memory = ConversationMemory(
        max_messages=4,
    )

    memory.add_user_message(
        "Hello",
    )

    messages = memory.messages
    messages.clear()

    assert len(memory.messages) == 1
    assert memory.messages[0].content == "Hello"


def test_zero_max_messages_rejected() -> None:
    """
    Verify a zero memory limit is rejected.
    """

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        ConversationMemory(
            max_messages=0,
        )


def test_negative_max_messages_rejected() -> None:
    """
    Verify a negative memory limit is rejected.
    """

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        ConversationMemory(
            max_messages=-2,
        )


def test_odd_max_messages_rejected() -> None:
    """
    Verify an odd memory limit is rejected
    to preserve complete conversation turns.
    """

    with pytest.raises(
        ValueError,
        match="even number",
    ):
        ConversationMemory(
            max_messages=5,
        )
