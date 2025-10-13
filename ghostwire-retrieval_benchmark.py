"""
retrieval_benchmark.py

Extended retrieval consistency and embedding stability test for Ghostwire controller.

Validates:
  1. Retrieval rank stability across multiple runs
  2. Cosine similarity consistency of embeddings
"""

import json
import time

import httpx
import numpy as np
from langchain.schema import Document

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant

CONTROLLER_URL = "http://localhost:8000/v1"
MODEL_NAME = "granite-embedding"

DOCS = [
    Document(page_content="Quantum computers exploit superposition and entanglement."),
    Document(page_content="Cats are fluffy, mischievous, and unpredictable animals."),
    Document(
        page_content="Black holes warp spacetime and produce gravitational singularities."
    ),
    Document(
        page_content="Neural networks learn representations through gradient descent."
    ),
    Document(
        page_content="Coffee contains caffeine, a stimulant that affects the central nervous system."
    ),
]

QUERIES = [
    "What are singularities in physics?",
    "Tell me about animals with fur.",
    "How do computers exploit quantum mechanics?",
]


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


async def fetch_embedding(text: str):
    """Query the controller directly for an embedding vector."""
    async with httpx.AsyncClient() as client:
        payload = {"model": MODEL_NAME, "input": text}
        start = time.perf_counter()
        resp = await client.post(f"{CONTROLLER_URL}/embeddings", json=payload)
        latency = time.perf_counter() - start
        data = resp.json()
        embedding = data.get("data", [{}])[0].get("embedding", [])
        return np.array(embedding), latency


def run_retrieval_test(rounds: int = 5):
    print(
        f"🔍 Running retrieval & embedding stability test via Ghostwire controller at {CONTROLLER_URL}"
    )
    print(f"Model: {MODEL_NAME}")
    print("=" * 80)

    embedding = OpenAIEmbeddings(
        openai_api_base=CONTROLLER_URL,
        openai_api_key="ghostwire",
        model=MODEL_NAME,
    )

    store = Qdrant.from_documents(
        DOCS,
        embedding=embedding,
        location=":memory:",
        collection_name="ghostwire-retrieval-test",
    )

    # --- Retrieval Consistency ---
    for query in QUERIES:
        ranks = []
        for _ in range(rounds):
            results = store.similarity_search(query, k=3)
            ranks.append([doc.page_content for doc in results])

        consistency = np.mean(
            [
                len(set(ranks[i]) & set(ranks[j])) / len(ranks[i])
                for i in range(rounds)
                for j in range(i + 1, rounds)
            ]
        )

        print(f"🧠 Query: {query}")
        print(f"   Retrieval stability (top-3 overlap): {consistency * 100:.2f}%")

    print("=" * 80)

    # --- Embedding Stability ---
    print("🧬 Measuring raw embedding cosine similarity across runs:")
    for text in [
        "Quantum entanglement links particles over distance.",
        "Fuzzy cats like to sleep on keyboards.",
        "Neural networks optimize loss functions.",
    ]:
        runs = []
        for _ in range(rounds):
            vec, _ = asyncio.run(fetch_embedding(text))
            runs.append(vec)
        sims = [
            cosine_similarity(runs[i], runs[j])
            for i in range(rounds)
            for j in range(i + 1, rounds)
        ]
        avg_sim = np.mean(sims)
        std_sim = np.std(sims)
        print(f"   Text: {text[:40]!r}...")
        print(f"     Avg cosine similarity: {avg_sim:.6f} ± {std_sim:.6f}")

    print("=" * 80)
    print("✅ Retrieval and embedding stability test complete.")


if __name__ == "__main__":
    import asyncio

    run_retrieval_test(rounds=5)
