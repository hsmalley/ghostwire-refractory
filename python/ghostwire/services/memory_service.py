"""
Memory service for GhostWire Refractory
"""

import logging

import numpy as np

from ..config.settings import settings
from ..database.repositories import MemoryRepository
from ..models.memory import Memory, MemoryCreate, MemoryQuery
from ..utils.error_handling import EmbeddingDimMismatchError
from ..utils.vector_utils import normalize_vector
from ..vector.hnsw_index import get_hnsw_manager


class MemoryService:
    """Service class for memory-related business logic"""

    def __init__(self):
        self.repository = MemoryRepository()
        self.hnsw_manager = get_hnsw_manager()
        self.logger = logging.getLogger(__name__)

    def create_memory(self, memory_create: MemoryCreate) -> Memory:
        """Create a new memory entry"""
        # Validate embedding dimension
        if len(memory_create.embedding) != settings.EMBED_DIM:
            raise EmbeddingDimMismatchError(
                settings.EMBED_DIM, len(memory_create.embedding)
            )

        # Validate embedding values
        vec = np.array(memory_create.embedding, dtype=np.float32)
        if not np.all(np.isfinite(vec)):
            raise ValueError("Embedding contains non-finite values")

        # Normalize the embedding
        normalized_vec = normalize_vector(vec)
        memory_create.embedding = normalized_vec.tolist()

        # Create memory in DB
        memory = self.repository.create_memory(memory_create)

        # Add to HNSW index for fast retrieval
        try:
            vec = np.array(memory_create.embedding, dtype=np.float32)
            self.hnsw_manager.add_items(
                vec.reshape(1, -1), np.array([memory.id], dtype=np.int64)
            )
            self.logger.info(f"[HNSW] Added vector with id {memory.id}")
        except Exception as e:
            self.logger.error(f"[HNSW] ERROR adding to index: {e}")

        return memory

    def query_similar_memories(self, query: MemoryQuery) -> list[Memory]:
        """Query for similar memories using HNSW or fallback to cosine similarity"""
        # Validate embedding dimension
        if len(query.embedding) != settings.EMBED_DIM:
            raise EmbeddingDimMismatchError(settings.EMBED_DIM, len(query.embedding))

        # Validate embedding values
        vec = np.array(query.embedding, dtype=np.float32)
        if not np.all(np.isfinite(vec)):
            raise ValueError("Query embedding contains non-finite values")

        # Normalize the query vector
        normalized_vec = normalize_vector(vec)
        query.embedding = normalized_vec.tolist()

        # Try HNSW if initialized
        self.hnsw_manager.initialize_index()  # Ensure index is ready
        count = self.hnsw_manager.get_current_count()

        if count > 0:
            try:
                k = min(query.limit, count)
                labels, distances = self.hnsw_manager.knn_query(
                    normalized_vec.reshape(1, -1), k=k
                )
                ids = [int(i) for i in labels[0]]

                if ids:
                    # Retrieve memories from DB based on HNSW results
                    # For now, retrieve from DB by session and filter by IDs
                    all_memories = self.repository.get_memories_by_session(
                        query.session_id,
                        limit=100,  # reasonable limit
                    )

                    # Filter to only those found by HNSW
                    hnsw_memories = [m for m in all_memories if m.id in ids]
                    # Sort to maintain HNSW order
                    id_order = {id_val: idx for idx, id_val in enumerate(ids)}
                    hnsw_memories.sort(key=lambda m: id_order[m.id])

                    result = hnsw_memories[: query.limit]
                    self.logger.info(
                        f"[HNSW] Retrieved {len(result)} neighbors from HNSW index."
                    )
                    return result
            except Exception as e:
                self.logger.error(
                    f"[HNSW] Query failed ({e}); falling back to cosine similarity."
                )

        # Fallback: cosine similarity on DB results
        self.logger.info("[DB] Using fallback cosine similarity")
        return self.repository.query_similar_by_embedding(
            query.session_id, query.embedding, query.limit
        )

    def query_similar_memories_with_scores(
        self, query: MemoryQuery
    ) -> list[tuple[Memory, float]]:
        """Query for similar memories and return with similarity scores"""
        # Validate embedding dimension
        if len(query.embedding) != settings.EMBED_DIM:
            raise EmbeddingDimMismatchError(settings.EMBED_DIM, len(query.embedding))

        # Validate embedding values
        vec = np.array(query.embedding, dtype=np.float32)
        if not np.all(np.isfinite(vec)):
            raise ValueError("Query embedding contains non-finite values")

        # Normalize the query vector
        normalized_vec = normalize_vector(vec)
        query.embedding = normalized_vec.tolist()

        # Try HNSW if initialized
        self.hnsw_manager.initialize_index()  # Ensure index is ready
        count = self.hnsw_manager.get_current_count()

        if count > 0:
            try:
                k = min(query.limit, count)
                labels, distances = self.hnsw_manager.knn_query(
                    normalized_vec.reshape(1, -1), k=k
                )
                ids = [int(i) for i in labels[0]]
                distances_list = distances[0].tolist()

                if ids:
                    # Retrieve memories from DB based on HNSW results
                    all_memories = self.repository.get_memories_by_session(
                        query.session_id,
                        limit=100,  # reasonable limit
                    )

                    # Create results list with proper score mapping
                    results = []
                    id_to_memory = {m.id: m for m in all_memories}

                    for memory_id, distance in zip(ids, distances_list):
                        if memory_id in id_to_memory:
                            # Convert distance to similarity (HNSW distance is typically Euclidean or cosine distance)
                            # For cosine distance, similarity = 1.0 - distance
                            similarity = 1.0 - float(distance)
                            results.append((id_to_memory[memory_id], similarity))

                    self.logger.info(
                        f"[HNSW] Retrieved {len(results)} neighbors from HNSW index with scores."
                    )
                    return results
            except Exception as e:
                self.logger.error(
                    f"[HNSW] Query with scores failed ({e}); falling back to cosine similarity."
                )

        # Fallback: cosine similarity on DB results
        self.logger.info("[DB] Using fallback cosine similarity for scored query")
        # For the fallback case, we return the memories with dummy scores
        # In the repository, cosine similarities are calculated but not returned
        memories = self.repository.query_similar_by_embedding(
            query.session_id, query.embedding, query.limit
        )
        return [
            (memory, 0.0) for memory in memories
        ]  # Placeholder - repository doesn't return actual scores

    def get_memories_by_session(self, session_id: str, limit: int = 10) -> list[Memory]:
        """Get memories for a specific session"""
        return self.repository.get_memories_by_session(session_id, limit)

    def get_all_sessions(self) -> list[str]:
        """Get all unique session IDs"""
        return self.repository.get_all_sessions()

    def delete_collection(self, collection_name: str) -> bool:
        """Delete all memories in a collection"""
        return self.repository.delete_collection(collection_name)

    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists"""
        return self.repository.collection_exists(collection_name)

    def get_collection_size(self, collection_name: str) -> int:
        """Get the number of memories in a collection"""
        return self.repository.get_collection_size(collection_name)


# Global instance
memory_service = MemoryService()
