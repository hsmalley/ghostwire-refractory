"""
Model comparison benchmarking using GHOSTWIRE scores
This file provides a comprehensive way to compare different models using the overall GHOSTWIRE score
"""

import argparse
import asyncio
import os
import sys
import time

import httpx
import numpy as np

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ghostwire.config.settings import settings
from ghostwire.utils.ghostwire_scoring import (
    compute_general_ghostwire_score,
    compute_rag_ghostwire_score,
    compute_summarization_ghostwire_score,
)


class ModelComparisonBenchmark:
    """Benchmark class for comparing different models using GHOSTWIRE scores"""

    def __init__(self, controller_url: str = None):
        self.controller_url = controller_url or "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=60.0)
        self.models = settings.EMBED_MODELS  # Use models from settings

    async def test_embedding_performance_for_model(
        self, model: str, text: str, iterations: int = 3
    ) -> dict:
        """Test embedding performance for a specific model"""
        latencies = []
        embeddings = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                response = await self.client.post(
                    f"{self.controller_url}/api/v1/embeddings",
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
                print(f"Embedding request failed for model {model}: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")

        # Calculate embedding stability (consistency) using cosine similarity
        stability = 1.0  # Default perfect stability
        if len(embeddings) > 1:
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    if len(embeddings[i]) > 0 and len(embeddings[j]) > 0:
                        similarity = np.dot(embeddings[i], embeddings[j]) / (
                            np.linalg.norm(embeddings[i])
                            * np.linalg.norm(embeddings[j])
                        )
                        similarities.append(similarity)
            stability = np.mean(similarities) if similarities else 1.0

        return {
            "avg_latency": avg_latency,
            "stability": stability,
            "memory_usage": 0.0,  # Placeholder, would need actual measurement
        }

    async def test_rag_performance_for_model(
        self, model: str, query: str, iterations: int = 3
    ) -> dict:
        """Test RAG performance for a specific model"""
        latencies = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                # First get embedding for the query
                embedding_response = await self.client.post(
                    f"{self.controller_url}/api/v1/embeddings",
                    json={"input": query, "model": model},
                )
                embedding_response.raise_for_status()
                embedding_data = embedding_response.json()
                embedding = embedding_data["data"][0]["embedding"]

                # Then make the RAG query
                rag_response = await self.client.post(
                    f"{self.controller_url}/api/v1/chat/chat_embedding",
                    json={
                        "session_id": "model_comparison_session",
                        "text": query,
                        "embedding": embedding,
                    },
                )
                rag_response.raise_for_status()

                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"RAG query failed for model {model}: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")

        # Placeholder values for quality metrics - in a real implementation,
        # we would evaluate the quality of the response
        quality = 0.75  # Placeholder quality score
        hallucination_rate = 0.15  # Placeholder hallucination rate (15%)

        return {
            "avg_latency": avg_latency,
            "quality": quality,
            "hallucination_rate": hallucination_rate,
            "memory_usage": 0.0,  # Placeholder, would need actual measurement
        }

    async def test_summarization_performance_for_model(
        self, model: str, text: str, iterations: int = 3
    ) -> dict:
        """Test summarization performance for a specific model"""
        latencies = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                # Test using the chat completion endpoint for summarization
                response = await self.client.post(
                    f"{self.controller_url}/api/v1/chat/chat_completion",
                    json={
                        "session_id": "summarization_comparison",
                        "text": f"Please summarize the following text: {text}",
                        "model": model,
                    },
                )
                response.raise_for_status()

                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Summarization request failed for model {model}: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")

        # Placeholder values for quality metrics
        quality = 0.70  # Placeholder quality score
        hallucination_rate = 0.10  # Placeholder hallucination rate (10%)
        length_penalty = 0.85  # Placeholder length penalty

        return {
            "avg_latency": avg_latency,
            "quality": quality,
            "hallucination_rate": hallucination_rate,
            "length_penalty": length_penalty,
            "memory_usage": 0.0,  # Placeholder, would need actual measurement
        }

    async def run_model_comparison(self):
        """Run the complete model comparison benchmark suite"""
        print("🚀 Starting Model Comparison Benchmark Suite using GHOSTWIRE Scores")
        print("=" * 80)
        print(f"Models to be tested: {self.models}")
        print("=" * 80)

        test_embedding_text = (
            "This is a test sentence for embedding performance evaluation."
        )
        test_rag_query = "What is artificial intelligence?"
        test_summarization_text = (
            "Artificial intelligence (AI) is intelligence demonstrated by machines, "
            "in contrast to the natural intelligence displayed by humans and animals. "
            "Leading AI textbooks define the field as the study of 'intelligent agents': "
            "any device that perceives its environment and takes actions that maximize "
            "its chance of successfully achieving its goals."
        )

        results = {}

        for model in self.models:
            print(f"\n🤖 Testing Model: {model}")
            print("-" * 50)

            # Test embedding performance
            print("  📝 Testing Embedding Performance...")
            embed_results = await self.test_embedding_performance_for_model(
                model, test_embedding_text
            )
            print(f"    Average embedding latency: {embed_results['avg_latency']:.4f}s")
            print(f"    Embedding stability: {embed_results['stability']:.4f}")

            # Test RAG performance
            print("  🤖 Testing RAG Performance...")
            rag_results = await self.test_rag_performance_for_model(
                model, test_rag_query
            )
            print(f"    Average RAG latency: {rag_results['avg_latency']:.4f}s")
            print(f"    RAG quality: {rag_results['quality']:.4f}")
            print(f"    Hallucination rate: {rag_results['hallucination_rate']:.4f}")

            # Test summarization performance
            print("  📝 Testing Summarization Performance...")
            summ_results = await self.test_summarization_performance_for_model(
                model, test_summarization_text
            )
            print(
                f"    Average summarization latency: {summ_results['avg_latency']:.4f}s"
            )
            print(f"    Summarization quality: {summ_results['quality']:.4f}")
            print(
                f"    Summarization hallucination rate: {summ_results['hallucination_rate']:.4f}"
            )

            # Calculate individual GHOSTWIRE scores
            embedding_score = compute_general_ghostwire_score(
                latency=embed_results["avg_latency"],
                stability=embed_results["stability"],
                memory_usage=embed_results["memory_usage"],
            )

            rag_score = compute_rag_ghostwire_score(
                quality=rag_results["quality"],
                hallucination=rag_results["hallucination_rate"],
                latency=rag_results["avg_latency"],
            )

            summarization_score = compute_summarization_ghostwire_score(
                quality=summ_results["quality"],
                hallucination=summ_results["hallucination_rate"],
                length_penalty=summ_results["length_penalty"],
                latency=summ_results["avg_latency"],
            )

            # Overall score - average of all benchmark scores
            overall_score = (embedding_score + rag_score + summarization_score) / 3

            print(f"  🏆 GHOSTWIRE Scores for {model}:")
            print(f"    Embedding Score: {embedding_score:.4f}")
            print(f"    RAG Score: {rag_score:.4f}")
            print(f"    Summarization Score: {summarization_score:.4f}")
            print(f"    Overall Score: {overall_score:.4f}")

            results[model] = {
                "embedding_latency": embed_results["avg_latency"],
                "embedding_stability": embed_results["stability"],
                "embedding_score": embedding_score,
                "rag_latency": rag_results["avg_latency"],
                "rag_quality": rag_results["quality"],
                "rag_hallucination_rate": rag_results["hallucination_rate"],
                "rag_score": rag_score,
                "summarization_latency": summ_results["avg_latency"],
                "summarization_quality": summ_results["quality"],
                "summarization_hallucination_rate": summ_results["hallucination_rate"],
                "summarization_length_penalty": summ_results["length_penalty"],
                "summarization_score": summarization_score,
                "overall_score": overall_score,
            }

        print("\n" + "=" * 80)
        print("🏆 FINAL MODEL COMPARISON RESULTS (Ranked by Overall GHOSTWIRE Score)")
        print("=" * 80)

        # Sort models by overall score
        sorted_models = sorted(
            results.items(), key=lambda x: x[1]["overall_score"], reverse=True
        )

        print(
            f"{'Rank':<4} {'Model':<25} {'Embedding':<10} {'RAG':<10} {'Summarization':<12} {'Overall':<10}"
        )
        print("-" * 80)

        for i, (model, data) in enumerate(sorted_models, 1):
            print(
                f"{i:<4} {model:<25} {data['embedding_score']:<10.4f} "
                f"{data['rag_score']:<10.4f} {data['summarization_score']:<12.4f} "
                f"{data['overall_score']:<10.4f}"
            )

        print("=" * 80)

        # Return the results for potential further analysis
        return results


async def main():
    parser = argparse.ArgumentParser(
        description="GhostWire Model Comparison Benchmark Tool using GHOSTWIRE Scores"
    )
    parser.add_argument(
        "--controller",
        type=str,
        default="http://localhost:8000",
        help="Controller URL for benchmarking",
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        help="Specific models to test (if not provided, uses models from settings)",
    )

    args = parser.parse_args()

    benchmark = ModelComparisonBenchmark(controller_url=args.controller)

    # If specific models were provided, override the default list
    if args.models:
        benchmark.models = args.models

    await benchmark.run_model_comparison()

    # Print a summary
    print("\n📋 SUMMARY:")
    print("The models have been ranked based on their overall GHOSTWIRE score,")
    print("which combines performance across embedding, RAG, and summarization tasks.")
    print("Higher scores indicate better overall performance considering latency,")
    print("quality, stability, and other factors.")


if __name__ == "__main__":
    asyncio.run(main())
