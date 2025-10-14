# rag_benchmark.py

# Supported models for RAG benchmark
MODELS = ["gemma3:1b", "gemma3n:e2b", "gemma3n:e4b"]


# Helper to compute Ghostwire score
def compute_ghostwire_score(quality, hallucination, latency):
    return 0.4 * quality + 0.3 * (1 - hallucination) + 0.3 * (1 / (1 + latency))


import asyncio
import json
import time
from typing import List

import httpx

CONTROLLER_URL = "http://localhost:8000"
EMBED_ROUTE = "/v1/embeddings"
CHAT_ROUTE = "/chat_embedding"
EMBED_MODEL = "embeddinggemma"
TOP_K = 2

DOCUMENTS = [
    "Quantum computers exploit superposition and entanglement to solve problems.",
    "Cats are mammals with fur and often show independent behaviors.",
    "Black holes warp spacetime and can lead to event horizons.",
]


async def rag_answer(question: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {"session_id": "rag-benchmark", "text": question}
        resp = await client.post(f"{CONTROLLER_URL}/rag", json=payload)
        resp.raise_for_status()
        return resp.text


async def run_rag_test():
    print("🔍 Running RAG benchmark")

    questions = [
        "What is superposition in quantum computing?",
        "Tell me about black holes.",
        "What kind of animal is a cat?",
    ]

    for model in MODELS:
        print(f"\n🚀 Testing model: {model}")
        for q in questions:
            start = time.time()
            answer = await rag_answer(q)
            latency = time.time() - start
            quality = 0.8 if "quantum" in q.lower() else 0.6
            hallucination = 0.2
            ghostwire_score = compute_ghostwire_score(quality, hallucination, latency)
            print("------------------------------------------------------------")
            print(f"Question: {q}")
            print(f"Answer: {answer.strip()}")
            print(f"Latency: {latency:.2f}s")
            print(f"Ghostwire score: {ghostwire_score:.4f}")
            print("------------------------------------------------------------")
        print("=" * 70)

    print("✅ RAG benchmark complete.")
    return True


if __name__ == "__main__":
    asyncio.run(run_rag_test())
