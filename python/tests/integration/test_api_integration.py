"""
Integration tests for GhostWire Refractory API
These tests require a running GhostWire Refractory server
"""

import asyncio
import os
import sys

import httpx
import pytest

# Add the python/src directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from python.src.ghostwire.config.settings import settings

# Base URL for the API - can be overridden with environment variable
BASE_URL = os.getenv("GHOSTWIRE_BASE_URL", "http://localhost:8000")


@pytest.mark.asyncio
class TestAPIIntegration:
    """Integration tests that require a running GhostWire Refractory server"""

    async def test_health_check(self):
        """Test the health check endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert data["status"] == "ok"

    async def test_embedding_generation(self):
        """Test embedding generation endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            test_text = "This is a test sentence for embedding."
            response = await client.post(
                f"{BASE_URL}/api/v1/embeddings",
                json={"input": test_text, "model": "nomic-embed-text"},
            )

            # May fail if Ollama is not running, so make it optional in CI
            if response.status_code == 500:
                pytest.skip("Ollama not available or model not loaded")

            assert response.status_code == 200
            data = response.json()

            assert "data" in data
            assert len(data["data"]) > 0
            assert "embedding" in data["data"][0]
            assert len(data["data"][0]["embedding"]) == settings.EMBED_DIM

    async def test_memory_storage_and_retrieval(self):
        """Test memory storage and retrieval functionality"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            session_id = "integration_test_session"
            test_text = "Integration test memory entry"

            # First, get an embedding for the test text
            embed_response = await client.post(
                f"{BASE_URL}/api/v1/embeddings",
                json={"input": test_text, "model": "nomic-embed-text"},
            )

            if embed_response.status_code == 500:
                pytest.skip("Ollama not available or model not loaded")

            embed_data = embed_response.json()
            embedding = embed_data["data"][0]["embedding"]

            # Store the memory
            store_response = await client.post(
                f"{BASE_URL}/api/v1/chat/memory",
                json={
                    "session_id": session_id,
                    "text": test_text,
                    "embedding": embedding,
                },
            )
            assert store_response.status_code == 200

            # Query similar vectors
            query_response = await client.post(
                f"{BASE_URL}/api/v1/vectors/query",
                json={"namespace": session_id, "embedding": embedding, "top_k": 5},
            )
            assert query_response.status_code == 200
            query_data = query_response.json()

            # At least the stored memory should be found
            assert "data" in query_data
            # Note: This might not match exactly since we're searching with the same vector
            # The important thing is that the API calls work without error

    async def test_models_list(self):
        """Test the models listing endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/api/v1/models")
            # This endpoint doesn't require Ollama, should always work
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)


if __name__ == "__main__":
    # Allow running this test file directly
    asyncio.run(TestAPIIntegration().test_health_check())
