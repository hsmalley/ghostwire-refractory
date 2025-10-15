#!/usr/bin/env python3
"""Seed a small set of example memories into the project's SQLite DB.

This script is intentionally minimal and uses the repo's settings to locate the DB.
It creates a tiny `memories` table if missing and inserts a few rows with embeddings
as JSON text (compact) so the rest of the project can discover example data.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# no-op: keep typings minimal and compatible with Python 3.9+

try:
    # prefer project settings when run from repo root with PYTHONPATH=python
    from ghostwire.config.settings import settings
except Exception:  # pragma: no cover - best-effort import
    # fallback defaults
    class _Dummy:
        DB_PATH = "memory.db"
        EMBED_DIM = 768

    settings = _Dummy()


def make_embedding(dim: int) -> list[float]:
    # Simple deterministic embedding useful for examples
    return [float(i % 10) / 10.0 for i in range(dim)]


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )
    conn.commit()


def insert_sample(
    conn: sqlite3.Connection, session: str, text: str, embedding: list[float]
) -> None:
    emb_json = json.dumps(embedding)
    # Avoid duplicate identical entries by checking for same text + session
    cur = conn.execute(
        "SELECT id FROM memories WHERE session_id = ? AND text = ?", (session, text)
    )
    if cur.fetchone():
        print(f"Skipping existing sample for session={session!r}")
        return
    conn.execute(
        "INSERT INTO memories (session_id, text, embedding) VALUES (?, ?, ?)",
        (session, text, emb_json),
    )
    conn.commit()


def main() -> None:
    db_path = Path(settings.DB_PATH)
    print(f"Using database: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        ensure_table(conn)

        # Insert a couple of sample memories
        insert_sample(
            conn,
            "demo_session",
            "The city remembers the rain.",
            make_embedding(settings.EMBED_DIM),
        )
        insert_sample(
            conn,
            "demo_session",
            "A neon ribbon traces the idea.",
            make_embedding(settings.EMBED_DIM),
        )

        print("Seeding complete — inserted sample memories (if missing).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
