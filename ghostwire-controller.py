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
from typing import Any, AsyncGenerator, List, Optional, Tuple

import hnswlib
import httpx
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

#
# Config via environment (with safe defaults)
REMOTE_OLLAMA_URL = os.getenv(
    "REMOTE_OLLAMA_URL", "http://100.103.237.60:11434/api/generate"
)
REMOTE_OLLAMA_MODEL = os.getenv("REMOTE_OLLAMA_MODEL", "llama3.2:latest")

# Local Ollama URL for summarization/embedding helpers
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


async def stream_from_ollama(prompt: str) -> AsyncGenerator[str, None]:
    """
    Open the channel to Ollama and stream `response` fragments as they arrive.

    Input
    - prompt: The fully composed prompt including any recalled memory context.

    Yields
    - Text fragments in arrival order; callers should concatenate.
    """
    try:
        async with httpx.AsyncClient(timeout=None, http2=True) as client:
            async with client.stream(
                "POST",
                REMOTE_OLLAMA_URL,
                json={"model": REMOTE_OLLAMA_MODEL, "prompt": prompt, "stream": True},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        # Skip malformed lines
                        continue
                    chunk = obj.get("response")
                    if chunk:
                        yield chunk
                    if obj.get("done"):
                        break
    except Exception as e:
        # Surface error to stream and server logs
        yield f"[ERROR] Failed to connect to Ollama: {e}"


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

# Set up root logger for debugging
logging.basicConfig(level=logging.INFO)


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


async def ollama_embed(text: str) -> list[float]:
    """Use local Ollama for embedding text."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
        )
        data = resp.json()
        return data.get("embedding", [])


async def ollama_summarize(text: str) -> str:
    """Use local Ollama for summarization."""
    prompt = f"Summarize this text concisely, keeping key details:\n\n{text}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OLLAMA_URL}/api/generate", json={"model": "mistral", "prompt": prompt}
        )
        output = ""
        async for chunk in resp.aiter_text():
            output += chunk
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
    session_id: str, prompt_text: str, answer_text: str, embedding: List[float]
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
    session_id: str, embedding: List[float], limit: int = 5
) -> List[Tuple[str, str]]:
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

    scored: List[Tuple[float, str, str]] = []
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

    def normalized(self):
        text_value = self.text or self.prompt_text or ""
        embed_value = self.embedding or []
        return self.session_id, text_value, embed_value


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
    session_id: str, text: str, embedding: List[float]
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
    async for token in stream_from_ollama(full_prompt):
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
        session_id, text, embedding = req.normalized()

    except Exception as e:
        print(f"[WARN] Could not parse chat_embedding payload: {e}")
        session_id, text, embedding = "unknown", "", []

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
# OpenAI-compatible /v1/embeddings endpoint (controller-native)
# -------------------------------


async def generate_embedding(text_input: str, model: str = "nomic-embed-text"):
    """
    Generate embedding for a single text string using Ollama backend.
    Always returns a single vector (list[float]).
    """
    import httpx

    if not isinstance(text_input, str):
        raise TypeError(f"generate_embedding expected str, got {type(text_input)}")

    try:
        async with httpx.AsyncClient() as client:
            payload = {"model": model, "input": text_input}
            resp = await client.post(
                "http://localhost:11434/api/embeddings", json=payload
            )
            resp.raise_for_status()
            data = resp.json()

            # Accept either "embedding" or "data[0]['embedding']"
            embedding = data.get("embedding") or data.get("data", [{}])[0].get(
                "embedding"
            )
            if not embedding:
                print(f"[WARN] No embedding returned for model={model}")
                return []

            return embedding
    except Exception as e:
        print(f"[ERROR] generate_embedding failed: {e}")
        return []


from fastapi.responses import JSONResponse


@app.post("/v1/embeddings")
async def v1_embeddings(req: dict):
    """
    OpenAI-compatible embedding endpoint.
    Accepts: {"model": "granite-embedding", "input": "text"} or {"input": ["t1", "t2", ...]}.
    Ensures generate_embedding() is always called with a single string.
    """
    try:
        model = req.get("model", "nomic-embed-text")
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
    filter: Optional[dict[str, Any]] = None


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
            if use_summary and text:
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


@app.post("/collections/{collection_name}/points/search")
async def q_search(collection_name: str, req: QSearchRequest):
    """Search points by vector similarity (Qdrant-style)."""
    try:
        recs = query_similar_by_embedding(collection_name, req.vector, req.top)
        response = []
        for idx, (p, a) in enumerate(recs):
            try:
                payload = json.loads(a)
            except Exception:
                payload = None
            response.append({"id": idx, "score": float(1.0 - 0.0), "payload": payload})
        return {"result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


# Qdrant-compatible delete: supports {"filter":{"must":[]}} or {"filter":{"must":[{"key":"id","match":{"any":[...]}}]}}
@app.post("/collections/{collection_name}/points/delete")
async def qdrant_delete_points(
    collection_name: str, request: Request, wait: Optional[bool] = False
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
    wait: Optional[bool] = False,
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
    collection_name: str, request: Request, wait: Optional[bool] = False
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


# -------------------------------
# Graceful shutdown
# -------------------------------


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
    """Summarize text and return both summary and embedding."""
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=422, detail="Missing text")
    summary = await ollama_summarize(text)
    emb = await ollama_embed(summary)
    return {"status": "ok", "result": {"summary": summary, "embedding": emb}}
