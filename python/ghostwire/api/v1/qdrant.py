"""
Qdrant-compatible endpoints for GhostWire Refractory
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...services.memory_service import MemoryCreate, memory_service
from ...utils.error_handling import handle_exception
from ...utils.security import validate_session_id

router = APIRouter()
logger = logging.getLogger(__name__)


# Qdrant-compatible models
class QdrantPoint(BaseModel):
    """Qdrant-compatible point model"""

    id: int | str
    payload: dict[str, Any] = Field(default_factory=dict)
    vector: list[float]


class QdrantUpsertRequest(BaseModel):
    """Qdrant-compatible upsert request"""

    points: list[QdrantPoint]


class QdrantUpsertResponse(BaseModel):
    """Qdrant-compatible upsert response"""

    result: dict[str, Any] = Field(default_factory=dict)
    status: str = "acknowledged"


class QdrantSearchRequest(BaseModel):
    """Qdrant-compatible search request"""

    vector: list[float]
    limit: int = 10
    with_payload: bool = True
    with_vectors: bool = False
    collection_name: str | None = None


class QdrantScoredPoint(BaseModel):
    """Qdrant-compatible scored point model"""

    id: int | str
    version: int = 0
    score: float
    payload: dict[str, Any] = Field(default_factory=dict)
    vector: list[float] | None = None


class QdrantSearchResponse(BaseModel):
    """Qdrant-compatible search response"""

    result: list[QdrantScoredPoint]
    status: str = "acknowledged"


class QdrantCollectionInfo(BaseModel):
    """Qdrant-compatible collection info"""

    status: str = "green"
    optimizer_status: str = "ok"
    vectors_count: int = 0
    segments_count: int = 1
    config: dict[str, Any] = Field(default_factory=dict)
    payload_schema: dict[str, Any] = Field(default_factory=dict)


class QdrantCollectionResponse(BaseModel):
    """Qdrant-compatible collection response"""

    result: QdrantCollectionInfo
    status: str = "acknowledged"


@router.put("/collections/{collection_name}")
async def create_collection(collection_name: str):
    """Qdrant-compatible endpoint to create a collection"""
    try:
        # In our implementation, collections map to session IDs
        # We don't need to create anything specific here since sessions are created on demand
        return {"result": {"acknowledged": True, "affected": 1}, "status": "ok"}
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """Qdrant-compatible endpoint to get collection info"""
    try:
        # Validate collection name as session ID
        validate_session_id(collection_name)

        # Get the size of the collection (number of memories in the session)
        collection_size = memory_service.get_collection_size(collection_name)

        collection_info = QdrantCollectionInfo(
            vectors_count=collection_size,
            config={
                "params": {
                    "vectors_count": collection_size,
                    "indexed_vectors_count": collection_size,
                    "points_count": collection_size,
                }
            },
        )

        return QdrantCollectionResponse(result=collection_info)
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/collections/{collection_name}/points")
async def upsert_points(collection_name: str, request: QdrantUpsertRequest):
    """Qdrant-compatible endpoint to upsert points"""
    try:
        # Validate collection name as session ID
        validate_session_id(collection_name)

        # Process each point in the request
        processed_ids = []
        for point in request.points:
            # Create a memory entry for this point
            memory_create = MemoryCreate(
                session_id=collection_name,
                prompt_text=point.payload.get("text", f"Vector data point {point.id}"),
                answer_text=point.payload.get(
                    "metadata", f"Vector data from point {point.id}"
                ),
                embedding=point.vector,
                summary_text=point.payload.get("summary", ""),
            )

            # Store in memory service
            memory = memory_service.create_memory(memory_create)
            processed_ids.append(memory.id)

        return QdrantUpsertResponse(
            result={"acknowledged": True, "processed_ids": processed_ids}
        )
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections/{collection_name}/points/search")
async def search_points(collection_name: str, request: QdrantSearchRequest):
    """Qdrant-compatible endpoint to search points"""
    try:
        # Validate collection name as session ID
        validate_session_id(collection_name)

        # Validate vector dimension
        from ...config.settings import settings

        if len(request.vector) != settings.EMBED_DIM:
            raise HTTPException(
                status_code=422,
                detail=f"Vector dimension {len(request.vector)} does not match expected {settings.EMBED_DIM}",
            )

        # Perform similarity search using our memory service with scores
        from ...models.memory import MemoryQuery

        query_obj = MemoryQuery(
            session_id=collection_name, embedding=request.vector, limit=request.limit
        )

        # Get memories with similarity scores
        memories_with_scores = memory_service.query_similar_memories_with_scores(
            query_obj
        )

        # Format results as Qdrant-scored points
        results = []
        for i, (memory, similarity_score) in enumerate(memories_with_scores):
            # Convert stored embedding from bytes back to list
            import numpy as np

            stored_embedding = np.frombuffer(
                memory.embedding, dtype=np.float32
            ).tolist()

            # Use the actual similarity score from HNSW or fallback to position-based score
            score = similarity_score if similarity_score > 0 else (1.0 - (i * 0.05))

            scored_point = QdrantScoredPoint(
                id=memory.id,
                version=0,
                score=score,
                payload={
                    "text": memory.prompt_text,
                    "metadata": memory.answer_text,
                    "summary": memory.summary_text or "",
                    "timestamp": memory.timestamp,
                },
                vector=stored_embedding if request.with_vectors else None,
            )
            results.append(scored_point)

        return QdrantSearchResponse(result=results)
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Qdrant-compatible endpoint to delete a collection"""
    try:
        # Validate collection name as session ID
        validate_session_id(collection_name)

        # Delete all memories in the collection
        success = memory_service.delete_collection(collection_name)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Collection {collection_name} not found"
            )

        return {"result": {"acknowledged": True, "affected": 1}, "status": "ok"}
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))
