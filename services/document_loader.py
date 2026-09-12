"""
Document loading service.

This module loads supported documents into
LangChain Document objects.
"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from config.settings import DATA_DIR, SUPPORTED_DOCUMENT_TYPES

DOCUMENT_LOADERS: dict[str, type] = {
    ".pdf": PyPDFLoader,
}


def load_document(
    document_path: str | Path,
) -> list[Document]:
    """
    Load a supported document.

    Args:
        document_path:
            Path to the document.

    Returns:
        A list of LangChain Document objects.

    Raises:
        FileNotFoundError:
            If the document does not exist.

        ValueError:
            If the document type is unsupported.
    """

    document_path = Path(document_path)

    if not document_path.is_file():
        raise FileNotFoundError(f"Document not found: {document_path}")

    suffix = document_path.suffix.lower()

    if suffix not in SUPPORTED_DOCUMENT_TYPES:
        raise ValueError(
            f"Unsupported document type: '{suffix}'. "
            f"Supported types: "
            f"{', '.join(SUPPORTED_DOCUMENT_TYPES)}."
        )

    loader_class = DOCUMENT_LOADERS[suffix]

    loader = loader_class(str(document_path))

    documents = loader.load()

    relative_path = document_path.relative_to(DATA_DIR)

    collection = relative_path.parts[0]

    for document in documents:
        document.metadata.update(
            {
                "collection": collection,
                "source_file": document_path.name,
                "relative_path": relative_path.as_posix(),
                "document_type": suffix,
            }
        )

    return documents
