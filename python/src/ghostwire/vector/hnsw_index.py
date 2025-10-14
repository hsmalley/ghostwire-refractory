"""
HNSW (Hierarchical Navigable Small World) index management for GhostWire Refractory
"""

import os
import threading

import hnswlib
import numpy as np

from ..config.settings import settings


class HNSWIndexManager:
    """Manages the HNSW index for fast vector similarity search"""

    def __init__(self):
        self._index: hnswlib.Index | None = None
        self._initialized = False
        self._lock = threading.RLock()  # Use RLock for reentrant operations
        self._hnsw_path = "memory_index.bin"

    def initialize_index(self):
        """Initialize the HNSW index and populate with existing data"""
        with self._lock:
            if self._initialized:
                return

            # Try to load persistent HNSW index if available
            if os.path.exists(self._hnsw_path):
                try:
                    self._index = hnswlib.Index(space="cosine", dim=settings.EMBED_DIM)
                    self._index.load_index(self._hnsw_path)
                    self._index.set_ef(settings.HNSW_EF)
                    self._initialized = True
                    print(
                        f"[HNSW] Loaded persistent vector index from {self._hnsw_path}."
                    )
                    return
                except Exception as e:
                    print(
                        f"[HNSW] WARNING: Failed to load persistent index ({e}). "
                        f"Falling back to DB backfill."
                    )

            # Initialize new index
            self._index = hnswlib.Index(space="cosine", dim=settings.EMBED_DIM)
            self._index.init_index(
                max_elements=settings.HNSW_MAX_ELEMENTS,
                ef_construction=settings.HNSW_EF_CONSTRUCTION,
                M=settings.HNSW_M,
            )
            self._index.set_ef(settings.HNSW_EF)

            # Backfill with existing data from DB
            self._backfill_from_db()

            self._initialized = True
            print(
                "[HNSW] In-memory vector index initialized. Loaded:",
                (self._index.get_current_count() if self._index else 0),
            )

    def _backfill_from_db(self):
        """Backfill the HNSW index with existing vectors from the database"""
        # This would require fetching all embeddings from the database
        # For now, we'll use a dummy implementation until we have the full data structure
        pass

    def add_items(self, vectors: np.ndarray, ids: np.ndarray) -> bool:
        """Add vectors to the index"""
        with self._lock:
            if not self._initialized or self._index is None:
                raise Exception("HNSW index not initialized")

            try:
                self._index.add_items(vectors, ids)
                return True
            except Exception as e:
                print(f"[HNSW] ERROR adding items: {e}")
                return False

    def knn_query(
        self, query_vectors: np.ndarray, k: int = 5
    ) -> tuple[np.ndarray, np.ndarray]:
        """Perform KNN query on the index"""
        with self._lock:
            if not self._initialized or self._index is None:
                raise Exception("HNSW index not initialized")

            try:
                labels, distances = self._index.knn_query(query_vectors, k=k)
                return labels, distances
            except Exception as e:
                print(f"[HNSW] ERROR querying index: {e}")
                raise

    def get_current_count(self) -> int:
        """Get the current number of elements in the index"""
        with self._lock:
            if not self._initialized or self._index is None:
                return 0
            return self._index.get_current_count()

    def save_index(self):
        """Save the HNSW index to disk"""
        with self._lock:
            if not self._initialized or self._index is None:
                return False

            try:
                self._index.save_index(self._hnsw_path)
                print(f"[HNSW] Saved vector index to {self._hnsw_path}.")
                return True
            except Exception as e:
                print(f"[HNSW] WARNING: Failed to save persistent index ({e}).")
                return False

    def delete_from_index(self, ids: list[int]) -> bool:
        """Mark vectors as deleted in the index (if supported)"""
        # Note: hnswlib doesn't support deletion by default
        # This is a placeholder for future implementation
        print(
            "[HNSW] Delete operation not supported by hnswlib. Consider rebuilding index."
        )
        return False


# Global instance
hnsw_manager = HNSWIndexManager()


def get_hnsw_manager() -> HNSWIndexManager:
    """Get the HNSW index manager instance"""
    return hnsw_manager
