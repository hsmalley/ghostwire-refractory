import asyncio

import pytest

# Import benchmark routines
# Make sure these functions exist or adjust to match your actual entrypoints.
from ghostwire_benchmarking import run_benchmark
from ghostwire_rag_benchmark import run_benchmark as run_rag_test
from ghostwire_retrieval_benchmark import run_retrieval_test
from ghostwire_summarization_benchmark import run_summarization_benchmark


@pytest.fixture(scope="session")
def event_loop():
    """Ensure each test session gets a clean asyncio event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_rag_benchmark():
    """Run the RAG benchmark with embeddinggemma + Gemma."""
    try:
        result = await run_rag_test()
        assert result is not None
        print("\n✅ RAG benchmark completed successfully.")
    except Exception as e:
        pytest.fail(f"RAG benchmark failed: {e}")


@pytest.mark.asyncio
async def test_general_benchmark():
    """Run the general Ghostwire benchmark."""
    try:
        result = await run_benchmark()
        assert result is not None
        print("\n✅ General benchmark completed successfully.")
    except Exception as e:
        pytest.fail(f"General benchmark failed: {e}")


@pytest.mark.asyncio
async def test_retrieval_benchmark():
    """Run the retrieval benchmark pipeline."""
    try:
        result = await run_retrieval_test()
        assert result is not None
        print("\n✅ Retrieval benchmark completed successfully.")
    except Exception as e:
        pytest.fail(f"Retrieval benchmark failed: {e}")


@pytest.mark.asyncio
async def test_summarization_benchmark():
    """Run the summarization benchmark."""
    result = await run_summarization_benchmark()
    assert result and all(len(s["summary"]) > 0 for s in result)
    print("\n✅ Summarization benchmark completed successfully.")
