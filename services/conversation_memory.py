"""
Conversation memory service.

This module manages bounded in-session
conversation history.
"""

from models.conversation_message import (
    ConversationMessage,
    MessageRole,
)


class ConversationMemory:
    """
    Manage conversation history for the
    current application session.
    """

    def __init__(
        self,
        max_messages: int,
    ) -> None:
        """
        Initialize conversation memory.

        Args:
            max_messages:
                Maximum number of messages
                retained in memory.

        Raises:
            ValueError:
                If max_messages is not positive
                or is not an even number.
        """

        if max_messages <= 0:
            raise ValueError("max_messages must be greater than zero.")

        if max_messages % 2 != 0:
            raise ValueError("max_messages must be an even number.")

        self._max_messages = max_messages
        self._messages: list[ConversationMessage] = []

    @property
    def messages(
        self,
    ) -> list[ConversationMessage]:
        """
        Return a copy of the current
        conversation history.
        """

        return self._messages.copy()

    def add_user_message(
        self,
        content: str,
    ) -> None:
        """
        Add a user message to memory.
        """

        self._add_message(
            ConversationMessage(
                role=MessageRole.USER,
                content=content,
            )
        )

    def add_assistant_message(
        self,
        content: str,
    ) -> None:
        """
        Add an assistant message to memory.
        """

        self._add_message(
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content=content,
            )
        )

    def clear(self) -> None:
        """
        Remove all conversation history.
        """

        self._messages.clear()

    def _add_message(
        self,
        message: ConversationMessage,
    ) -> None:
        """
        Add a message and enforce the
        configured memory limit.
        """

        self._messages.append(message)

        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages :]
