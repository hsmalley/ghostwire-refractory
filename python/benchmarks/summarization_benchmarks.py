"""
Summarization benchmarking for GhostWire Refractory
"""

import asyncio
import os
import sys
import time

import httpx

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python.ghostwire.config.settings import settings


class SummarizationBenchmark:
    """Benchmark class for text summarization performance"""

    def __init__(self, controller_url: str = None):
        self.controller_url = controller_url or "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def test_summarization(
        self, text: str, model: str = None, iterations: int = 5
    ) -> tuple[float, list[float]]:
        """Test summarization performance"""
        latencies = []
        model = model or settings.SUMMARY_MODEL

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                # For now, we'll test using the chat completion endpoint
                # In a full implementation, this would call a dedicated summarization endpoint
                response = await self.client.post(
                    f"{self.controller_url}/api/v1/chat/chat_completion",
                    json={
                        "session_id": "summarization_benchmark",
                        "text": f"Please summarize the following text: {text}",
                    },
                )
                response.raise_for_status()

                latency = time.perf_counter() - start_time
                latencies.append(latency)
            except Exception as e:
                print(f"Summarization request failed: {e}")
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else float("inf")
        return avg_latency, latencies

    async def run_summarization_benchmark(self):
        """Run the complete summarization benchmark suite"""
        print("🚀 Starting Summarization Benchmark Suite")
        print("=" * 60)

        test_texts = [
            "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.",
            "Climate change refers to long-term shifts in global or regional climate patterns. Since the mid-20th century, scientists have observed unprecedented changes attributed to human influence on the climate system. The effects of climate change include rising sea levels, changing precipitation patterns, and an increase in extreme weather events.",
            "The Internet of Things (IoT) refers to the network of physical objects—'things'—that are embedded with sensors, software, and other technologies for the purpose of connecting and exchanging data with other devices and systems over the internet. These objects range from ordinary household items to sophisticated industrial tools.",
        ]

        print("\n📝 Testing Summarization Performance...")
        results = []

        for i, text in enumerate(test_texts):
            print(f"  Testing with text {i + 1} ({len(text)} chars)...")
            avg_lat, latencies = await self.test_summarization(text, iterations=3)
            results.append(avg_lat)
            print(f"    Average latency: {avg_lat:.4f}s")

        overall_avg = sum(results) / len(results) if results else float("inf")

        print("\n✅ Summarization benchmark suite completed!")
        print("=" * 60)

        return {"average_latency": overall_avg, "individual_results": results}


async def main():
    benchmark = SummarizationBenchmark()
    results = await benchmark.run_summarization_benchmark()

    print("\n📈 SUMMARIZATION BENCHMARK RESULTS:")
    print(f"  Overall Average Latency: {results['average_latency']:.4f}s")


if __name__ == "__main__":
    asyncio.run(main())
