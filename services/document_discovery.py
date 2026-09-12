"""
Document discovery service.

This module discovers document collections
from the configured data directory.
"""

from config.settings import (
    DATA_DIR,
    SUPPORTED_DOCUMENT_TYPES,
)
from models.collection import Collection


def discover_collections() -> tuple[Collection, ...]:
    """
    Discover all document collections.

    Directory structure::

        data/
            finance/
                report.pdf
                invoice.pdf

            legal/
                nda.pdf

    Returns:
        A tuple of discovered collections.
    """

    if not DATA_DIR.is_dir():
        return ()

    collections: list[Collection] = []

    for collection_dir in sorted(DATA_DIR.iterdir()):

        if not collection_dir.is_dir():
            continue

        documents = tuple(
            sorted(
                document
                for document in collection_dir.rglob("*")
                if (
                    document.is_file()
                    and document.suffix.lower() in SUPPORTED_DOCUMENT_TYPES
                )
            )
        )

        if not documents:
            continue

        collections.append(
            Collection(
                name=collection_dir.name,
                path=collection_dir,
                documents=documents,
            )
        )

    return tuple(collections)
