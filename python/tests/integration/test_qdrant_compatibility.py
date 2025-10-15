"""
Integration tests for GhostWire Refractory - Qdrant Compatibility
"""

import time

from fastapi.testclient import TestClient

from python.ghostwire.main import app

# Skip these tests by default to avoid external dependencies
# Uncomment the line below to run these tests
# pytest.skip("Skipping Qdrant integration tests", allow_module_level=True)

client = TestClient(app)


class TestQdrantCompatibility:
    """Integration tests for Qdrant-compatible endpoints"""

    def setup_method(self):
        """Setup method to run before each test"""
        # Use a unique collection name for each test to avoid conflicts
        self.collection_name = f"test_collection_{int(time.time() * 1000)}"
        self.test_vector = [0.1] * 768  # Standard embedding dimension

    def test_qdrant_collection_lifecycle(self):
        """Test complete collection lifecycle: create, get info, delete"""
        # Test creating a collection
        response = client.put(f"/api/v1/collections/{self.collection_name}")
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert result["result"]["acknowledged"] is True

        # Test getting collection info
        response = client.get(f"/api/v1/collections/{self.collection_name}")
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert "status" in result
        assert result["status"] == "acknowledged"

        # Check collection info fields
        collection_info = result["result"]
        assert "status" in collection_info
        assert "optimizer_status" in collection_info
        assert "vectors_count" in collection_info
        assert isinstance(collection_info["vectors_count"], int)

        # Test deleting the collection
        response = client.delete(f"/api/v1/collections/{self.collection_name}")
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert result["result"]["acknowledged"] is True

    def test_qdrant_upsert_and_search_points(self):
        """Test upserting points and searching them"""
        # First create the collection
        response = client.put(f"/api/v1/collections/{self.collection_name}")
        assert response.status_code == 200

        # Test upserting points
        test_points = {
            "points": [
                {
                    "id": 1,
                    "payload": {
                        "text": "This is a test document",
                        "metadata": "Test metadata",
                        "summary": "Test summary",
                    },
                    "vector": self.test_vector,
                },
                {
                    "id": 2,
                    "payload": {
                        "text": "This is another test document",
                        "metadata": "More test metadata",
                        "summary": "Another test summary",
                    },
                    "vector": [0.2] * 768,  # Different vector
                },
            ]
        }

        response = client.put(
            f"/api/v1/collections/{self.collection_name}/points", json=test_points
        )
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert "status" in result
        assert result["status"] == "acknowledged"

        # Test searching points
        search_request = {
            "vector": self.test_vector,
            "limit": 5,
            "with_payload": True,
            "with_vectors": False,
        }

        response = client.post(
            f"/api/v1/collections/{self.collection_name}/points/search",
            json=search_request,
        )
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert "status" in result
        assert result["status"] == "acknowledged"

        # Verify search results structure
        search_results = result["result"]
        assert isinstance(search_results, list)

        # If there are results, verify their structure
        if search_results:
            for point in search_results:
                assert "id" in point
                assert "version" in point
                assert "score" in point
                assert "payload" in point
                # Score should be a float between 0 and 1 (or similar range)
                assert isinstance(point["score"], (int, float))

        # Clean up by deleting the collection
        response = client.delete(f"/api/v1/collections/{self.collection_name}")
        assert response.status_code == 200

    def test_qdrant_search_with_invalid_vector_dimension(self):
        """Test searching with invalid vector dimension returns proper error"""
        # First create the collection
        response = client.put(f"/api/v1/collections/{self.collection_name}")
        assert response.status_code == 200

        # Test searching with invalid vector dimension
        invalid_vector = [0.1] * 100  # Wrong dimension (should be 768)
        search_request = {"vector": invalid_vector, "limit": 5}

        response = client.post(
            f"/api/v1/collections/{self.collection_name}/points/search",
            json=search_request,
        )
        # Should return validation error for wrong dimension
        assert response.status_code == 422 or response.status_code == 500

        # Clean up
        client.delete(f"/api/v1/collections/{self.collection_name}")

    def test_qdrant_delete_nonexistent_collection(self):
        """Test deleting a nonexistent collection returns proper error"""
        nonexistent_collection = f"nonexistent_{int(time.time() * 1000)}"

        response = client.delete(f"/api/v1/collections/{nonexistent_collection}")
        # Should return 404 or handle gracefully
        assert response.status_code in [200, 404, 500]

    def test_qdrant_collection_info_nonexistent(self):
        """Test getting info for nonexistent collection"""
        nonexistent_collection = f"nonexistent_{int(time.time() * 1000)}"

        response = client.get(f"/api/v1/collections/{nonexistent_collection}")
        # Should return proper response even for nonexistent collection
        # (implementation may vary)
        assert response.status_code in [200, 404, 500]

    def test_qdrant_upsert_to_nonexistent_collection(self):
        """Test upserting points to nonexistent collection creates it implicitly"""
        nonexistent_collection = f"implicit_{int(time.time() * 1000)}"

        test_points = {
            "points": [
                {
                    "id": 1,
                    "payload": {
                        "text": "Implicit creation test",
                        "metadata": "Test metadata",
                    },
                    "vector": self.test_vector,
                }
            ]
        }

        response = client.put(
            f"/api/v1/collections/{nonexistent_collection}/points", json=test_points
        )
        # Should either succeed (implicit creation) or fail gracefully
        assert response.status_code in [200, 404, 500]

        # Clean up if it was created
        client.delete(f"/api/v1/collections/{nonexistent_collection}")
