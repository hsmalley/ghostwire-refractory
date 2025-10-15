"""
Unit tests for document ingestion functionality
"""

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..scripts.import_documents import DocumentIngestor

client = TestClient(app)


def test_document_ingestor_initialization():
    """Test that DocumentIngestor can be initialized correctly"""
    ingestor = DocumentIngestor(
        chunk_size=500, overlap_size=50, enable_summarization=False
    )
    assert ingestor.chunk_size == 500
    assert ingestor.overlap_size == 50
    assert not ingestor.enable_summarization


@pytest.mark.asyncio
async def test_document_ingestion_single_file():
    """Test that a single file can be ingested"""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write("This is a test document for ingestion.")
        tmp_file_path = Path(tmp_file.name)

    try:
        # Create ingestor
        ingestor = DocumentIngestor()

        # Test dry run ingestion
        chunks_processed, chunks_stored = await ingestor.ingest_document(
            tmp_file_path, dry_run=True
        )

        # We should have processed at least one chunk, but stored none in dry run
        assert chunks_processed >= 1
        assert chunks_stored == 0

    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)


@pytest.mark.asyncio
async def test_document_ingestion_directory():
    """Test that a directory can be ingested"""
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create test files
        (tmp_path / "test1.txt").write_text("This is test document 1.")
        (tmp_path / "test2.md").write_text(
            "# Test Document 2\n\nThis is a markdown test."
        )

        # Create ingestor
        ingestor = DocumentIngestor()

        # Test dry run ingestion
        chunks_processed, chunks_stored = await ingestor.ingest_directory(
            tmp_path, dry_run=True
        )

        # We should have processed at least two chunks, but stored none in dry run
        assert chunks_processed >= 2
        assert chunks_stored == 0


def test_document_ingestor_cli_script_exists():
    """Test that the document ingestion CLI script exists and is executable"""
    script_path = Path(__file__).parent.parent / "scripts" / "import_documents.py"
    assert script_path.exists(), f"Document ingestion script not found at {script_path}"
    assert os.access(script_path, os.X_OK) or script_path.suffix == ".py", (
        "Script should be executable or a Python file"
    )


@pytest.mark.asyncio
async def test_chunking_functionality():
    """Test that document chunking works correctly"""
    ingestor = DocumentIngestor(chunk_size=10, overlap_size=2)

    # Create a long text that should be chunked
    long_text = (
        "This is a very long text that should be split into multiple chunks. " * 5
    )

    # Use the chunker directly
    chunks = ingestor.chunker.chunk_text(long_text, source="test")

    # We should have multiple chunks
    assert len(chunks) > 1

    # Each chunk should have text content
    for chunk in chunks:
        assert "text" in chunk
        assert len(chunk["text"]) > 0


def test_document_ingestion_help_output():
    """Test that the document ingestion script provides help output"""
    import sys
    from io import StringIO

    from ..scripts.import_documents import main

    # Capture help output
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        # This should print help and exit
        main()
    except SystemExit:
        # Expected when --help is used
        pass
    finally:
        sys.stdout = old_stdout

    # Check that help text was printed
    output = captured_output.getvalue()
    assert "usage:" in output.lower() or "help" in output.lower()
