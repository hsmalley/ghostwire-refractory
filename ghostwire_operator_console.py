# /Users/hugh/git/ghostwire-refractory/client_repl.py

"""
👁️ GhostWire Client
--------------------
The mouth of the machine. Speaks to the controller, forges embeddings
locally via Ollama, and streams replies back to your terminal.

Ritual
- Turn text into a vector sigil (embedding).
- Send `session_id`, `prompt_text`, and `embedding` to the controller.
- Print streamed fragments as they arrive; the wire whispers back.
"""

import asyncio
import os

import httpx
from ollama import AsyncClient

LOCAL_OLLAMA = os.getenv(
    "LOCAL_OLLAMA", "http://127.0.0.1:11434"
)  # Local Ollama instance for embeddings
CONTROLLER_URL = os.getenv(
    "CONTROLLER_URL", "http://127.0.0.1:8000"
)  # Controller API endpoint (FastAPI)
EMBED_MODEL = os.getenv("EMBED_MODEL", "embeddinggemma")  # Local embedding model
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))

SUMMARIZER_URL = os.getenv(
    "SUMMARIZER_URL", f"{CONTROLLER_URL}/summarize"
)
RAG_URL = os.getenv("RAG_URL", f"{CONTROLLER_URL}/rag")
BENCH_URL = os.getenv("BENCH_URL", f"{CONTROLLER_URL}/benchmark")

DEFAULT_CHAT_MODEL = os.getenv("DEFAULT_CHAT_MODEL", "gemma3:1b")


async def embed_text(text: str):
    """Generate an embedding vector locally using Ollama (embeddinggemma by default)."""
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


async def post_json(url, payload):
    """Send JSON payload to URL using a shared AsyncClient and print streamed or JSON responses."""
    import json
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                text = await resp.aread()
                try:
                    data = json.loads(text)
                    print()
                    if "benchmarks" in data:
                        print("⚙️ Benchmark Results")
                        for task, results in data["benchmarks"].items():
                            print(f"  {task.upper()}:")
                            for r in results:
                                q = r.get("question") or r.get("input", "")
                                score = r.get("ghostwire_score", "N/A")
                                latency = r.get("latency", 0.0)
                                print(f"    • {q[:60]} → {score} score | {latency:.2f}s")
                        if "avg_score" in data:
                            print(f"\n  🧮 Average GhostWire Score: {data['avg_score']}\n")
                    elif "summary" in data:
                        print(f"📝 Summary:\n{data['summary']}")
                    elif "answer" in data:
                        print(f"📚 Answer:\n{data['answer']}")
                    else:
                        print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    # fallback to streaming
                    async for chunk in resp.aiter_text():
                        print(chunk, end="", flush=True)
                    print()
        except httpx.HTTPStatusError as e:
            try:
                content = await e.response.aread()
                body = content.decode(errors="ignore")
            except Exception:
                body = "<stream closed>"
            print(f"HTTP error {e.response.status_code}: {body}")
        except Exception as e:
            print(f"Error: {e}")


async def run_chat(session_id, text):
    """Run chat embedding command."""
    embedding = await embed_text(text)
    payload = {
        "session_id": session_id,
        "prompt_text": text,
        "embedding": embedding,
    }
    print(f"🗨️ Chat response:")
    await post_json(f"{CONTROLLER_URL}/chat_embedding", payload)


async def run_summarization(session_id, text):
    """Run summarization benchmark command."""
    payload = {
        "session_id": session_id,
        "text": text,
    }
    print(f"📝 Summarization benchmark response:")
    await post_json(SUMMARIZER_URL, payload)


async def run_rag(session_id, text):
    """Run RAG benchmark command."""
    payload = {
        "session_id": session_id,
        "text": text,
    }
    print(f"📚 RAG benchmark response:")
    await post_json(RAG_URL, payload)


async def run_benchmark(session_id, model):
    """Run benchmark suite command."""
    payload = {
        "session_id": session_id,
        "model": model,
    }
    print(f"⚙️ Benchmark suite response:")
    await post_json(BENCH_URL, payload)


async def run_direct(text):
    """Send a raw generation request directly to the local Ollama API and stream output."""
    print("💬 Direct Ollama response:")
    client = AsyncClient(host=LOCAL_OLLAMA)
    try:
        stream = await client.generate(
            model=DEFAULT_CHAT_MODEL,
            prompt=text,
            stream=True,
        )
        async for token in stream:
            # Each token is a dict like {'response': 'partial text', 'done': False}
            chunk = token.get("response")
            if chunk:
                print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"Error during direct generation: {e}")


async def repl():
    """Interactive REPL: type commands to commune; Ctrl+C to jack out."""
    session_id = "repl_session"
    print(f"Connected to ghostwire controller at {CONTROLLER_URL}")
    print("GhostWire Operator Console")
    print("---------------------------")
    print("Available commands:")
    print("  /chat <text>         - Chat with embeddings")
    print("  /summarize <text>    - Run summarization benchmark")
    print("  /rag <text>          - Run RAG benchmark")
    print("  /bench <model>       - Run benchmark suite for specified model")
    print("  /direct <text>       - Talk directly to local Ollama model (bypasses controller)")
    print("  /exit                - Exit the console")
    print("Type your messages or commands below.\n")

    while True:
        try:
            line = input("GhostWire> ").strip()
            if not line:
                continue
            if line.lower() in {"/exit", "exit", "quit"}:
                print("Exiting REPL.")
                break
            if line.startswith("/summarize "):
                text = line[len("/summarize ") :].strip()
                if not text:
                    print("Please provide text to summarize.")
                    continue
                await run_summarization(session_id, text)
            elif line.startswith("/rag "):
                text = line[len("/rag ") :].strip()
                if not text:
                    print("Please provide text for RAG benchmark.")
                    continue
                await run_rag(session_id, text)
            elif line.startswith("/bench "):
                model = line[len("/bench ") :].strip()
                if not model:
                    print("Please provide a model name for benchmarking.")
                    continue
                await run_benchmark(session_id, model)
            elif line.startswith("/direct "):
                text = line[len("/direct ") :].strip()
                if not text:
                    print("Please provide text to send directly to Ollama.")
                    continue
                await run_direct(text)
            elif line.startswith("/chat "):
                text = line[len("/chat ") :].strip()
                if not text:
                    print("Please provide text to chat.")
                    continue
                await run_chat(session_id, text)
            elif line.startswith("/"):
                print(f"Unknown command: {line}")
            else:
                # Default to chat embedding for plain text input
                await run_chat(session_id, line)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break

    print("🧩 Session closed. The wire grows silent.")


if __name__ == "__main__":
    asyncio.run(repl())
