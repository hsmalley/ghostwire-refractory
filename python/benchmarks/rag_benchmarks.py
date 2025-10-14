"""
RAG (Retrieval-Augmented Generation) benchmarking for GhostWire Refractory
"""

import asyncio
import os
import sys
import time

import httpx

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python.ghostwire.config.settings import settings


class RAGBenchmark:
    """Benchmark class for RAG performance testing"""

    def __init__(self, controller_url: str = None):
        self.controller_url = controller_url or "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def test_rag_query(
        self, session_id: str, query: str, model: str = None, iterations: int = 5
    ) -> tuple[float, list[float]]:
        """Test RAG query performance"""
        latencies = []
        model = model or settings.DEFAULT_OLLAMA_MODEL

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                # First get embedding for the query
                embedding_response = await self.client.post(
                    f"{self.controller_url}/api/v1/embeddings",
                    json={"input": query, "model": "nomic-embed-text"},
                )
                embedding_response.raise_for_status()
                embedding_data = embedding_response.json()
                embedding = embedding_data["data"][0]["embedding"]

                # Then make the RAG query
                rag_response = await self.client.post(
                    f"{self.controller_url}/api/v1/chat/chat_embedding",
                    json={
                        "session_id": session_id,
                        "text": query,
                        "embedding": embedding,
                    },
                )
                rag_response.raise_for_status()

                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"RAG query failed: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")
        return avg_latency, latencies

    async def test_retrieval_only(
        self, session_id: str, query: str, iterations: int = 5
    ) -> tuple[float, list[float]]:
        """Test retrieval-only performance (without generation)"""
        latencies = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                # Get embedding for the query
                embedding_response = await self.client.post(
                    f"{self.controller_url}/api/v1/embeddings",
                    json={"input": query, "model": "nomic-embed-text"},
                )
                embedding_response.raise_for_status()
                embedding_data = embedding_response.json()
                embedding = embedding_data["data"][0]["embedding"]

                # Query vectors
                rag_response = await self.client.post(
                    f"{self.controller_url}/api/v1/vectors/query",
                    json={"namespace": session_id, "embedding": embedding, "top_k": 5},
                )
                rag_response.raise_for_status()

                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Retrieval query failed: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")
        return avg_latency, latencies

    async def run_rag_benchmark(self):
        """Run the complete RAG benchmark suite"""
        print("🚀 Starting RAG Benchmark Suite")
        print("=" * 60)

        test_queries = [
            "What is quantum computing?",
            "Explain the theory of relativity",
            "How does photosynthesis work?",
            "What are neural networks?",
            "Explain blockchain technology",
        ]

        session_id = "rag_benchmark_session"

        # Test retrieval-only performance
        print("\n🔍 Testing Retrieval Performance...")
        avg_retrieval_lat, _ = await self.test_retrieval_only(
            session_id, test_queries[0], iterations=3
        )
        print(f"  Average retrieval latency: {avg_retrieval_lat:.4f}s")

        # Test full RAG performance
        print("\n🤖 Testing Full RAG Performance...")
        avg_rag_lat, _ = await self.test_rag_query(
            session_id, test_queries[0], iterations=3
        )
        print(f"  Average RAG latency: {avg_rag_lat:.4f}s")

        print("\n✅ RAG benchmark suite completed!")
        print("=" * 60)

        return {"retrieval_latency": avg_retrieval_lat, "rag_latency": avg_rag_lat}


async def main():
    benchmark = RAGBenchmark()
    results = await benchmark.run_rag_benchmark()

    print("\n📈 RAG BENCHMARK RESULTS:")
    print(f"  Retrieval Latency: {results['retrieval_latency']:.4f}s")
    print(f"  RAG Latency: {results['rag_latency']:.4f}s")


if __name__ == "__main__":
    asyncio.run(main())
