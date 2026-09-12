"""
Application startup pipeline.

This module prepares everything needed
before the interactive chat loop begins.
"""

from services.index_manager import IndexManager


def initialize_pipeline() -> IndexManager:
    """
    Initialize the RAG pipeline.

    Workflow:

        1. Discover available document collections.
        2. Initialize the index manager.

    Returns:
        An initialized IndexManager instance.
    """

    print("📂 Discovering document collections...")

    index_manager = IndexManager()

    if not index_manager.list_collections():
        print("⚠️ No document collections found.")

    print("✅ Pipeline initialized.\n")

    return index_manager
