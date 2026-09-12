"""
Language model initialization.

This module initializes the application's
language model using the configured settings
and environment variables.

The model configuration is centralized in
config.settings so services do not hardcode
provider or model details.
"""

import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from config.settings import (
    MODEL_NAME,
    OMNIROUTE_API_BASE,
    TEMPERATURE,
    USE_OMNIROUTE,
)


def _get_groq_api_key() -> str:
    """
    Return the configured Groq API key.

    Raises:
        ValueError:
            If GROQ_API_KEY is not configured and OmniRoute is inactive.
    """

    api_key = os.getenv(
        "GROQ_API_KEY",
    )

    if not api_key:
        if USE_OMNIROUTE:
            return "omni-route-dummy-key"
        raise ValueError("GROQ_API_KEY not found in environment variables.")

    return api_key


def _create_llm() -> BaseChatModel:
    """
    Create the application's configured
    chat model.
    """

    if USE_OMNIROUTE:
        return ChatOpenAI(
            model=MODEL_NAME,
            openai_api_key=_get_groq_api_key(),
            openai_api_base=OMNIROUTE_API_BASE,
            temperature=TEMPERATURE,
        )

    return ChatGroq(
        model=MODEL_NAME,
        api_key=_get_groq_api_key(),
        temperature=TEMPERATURE,
    )


llm = _create_llm()
