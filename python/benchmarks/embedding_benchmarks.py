"""
Updated benchmarking tools for GhostWire Refractory with GHOSTWIRE scoring
"""

import argparse
import asyncio
import os
import sys
import time

import httpx
import psutil
import numpy as np

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python.ghostwire.config.settings import settings
from python.ghostwire.utils.ghostwire_scoring import (
    compute_general_ghostwire_score,
    format_benchmark_results_with_scores
)


class BenchmarkRunner:
    """Benchmark runner for GhostWire Refractory"""

    def __init__(self, controller_url: str = None):
        self.controller_url = controller_url or settings.LOCAL_OLLAMA_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def test_embedding_performance(
        self, model: str, text: str, iterations: int = 10
    ) -> tuple[float, list[float], float]:
        """Test embedding performance and stability"""
        latencies = []
        embeddings = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                response = await self.client.post(
                    f"{self.controller_url}/api/embeddings",
                    json={"input": text, "model": model},
                )
                response.raise_for_status()
                latency = time.perf_counter() - start_time
                latencies.append(latency)
                
                # Store the embedding to calculate stability
                data = response.json()
                embedding = data.get("data", [{}])[0].get("embedding", [])
                if embedding:
                    embeddings.append(np.array(embedding))
            except Exception as e:
                print(f"Embedding request failed: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")
        
        # Calculate embedding stability (consistency) using cosine similarity
        stability = 1.0  # Default perfect stability
        if len(embeddings) > 1:
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    similarity = np.dot(embeddings[i], embeddings[j]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                    )
                    similarities.append(similarity)
            stability = np.mean(similarities) if similarities else 1.0

        return avg_latency, latencies, stability

    async def test_memory_storage_performance(
        self, iterations: int = 10
    ) -> tuple[float, list[float]]:
        """Test memory storage performance"""
        latencies = []

        for i in range(iterations):
            text = f"Test memory entry {i} for performance evaluation"
            embedding = [0.1] * settings.EMBED_DIM  # Mock embedding

            start_time = time.perf_counter()
            try:
                response = await self.client.post(
                    f"{self.controller_url}/api/v1/chat/memory",
                    json={
                        "session_id": "benchmark_session",
                        "text": text,
                        "embedding": embedding,
                    },
                )
                response.raise_for_status()
                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Memory storage request failed: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")
        return avg_latency, latencies

    async def test_similarity_search_performance(
        self, iterations: int = 10
    ) -> tuple[float, list[float]]:
        """Test similarity search performance"""
        latencies = []

        for _ in range(iterations):
            query_embedding = [0.1] * settings.EMBED_DIM  # Mock query embedding

            start_time = time.perf_counter()
            try:
                response = await self.client.post(
                    f"{self.controller_url}/api/v1/vectors/query",
                    json={
                        "namespace": "benchmark_session",
                        "embedding": query_embedding,
                        "top_k": 5,
                    },
                )
                response.raise_for_status()
                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Similarity search request failed: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")
        return avg_latency, latencies

    async def run_full_benchmark(self):
        """Run the complete benchmark suite"""
        print("🚀 Starting GhostWire Refractory Benchmark Suite")
        print("=" * 60)

        # Start memory monitoring
        initial_memory = psutil.virtual_memory().used / (1024**3)  # GB

        # Test embedding performance
        print("\n📝 Testing Embedding Performance...")
        avg_emb_lat, latencies, embedding_stability = await self.test_embedding_performance(
            model="nomic-embed-text",
            text="This is a test sentence for embedding performance evaluation.",
            iterations=5,
        )
        print(f"  Average embedding latency: {avg_emb_lat:.4f}s")
        print(f"  Embedding stability: {embedding_stability:.4f}")

        # Test memory storage
        print("\n💾 Testing Memory Storage Performance...")
        avg_store_lat, _ = await self.test_memory_storage_performance(iterations=5)
        print(f"  Average memory storage latency: {avg_store_lat:.4f}s")

        # Test similarity search
        print("\n🔍 Testing Similarity Search Performance...")
        avg_search_lat, _ = await self.test_similarity_search_performance(iterations=5)
        print(f"  Average similarity search latency: {avg_search_lat:.4f}s")

        # Memory usage difference
        final_memory = psutil.virtual_memory().used / (1024**3)  # GB
        memory_diff = final_memory - initial_memory
        print(f"\n📊 Memory usage difference: {memory_diff:.3f} GB")

        print("\n✅ Benchmark suite completed!")
        print("=" * 60)

        # Calculate GHOSTWIRE scores
        embedding_ghostwire_score = compute_general_ghostwire_score(
            latency=avg_emb_lat,
            stability=embedding_stability,
            memory_usage=memory_diff
        )
        
        storage_ghostwire_score = compute_general_ghostwire_score(
            latency=avg_store_lat,
            stability=1.0,  # Perfect stability for storage
            memory_usage=memory_diff
        )
        
        search_ghostwire_score = compute_general_ghostwire_score(
            latency=avg_search_lat,
            stability=1.0,  # Assuming perfect stability for search
            memory_usage=memory_diff
        )
        
        overall_ghostwire_score = compute_general_ghostwire_score(
            # Weighted average of all latencies
            latency=(avg_emb_lat + avg_store_lat + avg_search_lat) / 3,
            stability=embedding_stability,  # Use embedding stability as overall stability
            memory_usage=memory_diff
        )

        print(f"\n🏆 GHOSTWIRE SCORES:")
        print(f"  Embedding Performance Score: {embedding_ghostwire_score:.4f}")
        print(f"  Memory Storage Performance Score: {storage_ghostwire_score:.4f}")
        print(f"  Similarity Search Performance Score: {search_ghostwire_score:.4f}")
        print(f"  Overall GHOSTWIRE Score: {overall_ghostwire_score:.4f}")

        return {
            "embedding_latency": avg_emb_lat,
            "embedding_stability": embedding_stability,
            "storage_latency": avg_store_lat,
            "search_latency": avg_search_lat,
            "memory_usage_gb": memory_diff,
            "embedding_ghostwire_score": embedding_ghostwire_score,
            "storage_ghostwire_score": storage_ghostwire_score,
            "search_ghostwire_score": search_ghostwire_score,
            "overall_ghostwire_score": overall_ghostwire_score,
        }


async def main():
    parser = argparse.ArgumentParser(description="GhostWire Refractory Benchmark Tool")
    parser.add_argument(
        "--controller",
        type=str,
        default=settings.LOCAL_OLLAMA_URL,
        help="Controller URL for benchmarking",
    )
    parser.add_argument(
        "--iterations", type=int, default=5, help="Number of iterations for each test"
    )

    args = parser.parse_args()

    benchmark_runner = BenchmarkRunner(controller_url=args.controller)
    results = await benchmark_runner.run_full_benchmark()

    print("\n📈 FINAL RESULTS:")
    print(f"  Embedding Latency: {results['embedding_latency']:.4f}s")
    print(f"  Embedding Stability: {results['embedding_stability']:.4f}")
    print(f"  Storage Latency: {results['storage_latency']:.4f}s")
    print(f"  Search Latency: {results['search_latency']:.4f}s")
    print(f"  Memory Usage: {results['memory_usage_gb']:.3f} GB")
    print(f"  Embedding GHOSTWIRE Score: {results['embedding_ghostwire_score']:.4f}")
    print(f"  Storage GHOSTWIRE Score: {results['storage_ghostwire_score']:.4f}")
    print(f"  Search GHOSTWIRE Score: {results['search_ghostwire_score']:.4f}")
    print(f"  Overall GHOSTWIRE Score: {results['overall_ghostwire_score']:.4f}")

    # Also print formatted results with GHOSTWIRE scoring
    print("\n" + format_benchmark_results_with_scores(results, score_function_name="general"))


if __name__ == "__main__":
    asyncio.run(main())
