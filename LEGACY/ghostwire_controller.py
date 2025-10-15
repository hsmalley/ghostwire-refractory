from __future__ import annotations

"""
👁️ GhostWire Controller
-----------------------
The daemon priest. Uvicorn-fed, SQLite‑souled, speaking HTTP to the void.

Purpose
- Accept an incoming prompt + embedding from the client.
- Recall relevant prior whispers (memories) via HNSW or cosine fallback.
- Stream generation from a remote Ollama host, token by token.
- Etch the conversation back into the archive.

Notes
- Vectors are normalized and stored as BLOBs; HNSW keeps hot neighbors in RAM.
- Streaming uses Ollama's JSONL /api/generate protocol; only `response` chunks
  are yielded to callers. When `done` appears, the ritual ends.
- Environment variables shape the conduit (REMOTE_OLLAMA_URL, MODEL, EMBED_DIM, DB_PATH).
"""

import atexit
import json
import logging
import os
import re
import sqlite3
import time
from collections.abc import AsyncGenerator
from typing import Any

import hnswlib
import httpx
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

#
#
# Config via environment (with safe defaults)
# Sanitize REMOTE_OLLAMA_URL so it never includes /api/generate twice
_remote_base = os.getenv("REMOTE_OLLAMA_URL", "http://100.103.237.60:11434")
REMOTE_OLLAMA_URL = _remote_base.rstrip("/api/generate")
DEFAULT_OLLAMA_MODEL = os.getenv("LOCAL_OLLAMA_MODEL", "gemma3:1b")
REMOTE_OLLAMA_MODEL = os.getenv("REMOTE_OLLAMA_MODEL", "gemma3:12b")


# Local Ollama URL for summarization/embedding helpers
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Additional model configuration
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gemma3:1b")
DISABLE_SUMMARIZATION = os.getenv("DISABLE_SUMMARIZATION", "false").lower() in (
    "1",
    "true",
    "yes",
)
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ("1", "true", "yes")
EMBED_MODELS = os.getenv(
    "EMBED_MODELS",
    "embeddinggemma,granite-embedding,nomic-embed-text,mxbai-embed-large,snowflake-arctic-embed,all-minilm",
).split(",")


if not DEBUG_MODE:
    logging.getLogger("httpx").setLevel(logging.WARNING)

logging.info(f"REMOTE_OLLAMA_URL = {REMOTE_OLLAMA_URL}")
logging.info(f"OLLAMA_URL = {OLLAMA_URL}")


async def stream_from_ollama(
    prompt: str, model: str = DEFAULT_OLLAMA_MODEL, local: bool = False
) -> AsyncGenerator[str, None]:
    """
    Open the channel to Ollama and stream `response` fragments as they arrive.

    Input
    - prompt: The fully composed prompt including any recalled memory context.
    - model: The model name to use for generation.
    - local: If True, use the local Ollama endpoint; else use remote.

    Yields
    - Text fragments in arrival order; callers should concatenate.
    """
    if local:
        target_url = f"{OLLAMA_URL}/api/chat"
        payload = {
            "model": model,
            "stream": True,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert summarization assistant. Summarize the provided text clearly and concisely.",
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following text:\n\n{prompt}",
                },
            ],
        }
    else:
        target_url = f"{REMOTE_OLLAMA_URL}/api/generate"
        payload = {"model": model, "stream": True, "prompt": prompt}
    logging.info(f"[stream_from_ollama] → {target_url} (local={local})")
    try:
        async with httpx.AsyncClient(timeout=None, http2=True) as client:
            async with client.stream(
                "POST",
                target_url,
                json=payload,
            ) as response:
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404 and local:
                        logging.warning(
                            f"[stream_from_ollama] Model {model} not found locally. Falling back to gemma3:1b."
                        )
                        # Prepare fallback payload for local
                        fallback_payload = {
                            "model": "gemma3:1b",
                            "stream": True,
                            "input": prompt,
                        }
                        async with client.stream(
                            "POST",
                            target_url,
                            json=fallback_payload,
                        ) as response2:
                            response2.raise_for_status()
                            async for line in response2.aiter_lines():
                                if not line:
                                    continue
                                try:
                                    obj = json.loads(line)
                                except Exception as e:
                                    logging.warning(
                                        f"[stream_from_ollama] Failed to parse line: {e}"
                                    )
                                    continue

                                chunk = obj.get("response") or (
                                    obj.get("message", {}) or {}
                                ).get("content")

                                if chunk:
                                    logging.info(
                                        f"[stream_from_ollama] chunk: {repr(chunk)}"
                                    )
                                    yield chunk

                                # Make sure we yield the final chunk before breaking
                                if obj.get("done"):
                                    logging.info("[stream_from_ollama] stream complete")
                                    break
                        return
                    else:
                        raise
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception as e:
                        logging.warning(
                            f"[stream_from_ollama] Failed to parse line: {e}"
                        )
                        continue

                    chunk = obj.get("response") or (obj.get("message", {}) or {}).get(
                        "content"
                    )

                    if chunk:
                        if DEBUG_MODE:
                            logging.info(f"[stream_from_ollama] chunk: {repr(chunk)}")
                        yield chunk

                    # Make sure we yield the final chunk before breaking
                    if obj.get("done"):
                        logging.info("[stream_from_ollama] stream complete")
                        break
    except Exception as e:
        yield f"[ERROR] Failed to connect to Ollama: {e}"


# -------------------------------
# Chat completion endpoint (summarization/generation)
# -------------------------------


# Request schema for chat completion
class ChatCompletionRequest(BaseModel):
    text: str
    model: str | None = None
    history: list[dict[str, str]] | None = None
    stream: bool = False


# -------------------------------
# Config
# -------------------------------

DB_PATH = os.getenv("DB_PATH", "memory.db")
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))
HNSW_MAX_ELEMENTS = 100_000  # adjust as needed
HNSW_EF_CONSTRUCTION = 200
HNSW_M = 16
HNSW_EF = 50

# -------------------------------
# FastAPI app
# -------------------------------

app = FastAPI()

# add once, right after app = FastAPI(...)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Set up root logger for debugging
logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# -------------------------------
# Globals: DB + HNSW
# -------------------------------

_global_conn: sqlite3.Connection | None = None
_hnsw_index: hnswlib.Index | None = None
_hnsw_initialized = False


def _ensure_tables(conn: sqlite3.Connection) -> None:
    # Unified table: stores text+answer+embedding blob
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_text (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            prompt_text TEXT,
            answer_text TEXT,
            timestamp REAL,
            embedding BLOB
        );
        """
    )
    # Add summary_text column if not present
    try:
        conn.execute("ALTER TABLE memory_text ADD COLUMN summary_text TEXT;")
    except Exception as e:
        # Ignore duplicate column error
        if (
            "duplicate column" not in str(e).lower()
            and "already exists" not in str(e).lower()
        ):
            raise
    # Table to track dropped collections
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dropped_collections (
            name TEXT PRIMARY KEY
        );
        """
    )
    conn.commit()


# -------------------------------
# Helper functions: Ollama embed/summarize and code detection
# -------------------------------


# ---------------------------------------------
# Embedding model cache for ollama_embed
# ---------------------------------------------

# Global variable for embedding model cache
_cached_embed_model: str | None = None


async def ollama_embed(text: str) -> list[float]:
    """Use local Ollama for embedding text, trying both /api/embeddings and /api/embed endpoints for each model."""
    global _cached_embed_model
    import json as _json  # for logging response JSON

    candidate_models = EMBED_MODELS
    # If we have a cached model, try it first and only
    if _cached_embed_model:
        logging.info(
            f"[ollama_embed] Using cached embedding model: '{_cached_embed_model}'"
        )
        candidate_models = [_cached_embed_model]
    last_error = None

    for model_name in candidate_models:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First try /api/embeddings
                logging.info(
                    f"[ollama_embed] Trying /api/embeddings for model '{model_name}'..."
                )
                resp = await client.post(
                    f"{OLLAMA_URL}/api/embeddings",
                    json={"model": model_name, "input": text},
                )
                resp.raise_for_status()
                data = resp.json()
                emb = data.get("embedding") or data.get("data", [{}])[0].get(
                    "embedding"
                )
                # NEW: Check for "embeddings" (plural) at root if not found
                if (
                    not emb
                    and "embeddings" in data
                    and isinstance(data["embeddings"], list)
                    and data["embeddings"]
                ):
                    emb = data["embeddings"][0]
                    logging.info(
                        f"[ollama_embed] Found embedding under 'embeddings' key for model '{model_name}'"
                    )
                if emb:
                    logging.info(
                        f"[ollama_embed] Success with model '{model_name}' using /api/embeddings endpoint."
                    )
                    if _cached_embed_model != model_name:
                        _cached_embed_model = model_name
                        logging.info(
                            f"[ollama_embed] Caching embedding model: '{model_name}' for future use."
                        )
                    return emb
                # Log diagnostic info for /api/embeddings
                if "error" in data or "message" in data:
                    logging.warning(
                        f"[ollama_embed] /api/embeddings model '{model_name}' returned error: {data.get('error') or data.get('message')}"
                    )
                else:
                    logging.warning(
                        f"[ollama_embed] No embedding in /api/embeddings response for model '{model_name}'. "
                        f"Response JSON: {_json.dumps(data)[:500]}"
                    )
                # Now try /api/embed as fallback
                logging.info(
                    f"[ollama_embed] Trying /api/embed fallback for model '{model_name}'..."
                )
                resp2 = await client.post(
                    f"{OLLAMA_URL}/api/embed",
                    json={"model": model_name, "input": text},
                )
                resp2.raise_for_status()
                data2 = resp2.json()
                emb2 = data2.get("embedding") or data2.get("data", [{}])[0].get(
                    "embedding"
                )
                # NEW: Check for "embeddings" (plural) at root if not found
                if (
                    not emb2
                    and "embeddings" in data2
                    and isinstance(data2["embeddings"], list)
                    and data2["embeddings"]
                ):
                    emb2 = data2["embeddings"][0]
                    logging.info(
                        f"[ollama_embed] Found embedding under 'embeddings' key for model '{model_name}'"
                    )
                if emb2:
                    logging.info(
                        f"[ollama_embed] Success with model '{model_name}' using /api/embed endpoint."
                    )
                    if _cached_embed_model != model_name:
                        _cached_embed_model = model_name
                        logging.info(
                            f"[ollama_embed] Caching embedding model: '{model_name}' for future use."
                        )
                    return emb2
                # Log diagnostic info for /api/embed
                if "error" in data2 or "message" in data2:
                    logging.warning(
                        f"[ollama_embed] /api/embed model '{model_name}' returned error: {data2.get('error') or data2.get('message')}"
                    )
                else:
                    logging.warning(
                        f"[ollama_embed] No embedding in /api/embed response for model '{model_name}'. "
                        f"Response JSON: {_json.dumps(data2)[:500]}"
                    )
        except Exception as e:
            last_error = e
            logging.warning(f"[ollama_embed] Model '{model_name}' failed: {e}")
            # If this was the cached model, clear cache so we try all on next call
            if _cached_embed_model == model_name:
                logging.info(
                    f"[ollama_embed] Cached embedding model '{model_name}' failed. Clearing cache for fallback."
                )
                _cached_embed_model = None
            continue

    logging.error(
        f"[ollama_embed] All embedding models failed. Last error: {last_error}"
    )
    return []


async def ollama_summarize(text: str) -> str:
    if DISABLE_SUMMARIZATION:
        logging.info("[ollama_summarize] Summarization disabled via environment flag.")
        return text
    """Use local Ollama for summarization."""
    prompt = f"Summarize this text concisely, keeping key details:\n\n{text}"
    logging.info("[ollama_summarize] Using local Ollama for summarization.")
    output = ""
    async for chunk in stream_from_ollama(prompt, model=SUMMARY_MODEL, local=True):
        output += chunk
    logging.info(f"[ollama_summarize] Summary result preview: {output[:120]}...")
    return output.strip()


def contains_code(text: str) -> bool:
    """Detect code-like content (skip summarization if present)."""
    if re.search(r"```|def |class |;|{|\}|<[^>]+>", text):
        return True
    return False


def get_connection() -> sqlite3.Connection:
    """Return a shared SQLite connection, creating tables on first touch."""
    global _global_conn
    if _global_conn is not None:
        # print("[DB] Using global SQLite connection")
        return _global_conn

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _ensure_tables(conn)
    _global_conn = conn
    return _global_conn


def _ensure_hnsw_initialized(conn: sqlite3.Connection) -> None:
    """
    Initialize the in‑memory HNSW index and backfill any stored vectors once.

    Keeps RAM hot for fast recall; gracefully skips rows with mismatched dims.
    """
    global _hnsw_index, _hnsw_initialized
    if _hnsw_initialized:
        return

    # Try to load persistent HNSW index if available
    hnsw_path = "memory_index.bin"
    if os.path.exists(hnsw_path):
        try:
            _hnsw_index = hnswlib.Index(space="cosine", dim=EMBED_DIM)
            _hnsw_index.load_index(hnsw_path)
            _hnsw_index.set_ef(HNSW_EF)
            _hnsw_initialized = True
            print(f"[HNSW] Loaded persistent vector index from {hnsw_path}.")
            return
        except Exception as e:
            print(
                f"[HNSW] WARNING: Failed to load persistent index ({e}). Falling back to DB backfill."
            )

    # Init index
    _hnsw_index = hnswlib.Index(space="cosine", dim=EMBED_DIM)
    _hnsw_index.init_index(
        max_elements=HNSW_MAX_ELEMENTS, ef_construction=HNSW_EF_CONSTRUCTION, M=HNSW_M
    )
    _hnsw_index.set_ef(HNSW_EF)

    # Backfill existing rows
    cur = conn.execute("SELECT id, embedding FROM memory_text")
    rows = cur.fetchall()
    if rows:
        ids, vecs = [], []
        for rid, blob in rows:
            if blob is None:
                continue
            vec = np.frombuffer(blob, dtype=np.float32)
            if vec.shape[0] != EMBED_DIM:
                continue
            ids.append(int(rid))
            vecs.append(vec)
        if vecs:
            vecs_np = np.stack(vecs, axis=0).astype(np.float32)
            ids_np = np.array(ids, dtype=np.int64)
            _hnsw_index.add_items(vecs_np, ids_np)
    _hnsw_initialized = True
    print(
        "[HNSW] In-memory vector index initialized. Loaded:",
        (_hnsw_index.get_current_count() if _hnsw_index else 0),
    )


def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / (n + 1e-8)


def upsert_memory_with_embedding(
    session_id: str, prompt_text: str, answer_text: str, embedding: list[float]
) -> None:
    """
    Etch a conversation turn into the archive.

    Stores: session id, user prompt, assistant answer, timestamp, and normalized
    embedding. Adds the vector to HNSW for fast future recall.
    """
    conn = get_connection()
    _ensure_hnsw_initialized(conn)

    # Validate embedding
    if not isinstance(embedding, (list, tuple)):
        raise ValueError("embedding must be a list of floats")
    if len(embedding) != EMBED_DIM:
        raise ValueError(f"Embedding dim {len(embedding)} != EMBED_DIM {EMBED_DIM}")

    vec = np.asarray(embedding, dtype=np.float32)
    if not np.all(np.isfinite(vec)):
        raise ValueError("Embedding contains non-finite values")
    vec = _normalize(vec)
    blob = vec.tobytes()
    ts = time.time()

    conn.execute(
        "INSERT INTO memory_text (session_id,prompt_text,answer_text,timestamp,embedding) VALUES (?,?,?,?,?)",
        (session_id, prompt_text, answer_text, ts, blob),
    )
    rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()

    # Add to HNSW (best effort)
    try:
        if _hnsw_index is not None:
            _hnsw_index.add_items(vec.reshape(1, -1), np.array([rowid]))
            print(f"[HNSW] Added vector with rowid {rowid}")
    except Exception as e:
        print(f"[HNSW] WARNING: could not add to HNSW ({e})")


def query_similar_by_embedding(
    session_id: str, embedding: list[float], limit: int = 5
) -> list[tuple[str, str]]:
    """
    Retrieve prior whispers most aligned with the incoming embedding.

    Returns ordered `(prompt_text, answer_text)` pairs, preferring HNSW when
    available, else falling back to cosine over session rows.
    """
    conn = get_connection()
    _ensure_hnsw_initialized(conn)

    # Validate embedding
    if not isinstance(embedding, (list, tuple)):
        raise ValueError("embedding must be a list of floats")
    if len(embedding) != EMBED_DIM:
        raise ValueError(f"Embedding dim {len(embedding)} != EMBED_DIM {EMBED_DIM}")
    vec = _normalize(np.asarray(embedding, dtype=np.float32))

    # Try HNSW if populated
    if _hnsw_index is not None:
        try:
            count = _hnsw_index.get_current_count()
            if count > 0:
                k = min(limit, count)
                labels, distances = _hnsw_index.knn_query(vec.reshape(1, -1), k=k)
                ids = [int(i) for i in labels[0]]
                if ids:
                    qmarks = ",".join("?" * len(ids))
                    rows = conn.execute(
                        f"SELECT id, prompt_text, answer_text FROM memory_text WHERE id IN ({qmarks}) AND session_id = ?",
                        (*ids, session_id),
                    ).fetchall()
                    by_id = {rid: (p, a) for rid, p, a in rows}
                    ordered = [by_id[i] for i in ids if i in by_id]
                    if ordered:
                        print(
                            f"[HNSW] Retrieved {len(ordered)} neighbors from HNSW index."
                        )
                        return ordered[:limit]
            else:
                print("[HNSW] Index empty; using fallback cosine similarity.")
        except RuntimeError as e:
            print(f"[HNSW] Query failed ({e}); falling back to cosine similarity.")
        except Exception as e:
            print(
                f"[HNSW] Unexpected query error ({e}); falling back to cosine similarity."
            )

    # Fallback: cosine over session rows
    rows = conn.execute(
        "SELECT prompt_text, answer_text, embedding FROM memory_text WHERE session_id = ?",
        (session_id,),
    ).fetchall()

    def cosine(a: np.ndarray, b: np.ndarray) -> float:
        return float(
            np.dot(a, b) / ((np.linalg.norm(a) + 1e-8) * (np.linalg.norm(b) + 1e-8))
        )

    scored: list[tuple[float, str, str]] = []
    for p, a, blob in rows:
        if blob is None:
            continue
        v = np.frombuffer(blob, dtype=np.float32)
        scored.append((cosine(vec, v), p, a))

    scored.sort(reverse=True, key=lambda x: x[0])
    results = [(p, a) for _, p, a in scored[:limit]]
    print(f"[DB] Retrieved {len(results)} rows by fallback cosine similarity")
    return results


# -------------------------------
# Minimal streaming chat endpoint
# -------------------------------


class ChatEmbeddingRequest(BaseModel):
    session_id: str
    text: str | None = None
    prompt_text: str | None = None
    embedding: list[float] | None = None
    context: str | None = None

    def normalized(self):
        text_value = self.text or self.prompt_text or ""
        embed_value = self.embedding or []
        return self.session_id, text_value, embed_value, self.context


# --- OpenAI compatibility models ---


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str | None = None


class VectorUpsertRequest(BaseModel):
    namespace: str
    id: str | None = None
    text: str
    embedding: list[float]
    metadata: dict | None = None


class VectorQueryRequest(BaseModel):
    namespace: str
    embedding: list[float]
    top_k: int = 5


async def ask_streaming_with_embedding(
    session_id: str, text: str, embedding: list[float]
) -> AsyncGenerator[str, None]:
    """
    Orchestrate recall + generation.

    - Pull relevant context from memory.
    - Compose a prompt that honors those echoes.
    - Stream tokens from Ollama while accumulating the final answer.
    - Persist the turn once the stream concludes.
    """
    # Retrieve memories
    memories = query_similar_by_embedding(session_id, embedding, limit=5)

    # Build context for Ollama
    context_text = ""
    if memories:
        context_snippets = " | ".join(f"{p}" for p, _ in memories[:3])
        context_text = f"Relevant prior notes: {context_snippets}\n\n"

    full_prompt = f"{context_text}User: {text}\n\nAssistant:"
    answer_parts: list[str] = []
    # Always use local Ollama for embedding chat/summarization
    async for token in stream_from_ollama(
        full_prompt, model=DEFAULT_OLLAMA_MODEL, local=True
    ):
        answer_parts.append(token)
        yield token

    # Save to memory: persist actual assistant reply
    answer_text = "".join(answer_parts)
    try:
        upsert_memory_with_embedding(session_id, text, answer_text, embedding)
    except Exception as e:
        print(f"[DB] WARNING: failed to upsert memory: {e}")


@app.post("/chat_embedding")
async def chat_embedding(req: ChatEmbeddingRequest):
    """HTTP entrypoint: chat via embedding. Streams plain text back to caller."""
    try:
        session_id, text, embedding, context = req.normalized()
    except Exception as e:
        print(f"[WARN] Could not parse chat_embedding payload: {e}")
        session_id, text, embedding, context = "unknown", "", [], None

    # Auto-generate embedding if missing
    if not embedding:
        logging.info(
            "[chat_embedding] No embedding provided; auto-generating with ollama_embed."
        )
        embedding = await ollama_embed(text)
        if not embedding:
            raise HTTPException(
                status_code=500, detail="Failed to auto-generate embedding"
            )

    # Merge context if provided
    if context:
        text = f"{context.strip()}\n\nQuestion: {text.strip()}"

    # Validate request before streaming
    if not text:
        raise HTTPException(status_code=422, detail="text/prompt_text is required")
    if not isinstance(embedding, list) or not embedding:
        raise HTTPException(status_code=422, detail="embedding is required")
    if len(embedding) != EMBED_DIM:
        raise HTTPException(
            status_code=422,
            detail=f"embedding dim {len(embedding)} != EMBED_DIM {EMBED_DIM}",
        )
    if not np.all(np.isfinite(np.asarray(embedding, dtype=np.float32))):
        raise HTTPException(status_code=422, detail="embedding has non-finite values")

    async def event_generator():
        try:
            async for chunk in ask_streaming_with_embedding(
                session_id, text, embedding
            ):
                yield chunk
        except Exception as e:
            err = f"[ERROR] {type(e).__name__}: {e}"
            yield f"\n{err}\n"

    return StreamingResponse(event_generator(), media_type="text/plain")


# -------------------------------
# /chat_completion endpoint
# -------------------------------


@app.post("/chat_completion")
async def chat_completion(req: ChatCompletionRequest):
    prompt = req.text or ""
    if DISABLE_SUMMARIZATION:
        logging.info(
            "[chat_completion] Summarization disabled; returning original text."
        )
        return {"summary": prompt}
    model = req.model or DEFAULT_OLLAMA_MODEL
    summary_text = ""

    # Select remote/local based on model name
    use_remote = model.startswith("remote-") or model.endswith(":remote")
    clean_model = (
        model.removeprefix("remote-")
        .removeprefix("local-")
        .removesuffix(":remote")
        .removesuffix(":local")
    )

    logging.info(
        f"[chat_completion] Starting summarization with {model} (remote={use_remote})"
    )
    chunks = []
    async for chunk in stream_from_ollama(
        prompt, model=clean_model, local=not use_remote
    ):
        if chunk:
            chunks.append(chunk)
    summary_text = "".join(chunks).strip()
    logging.info(f"[chat_completion] Final summary length: {len(summary_text)}")

    if not summary_text:
        summary_text = "[ERROR] No summary generated."

    return {"summary": summary_text}


# -------------------------------
# OpenAI-compatible /v1/embeddings endpoint (controller-native)
# -------------------------------


async def generate_embedding(text_input: str, model: str = "embeddinggemma"):
    """
    Generate embedding using local Ollama /api/embeddings endpoint.
    """
    if not isinstance(text_input, str):
        raise TypeError(f"generate_embedding expected str, got {type(text_input)}")
    logging.info("[generate_embedding] Using local Ollama /api/embeddings endpoint.")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": model, "input": text_input},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [])
    except Exception as e:
        logging.error(f"[generate_embedding] Failed to get embedding: {e}")
        return []


@app.post("/v1/embeddings")
async def v1_embeddings(req: dict):
    """
    OpenAI-compatible embedding endpoint.
    Accepts: {"model": "granite-embedding", "input": "text"} or {"input": ["t1", "t2", ...]}.
    Ensures generate_embedding() is always called with a single string.
    """
    try:
        model = req.get("model", "embeddinggemma")
        inputs = req.get("input", "")

        if not inputs:
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "message": "Missing input text",
                        "type": "invalid_request",
                    }
                },
            )

        # Normalize to list of strings
        if isinstance(inputs, str):
            inputs = [inputs]
        elif isinstance(inputs, list):
            # Flatten nested lists if LangChain sends [[text]]
            flat_inputs = []
            for item in inputs:
                if isinstance(item, list):
                    flat_inputs.extend(str(x) for x in item)
                else:
                    flat_inputs.append(str(item))
            inputs = flat_inputs
        else:
            raise TypeError(f"Invalid input type: {type(inputs)}")

        data = []
        total_tokens = 0

        for i, text_input in enumerate(inputs):
            if not isinstance(text_input, str):
                text_input = str(text_input)

            embedding_vector = await generate_embedding(text_input, model=model)
            if not embedding_vector:
                embedding_vector = [1e-8] * 768  # tiny nonzero fallback

            # Sanitize non-finite values (NaN or inf)
            import math

            embedding_vector = [
                float(x) if isinstance(x, (float, int)) and math.isfinite(x) else 1e-8
                for x in embedding_vector
            ]

            # Prevent all-zero vectors that cause normalization NaN downstream
            if sum(abs(x) for x in embedding_vector) < 1e-12:
                embedding_vector = [1e-8] * len(embedding_vector)

            total_tokens += len(text_input.split())
            data.append(
                {"object": "embedding", "embedding": embedding_vector, "index": i}
            )

        response = {
            "object": "list",
            "data": data,
            "model": model,
            "usage": {"prompt_tokens": total_tokens, "total_tokens": total_tokens},
        }

        print(f"[EMBED] Successfully generated {len(inputs)} embeddings via {model}")
        return JSONResponse(content=response)

    except Exception as e:
        print(f"[ERROR] /v1/embeddings failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e), "type": "internal_error"}},
        )


# -------------------------------
# OpenAI-compatible /v1/models endpoint
# -------------------------------


# Inserted: OpenAI-compatible models listing
@app.get("/v1/models")
async def v1_models():
    """OpenAI-compatible models listing for both local and remote Ollama hosts."""
    models = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        # --- Local models ---
        try:
            local_resp = await client.get(f"{OLLAMA_URL}/api/tags")
            local_resp.raise_for_status()
            local_data = local_resp.json()
            for m in local_data.get("models", []):
                models.append(
                    {
                        "id": m.get("name"),
                        "object": "model",
                        "owned_by": "ghostwire-local",
                    }
                )
        except Exception as e:
            logging.warning(f"[v1_models] Local model listing failed: {e}")
            models.append(
                {
                    "id": DEFAULT_OLLAMA_MODEL,
                    "object": "model",
                    "owned_by": "ghostwire-local",
                }
            )

        # --- Remote models ---
        try:
            remote_resp = await client.get(f"{REMOTE_OLLAMA_URL}/api/tags")
            remote_resp.raise_for_status()
            remote_data = remote_resp.json()
            for m in remote_data.get("models", []):
                models.append(
                    {
                        "id": f"remote-{m.get('name')}",
                        "object": "model",
                        "owned_by": "ghostwire-remote",
                    }
                )
        except Exception as e:
            logging.warning(f"[v1_models] Remote model listing failed: {e}")
            models.append(
                {
                    "id": f"remote-{REMOTE_OLLAMA_MODEL}",
                    "object": "model",
                    "owned_by": "ghostwire-remote",
                }
            )

    return {"object": "list", "data": models}


# -------------------------------
# OpenAI-compatible /v1/chat/completions endpoint
# -------------------------------


# OpenAI-style error response helper
def openai_error(
    message: str, type_: str = "invalid_request_error", code: str | None = None
):
    return JSONResponse(
        status_code=400,
        content={
            "error": {"message": message, "type": type_, "param": None, "code": code}
        },
    )


@app.post("/v1/chat/completions")
async def v1_chat_completions(req: Request):
    """
    OpenAI-compatible chat completions endpoint.
    Accepts {"model": "gemma3:1b", "messages": [{"role": "user", "content": "Hello"}]} and proxies to local Ollama.
    Supports OpenAI-style streaming and extra parameters.
    """
    try:
        # Dummy parse of Authorization header (ignore validation errors)
        auth = req.headers.get("authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[7:]
            # Ignore token, just for compatibility
        data = await req.json()
        model = data.get("model", DEFAULT_OLLAMA_MODEL)
        messages = data.get("messages", [])
        # Sanitize message contents to plain text (handles both strings and lists)
        parts = []
        for m in messages:
            content = m.get("content", "")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        parts.append(str(item["text"]))
                    else:
                        parts.append(str(item))
            else:
                parts.append(str(content))
        prompt = "\n".join(parts)
        temperature = data.get("temperature")
        max_tokens = data.get("max_tokens")
        top_p = data.get("top_p")
        n = data.get("n", 1)
        stop = data.get("stop")
        stream = data.get("stream", False)
        # Only n=1 supported
        if n and n != 1:
            return openai_error("Only n=1 is supported", code="not_implemented")

        # Select remote/local based on model name
        use_remote = model.startswith("remote-") or model.endswith(":remote")
        clean_model = (
            model.removeprefix("remote-")
            .removeprefix("local-")
            .removesuffix(":remote")
            .removesuffix(":local")
        )

        # Only single stop supported, if at all
        # Streaming mode
        if stream:

            async def event_stream():
                content_so_far = ""
                try:
                    async for chunk in stream_from_ollama(
                        prompt, model=clean_model, local=not use_remote
                    ):
                        content_so_far += chunk
                        chunk_obj = {
                            "id": f"chatcmpl-{int(time.time())}",
                            "object": "chat.completion.chunk",
                            "model": model,
                            "choices": [
                                {
                                    "delta": {"content": chunk},
                                    "index": 0,
                                    "finish_reason": None,
                                }
                            ],
                        }
                        yield f"data: {json.dumps(chunk_obj)}\n\n"
                    # Final chunk with finish_reason
                    chunk_obj = {
                        "id": f"chatcmpl-{int(time.time())}",
                        "object": "chat.completion.chunk",
                        "model": model,
                        "choices": [
                            {
                                "delta": {},
                                "index": 0,
                                "finish_reason": "stop",
                            }
                        ],
                    }
                    yield f"data: {json.dumps(chunk_obj)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")
        # Non-streaming mode
        output = ""
        async for chunk in stream_from_ollama(
            prompt, model=clean_model, local=not use_remote
        ):
            output += chunk
        # OpenAI-compliant response with finish_reason and usage
        prompt_tokens = len(prompt.split())
        completion_tokens = len(output.split())
        total_tokens = prompt_tokens + completion_tokens
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": output},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        }
    except Exception as e:
        logging.error(f"[v1_chat_completions] Failed: {e}")
        return openai_error(str(e), "internal_error")


# Inserted: OpenAI-compatible legacy completions endpoint and model detail endpoint
@app.post("/v1/completions")
async def v1_completions(req: Request):
    """Legacy OpenAI completions endpoint, translates prompt to chat format."""
    try:
        # Dummy parse of Authorization header (ignore validation errors)
        auth = req.headers.get("authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[7:]
        data = await req.json()
        model = data.get("model", DEFAULT_OLLAMA_MODEL)
        prompt = data.get("prompt", "")
        # Support extra params, pass through
        temperature = data.get("temperature")
        max_tokens = data.get("max_tokens")
        top_p = data.get("top_p")
        n = data.get("n", 1)
        stop = data.get("stop")
        stream = data.get("stream", False)
        messages = [{"role": "user", "content": prompt}]
        # Compose new request for /v1/chat/completions
        new_body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "n": n,
            "stop": stop,
            "stream": stream,
        }
        # Remove None values
        new_body = {k: v for k, v in new_body.items() if v is not None}
        # Clone scope and receive for new Request
        new_req = Request(req.scope, req.receive)
        new_req._body = json.dumps(new_body).encode()
        return await v1_chat_completions(new_req)
    except Exception as e:
        return openai_error(str(e))


@app.get("/v1/models/{model_id}")
async def v1_model_detail(model_id: str):
    """Return a single model detail object in OpenAI format."""
    return {
        "id": model_id,
        "object": "model",
        "owned_by": "ghostwire-local",
        "permission": [
            {
                "id": f"perm-{model_id}",
                "object": "model_permission",
                "allow_create_engine": True,
            }
        ],
    }


# -------------------------------
# OpenAI-compatible endpoints
# -------------------------------


@app.post("/v1/vectors/upsert")
async def upsert_vector(req: VectorUpsertRequest):
    """Insert or update a vector record (OpenAI-compatible style)."""
    try:
        upsert_memory_with_embedding(
            req.namespace,
            req.text,
            json.dumps(req.metadata) if req.metadata else "",
            req.embedding,
        )
        return {"object": "vector.upsert", "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/vectors/query")
async def query_vector(req: VectorQueryRequest):
    """Query most similar vectors (OpenAI-compatible style)."""
    try:
        results = query_similar_by_embedding(req.namespace, req.embedding, req.top_k)
        return {
            "object": "list",
            "data": [
                {"prompt_text": p, "answer_text": a, "score": idx}
                for idx, (p, a) in enumerate(results)
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/health")
async def v1_health():
    """Health check route for OpenAI-compatible services."""
    return {"object": "health", "status": "ok"}


# -------------------------------
# Qdrant-compatible endpoints
# -------------------------------


class QCollectionParams(BaseModel):
    vectors: dict[str, Any]


class QPointStruct(BaseModel):
    id: int | str
    vector: list[float]
    payload: dict[str, Any] | None = None


class QSearchRequest(BaseModel):
    vector: list[float]
    top: int = 5
    filter: dict[str, Any] | None = None


# --- Qdrant index request model ---
class QIndexRequest(BaseModel):
    field_name: str
    field_schema: str


@app.put("/collections/{collection_name}")
async def q_create_collection(collection_name: str, params: QCollectionParams):
    """Create a Qdrant-like collection (maps to a GhostWire namespace)."""
    # Remove from dropped_collections if re-created
    conn = get_connection()
    conn.execute("DELETE FROM dropped_collections WHERE name = ?", (collection_name,))
    conn.commit()
    size = params.vectors.get("size")
    if size != EMBED_DIM:
        raise HTTPException(status_code=400, detail="vector size mismatch")
    # Optionally store collection metadata here
    return {
        "status": "ok",
        "result": {"name": collection_name, "vectors": params.vectors},
    }


# --- Qdrant-compatible collection info endpoint ---
@app.get("/collections/{collection_name}")
async def q_get_collection_info(collection_name: str):
    """Qdrant-compatible collection info endpoint."""
    conn = get_connection()
    dropped = conn.execute(
        "SELECT 1 FROM dropped_collections WHERE name = ?", (collection_name,)
    ).fetchone()
    if dropped:
        raise HTTPException(status_code=404, detail="collection not found")
    cur = conn.execute(
        "SELECT COUNT(*) FROM memory_text WHERE session_id = ?", (collection_name,)
    )
    count = cur.fetchone()[0]

    return {
        "status": "ok",
        "result": {
            "name": collection_name,
            "vectors_count": count,
            "config": {"params": {"vectors": {"size": 1536, "distance": "Cosine"}}},
        },
        "time": 0.0001,
    }


# --- Qdrant-compatible collection delete endpoint ---
@app.delete("/collections/{collection_name}")
async def q_delete_collection(collection_name: str):
    """Delete (drop) a collection, removing all its data (Qdrant-compatible)."""
    conn = get_connection()
    conn.execute("DELETE FROM memory_text WHERE session_id = ?", (collection_name,))
    # Record the dropped collection
    conn.execute(
        "INSERT OR REPLACE INTO dropped_collections (name) VALUES (?)",
        (collection_name,),
    )
    conn.commit()
    logging.info(f"[DELETE COLLECTION] Dropped collection {collection_name}")
    return {"status": "ok", "result": True}


@app.post("/collections/{collection_name}/points")
async def q_upsert_points(collection_name: str, pts: list[QPointStruct]):
    """Upsert points into a collection (Qdrant-style)."""
    results = []
    for qp in pts:
        try:
            # Summarization/embedding logic
            text = (qp.payload or {}).get("text", "")
            use_summary = (qp.payload or {}).get("summarize", False)
            # Auto summarization if long and not code
            if not use_summary and len(text) > 2000 and not contains_code(text):
                use_summary = True

            summary_text = None
            if use_summary and text and not DISABLE_SUMMARIZATION:
                try:
                    summary_text = await ollama_summarize(text)
                    emb = await ollama_embed(summary_text)
                    logging.info(
                        f"[SUMMARIZE] Text summarized before embedding for {collection_name}"
                    )
                except Exception as e:
                    logging.warning(
                        f"[SUMMARIZE] Summarization failed, falling back to full text: {e}"
                    )
                    emb = await ollama_embed(text)
            else:
                emb = await ollama_embed(text)

            upsert_memory_with_embedding(
                session_id=collection_name,
                prompt_text="",
                answer_text=json.dumps(qp.payload or {}),
                embedding=emb,
            )
            # Store summary_text if it exists
            if summary_text:
                conn = get_connection()
                conn.execute(
                    "UPDATE memory_text SET summary_text = ? WHERE session_id = ? ORDER BY id DESC LIMIT 1",
                    (summary_text, collection_name),
                )
                conn.commit()
            results.append({"id": qp.id})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok", "result": results}


from fastapi import Body


@app.post("/collections/{collection_name}/points/search")
async def q_search(
    collection_name: str,
    req: QSearchRequest = Body(...),
    offset: int = 0,
    with_payload: bool = False,
    with_vectors: bool = False,
):
    """Search points by vector similarity (Qdrant-style, extended for full compatibility)."""
    try:
        recs = query_similar_by_embedding(collection_name, req.vector, req.top + offset)
        # apply offset & limit slice:
        sliced = recs[offset : offset + req.top]
        response = []

        conn = get_connection()

        for idx, (p_text, a_json_str) in enumerate(sliced):
            item = {"id": idx + offset}
            item["score"] = 1.0  # placeholder; can compute real cosine similarity later

            if with_payload:
                try:
                    item["payload"] = json.loads(a_json_str)
                except Exception:
                    item["payload"] = {"text": a_json_str}

            if with_vectors:
                row = conn.execute(
                    "SELECT embedding FROM memory_text WHERE session_id = ? ORDER BY id LIMIT 1 OFFSET ?",
                    (collection_name, idx + offset),
                ).fetchone()
                if row and row[0]:
                    item["vector"] = np.frombuffer(row[0], dtype=np.float32).tolist()
                else:
                    item["vector"] = None

            response.append(item)

        return {"status": "ok", "time": 0.0001, "result": response}
    except Exception as e:
        logging.error(f"[ERROR] q_search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/collections/{collection_name}/points/query")
async def q_query_alias(collection_name: str, request: Request):
    """Alias for /points/search to support Qdrant-style 'query' endpoint with flexible input formats."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    if not isinstance(body, dict):
        body = {}
    filt = body.get("filter")
    if filt is None or not isinstance(filt, dict):
        filt = {}

    vector = (
        body.get("vector")
        or body.get("query")
        or (body.get("vector", {}) or {}).get("vector")
        or []
    )
    top = body.get("top") or body.get("limit") or 5

    offset = body.get("offset", 0)
    with_payload = bool(body.get("with_payload", False))
    with_vectors = bool(body.get("with_vectors", False))

    try:
        req = QSearchRequest(vector=vector, top=top, filter=filt)
    except Exception as e:
        logging.error(f"[ERROR] Failed to parse QSearchRequest: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid query payload: {e}")

    try:
        res = await q_search(
            collection_name,
            req,
            offset=offset,
            with_payload=with_payload,
            with_vectors=with_vectors,
        )
        if not isinstance(res, dict):
            res = {}
        if "result" not in res or not isinstance(res["result"], list):
            res["result"] = []
        if "status" not in res:
            res["status"] = "ok"
        if "time" not in res:
            res["time"] = 0.0
        return res
    except Exception as e:
        logging.error(f"[ERROR] /points/query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {e}")


@app.get("/collections/{collection_name}/points/{point_id}")
async def q_get_point(collection_name: str, point_id: str):
    """Fetch a single point by ID (Qdrant-style)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT embedding, answer_text FROM memory_text WHERE id = ? AND session_id = ?",
        (point_id, collection_name),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="point not found")
    embedding_blob, ans = row
    vec = np.frombuffer(embedding_blob, dtype=np.float32).tolist()
    try:
        payload = json.loads(ans)
    except Exception:
        payload = None
    return {"id": point_id, "vector": vec, "payload": payload}


# ----------------------------------------
# Qdrant/KiloCode Compatibility Extensions
# ----------------------------------------


# -------------------------------
# Ollama-compatible endpoints
# -------------------------------

from fastapi import Body


@app.post("/api/generate")
async def api_generate(body: dict = Body(...)):
    """
    Ollama‑compatible /api/generate endpoint.
    Accepts: {"model": str, "prompt": str, "stream": bool, "suffix"? …}
    """
    model = body.get("model", DEFAULT_OLLAMA_MODEL)
    prompt = body.get("prompt", "")
    stream = body.get("stream", True)
    suffix = body.get("suffix")
    options = body.get("options", {})

    # Decide remote/local routing
    use_remote = model.startswith("remote-") or model.endswith(":remote")
    clean_model = (
        model.removeprefix("remote-")
        .removeprefix("local-")
        .removesuffix(":remote")
        .removesuffix(":local")
    )

    if stream:

        async def gen_stream():
            async for chunk in stream_from_ollama(
                prompt, model=clean_model, local=not use_remote
            ):
                obj = {
                    "model": model,
                    "response": chunk,
                    "done": False,
                    "done_reason": None,
                }
                yield json.dumps(obj) + "\n"
            done_obj = {
                "model": model,
                "response": "",
                "done": True,
                "done_reason": "stop",
            }
            yield json.dumps(done_obj) + "\n"

        return StreamingResponse(gen_stream(), media_type="application/json")
    else:
        text = ""
        async for chunk in stream_from_ollama(
            prompt, model=clean_model, local=not use_remote
        ):
            text += chunk
        return {
            "model": model,
            "response": text,
            "done": True,
            "done_reason": "stop",
        }


@app.post("/api/chat")
async def api_chat(body: dict = Body(...)):
    """
    Ollama‑compatible /api/chat endpoint.
    Accepts: {"model": str, "messages": [...], "stream": bool, "options", "format", etc.}
    """
    model = body.get("model", DEFAULT_OLLAMA_MODEL)
    messages = body.get("messages", [])
    stream = body.get("stream", True)
    options = body.get("options", {})

    # Flatten messages into a single prompt text
    prompt = "\n".join(str(m.get("content", "")) for m in messages)

    # Decide remote/local routing
    use_remote = model.startswith("remote-") or model.endswith(":remote")
    clean_model = (
        model.removeprefix("remote-")
        .removeprefix("local-")
        .removesuffix(":remote")
        .removesuffix(":local")
    )

    if stream:

        async def chat_stream():
            async for chunk in stream_from_ollama(
                prompt, model=clean_model, local=not use_remote
            ):
                obj = {
                    "model": model,
                    "message": {"role": "assistant", "content": chunk},
                    "done": False,
                }
                yield json.dumps(obj) + "\n"
            done_obj = {
                "model": model,
                "message": {"role": "assistant", "content": ""},
                "done": True,
                "done_reason": "stop",
            }
            yield json.dumps(done_obj) + "\n"

        return StreamingResponse(chat_stream(), media_type="application/json")
    else:
        text = ""
        async for chunk in stream_from_ollama(
            prompt, model=clean_model, local=not use_remote
        ):
            text += chunk
        return {
            "model": model,
            "message": {"role": "assistant", "content": text},
            "done": True,
            "done_reason": "stop",
        }


@app.get("/api/tags")
async def api_tags_alias():
    """Alias for Ollama-compatible /api/tags, proxies to api_list_models."""
    return await api_list_models()


@app.get("/api/list")
async def api_list_models():
    """List models from both local and remote Ollama servers, using only /api/tags for compatibility."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        models = []
        # Local models
        try:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            j = resp.json()
            for m in j.get("models", []):
                models.append(f"local-{m.get('name')}")
        except Exception as e:
            logging.warning(f"[api_list_models] Local /api/tags failed: {e}")
        # Remote models
        try:
            resp = await client.get(f"{REMOTE_OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            j = resp.json()
            for m in j.get("models", []):
                models.append(f"remote-{m.get('name')}")
        except Exception as e:
            logging.warning(f"[api_list_models] Remote /api/tags failed: {e}")
    return {"models": models}


@app.post("/api/pull")
async def api_pull(body: dict = Body(...)):
    """Ollama-compatible /api/pull proxy."""
    model = body.get("model")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f"{REMOTE_OLLAMA_URL}/api/pull", json={"model": model}
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pull failed: {e}")


@app.post("/api/delete")
async def api_delete(body: dict = Body(...)):
    """Ollama-compatible /api/delete proxy."""
    model = body.get("model")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{REMOTE_OLLAMA_URL}/api/delete", json={"model": model}
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete failed: {e}")


# Qdrant-compatible delete: supports {"filter":{"must":[]}} or {"filter":{"must":[{"key":"id","match":{"any":[...]}}]}}
@app.post("/collections/{collection_name}/points/delete")
async def qdrant_delete_points(
    collection_name: str, request: Request, wait: bool | None = False
):
    """Qdrant-compatible delete: supports {"filter":{"must":[]}} or {"filter":{"must":[{"key":"id","match":{"any":[...]}}]}}"""
    try:
        body = await request.json()
    except Exception:
        body = {}
    conn = get_connection()

    filt = (body or {}).get("filter", {})
    must = filt.get("must", [])

    deleted_ids = []
    if not must:
        # Delete all points in this collection
        cur = conn.execute(
            "SELECT id FROM memory_text WHERE session_id = ?", (collection_name,)
        )
        deleted_ids = [r[0] for r in cur.fetchall()]
        conn.execute("DELETE FROM memory_text WHERE session_id = ?", (collection_name,))
        conn.commit()
        logging.info(
            f"[DELETE] Cleared all points from collection {collection_name} ({len(deleted_ids)} records)"
        )
    else:
        # Check for id-based filter
        for clause in must:
            match = clause.get("match", {})
            key = clause.get("key")
            if key == "id" and "any" in match:
                ids = match["any"]
                conn.execute(
                    f"DELETE FROM memory_text WHERE session_id = ? AND id IN ({','.join('?' * len(ids))})",
                    (collection_name, *ids),
                )
                deleted_ids.extend(ids)
        conn.commit()
        logging.info(
            f"[DELETE] Removed {len(deleted_ids)} points from {collection_name}"
        )

    return {
        "status": "ok",
        "result": {
            "deleted": len(deleted_ids),
            "ids": deleted_ids,
        },
    }


# 1. Updated /collections/{collection_name}/index route with logging and flexible parsing
@app.put("/collections/{collection_name}/index")
async def q_create_index_alias(
    collection_name: str,
    request: Request,
    wait: bool | None = False,
):
    """Diagnose Kilo index creation requests."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    logging.info(f"[DEBUG] /index payload for {collection_name}: {body}")

    if "field_name" in body and "field_schema" in body:
        return {
            "status": "ok",
            "result": {"status": "acknowledged", "operation_id": 0},
        }
    elif "vectors" in body:
        params = QCollectionParams(**body)
        return await q_create_collection(collection_name, params)
    else:
        return {"status": "ok", "note": "Index request received", "body": body}


# 2. Flexible upsert points route with logging (PUT/POST)
@app.api_route("/collections/{collection_name}/points", methods=["PUT", "POST"])
async def q_upsert_points_debug(collection_name: str, request: Request):
    """Debugging wrapper for Kilo upsert; logs full body."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    logging.info(f"[DEBUG] /points payload for {collection_name}: {body}")

    points = (
        body
        if isinstance(body, list)
        else body.get("points") or body.get("batch") or []
    )
    if not isinstance(points, list):
        raise HTTPException(status_code=422, detail="Invalid upsert payload")

    results_ids = []
    for p in points:
        try:
            qpoint = QPointStruct(**p)
            upsert_memory_with_embedding(
                session_id=collection_name,
                prompt_text="",
                answer_text=json.dumps(qpoint.payload or {}),
                embedding=qpoint.vector,
            )
            results_ids.append(qpoint.id)
        except Exception as e:
            logging.error(f"[ERROR] Failed upsert for point {p}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "result": {
            "operation_id": int(time.time()),
            "ids": results_ids,
            "num_received": len(points),
        },
    }


# Debug-only delete endpoint: logs everything, always returns OK.
@app.api_route(
    "/collections/{collection_name}/points/delete", methods=["POST", "DELETE", "PUT"]
)
async def q_delete_points_debug_all(
    collection_name: str, request: Request, wait: bool | None = False
):
    """Debug-only delete endpoint: logs everything, always returns OK."""
    content_type = request.headers.get("content-type", "")
    qp = dict(request.query_params)
    raw_body = await request.body()
    logging.info(f"[DEBUG‑FORCE] Delete request for {collection_name}")
    logging.info(f"  Headers: content-type={content_type}")
    logging.info(f"  Query params: {qp}")
    logging.info(f"  Raw body bytes: {raw_body!r}")

    try:
        body_text = raw_body.decode("utf-8", errors="ignore")
    except Exception:
        body_text = str(raw_body)
    logging.info(f"  Raw body text: {body_text}")

    return {"status": "ok", "result": {"deleted": 0, "ids": []}}


def _close_global_conn():
    global _global_conn, _hnsw_index
    # Save HNSW index before closing DB
    if _hnsw_index is not None:
        hnsw_path = "memory_index.bin"
        try:
            _hnsw_index.save_index(hnsw_path)
            print(f"[HNSW] Saved vector index to {hnsw_path}.")
        except Exception as e:
            print(f"[HNSW] WARNING: Failed to save persistent index ({e}).")
    if _global_conn:
        print("[DB] Closing global SQLite connection.")
        _global_conn.close()
        _global_conn = None


atexit.register(_close_global_conn)

# -------------------------------
# Entrypoint
# -------------------------------

if __name__ == "__main__":
    import uvicorn

    print("[SERVER] Starting Ghostwire controller...")
    # Run with direct app object to avoid hyphen module import issues
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


# -------------------------------
# Summarization endpoint
# -------------------------------


@app.post("/summarize")
async def summarize_endpoint(payload: dict):
    """Summarize text using local Ollama and return summary text."""
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=422, detail="Missing text")
    if DISABLE_SUMMARIZATION:
        logging.info(
            "[summarize_endpoint] Summarization disabled; returning input text."
        )
        return {"status": "ok", "summary": text}
    summary = await ollama_summarize(text)
    return {"status": "ok", "summary": summary}


# -------------------------------
# Retrieval-only endpoint
# -------------------------------

from fastapi import Body


@app.post("/retrieve")
async def retrieve_endpoint(payload: dict = Body(...)):
    """
    Retrieval-only endpoint for benchmarks.
    Accepts: {"session_id": str, "text": str}
    Returns: {"status": "ok", "contexts": [list of prompt_text strings]}
    """
    try:
        session_id = payload.get("session_id")
        text = payload.get("text")
        if not session_id or not isinstance(session_id, str) or not session_id.strip():
            logging.error("[/retrieve] Missing or invalid session_id")
            raise HTTPException(status_code=422, detail="Missing or invalid session_id")
        if not text or not isinstance(text, str) or not text.strip():
            logging.error("[/retrieve] Missing or invalid text")
            raise HTTPException(status_code=422, detail="Missing or invalid text")
    except Exception as e:
        logging.error(f"[/retrieve] Error parsing input: {e}")
        raise HTTPException(status_code=422, detail="Invalid input payload")

    try:
        embedding = await ollama_embed(text)
        if not embedding:
            logging.error("[/retrieve] Failed to generate embedding")
            raise HTTPException(status_code=500, detail="Failed to generate embedding")
        memories = query_similar_by_embedding(session_id, embedding, limit=5)
        contexts = [p for p, _ in memories]
        logging.info(
            f"[/retrieve] Retrieved {len(contexts)} contexts for session_id={session_id}"
        )
        return {"status": "ok", "contexts": contexts}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"[/retrieve] Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval error: {e}")


# -------------------------------
# RAG benchmark endpoint
# -------------------------------


@app.post("/rag")
async def rag_endpoint(payload: dict):
    """RAG endpoint: embed query, recall similar memory, and stream augmented answer."""
    session_id = payload.get("session_id", "default_session")
    text = payload.get("text")
    model = payload.get("model", DEFAULT_OLLAMA_MODEL)
    if not text:
        raise HTTPException(status_code=422, detail="Missing text for RAG")

    # Generate embedding for the query
    embedding = await ollama_embed(text)
    if not embedding:
        raise HTTPException(status_code=500, detail="Failed to generate embedding")

    # Retrieve context
    memories = query_similar_by_embedding(session_id, embedding, limit=5)
    context = ""
    if memories:
        snippets = " | ".join(f"{p}" for p, _ in memories[:3])
        context = f"Context: {snippets}\n\n"

    prompt = f"{context}User question: {text}\n\nAnswer:"
    # Select remote/local based on model name
    use_remote = model.startswith("remote-") or model.endswith(":remote")
    clean_model = (
        model.removeprefix("remote-")
        .removeprefix("local-")
        .removesuffix(":remote")
        .removesuffix(":local")
    )

    async def stream_response():
        try:
            async for chunk in stream_from_ollama(
                prompt, model=model, local=not use_remote
            ):
                yield chunk
        except Exception as e:
            yield f"[ERROR] {e}"

    return StreamingResponse(stream_response(), media_type="text/plain")


# -------------------------------
# Benchmark endpoint
# -------------------------------


@app.post("/benchmark")
async def benchmark_endpoint(payload: dict):
    """
    Run a benchmark task.
    payload: {
        "session_id": str,
        "task": "rag" | "summarize" | "all",
        "model": Optional[str]  # which generation model to use, defaults to DEFAULT_OLLAMA_MODEL
    }
    Returns JSON with results for the requested benchmarks.
    """

    # Helper function for GhostWire scoring
    def ghostwire_score(latency: float, length_factor: float = 1.0) -> float:
        base = max(0.0, 1.0 - latency / 5.0)
        return round(100 * base * length_factor, 2)

    session_id = payload.get("session_id", "benchmark")
    # Allow both "task" and "model" keys to trigger benchmarks from the operator console
    task = payload.get("task") or payload.get("model")
    model = payload.get("model", DEFAULT_OLLAMA_MODEL)

    # If the provided task isn't one of the known types, assume it's a model name and run all benchmarks
    if task not in ("rag", "summarize", "all"):
        logging.info(
            f"[benchmark] Unknown task '{task}', treating it as model name for full benchmark suite."
        )
        model = task  # interpret the task value as a model name
        task = "all"

    results: dict[str, Any] = {}

    # 1. Summarization benchmark
    if task in ("summarize", "all") and not DISABLE_SUMMARIZATION:
        sum_cases = [
            "Quantum computing uses quantum bits called qubits that can represent 0 and 1 simultaneously.",
            "Large language models are trained on massive text corpora to predict the next word.",
        ]
        sum_out = []
        # Select remote/local for summarization
        use_remote = model.startswith("remote-") or model.endswith(":remote")
        clean_model = (
            model.removeprefix("remote-")
            .removeprefix("local-")
            .removesuffix(":remote")
            .removesuffix(":local")
        )
        for text in sum_cases:
            start = time.time()
            # If using remote, call stream_from_ollama directly; else ollama_summarize
            if use_remote:
                summary = ""
                async for chunk in stream_from_ollama(
                    f"Summarize this text concisely, keeping key details:\n\n{text}",
                    model=model,
                    local=False,
                ):
                    summary += chunk
            else:
                summary = await ollama_summarize(text)
            latency = time.time() - start
            # Compute compression ratio and ghostwire_score
            ratio = len(summary.split()) / len(text.split()) if text.split() else 1.0
            score = ghostwire_score(latency, 1.0 / max(1.0, ratio))
            sum_out.append(
                {
                    "input": text,
                    "summary": summary,
                    "latency": latency,
                    "ghostwire_score": score,
                }
            )
        results["summarize"] = sum_out
    else:
        if task in ("summarize", "all") and DISABLE_SUMMARIZATION:
            logging.info(
                "[benchmark] Summarization disabled; skipping summarization benchmark."
            )

    # 2. RAG benchmark
    if task in ("rag", "all"):
        rag_cases = [
            "What is superposition in quantum computing?",
            "How does photosynthesis work in plants?",
        ]
        rag_out = []
        use_remote = model.startswith("remote-") or model.endswith(":remote")
        clean_model = (
            model.removeprefix("remote-")
            .removeprefix("local-")
            .removesuffix(":remote")
            .removesuffix(":local")
        )
        for q in rag_cases:
            start = time.time()
            # Generate embedding for the query
            embedding = await ollama_embed(q)
            if not embedding:
                rag_out.append({"question": q, "error": "Failed to generate embedding"})
                continue
            memories = query_similar_by_embedding(session_id, embedding, limit=5)
            context = ""
            if memories:
                snippets = " | ".join(f"{p}" for p, _ in memories[:3])
                context = f"Context: {snippets}\n\n"
            prompt = f"{context}User question: {q}\n\nAnswer:"
            resp_chunks = []
            async for chunk in stream_from_ollama(
                prompt, model=model, local=not use_remote
            ):
                resp_chunks.append(chunk)
            answer_text = "".join(resp_chunks)
            latency = time.time() - start
            score = ghostwire_score(latency)
            rag_out.append(
                {
                    "question": q,
                    "answer": answer_text,
                    "latency": latency,
                    "ghostwire_score": score,
                }
            )
        results["rag"] = rag_out

    # Compute overall average ghostwire_score
    all_scores = []
    for cat in results.values():
        for case in cat:
            if "ghostwire_score" in case:
                all_scores.append(case["ghostwire_score"])
    avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0

    # Log formatted console output for human-readability
    for task_name in results:
        logging.info(f"⚙️  {task_name.upper()} Benchmark Results")
        for case in results[task_name]:
            logging.info(
                f" • {case.get('question', case.get('input', ''))[:60]} → {case.get('ghostwire_score', 'N/A')} score | {case.get('latency', 0.0):.2f}s"
            )
    logging.info(f"Average GhostWire score: {avg_score}")

    return {"status": "ok", "benchmarks": results, "avg_score": avg_score}
