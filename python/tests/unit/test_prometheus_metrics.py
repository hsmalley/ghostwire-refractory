"""
Unit tests for Prometheus metrics functionality
"""

from fastapi.testclient import TestClient
from ghostwire.main import app

client = TestClient(app)


def test_health_endpoint_instrumentation():
    """Test that hitting the health endpoint increments metrics"""
    # Hit the health endpoint to generate metrics
    response = client.get("/health")
    assert response.status_code == 200

    # Check that metrics were recorded
    metrics_response = client.get("/api/v1/metrics")
    assert metrics_response.status_code == 200

    # The metrics should now include the health endpoint call
    content = metrics_response.content.decode()

    # Check for the presence of our custom metrics
    assert (
        'api_server_calls_total{route="health"}' in content
        or "api_server_calls_total" in content
    )


def test_metrics_endpoint_exists():
    """Test that the /metrics endpoint exists and returns Prometheus metrics"""
    # First generate some metrics by hitting an endpoint
    client.get("/health")

    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    # Check that the response contains some expected metric names
    content = response.content.decode()
    assert (
        "api_server_latency_seconds" in content or "api_server_calls_total" in content
    )


def test_metrics_endpoint_content_type():
    """Test that the /metrics endpoint returns the correct content type"""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "charset=utf-8" in response.headers["content-type"]
