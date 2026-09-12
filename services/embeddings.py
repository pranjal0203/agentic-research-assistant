"""
Embedding model initialization.

This module initializes the embedding model
used for semantic search.
"""

from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import EMBEDDING_MODEL

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
)
