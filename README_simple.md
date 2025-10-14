**GhostWire Refractory — Simple README (Refactored)**

This repo is a refactored neural network-based chat system with memory. The system now features:

- A modular FastAPI web service that stores message embeddings in SQLite and finds similar past messages using an in-memory HNSW index.
- A terminal client that integrates with the API to provide conversational memory.
- Multiple API compatibility layers (OpenAI, Qdrant, Ollama).
- Comprehensive benchmarking tools.
- Security measures including authentication, rate limiting, and input validation.

Use it to experiment with "memory" for conversational apps: each turn is embedded and saved; future turns retrieve similar past content as context for the model that generates the reply.

**How It Works**
- The client creates an embedding for your text and sends `session_id`, `text`, and `embedding` to the API.
- The API finds similar past messages (via HNSW or a cosine fallback), builds a prompt that includes those snippets, calls an Ollama text model, and streams the response.
- The API stores the pair `(prompt_text, answer_text, embedding)` in `memory.db` for future recall.

**What You Need**
- Python 3.12+
- Ollama installed
  - Local Ollama for embeddings (pull an embedding model, e.g. `nomic-embed-text`).
  - An Ollama text model for generation (can be the same machine). Example: `llama3.2`.

**Quick Start**
- Start Ollama locally and pull models:
  - `ollama serve`
  - `ollama pull nomic-embed-text`
  - `ollama pull llama3.2`
- Install dependencies:
  - `pip install -r requirements.txt`
- In one terminal, start the server:
  - `cd python/src/ghostwire`
  - `python main.py`
- In another terminal, run the client:
  - `cd python/client`
  - `python operator_console.py`

**Configuration**
- Application settings are configured through environment variables in `.env` file or system environment
- Key settings include: HOST, PORT, DB_PATH, EMBED_DIM, LOCAL_OLLAMA_URL, REMOTE_OLLAMA_URL, etc.

**API Endpoints**
- Health check: `GET /api/v1/health`
- Embeddings: `POST /api/v1/embeddings`
- Chat with memory: `POST /api/v1/chat/chat_embedding`
- Memory storage: `POST /api/v1/chat/memory`
- Vector operations: `POST /api/v1/vectors/upsert` and `POST /api/v1/vectors/query`

**Data Storage**
- SQLite database: `memory.db` is created automatically with table `memory_text` containing `session_id`, `prompt_text`, `answer_text`, `timestamp`, and the vector `embedding` as a BLOB.
- HNSW index: built in memory at startup and backfilled from existing rows. It is persisted to `memory_index.bin` and loaded on startup.

**What Lives Where**
- `python/src/ghostwire/` — Main application code organized in modules
- `python/client/` — Client application
- `python/benchmarks/` — Benchmarking tools
- `python/tests/` — Unit and integration tests
- `APIDOC.md` — API documentation

**Security Features**
- JWT-based authentication
- Rate limiting
- Input validation and sanitization
- Secure password hashing
- Proper CORS configuration (no longer allows all origins)

**License**
- MIT‑style. See `LICENSE.md`.
