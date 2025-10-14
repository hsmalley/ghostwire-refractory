"""
Database models for GhostWire Refractory
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import sqlite3
import json


class Memory(BaseModel):
    """Database model for memory entries"""
    id: Optional[int] = None
    session_id: str
    prompt_text: str
    answer_text: str
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    embedding: bytes  # Serialized embedding vector
    summary_text: Optional[str] = None


class MemoryCreate(BaseModel):
    """Model for creating new memories"""
    session_id: str
    prompt_text: str
    answer_text: str
    embedding: list[float]
    summary_text: Optional[str] = None


class MemoryQuery(BaseModel):
    """Model for memory queries"""
    session_id: str
    embedding: list[float]
    limit: int = 5


# Database schema
DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_text (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    timestamp REAL NOT NULL,
    embedding BLOB NOT NULL,
    summary_text TEXT
);

CREATE TABLE IF NOT EXISTS dropped_collections (
    name TEXT PRIMARY KEY
);

-- Index for faster session-based queries
CREATE INDEX IF NOT EXISTS idx_session_id ON memory_text(session_id);

-- Index for faster timestamp queries
CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_text(timestamp);
"""