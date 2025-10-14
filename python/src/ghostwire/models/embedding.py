"""
Embedding-related data models for GhostWire Refractory
"""

from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    """Request model for creating embeddings"""

    input: str | list[str]
    model: str = "embeddinggemma"


class EmbeddingResponse(BaseModel):
    """Response model for embeddings"""

    object: str = "list"
    data: list[dict]
    model: str
    usage: dict


class EmbeddingData(BaseModel):
    """Individual embedding data"""

    object: str = "embedding"
    embedding: list[float]
    index: int


class VectorUpsertRequest(BaseModel):
    """Request model for upserting vectors"""

    namespace: str
    id: str | None = None
    text: str
    embedding: list[float]
    metadata: dict | None = None


class VectorQueryRequest(BaseModel):
    """Request model for querying vectors"""

    namespace: str
    embedding: list[float]
    top_k: int = 5


class VectorQueryResponse(BaseModel):
    """Response model for vector queries"""

    object: str = "list"
    data: list[dict]
