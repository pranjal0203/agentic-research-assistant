from pathlib import Path
from unittest.mock import patch

import pytest

from models.collection import Collection
from services.index_manager import IndexManager
from services.pipeline import initialize_pipeline


@patch("services.index_manager.discover_collections")
def test_initialize_pipeline(mock_discover):
    """
    Verify pipeline initialize steps trigger correctly.
    """
    col1 = Collection(
        name="research", path=Path("data/research"), documents=(Path("doc1.pdf"),)
    )
    mock_discover.return_value = (col1,)

    index_manager = initialize_pipeline()
    assert isinstance(index_manager, IndexManager)
    assert len(index_manager.list_collections()) == 1


@patch("services.index_manager.discover_collections")
def test_index_manager_collections(mock_discover):
    """
    Verify list_collections and get_collection error scenarios.
    """
    col1 = Collection(
        name="finance", path=Path("data/finance"), documents=(Path("fin1.pdf"),)
    )
    mock_discover.return_value = (col1,)

    manager = IndexManager()
    assert manager.list_collections() == (col1,)

    # Retrieve valid collection
    assert manager.get_collection("finance") == col1

    # Retrieve invalid collection expects ValueError
    with pytest.raises(ValueError, match="Unknown collection"):
        manager.get_collection("unknown_col")
