"""
src/memory/embedder.py

Handles creating and managing context embeddings, tying them to your vector store and DB.
"""

from typing import Any, List

class ContextMemory:
    """
    A stubbed context memory engine.
    Should interface between your raw content, embeddings, and storage.
    """

    def __init__(self, db_manager: Any, vector_store: Any = None):
        """
        Initialize with a database manager and an optional vector store.
        """
        self.db_manager = db_manager
        self.vector_store = vector_store
        # TODO: Initialize embedding model or API client here

    def store_context(self, key: str, text: str) -> None:
        """
        Generate an embedding for `text` and store it with `key`.
        """
        vector = self._embed_text(text)
        if self.vector_store:
            self.vector_store.add_vector(key, vector)
        # Optionally log to DB
        print(f"🧠 Stored context for key={key}")

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """
        Embed the `query` and return top_k matching keys from the vector store.
        """
        vector = self._embed_text(query)
        if self.vector_store:
            return self.vector_store.query(vector, top_k=top_k)
        return []

    def _embed_text(self, text: str) -> List[float]:
        """
        Placeholder embedding function.
        Replace with actual model or API call.
        """
        print(f"🔗 Embedding text (stub): {text[:30]}...")
        return [0.0] * 768  # stub vector
