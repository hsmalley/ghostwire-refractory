"""
Updated benchmarking tools for GhostWire Refractory
"""
import argparse
import asyncio
import time
from typing import List, Tuple
import numpy as np
import psutil

import httpx
from ..config.settings import settings


class BenchmarkRunner:
    """Benchmark runner for GhostWire Refractory"""
    
    def __init__(self, controller_url: str = None):
        self.controller_url = controller_url or settings.LOCAL_OLLAMA_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_embedding_performance(
        self, 
        model: str, 
        text: str, 
        iterations: int = 10
    ) -> Tuple[float, List[float]]:
        """Test embedding performance"""
        latencies = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                response = await self.client.post(
                    f"{self.controller_url}/api/embeddings",
                    json={"input": text, "model": model}
                )
                response.raise_for_status()
                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Embedding request failed: {e}")
                continue
        
        avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')
        return avg_latency, latencies
    
    async def test_memory_storage_performance(
        self, 
        iterations: int = 10
    ) -> Tuple[float, List[float]]:
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
                        "embedding": embedding
                    }
                )
                response.raise_for_status()
                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Memory storage request failed: {e}")
                continue
        
        avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')
        return avg_latency, latencies
    
    async def test_similarity_search_performance(
        self, 
        iterations: int = 10
    ) -> Tuple[float, List[float]]:
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
                        "top_k": 5
                    }
                )
                response.raise_for_status()
                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Similarity search request failed: {e}")
                continue
        
        avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')
        return avg_latency, latencies
    
    async def run_full_benchmark(self):
        """Run the complete benchmark suite"""
        print("🚀 Starting GhostWire Refractory Benchmark Suite")
        print("=" * 60)
        
        # Test embedding performance
        print("\n📝 Testing Embedding Performance...")
        avg_emb_lat, latencies = await self.test_embedding_performance(
            model="nomic-embed-text", 
            text="This is a test sentence for embedding performance evaluation.",
            iterations=5
        )
        print(f"  Average embedding latency: {avg_emb_lat:.4f}s")
        
        # Test memory storage
        print("\n💾 Testing Memory Storage Performance...")
        avg_store_lat, _ = await self.test_memory_storage_performance(iterations=5)
        print(f"  Average memory storage latency: {avg_store_lat:.4f}s")
        
        # Test similarity search
        print("\n🔍 Testing Similarity Search Performance...")
        avg_search_lat, _ = await self.test_similarity_search_performance(iterations=5)
        print(f"  Average similarity search latency: {avg_search_lat:.4f}s")
        
        # Memory usage
        memory_usage = psutil.virtual_memory().used / (1024**3)  # GB
        print(f"\n📊 Memory usage: {memory_usage:.3f} GB")
        
        print("\n✅ Benchmark suite completed!")
        print("=" * 60)
        
        return {
            "embedding_latency": avg_emb_lat,
            "storage_latency": avg_store_lat,
            "search_latency": avg_search_lat,
            "memory_usage_gb": memory_usage
        }


async def main():
    parser = argparse.ArgumentParser(description="GhostWire Refractory Benchmark Tool")
    parser.add_argument("--controller", type=str, default=settings.LOCAL_OLLAMA_URL,
                       help="Controller URL for benchmarking")
    parser.add_argument("--iterations", type=int, default=5,
                       help="Number of iterations for each test")
    
    args = parser.parse_args()
    
    benchmark_runner = BenchmarkRunner(controller_url=args.controller)
    results = await benchmark_runner.run_full_benchmark()
    
    print("\n📈 FINAL RESULTS:")
    print(f"  Embedding Latency: {results['embedding_latency']:.4f}s")
    print(f"  Storage Latency: {results['storage_latency']:.4f}s") 
    print(f"  Search Latency: {results['search_latency']:.4f}s")
    print(f"  Memory Usage: {results['memory_usage_gb']:.3f} GB")


if __name__ == "__main__":
    asyncio.run(main())