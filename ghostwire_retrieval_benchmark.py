MODELS = [
    "embeddinggemma",
    "granite-embedding",
    "nomic-embed-text",
    "gemma3:1b",
    "gemma3n:e2b",
    "gemma3n:e4b",
]


def compute_ghostwire_score(consistency, avg_sim, latency):
    """
    Compute a weighted Ghostwire score.
    Score = 0.4 * consistency + 0.4 * avg_sim + 0.2 * (1 / (1 + latency))
    """
    return 0.4 * consistency + 0.4 * avg_sim + 0.2 * (1 / (1 + latency))


"""
retrieval_benchmark.py

Extended retrieval consistency and embedding stability test for Ghostwire controller.

Validates:
  1. Retrieval rank stability across multiple runs
  2. Cosine similarity consistency of embeddings
"""

import asyncio
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
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {"model": MODEL_NAME, "input": text}
        start = time.perf_counter()
        resp = await client.post(f"{CONTROLLER_URL}/embeddings", json=payload)
        latency = time.perf_counter() - start
        data = resp.json()
        embedding = data.get("data", [{}])[0].get("embedding", [])
        return np.array(embedding), latency


async def run_retrieval_test(rounds: int = 5):
    print(
        f"🔍 Running retrieval & embedding stability test via Ghostwire controller at {CONTROLLER_URL}"
    )
    print("=" * 80)

    for model in MODELS:
        global MODEL_NAME
        MODEL_NAME = model
        print(f"\n🚀 Testing model: {model}")
        print("-" * 80)

        embedding = OpenAIEmbeddings(
            openai_api_base=CONTROLLER_URL,
            openai_api_key="ghostwire",
            model=MODEL_NAME,
        )

        store = Qdrant.from_documents(
            DOCS,
            embedding=embedding,
            location=":memory:",
            collection_name=f"ghostwire-retrieval-test-{model}",
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

            # --- Embedding Stability for this query ---
            runs = []
            for _ in range(rounds):
                vec, _ = await fetch_embedding(query)
                runs.append(vec)
            sims = [
                cosine_similarity(runs[i], runs[j])
                for i in range(rounds)
                for j in range(i + 1, rounds)
            ]
            avg_sim = np.mean(sims)
            std_sim = np.std(sims)
            print(f"     Avg cosine similarity: {avg_sim:.6f} ± {std_sim:.6f}")

            # --- Ghostwire score (latency is placeholder 1.0) ---
            ghostwire_score = compute_ghostwire_score(consistency, avg_sim, latency=1.0)
            print(f"     Ghostwire score: {ghostwire_score:.4f}")

        print("-" * 80)
        # --- Embedding Stability (extra test texts) ---
        print("🧬 Measuring raw embedding cosine similarity across runs (extra texts):")
        for text in [
            "Quantum entanglement links particles over distance.",
            "Fuzzy cats like to sleep on keyboards.",
            "Neural networks optimize loss functions.",
        ]:
            runs = []
            for _ in range(rounds):
                vec, _ = await fetch_embedding(text)
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
    return True


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_retrieval_test(rounds=5))
