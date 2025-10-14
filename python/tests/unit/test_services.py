"""
Unit tests for GhostWire Refractory - Services
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from unittest.mock import MagicMock, patch

from python.src.ghostwire.models.memory import MemoryCreate
from python.src.ghostwire.services.memory_service import MemoryService


class TestMemoryService:
    def setup_method(self):
        """Setup method to create a memory service instance for each test"""
        self.service = MemoryService()

    @patch("src.ghostwire.database.repositories.MemoryRepository.create_memory")
    @patch("src.ghostwire.vector.hnsw_index.get_hnsw_manager")
    def test_create_memory(self, mock_get_hnsw_manager, mock_create_memory):
        """Test creating a memory entry"""
        # Mock the HNSW manager
        mock_hnsw_manager = MagicMock()
        mock_hnsw_manager.add_items = MagicMock(return_value=True)
        mock_get_hnsw_manager.return_value = mock_hnsw_manager

        # Mock the repository response
        mock_memory = MagicMock()
        mock_memory.id = 1
        mock_memory.session_id = "test_session"
        mock_memory.embedding = b"test_embedding"
        mock_create_memory.return_value = mock_memory

        # Create a test memory
        memory_create = MemoryCreate(
            session_id="test_session",
            prompt_text="Test prompt",
            answer_text="Test answer",
            embedding=[0.1, 0.2, 0.3] * 256,  # Ensure it matches EMBED_DIM (768)
        )

        result = self.service.create_memory(memory_create)

        # Verify the result
        assert result.id == 1
        assert result.session_id == "test_session"

        # Verify that HNSW add_items was called
        mock_hnsw_manager.add_items.assert_called_once()

    @patch(
        "src.ghostwire.database.repositories.MemoryRepository.query_similar_by_embedding"
    )
    @patch("src.ghostwire.vector.hnsw_index.get_hnsw_manager")
    def test_query_similar_memories(self, mock_get_hnsw_manager, mock_query_db):
        """Test querying similar memories"""
        # Mock the HNSW manager
        mock_hnsw_manager = MagicMock()
        mock_hnsw_manager.initialize_index = MagicMock()
        mock_hnsw_manager.get_current_count = MagicMock(
            return_value=0
        )  # No HNSW results
        mock_get_hnsw_manager.return_value = mock_hnsw_manager

        # Mock the repository response
        mock_memory = MagicMock()
        mock_memory.id = 1
        mock_memory.session_id = "test_session"
        mock_memory.prompt_text = "Test prompt"
        mock_memory.answer_text = "Test answer"
        mock_memory.embedding = b"test_embedding"
        mock_query_db.return_value = [mock_memory]

        # Query similar memories
        from src.ghostwire.models.memory import MemoryQuery

        query = MemoryQuery(
            session_id="test_session",
            embedding=[0.1, 0.2, 0.3] * 256,  # Ensure it matches EMBED_DIM (768)
            limit=5,
        )

        result = self.service.query_similar_memories(query)

        # Verify the result
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].session_id == "test_session"

        # Verify that DB fallback was used (since HNSW count was 0)
        mock_query_db.assert_called_once()
