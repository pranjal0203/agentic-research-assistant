"""
Conversation orchestration service.

This module coordinates conversation memory,
context-aware question rewriting, retrieval,
and memory updates.
"""

from langchain_chroma import Chroma

from models.response import Response
from services.agent import answer_question
from services.conversation_memory import ConversationMemory
from services.question_rewriter import rewrite_question


class ConversationService:
    """
    Orchestrate context-aware conversational
    interactions with the retrieval pipeline.
    """

    def __init__(
        self,
        vector_store: Chroma,
        memory: ConversationMemory,
    ) -> None:
        """
        Initialize the conversation service.

        Args:
            vector_store:
                The initialized Chroma vector store.

            memory:
                Conversation memory for the
                current application session.
        """

        self._vector_store = vector_store
        self._memory = memory

    def ask(
        self,
        question: str,
    ) -> Response | None:
        """
        Process a conversational question.

        The question is resolved against recent
        conversation history before being routed
        through the retrieval pipeline.

        Args:
            question:
                The user's original question.

        Returns:
            The generated response when the
            question can be resolved.

            None when additional conversational
            context is required.
        """

        question = question.strip()

        if not question:
            return None

        # --------------------------------------------------
        # Resolve conversational references BEFORE retrieval.
        # --------------------------------------------------

        rewrite_result = rewrite_question(
            question,
            self._memory.messages,
        )

        if not rewrite_result.resolved:
            return None

        standalone_question = rewrite_result.question.strip()

        if not standalone_question:
            return None

        # --------------------------------------------------
        # Show rewrite when the user's question
        # depended on conversation context.
        # --------------------------------------------------

        if standalone_question != question:
            print(
                "[Conversation] Rewritten question:",
                standalone_question,
            )

        # --------------------------------------------------
        # Send ONLY the standalone question to the agent.
        #
        # The agent should not perform another rewrite.
        # --------------------------------------------------

        response = answer_question(
            self._vector_store,
            standalone_question,
        )

        # --------------------------------------------------
        # Update conversation memory only after
        # successful answer generation.
        # --------------------------------------------------

        if response is None:
            return None

        self._memory.add_user_message(
            question,
        )

        self._memory.add_assistant_message(
            response.answer,
        )

        return response

    def clear(self) -> None:
        """
        Clear the current conversation history.
        """

        self._memory.clear()
