# /Users/hugh/git/ghostwire-refractory/client_repl.py

import os
import asyncio
import httpx
from ollama import AsyncClient

LOCAL_OLLAMA = os.getenv(
    "LOCAL_OLLAMA", "http://127.0.0.1:11434"
)  # Local Ollama instance for embeddings
CONTROLLER_URL = os.getenv(
    "CONTROLLER_URL", "http://127.0.0.1:8000"
)  # Controller API endpoint (FastAPI)
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")  # Local embedding model
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))


async def embed_text(text: str):
    """Generate an embedding vector locally using Ollama."""
    client = AsyncClient(host=LOCAL_OLLAMA)
    resp = await client.embeddings(model=EMBED_MODEL, prompt=text)
    embedding = resp.get("embedding") or resp.get("embeddings")
    if embedding is None:
        raise RuntimeError("No embedding in response from Ollama")
    if isinstance(embedding, list) and embedding and isinstance(embedding[0], list):
        embedding = embedding[0]
    if not isinstance(embedding, list) or not embedding:
        raise RuntimeError("Unexpected embedding format")
    if len(embedding) != EMBED_DIM:
        raise RuntimeError(
            f"Unexpected embedding dim {len(embedding)} (expected {EMBED_DIM})"
        )
    return embedding


async def send_message(session_id: str, text: str):
    """Send the text and its embedding to the controller."""
    embedding = await embed_text(text)

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            f"{CONTROLLER_URL}/chat_embedding",
            json={
                "session_id": session_id,
                "prompt_text": text,
                "embedding": embedding,
            },
        ) as resp:
            resp.raise_for_status()
            async for chunk in resp.aiter_text():
                print(chunk, end="", flush=True)
    print("\n", end="")


async def repl():
    """Interactive REPL for chatting via controller."""
    session_id = "repl_session"
    print(f"Connected to ghostwire controller at {CONTROLLER_URL}/chat_embedding")
    print("Type your messages below. Type 'exit' or press Ctrl+C to quit.\n")

    while True:
        try:
            text = input("You: ").strip()
            if not text or text.lower() in {"exit", "quit"}:
                print("Exiting REPL.")
                break
            await send_message(session_id, text)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break


if __name__ == "__main__":
    asyncio.run(repl())
