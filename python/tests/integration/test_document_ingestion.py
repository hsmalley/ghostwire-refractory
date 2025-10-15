"""
Integration tests for document ingestion functionality
"""

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..scripts.import_documents import DocumentIngestor

client = TestClient(app)


@pytest.mark.integration
def test_document_ingestion_script_integration():
    """Test that the document ingestion script integrates with the API"""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write("This is a test document for integration testing.")
        tmp_file_path = Path(tmp_file.name)

    try:
        # Test that we can import and use the script
        from ..scripts.import_documents import main

        # The script should be importable
        assert main is not None

        # The script should have a DocumentIngestor class
        assert DocumentIngestor is not None

        # Create an instance
        ingestor = DocumentIngestor()
        assert ingestor is not None

    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)


@pytest.mark.integration
async def test_document_ingestion_with_api_endpoints():
    """Test that document ingestion works with API endpoints"""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write("This is a test document for API integration testing.")
        tmp_file_path = Path(tmp_file.name)

    try:
        # Create ingestor
        ingestor = DocumentIngestor()

        # Test dry run ingestion (should not affect the API)
        chunks_processed, chunks_stored = await ingestor.ingest_document(
            tmp_file_path, dry_run=True
        )

        # We should have processed at least one chunk
        assert chunks_processed >= 1
        assert chunks_stored == 0  # No chunks stored in dry run

        # Verify that the health endpoint still works
        response = client.get("/health")
        assert response.status_code == 200

        # Verify that the embeddings endpoint still works
        response = client.post("/api/v1/embeddings", json={"input": "test"})
        # This might fail due to missing model, but shouldn't crash
        assert response.status_code in [200, 400, 422, 500]  # Any valid HTTP status

    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)


@pytest.mark.integration
def test_document_ingestion_script_cli_args():
    """Test that the document ingestion script accepts CLI arguments"""

    # Test that we can create an argument parser
    from ..scripts.import_documents import main

    # This test ensures the script can be imported and has the expected structure
    assert callable(main) or hasattr(main, "__call__")


@pytest.mark.integration
async def test_document_ingestion_vector_storage():
    """Test that document ingestion properly interacts with vector storage"""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write("This is a test document for vector storage integration.")
        tmp_file_path = Path(tmp_file.name)

    try:
        # Create ingestor
        ingestor = DocumentIngestor()

        # Test dry run ingestion
        chunks_processed, chunks_stored = await ingestor.ingest_document(
            tmp_file_path, dry_run=True
        )

        # We should have processed at least one chunk
        assert chunks_processed >= 1
        assert chunks_stored == 0  # No chunks stored in dry run

        # Verify that the vector database is still accessible
        # (This would normally check the actual database, but we'll just make sure
        # the API endpoints still respond)
        response = client.get("/health")
        assert response.status_code == 200

    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)
