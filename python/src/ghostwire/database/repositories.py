"""
Database repositories for GhostWire Refractory
"""
import sqlite3
import time
from typing import List, Optional
import numpy as np

from ..models.memory import Memory, MemoryCreate
from .connection import get_db_connection


class MemoryRepository:
    """Repository for memory-related database operations"""
    
    @staticmethod
    def create_memory(memory_create: MemoryCreate) -> Memory:
        """Create a new memory entry in the database"""
        with get_db_connection() as conn:
            # Convert embedding list to bytes
            embedding_bytes = np.array(memory_create.embedding, dtype=np.float32).tobytes()
            
            cursor = conn.execute(
                """
                INSERT INTO memory_text (session_id, prompt_text, answer_text, timestamp, embedding, summary_text)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_create.session_id,
                    memory_create.prompt_text,
                    memory_create.answer_text,
                    memory_create.timestamp or time.time(),
                    embedding_bytes,
                    memory_create.summary_text
                )
            )
            memory_id = cursor.lastrowid
            
            # Return the created memory with ID
            return Memory(
                id=memory_id,
                session_id=memory_create.session_id,
                prompt_text=memory_create.prompt_text,
                answer_text=memory_create.answer_text,
                timestamp=time.time(),
                embedding=embedding_bytes,
                summary_text=memory_create.summary_text
            )
    
    @staticmethod
    def get_memories_by_session(session_id: str, limit: int = 10) -> List[Memory]:
        """Get memories for a specific session"""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, session_id, prompt_text, answer_text, timestamp, embedding, summary_text
                FROM memory_text
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (session_id, limit)
            )
            
            rows = cursor.fetchall()
            memories = []
            for row in rows:
                memories.append(
                    Memory(
                        id=row["id"],
                        session_id=row["session_id"],
                        prompt_text=row["prompt_text"],
                        answer_text=row["answer_text"],
                        timestamp=row["timestamp"],
                        embedding=row["embedding"],
                        summary_text=row["summary_text"]
                    )
                )
            return memories
    
    @staticmethod
    def get_all_sessions() -> List[str]:
        """Get all unique session IDs"""
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT DISTINCT session_id FROM memory_text")
            rows = cursor.fetchall()
            return [row["session_id"] for row in rows]
    
    @staticmethod
    def query_similar_by_embedding(
        session_id: str, 
        embedding: List[float], 
        limit: int = 5
    ) -> List[Memory]:
        """Query memories similar to the provided embedding"""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, session_id, prompt_text, answer_text, timestamp, embedding, summary_text
                FROM memory_text
                WHERE session_id = ?
                """,
                (session_id,)
            )
            
            rows = cursor.fetchall()
            target_vec = np.array(embedding, dtype=np.float32)
            
            # Calculate cosine similarity with all stored embeddings
            scored_memories = []
            for row in rows:
                stored_embedding = np.frombuffer(row["embedding"], dtype=np.float32)
                
                # Calculate cosine similarity
                dot_product = np.dot(target_vec, stored_embedding)
                norm_product = np.linalg.norm(target_vec) * np.linalg.norm(stored_embedding)
                similarity = dot_product / (norm_product + 1e-8)  # Add small epsilon to avoid division by zero
                
                scored_memories.append((similarity, Memory(
                    id=row["id"],
                    session_id=row["session_id"],
                    prompt_text=row["prompt_text"],
                    answer_text=row["answer_text"],
                    timestamp=row["timestamp"],
                    embedding=row["embedding"],
                    summary_text=row["summary_text"]
                )))
            
            # Sort by similarity in descending order
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            
            # Return top 'limit' results
            return [memory for _, memory in scored_memories[:limit]]
    
    @staticmethod
    def delete_collection(collection_name: str) -> bool:
        """Delete all memories in a collection (session)"""
        with get_db_connection() as conn:
            conn.execute("DELETE FROM memory_text WHERE session_id = ?", (collection_name,))
            
            # Record in dropped_collections table
            conn.execute(
                "INSERT OR REPLACE INTO dropped_collections (name) VALUES (?)",
                (collection_name,)
            )
            return True
    
    @staticmethod
    def collection_exists(collection_name: str) -> bool:
        """Check if a collection exists"""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM dropped_collections WHERE name = ?",
                (collection_name,)
            )
            dropped = cursor.fetchone() is not None
            
            if dropped:
                return False
                
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM memory_text WHERE session_id = ?",
                (collection_name,)
            )
            count = cursor.fetchone()["count"]
            return count > 0
    
    @staticmethod
    def get_collection_size(collection_name: str) -> int:
        """Get the number of memories in a collection"""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM memory_text WHERE session_id = ?",
                (collection_name,)
            )
            return cursor.fetchone()["count"]