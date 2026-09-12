"""
Index manager service.

This module manages document collections and
their corresponding vector stores.
"""

import json
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config.settings import (
    CHROMA_DB_PATH,
    INDEX_MANIFEST_FILENAME,
)
from models.collection import Collection
from services.document_discovery import discover_collections
from services.document_loader import load_document
from services.text_splitter import split_documents
from services.vector_store import get_vector_store

Manifest = dict[str, dict[str, dict[str, int]]]


class IndexManager:
    """
    Lazily manages document collection indexes.
    """

    def __init__(self) -> None:
        """
        Discover available document collections.
        """

        self._collections: dict[str, Collection] = {
            collection.name: collection for collection in discover_collections()
        }

        self._collection_list = tuple(
            sorted(
                self._collections.values(),
                key=lambda collection: collection.name,
            )
        )

        self._vector_stores: dict[str, Chroma] = {}

    def list_collections(self) -> tuple[Collection, ...]:
        """
        Return all discovered collections.
        """

        return self._collection_list

    def get_collection(
        self,
        name: str,
    ) -> Collection:
        """
        Return a discovered collection.

        Args:
            name:
                Collection name.

        Returns:
            The requested collection.

        Raises:
            ValueError:
                If the collection does not exist.
        """

        collection = self._collections.get(name)

        if collection is None:
            available = ", ".join(
                self._collections.keys(),
            )

            raise ValueError(
                f"Unknown collection '{name}'. " f"Available collections: {available}"
            )

        return collection

    def get_vector_store(
        self,
        name: str,
    ) -> Chroma:
        """
        Return the vector store for a collection.

        The vector store is lazily loaded,
        cached and automatically rebuilt
        when the collection changes.

        Args:
            name:
                Collection name.

        Returns:
            An initialized Chroma vector store.
        """

        vector_store = self._vector_stores.get(name)

        if vector_store is not None:
            return vector_store

        collection = self.get_collection(name)

        db_path = CHROMA_DB_PATH / collection.name

        if self._needs_reindex(
            collection,
            db_path,
        ):
            print(f"♻️ Collection changed. Rebuilding index: {collection.name}")

            self._remove_index(db_path)

            documents = self._load_documents(
                collection,
            )

            chunks = split_documents(
                documents,
            )

            vector_store = get_vector_store(
                db_path=db_path,
                documents=chunks,
            )

            self._save_manifest(
                collection,
                db_path,
            )

        else:
            print(f"📂 Loading existing index: {collection.name}")

            vector_store = get_vector_store(
                db_path=db_path,
            )

        self._vector_stores[name] = vector_store

        return vector_store

    def _load_documents(
        self,
        collection: Collection,
    ) -> list[Document]:
        """
        Load every document belonging
        to a collection.
        """

        documents: list[Document] = []

        for document_path in collection.documents:
            documents.extend(load_document(document_path))

        return documents

    def _manifest_path(
        self,
        db_path: Path,
    ) -> Path:
        """
        Return the manifest path for a vector database.
        """

        return db_path / INDEX_MANIFEST_FILENAME

    def _build_manifest(
        self,
        collection: Collection,
    ) -> Manifest:
        """
        Build the current manifest for a collection.
        """

        documents: dict[str, dict[str, int]] = {}

        for document in collection.documents:
            stats = document.stat()

            documents[
                document.relative_to(
                    collection.path,
                ).as_posix()
            ] = {
                "size": stats.st_size,
                "modified": int(stats.st_mtime),
            }

        return {
            "documents": documents,
        }

    def _load_manifest(
        self,
        db_path: Path,
    ) -> Manifest | None:
        """
        Load the persisted index manifest.

        Returns:
            The manifest if it exists,
            otherwise None.
        """

        manifest_path = self._manifest_path(
            db_path,
        )

        if not manifest_path.is_file():
            return None

        try:
            with manifest_path.open(
                encoding="utf-8",
            ) as file:
                return json.load(file)

        except json.JSONDecodeError:
            return None

    def _save_manifest(
        self,
        collection: Collection,
        db_path: Path,
    ) -> None:
        """
        Persist the current collection manifest.
        """

        manifest = self._build_manifest(
            collection,
        )

        db_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._manifest_path(
            db_path,
        ).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                manifest,
                file,
                indent=4,
                sort_keys=True,
            )

    def _needs_reindex(
        self,
        collection: Collection,
        db_path: Path,
    ) -> bool:
        """
        Determine whether the collection
        requires re-indexing.
        """

        manifest = self._load_manifest(
            db_path,
        )

        if manifest is None:
            return True

        current_manifest = self._build_manifest(
            collection,
        )

        return manifest != current_manifest

    def _remove_index(
        self,
        db_path: Path,
    ) -> None:
        """
        Remove an existing vector database.
        """

        if db_path.is_dir():
            shutil.rmtree(db_path)
