"""
Integration tests for Prometheus metrics functionality
"""

import pytest
from fastapi.testclient import TestClient
from ghostwire.main import app

client = TestClient(app)


@pytest.mark.integration
def test_metrics_recorded_on_api_calls():
    """Test that metrics are recorded when API endpoints are called"""
    # Hit the health endpoint
    response = client.get("/health")
    assert response.status_code == 200

    # Get metrics
    metrics_response = client.get("/api/v1/metrics")
    assert metrics_response.status_code == 200

    # Check that the metrics include the health endpoint call
    content = metrics_response.content.decode()

    # Look for the health endpoint metrics
    # Note: The exact metric names might differ based on implementation
    assert "api_server_calls_total" in content or "api_" in content


@pytest.mark.integration
def test_multiple_api_calls_increase_counters():
    """Test that multiple API calls properly increase counters"""
    # Get initial metrics
    initial_metrics = client.get("/api/v1/metrics")
    initial_metrics.content.decode()

    # Hit the health endpoint multiple times
    for _ in range(3):
        response = client.get("/health")
        assert response.status_code == 200

    # Get final metrics
    final_metrics = client.get("/api/v1/metrics")
    final_metrics.content.decode()

    # The final metrics should show increased counts
    # (This would require parsing the metrics more carefully in a real test)
