from __future__ import annotations

import atexit
import json
import os
import httpx
import sqlite3
import time
from typing import AsyncGenerator, List, Tuple

import hnswlib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


# Config via environment (with safe defaults)
REMOTE_OLLAMA_URL = os.getenv(
    "REMOTE_OLLAMA_URL", "http://100.103.237.60:11434/api/generate"
)
REMOTE_OLLAMA_MODEL = os.getenv("REMOTE_OLLAMA_MODEL", "llama3.2:latest")


async def stream_from_ollama(prompt: str) -> AsyncGenerator[str, None]:
    """Stream text tokens from remote Ollama server (JSONL protocol)."""
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
    conn.commit()


def get_connection() -> sqlite3.Connection:
    global _global_conn
    if _global_conn is not None:
        # print("[DB] Using global SQLite connection")
        return _global_conn

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _ensure_tables(conn)
    _global_conn = conn
    return _global_conn


def _ensure_hnsw_initialized(conn: sqlite3.Connection) -> None:
    """Initialize HNSW and backfill from DB once."""
    global _hnsw_index, _hnsw_initialized
    if _hnsw_initialized:
        return

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


async def ask_streaming_with_embedding(
    session_id: str, text: str, embedding: List[float]
) -> AsyncGenerator[str, None]:
    """
    Streaming generator using remote Ollama server, with memory context.
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
# Graceful shutdown
# -------------------------------


def _close_global_conn():
    global _global_conn
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
