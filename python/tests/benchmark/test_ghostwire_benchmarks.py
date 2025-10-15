import asyncio
import os
import sys

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest

# Import benchmark routines from the new module locations
from benchmarks.embedding_benchmarks import BenchmarkRunner
from benchmarks.rag_benchmarks import RAGBenchmark
from benchmarks.summarization_benchmarks import SummarizationBenchmark


@pytest.fixture(scope="session")
def event_loop():
    """Ensure each test session gets a clean asyncio event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_embedding_benchmark():
    """Run the embedding benchmark."""
    try:
        benchmark_runner = BenchmarkRunner()
        result = await benchmark_runner.run_full_benchmark()
        assert result is not None
        print("\n✅ Embedding benchmark completed successfully.")
    except Exception as e:
        pytest.fail(f"Embedding benchmark failed: {e}")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_rag_benchmark():
    """Run the RAG benchmark."""
    try:
        benchmark = RAGBenchmark()
        result = await benchmark.run_rag_benchmark()
        assert result is not None
        print("\n✅ RAG benchmark completed successfully.")
    except Exception as e:
        pytest.fail(f"RAG benchmark failed: {e}")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_summarization_benchmark():
    """Run the summarization benchmark."""
    try:
        benchmark = SummarizationBenchmark()
        result = await benchmark.run_summarization_benchmark()
        assert result is not None
        print("\n✅ Summarization benchmark completed successfully.")
    except Exception as e:
        pytest.fail(f"Summarization benchmark failed: {e}")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_model_comparison_benchmark():
    """Run the model comparison benchmark."""
    try:
        from python.benchmarks.model_comparison_benchmark import (
            ModelComparisonBenchmark,
        )

        benchmark = ModelComparisonBenchmark()
        # Limit to fewer models and iterations for testing purposes
        benchmark.models = benchmark.models[:2]  # Only test first 2 models
        result = await benchmark.run_model_comparison()
        assert result is not None
        print("\n✅ Model comparison benchmark completed successfully.")
    except Exception as e:
        pytest.fail(f"Model comparison benchmark failed: {e}")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_benchmark_output_structure():
    """Test that benchmark outputs have the expected JSON structure with GHOSTWIRE scores."""
    try:
        benchmark_runner = BenchmarkRunner()
        result = await benchmark_runner.run_full_benchmark()

        # Verify that the result contains GHOSTWIRE scores
        expected_keys = [
            "embedding_latency",
            "embedding_stability",
            "storage_latency",
            "search_latency",
            "memory_usage_gb",
            "embedding_ghostwire_score",
            "storage_ghostwire_score",
            "search_ghostwire_score",
            "overall_ghostwire_score",
        ]

        for key in expected_keys:
            assert key in result, f"Missing expected key '{key}' in benchmark result"

        # Verify scores are numeric and in reasonable range
        assert isinstance(result["embedding_ghostwire_score"], (int, float)), (
            "Embedding GHOSTWIRE score should be numeric"
        )
        assert 0 <= result["embedding_ghostwire_score"] <= 10, (
            "Embedding GHOSTWIRE score should be in reasonable range"
        )

        print("\n✅ Benchmark output structure validation passed.")
    except Exception as e:
        pytest.fail(f"Benchmark output structure test failed: {e}")
