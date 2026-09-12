"""
Vector store service.

This module creates or loads a Chroma
vector database used for semantic retrieval.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from services.embeddings import embeddings


def _vector_store_exists(db_path: Path) -> bool:
    """
    Return whether a persisted Chroma
    vector store exists.

    Args:
        db_path:
            Path to the vector database.

    Returns:
        True if the vector store exists,
        otherwise False.
    """

    return db_path.is_dir() and (db_path / "chroma.sqlite3").is_file()


def get_vector_store(
    db_path: Path,
    documents: list[Document] | None = None,
) -> Chroma:
    """
    Load an existing Chroma vector store.

    If the vector database does not exist,
    create a new one using the supplied
    documents.

    Args:
        db_path:
            Path to the vector database.

        documents:
            Documents used to create the
            vector store if it does not
            already exist.

    Returns:
        An initialized Chroma vector store.

    Raises:
        ValueError:
            If the vector database does not
            exist and no documents are
            provided.
    """

    if _vector_store_exists(db_path):

        print(f"📂 Loading vector database: {db_path.name}")

        return Chroma(
            persist_directory=str(db_path),
            embedding_function=embeddings,
        )

    if documents is None:
        raise ValueError("Documents are required when creating a new vector database.")

    print(f"🆕 Creating vector database: {db_path.name}")

    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(db_path),
    )
