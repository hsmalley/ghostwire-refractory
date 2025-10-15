"""
HNSW (Hierarchical Navigable Small World) index management for GhostWire Refractory
"""

import os
import threading

import hnswlib
import numpy as np

from ..config.settings import settings
from ..database.repositories import MemoryRepository


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
        # Fetch all memories from the database
        try:
            # Get all unique session IDs to fetch memories for all sessions
            all_sessions = MemoryRepository.get_all_sessions()

            if not all_sessions:
                print("[HNSW] No existing sessions found in database to backfill")
                return

            # For each session, load memories and add embeddings to HNSW index
            total_items = 0
            for session_id in all_sessions:
                # Get memories with embeddings from the database
                memories = MemoryRepository.get_memories_by_session(
                    session_id, limit=1000
                )  # Prevent loading too many at once

                if memories:
                    # Extract embeddings and IDs for the HNSW index
                    embeddings = []
                    ids = []

                    for memory in memories:
                        # Convert embedding bytes back to array
                        embedding_array = np.frombuffer(
                            memory.embedding, dtype=np.float32
                        )
                        if (
                            len(embedding_array) == settings.EMBED_DIM
                        ):  # Ensure it matches expected dimension
                            embeddings.append(embedding_array)
                            ids.append(memory.id)
                        else:
                            print(
                                f"[HNSW] Skipping memory {memory.id} with mismatched embedding dimension"
                            )

                    # Add embeddings to HNSW index in batches if there are any
                    if embeddings and ids:
                        vectors = np.array(embeddings, dtype=np.float32)
                        ids_array = np.array(ids, dtype=np.int64)

                        if self._index is not None:
                            self._index.add_items(vectors, ids_array)
                            total_items += len(ids)

            print(f"[HNSW] Successfully backfilled {total_items} vectors from database")
        except Exception as e:
            print(f"[HNSW] ERROR during DB backfill: {e}")

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
            "[HNSW] Delete operation not supported by hnswlib. "
            "Consider rebuilding index."
        )
        return False


# Global instance
hnsw_manager = HNSWIndexManager()


def get_hnsw_manager() -> HNSWIndexManager:
    """Get the HNSW index manager instance"""
    return hnsw_manager
