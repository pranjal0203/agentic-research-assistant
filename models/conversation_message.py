"""
Conversation message model.

This module defines a single message
within a conversation.
"""

from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """
    Role associated with a conversation message.
    """

    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ConversationMessage:
    """
    Represent a single conversation message.

    Attributes:
        role:
            The participant that produced
            the message.

        content:
            The textual message content.
    """

    role: MessageRole
    content: str
