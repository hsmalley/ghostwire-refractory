"""
Unit tests for GhostWire Refractory - Enhanced Cache Service
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from python.ghostwire.services.cache_service import CacheService


class TestEnhancedCacheService:
    def setup_method(self):
        """Setup method to create a cache service instance for each test"""
        # Use a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Patch the database path to use our temporary database
        self.original_db_path = os.environ.get("DB_PATH")
        os.environ["DB_PATH"] = self.temp_db.name

        self.service = CacheService()

    def teardown_method(self):
        """Teardown method to clean up after each test"""
        # Restore original database path
        if self.original_db_path:
            os.environ["DB_PATH"] = self.original_db_path
        elif "DB_PATH" in os.environ:
            del os.environ["DB_PATH"]

        # Clean up temporary database file
        try:
            os.unlink(self.temp_db.name)
        except OSError:
            pass

    def test_initialize_cache_tables(self):
        """Test that cache tables are initialized correctly"""
        # The service should have been initialized in setup_method
        assert self.service is not None

        # Check that both tables exist by attempting to insert data
        result = self.service.cache_response(
            session_id="test_session",
            query="test query",
            query_embedding=[0.1, 0.2, 0.3] * 256,  # 768 dimensions
            response="test response",
        )
        assert result is True

        result = self.service.cache_exact_response(
            session_id="test_session", query="test query", response="test response"
        )
        assert result is True

    def test_exact_response_caching(self):
        """Test exact response caching and retrieval"""
        session_id = "test_session"
        query = "What is the capital of France?"
        response = "The capital of France is Paris."

        # Cache the exact response
        result = self.service.cache_exact_response(
            session_id=session_id, query=query, response=response
        )
        assert result is True

        # Retrieve the exact response
        cached_result = self.service.get_exact_response(session_id, query)
        assert cached_result is not None
        assert cached_result["response"] == response
        assert "context" in cached_result

    def test_exact_response_cache_miss(self):
        """Test exact response cache miss"""
        session_id = "test_session"
        query = "What is the capital of France?"

        # Try to retrieve a non-existent exact response
        cached_result = self.service.get_exact_response(session_id, query)
        assert cached_result is None

    def test_exact_response_cache_expiration(self):
        """Test exact response cache expiration"""
        session_id = "test_session"
        query = "What is the capital of France?"
        response = "The capital of France is Paris."

        # Cache the exact response with a very short TTL
        result = self.service.cache_exact_response(
            session_id=session_id,
            query=query,
            response=response,
            ttl_minutes=0,  # Expire immediately
        )
        assert result is True

        # Try to retrieve the expired response (should be cleaned up)
        cached_result = self.service.get_exact_response(session_id, query)
        assert cached_result is None

    def test_original_similarity_cache_still_works(self):
        """Test that original similarity-based caching still works"""
        session_id = "test_session"
        query = "What is the capital of France?"
        query_embedding = [0.1, 0.2, 0.3] * 256  # 768 dimensions
        response = "The capital of France is Paris."

        # Cache the response using similarity-based caching
        result = self.service.cache_response(
            session_id=session_id,
            query=query,
            query_embedding=query_embedding,
            response=response,
        )
        assert result is True

        # Retrieve the response using similarity-based caching
        cached_result = self.service.get_cached_response(
            session_id=session_id, query=query, query_embedding=query_embedding
        )
        assert cached_result is not None
        assert cached_result["response"] == response

    def test_both_caching_layers_work_together(self):
        """Test that both exact and similarity caching work together"""
        session_id = "test_session"
        query = "What is the capital of France?"
        query_embedding = [0.1, 0.2, 0.3] * 256  # 768 dimensions
        response = "The capital of France is Paris."

        # Cache using both methods
        exact_result = self.service.cache_exact_response(
            session_id=session_id, query=query, response=response
        )
        similarity_result = self.service.cache_response(
            session_id=session_id,
            query=query,
            query_embedding=query_embedding,
            response=response,
        )
        assert exact_result is True
        assert similarity_result is True

        # Retrieve using exact match (should be faster)
        exact_cached = self.service.get_exact_response(session_id, query)
        assert exact_cached is not None
        assert exact_cached["response"] == response

        # Retrieve using similarity match
        similarity_cached = self.service.get_cached_response(
            session_id=session_id, query=query, query_embedding=query_embedding
        )
        assert similarity_cached is not None
        assert similarity_cached["response"] == response
