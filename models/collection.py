"""
Collection model.

Represents a logical collection of documents.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class Collection:
    """
    Represents a document collection discovered
    from the configured data directory.
    """

    name: str
    path: Path
    documents: tuple[Path, ...]

    @property
    def document_count(self) -> int:
        """
        Return the number of documents
        in the collection.
        """

        return len(self.documents)
