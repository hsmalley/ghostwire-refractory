from fastapi.testclient import TestClient

from ...ghostwire.main import app


def test_health_check():
    """Test the /health endpoint."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0.0"}


def test_qdrant_endpoints_registered():
    """Test that Qdrant-compatible endpoints are properly registered."""
    with TestClient(app) as client:
        # Test that Qdrant collection endpoints exist
        response = client.options("/api/v1/collections/test-collection")
        # Should return 200 or 405 (method not allowed) but not 404
        assert response.status_code in [200, 405], (
            f"Expected 200 or 405, got {response.status_code}"
        )

        # Test that Qdrant points endpoints exist
        response = client.options("/api/v1/collections/test-collection/points")
        # Should return 200 or 405 (method not allowed) but not 404
        assert response.status_code in [200, 405], (
            f"Expected 200 or 405, got {response.status_code}"
        )

        # Test that Qdrant search endpoints exist
        response = client.options("/api/v1/collections/test-collection/points/search")
        # Should return 200 or 405 (method not allowed) but not 404
        assert response.status_code in [200, 405], (
            f"Expected 200 or 405, got {response.status_code}"
        )


def test_chat_completion():
    """Test the /api/v1/chat_completion endpoint."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat_completion",
            json={"session_id": "test-session", "text": "Hello, GhostWire!"},
        )
        assert response.status_code == 200
        assert "response" in response.json()


def test_chat_embedding():
    """Test the /api/v1/chat_embedding endpoint."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat_embedding",
            json={
                "session_id": "test-session",
                "text": "Test embedding request",
                "embedding": [0.1, 0.2, 0.3],
            },
        )
        assert response.status_code == 200
        assert "response" in response.json()


def test_rate_limiting():
    """Test rate limiting middleware."""
    with TestClient(app) as client:
        # First request - should pass
        response = client.post(
            "/api/v1/chat_completion",
            json={"session_id": "test-session", "text": "First request"},
        )
        assert response.status_code == 200

        # Second request - should pass
        response = client.post(
            "/api/v1/chat_completion",
            json={"session_id": "test-session", "text": "Second request"},
        )
        assert response.status_code == 200

        # Third request - should trigger rate limit
        response = client.post(
            "/api/v1/chat_completion",
            json={"session_id": "test-session", "text": "Third request"},
        )
        assert response.status_code == 429
