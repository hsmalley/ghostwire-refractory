**GhostWire Refractory — Simple README**

This repo is a small, two‑part system for chat with memory:
- A web service (the “controller”) that stores message embeddings in SQLite and finds similar past messages using an in‑memory HNSW index.
- A tiny terminal client that turns your text into an embedding (with a local Ollama model), calls the controller, and streams the reply back.

Use it to experiment with “memory” for conversational apps: each turn is embedded and saved; future turns retrieve similar past content as context for the model that generates the reply.

**How It Works**
- The client creates an embedding for your text using your local Ollama instance (default model `nomic-embed-text`).
- The client POSTs `session_id`, `prompt_text`, and `embedding` to the controller.
- The controller finds similar past messages (via HNSW or a cosine fallback), builds a prompt that includes those snippets, calls an Ollama text model (local or remote), and streams the response.
- The controller stores the pair `(prompt_text, answer_text, embedding)` in `memory.db` for future recall.

**What You Need**
- Python 3.12+
- Ollama installed
  - Local Ollama for embeddings (pull an embedding model, e.g. `nomic-embed-text`).
  - An Ollama text model for generation (can be the same machine). Example: `llama3.2`.
- Recommended: `uv` (fast Python tool) to run without managing a venv manually. If you prefer, you can use `pip` with the dependencies listed in `pyproject.toml`.

**Quick Start (recommended with uv)**
- Start Ollama locally and pull models:
  - `ollama serve`
  - `ollama pull nomic-embed-text`
  - `ollama pull llama3.2`
- In one terminal, start the controller (run the script to avoid module‑name issues):
  - `REMOTE_OLLAMA_URL=http://127.0.0.1:11434/api/generate uv run python ghostwire-controller.py`
  - If your embedding model has 768 dimensions (e.g., `nomic-embed-text`), the defaults match. If not, set `EMBED_DIM` to the correct size on both client and controller.
- In another terminal, run the client REPL:
  - `uv run python ghostwire-client.py`
  - Type a message, press Enter. Type `exit` to quit.

Tip: If your generation host isn’t local, point the controller at it with `REMOTE_OLLAMA_URL=http://<host>:11434/api/generate`. To change models, set `REMOTE_OLLAMA_MODEL` (default `llama3.2:latest`).

**Configuration**
- Controller (environment variables):
  - `DB_PATH` — SQLite file path (default `memory.db`).
  - `EMBED_DIM` — embedding size (default `768`). Must match the client’s embedding model dimension.
  - `REMOTE_OLLAMA_URL` — Ollama generate endpoint (default points to a sample IP; override it).
  - `REMOTE_OLLAMA_MODEL` — text model tag for generation (default `llama3.2:latest`).
- Client (environment variables):
  - `LOCAL_OLLAMA` — local Ollama base URL for embeddings (default `http://127.0.0.1:11434`).
  - `CONTROLLER_URL` — controller base URL (default `http://127.0.0.1:8000`).
  - `EMBED_MODEL` — embedding model (default `nomic-embed-text`).
  - `EMBED_DIM` — must equal the chosen embedding model’s dimension.

**API (for use without the client)**
- Health check:
  - `GET /health` → `{ "status": "ok" }`
- Streamed chat with embedding:
  - `POST /chat_embedding`
  - JSON body: `{ "session_id": "string", "text" (or "prompt_text"): "string", "embedding": [float, ...] }`
  - Response: plain‑text stream of the generated answer.
  - Example curl (streaming):
    - ``curl -N -s -X POST "$CONTROLLER_URL/chat_embedding" -H "Content-Type: application/json" -d '{"session_id":"demo","text":"hello","embedding":[0.0, ...]}'``

**Data Storage**
- SQLite database: `memory.db` is created automatically with table `memory_text` containing `session_id`, `prompt_text`, `answer_text`, `timestamp`, and the vector `embedding` as a BLOB.
- HNSW index: built in memory at startup and backfilled from existing rows. It is not persisted; it’s rebuilt from the DB when the controller starts.

**Common Issues**
- “embedding dim X != EMBED_DIM Y”
  - Your embedding model’s output size doesn’t match. Set `EMBED_DIM` on both client and controller to your model’s dimension, or switch to a matching model.
- Connection errors to Ollama
  - Ensure `ollama serve` is running. For remote generation, verify `REMOTE_OLLAMA_URL` is reachable and ends with `/api/generate`.
- hnswlib install/build problems
  - Ensure a working C/C++ toolchain is available on your system. On macOS, install Xcode Command Line Tools.

**What Lives Where**
- `ghostwire-controller.py` — FastAPI app; stores and retrieves embeddings; streams replies.
- `ghostwire-client.py` — Terminal client; builds embeddings via local Ollama and calls the controller.
- `memory.db` — SQLite file with stored turns (created on first run).
- `.github/workflows/` — CI for building and cutting releases with `uv`.

**Notes and Limits**
- This is a minimal demo, not a production service. There’s no auth, no rate limiting, and no encryption beyond what your environment provides.
- The HNSW index lives in RAM and is rebuilt from the DB on startup.
- If you point the controller at a remote Ollama host, your prompts are sent there for generation.

**License**
- MIT‑style. See `LICENSE.md`.
