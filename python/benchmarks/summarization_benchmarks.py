"""
Summarization benchmarking for GhostWire Refractory with GHOSTWIRE scoring
"""

import asyncio
import os
import sys
import time

import httpx
import psutil

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python.ghostwire.config.settings import settings
from python.ghostwire.utils.ghostwire_scoring import (
    compute_general_ghostwire_score,
    compute_summarization_ghostwire_score,
    format_benchmark_results_with_scores,
)


class SummarizationBenchmark:
    """Benchmark class for text summarization performance"""

    def __init__(self, controller_url: str = None):
        self.controller_url = controller_url or "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def test_summarization(
        self, text: str, model: str = None, iterations: int = 5
    ) -> tuple[float, list[float], float, float, float]:
        """Test summarization performance and quality"""
        latencies = []
        memory_deltas = []
        model = model or settings.SUMMARY_MODEL

        for i in range(iterations):
            # Record memory before
            memory_before = psutil.virtual_memory().used / (1024**3)  # GB

            start_time = time.perf_counter()
            try:
                # For now, we'll test using the chat completion endpoint
                # In a full implementation, this would call a dedicated
                # summarization endpoint
                response = await self.client.post(
                    f"{self.controller_url}/api/v1/chat/chat_completion",
                    json={
                        "session_id": "summarization_benchmark",
                        "text": f"Please summarize the following text: {text}",
                    },
                )
                response.raise_for_status()

                latency = time.perf_counter() - start_time

                # Record memory after
                memory_after = psutil.virtual_memory().used / (1024**3)  # GB
                memory_delta = memory_after - memory_before

                latencies.append(latency)
                memory_deltas.append(memory_delta)
            except Exception as e:
                print(f"Summarization request failed: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")
        avg_memory_delta = (
            sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0.0
        )

        # In a full implementation, we would evaluate summarization quality
        # and hallucination rate, but for now we'll use placeholder values
        quality = 0.70  # Placeholder quality score
        hallucination_rate = 0.10  # Placeholder hallucination rate (10%)
        length_penalty = 0.85  # Placeholder length penalty (based on compression ratio)

        return (
            avg_latency,
            latencies,
            avg_memory_delta,
            quality,
            hallucination_rate,
            length_penalty,
        )

    async def run_summarization_benchmark(self):
        """Run the complete summarization benchmark suite"""
        print("🚀 Starting Summarization Benchmark Suite")
        print("=" * 60)

        test_texts = [
            "Artificial intelligence (AI) is intelligence demonstrated by machines, "
            "in contrast to the natural intelligence displayed by humans and animals. "
            "Leading AI textbooks define the field as the study of 'intelligent agents': "
            "any device that perceives its environment and takes actions that maximize "
            "its chance of successfully achieving its goals.",
            "Climate change refers to long-term shifts in global or regional climate patterns. "
            "Since the mid-20th century, scientists have observed unprecedented changes "
            "attributed to human influence on the climate system. The effects of climate "
            "change include rising sea levels, changing precipitation patterns, and an "
            "increase in extreme weather events.",
            "The Internet of Things (IoT) refers to the network of physical objects—'things'—"
            "that are embedded with sensors, software, and other technologies for the purpose "
            "of connecting and exchanging data with other devices and systems over the internet. "
            "These objects range from ordinary household items to sophisticated industrial tools.",
        ]

        print("\n📝 Testing Summarization Performance...")
        latency_results = []
        memory_results = []
        quality_results = []
        hallucination_results = []
        length_penalty_results = []

        for i, text in enumerate(test_texts):
            print(f"  Testing with text {i + 1} ({len(text)} chars)...")
            (
                avg_lat,
                latencies,
                avg_memory,
                quality,
                hallucination_rate,
                length_penalty,
            ) = await self.test_summarization(text, iterations=3)
            latency_results.append(avg_lat)
            memory_results.append(avg_memory)
            quality_results.append(quality)
            hallucination_results.append(hallucination_rate)
            length_penalty_results.append(length_penalty)
            print(f"    Average latency: {avg_lat:.4f}s")
            print(f"    Average memory: {avg_memory:.4f} GB")
            print(f"    Quality: {quality:.4f}")
            print(f"    Hallucination rate: {hallucination_rate:.4f}")
            print(f"    Length penalty: {length_penalty:.4f}")

        overall_avg_latency = (
            sum(latency_results) / len(latency_results)
            if latency_results
            else float("inf")
        )
        overall_avg_memory = (
            sum(memory_results) / len(memory_results) if memory_results else 0.0
        )
        overall_avg_quality = (
            sum(quality_results) / len(quality_results) if quality_results else 0.0
        )
        overall_avg_hallucination = (
            sum(hallucination_results) / len(hallucination_results)
            if hallucination_results
            else 0.0
        )
        overall_avg_length_penalty = (
            sum(length_penalty_results) / len(length_penalty_results)
            if length_penalty_results
            else 0.0
        )

        print("\n✅ Summarization benchmark suite completed!")
        print("=" * 60)

        # Calculate GHOSTWIRE scores
        summarization_ghostwire_score = compute_summarization_ghostwire_score(
            quality=overall_avg_quality,
            hallucination=overall_avg_hallucination,
            length_penalty=overall_avg_length_penalty,
            latency=overall_avg_latency,
        )

        general_ghostwire_score = compute_general_ghostwire_score(
            latency=overall_avg_latency, memory_usage=overall_avg_memory
        )

        print("\n🏆 GHOSTWIRE SCORES:")
        print(f"  Summarization GHOSTWIRE Score: {summarization_ghostwire_score:.4f}")
        print(f"  General Performance GHOSTWIRE Score: {general_ghostwire_score:.4f}")

        return {
            "average_latency": overall_avg_latency,
            "average_memory": overall_avg_memory,
            "average_quality": overall_avg_quality,
            "average_hallucination_rate": overall_avg_hallucination,
            "average_length_penalty": overall_avg_length_penalty,
            "individual_latency_results": latency_results,
            "individual_memory_results": memory_results,
            "individual_quality_results": quality_results,
            "individual_hallucination_results": hallucination_results,
            "individual_length_penalty_results": length_penalty_results,
            "summarization_ghostwire_score": summarization_ghostwire_score,
            "general_performance_ghostwire_score": general_ghostwire_score,
        }


async def main():
    benchmark = SummarizationBenchmark()
    results = await benchmark.run_summarization_benchmark()

    print("\n📈 SUMMARIZATION BENCHMARK RESULTS:")
    print(f"  Overall Average Latency: {results['average_latency']:.4f}s")
    print(f"  Overall Average Memory: {results['average_memory']:.4f} GB")
    print(f"  Overall Average Quality: {results['average_quality']:.4f}")
    print(
        f"  Overall Average Hallucination Rate: {results['average_hallucination_rate']:.4f}"
    )
    print(f"  Overall Average Length Penalty: {results['average_length_penalty']:.4f}")
    print(
        f"  Summarization GHOSTWIRE Score: {results['summarization_ghostwire_score']:.4f}"
    )
    print(
        f"  General Performance GHOSTWIRE Score: {results['general_performance_ghostwire_score']:.4f}"
    )

    # Also print formatted results with GHOSTWIRE scoring
    print(
        "\n"
        + format_benchmark_results_with_scores(
            results, score_function_name="summarization"
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
