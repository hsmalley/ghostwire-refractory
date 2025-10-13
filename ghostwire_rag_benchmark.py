# rag_benchmark.py

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


# Simple in-memory vector store
class SimpleVectorStore:
    def __init__(self):
        self.texts: List[str] = []
        self.embeddings: List[List[float]] = []

    async def add(self, text: str):
        vec, _ = await fetch_embedding(text)
        self.texts.append(text)
        self.embeddings.append(vec)

    def similarity(self, query_vec: List[float]):
        # cosine similarity
        import numpy as np

        sims = []
        q = np.array(query_vec)
        for vec in self.embeddings:
            v = np.array(vec)
            # handle zero vector
            if np.linalg.norm(v) == 0 or np.linalg.norm(q) == 0:
                sims.append(0.0)
            else:
                sims.append(
                    float(np.dot(q, v) / (np.linalg.norm(q) * np.linalg.norm(v)))
                )
        return sims

    async def query(self, question: str):
        qvec, _ = await fetch_embedding(question)
        sims = self.similarity(qvec)
        # get top K
        ranked = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
        return [self.texts[i] for i in ranked[:TOP_K]], qvec


async def fetch_embedding(text: str):
    async with httpx.AsyncClient() as client:
        payload = {"model": EMBED_MODEL, "input": text}
        resp = await client.post(f"{CONTROLLER_URL}{EMBED_ROUTE}", json=payload)
        resp.raise_for_status()
        data = resp.json()
        vec = data.get("data", [{}])[0].get("embedding", [])
        return vec, resp.elapsed.total_seconds()


async def chat_answer(question: str, contexts: List[str]):
    """
    Calls your controller’s chat endpoint with a prompt including the retrieved contexts.
    """
    prompt = "Use the following context snippets to answer the question.\n\n"
    for c in contexts:
        prompt += f"Context: {c}\n"
    prompt += f"\nQuestion: {question}\nAnswer:"

    async with httpx.AsyncClient() as client:
        payload = {"session_id": "rag-test", "prompt_text": str(prompt)}

        # Add optional embedding data if required by the API schema
        # For safety, avoid sending empty or null fields
        if contexts:
            payload["embedding"] = [0.0] * 768  # Match required embedding dimension

        print(
            f"[DEBUG] Sending payload to {CHAT_ROUTE}: {json.dumps(payload)[:200]}..."
        )
        resp = await client.post(f"{CONTROLLER_URL}{CHAT_ROUTE}", json=payload)
        if resp.status_code != 200:
            print(f"[ERROR] {resp.status_code} - {resp.text}")
        resp.raise_for_status()
        return resp.text


async def run_rag_test():
    print("🔍 Running RAG benchmark")
    store = SimpleVectorStore()
    for doc in DOCUMENTS:
        await store.add(doc)

    questions = [
        "What is superposition in quantum computing?",
        "Tell me about black holes.",
        "What kind of animal is a cat?",
    ]

    for q in questions:
        contexts, _ = await store.query(q)
        answer = await chat_answer(q, contexts)
        print("Question:", q)
        print("Retrieved contexts:", contexts)
        print("Answer:", answer)
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(run_rag_test())
