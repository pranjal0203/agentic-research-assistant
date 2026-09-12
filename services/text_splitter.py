"""
Document chunking service.

This module splits loaded documents into
smaller chunks suitable for embedding
and semantic retrieval.
"""

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from config.settings import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split documents into smaller chunks.

    Document metadata is preserved for every
    generated chunk.

    Args:
        documents:
            Documents to split.

    Returns:
        A list of chunked documents.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return text_splitter.split_documents(
        documents,
    )
