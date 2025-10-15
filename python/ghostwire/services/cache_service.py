"""
Cache service for GhostWire Refractory to optimize token usage
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta

import numpy as np

from ..database.connection import get_db_connection


class CacheService:
    """Service for caching embedding comparisons and responses to reduce token usage"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_cache_table()

    def _initialize_cache_table(self):
        """Initialize the cache table in the database"""
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    session_id TEXT NOT NULL,
                    query_embedding BLOB NOT NULL,
                    response TEXT NOT NULL,
                    context TEXT,
                    similarity_threshold REAL DEFAULT 0.9,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            # Create index for faster lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON cache(cache_key)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_session_id ON cache(session_id)"
            )

            # Create table for exact response caching (for repeated requests)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS exact_response_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    context TEXT,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    UNIQUE(session_id, query)
                )
            """)
            # Create indexes for faster lookups
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_exact_query ON exact_response_cache(session_id, query)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_exact_expires_at ON exact_response_cache(expires_at)"
            )

    def _generate_cache_key(
        self, session_id: str, query: str, query_embedding: list[float]
    ) -> str:
        """
        Generate a unique cache key based on session, query, and embedding
        """
        # Create a hash combining session_id, query text, and embedding
        content = (
            f"{session_id}:{query}:{json.dumps(query_embedding, separators=(',', ':'))}"
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def _calculate_similarity(
        self, embedding1: list[float], embedding2: list[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        vec1 = np.array(embedding1, dtype=np.float32)
        vec2 = np.array(embedding2, dtype=np.float32)

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)

        if norm_product == 0:
            return 0.0

        similarity = dot_product / norm_product
        return float(similarity)

    def get_cached_response(
        self,
        session_id: str,
        query: str,
        query_embedding: list[float],
        similarity_threshold: float = 0.9,
    ) -> dict | None:
        """
        Get cached response if similar query exists
        """
        try:
            cache_key = self._generate_cache_key(session_id, query, query_embedding)

            # First try exact match
            with get_db_connection() as conn:
                # Clean expired entries first
                conn.execute(
                    "DELETE FROM cache WHERE expires_at < ?",
                    (datetime.utcnow().timestamp(),),
                )

                # Try exact match
                cursor = conn.execute(
                    "SELECT response, context FROM cache WHERE cache_key = ? AND expires_at > ?",
                    (cache_key, datetime.utcnow().timestamp()),
                )
                row = cursor.fetchone()

                if row:
                    self.logger.info(
                        f"Cache HIT: Exact match found for session {session_id}"
                    )
                    return {"response": row[0], "context": row[1]}

                # If no exact match, try similarity-based search within the session
                cursor = conn.execute(
                    """
                    SELECT cache_key, query_embedding, response, context, similarity_threshold
                    FROM cache
                    WHERE session_id = ? AND expires_at > ?
                    ORDER BY created_at DESC
                    LIMIT 100
                """,
                    (session_id, datetime.utcnow().timestamp()),
                )

                rows = cursor.fetchall()

                for row in rows:
                    stored_embedding_bytes = row[1]
                    stored_embedding = np.frombuffer(
                        stored_embedding_bytes, dtype=np.float32
                    ).tolist()

                    similarity = self._calculate_similarity(
                        query_embedding, stored_embedding
                    )

                    # Use the stored threshold or default to the parameter
                    threshold = row[4] if row[4] is not None else similarity_threshold

                    if similarity >= threshold:
                        self.logger.info(
                            f"Cache HIT: Similar match found (similarity: {similarity:.3f}) "
                            f"for session {session_id}"
                        )
                        return {
                            "response": row[2],
                            "context": row[3],
                            "similarity": similarity,
                        }

                self.logger.info(
                    f"Cache MISS: No similar match found for session {session_id}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving cached response: {e}")
            return None

    def cache_response(
        self,
        session_id: str,
        query: str,
        query_embedding: list[float],
        response: str,
        context: str | None = None,
        similarity_threshold: float = 0.9,
        ttl_minutes: int = 60,
    ) -> bool:
        """
        Cache a response for future similar queries
        """
        try:
            cache_key = self._generate_cache_key(session_id, query, query_embedding)

            expires_at = (
                datetime.utcnow() + timedelta(minutes=ttl_minutes)
            ).timestamp()
            created_at = datetime.utcnow().timestamp()

            # Convert embedding to bytes for storage
            embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()

            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache
                    (cache_key, session_id, query_embedding, response, context, similarity_threshold, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        cache_key,
                        session_id,
                        embedding_bytes,
                        response,
                        context,
                        similarity_threshold,
                        created_at,
                        expires_at,
                    ),
                )

            self.logger.info(
                f"Response cached for session {session_id} with key {cache_key[:8]}..."
            )
            return True

        except Exception as e:
            self.logger.error(f"Error caching response: {e}")
            return False

    def get_exact_response(self, session_id: str, query: str) -> dict | None:
        """
        Get exact cached response for repeated requests
        """
        try:
            with get_db_connection() as conn:
                # Clean expired entries first
                conn.execute(
                    "DELETE FROM exact_response_cache WHERE expires_at < ?",
                    (datetime.utcnow().timestamp(),),
                )

                # Try exact match
                cursor = conn.execute(
                    "SELECT response, context FROM exact_response_cache WHERE session_id = ? AND query = ? AND expires_at > ?",
                    (session_id, query, datetime.utcnow().timestamp()),
                )
                row = cursor.fetchone()

                if row:
                    self.logger.info(
                        f"Exact cache HIT: Found response for repeated query in session {session_id}"
                    )
                    return {"response": row[0], "context": row[1]}

                self.logger.info(
                    f"Exact cache MISS: No exact match found for query in session {session_id}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving exact cached response: {e}")
            return None

    def cache_exact_response(
        self,
        session_id: str,
        query: str,
        response: str,
        context: str | None = None,
        ttl_minutes: int = 120,  # Longer TTL for exact responses
    ) -> bool:
        """
        Cache exact response for repeated requests
        """
        try:
            expires_at = (
                datetime.utcnow() + timedelta(minutes=ttl_minutes)
            ).timestamp()
            created_at = datetime.utcnow().timestamp()

            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO exact_response_cache
                    (session_id, query, response, context, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        session_id,
                        query,
                        response,
                        context,
                        created_at,
                        expires_at,
                    ),
                )

            self.logger.info(
                f"Exact response cached for session {session_id} query '{query[:50]}...'"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error caching exact response: {e}")
            return False

    def invalidate_cache_for_session(self, session_id: str) -> bool:
        """
        Remove all cached entries for a session (e.g., when memory changes)
        """
        try:
            with get_db_connection() as conn:
                # Note: We don't currently store session_id in cache table
                # This would need to be added for per-session invalidation
                # For now, we'll implement a more general cleanup
                conn.execute(
                    "DELETE FROM cache WHERE created_at < ?",
                    ((datetime.utcnow() - timedelta(days=7)).timestamp(),),
                )  # Remove very old entries
            return True
        except Exception as e:
            self.logger.error(f"Error invalidating cache: {e}")
            return False

    def get_cache_stats(self) -> dict:
        """
        Get statistics about the cache
        """
        try:
            with get_db_connection() as conn:
                total_count = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
                expired_count = conn.execute(
                    "SELECT COUNT(*) FROM cache WHERE expires_at < ?",
                    (datetime.utcnow().timestamp(),),
                ).fetchone()[0]

                return {
                    "total_entries": total_count,
                    "expired_entries": expired_count,
                    "active_entries": total_count - expired_count,
                }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"total_entries": 0, "expired_entries": 0, "active_entries": 0}


# Global instance
cache_service = CacheService()
