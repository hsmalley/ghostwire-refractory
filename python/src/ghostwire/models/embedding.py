"""
Embedding-related data models for GhostWire Refractory
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Request model for creating embeddings"""
    input: Union[str, List[str]]
    model: str = "embeddinggemma"


class EmbeddingResponse(BaseModel):
    """Response model for embeddings"""
    object: str = "list"
    data: List[dict]
    model: str
    usage: dict


class EmbeddingData(BaseModel):
    """Individual embedding data"""
    object: str = "embedding"
    embedding: List[float]
    index: int


class VectorUpsertRequest(BaseModel):
    """Request model for upserting vectors"""
    namespace: str
    id: Optional[str] = None
    text: str
    embedding: List[float]
    metadata: Optional[dict] = None


class VectorQueryRequest(BaseModel):
    """Request model for querying vectors"""
    namespace: str
    embedding: List[float]
    top_k: int = 5


class VectorQueryResponse(BaseModel):
    """Response model for vector queries"""
    object: str = "list"
    data: List[dict]