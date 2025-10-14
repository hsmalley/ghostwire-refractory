"""
Vector endpoints for GhostWire Refractory
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from ...models.embedding import (
    VectorQueryRequest,
    VectorQueryResponse,
    VectorUpsertRequest,
)
from ...services.memory_service import MemoryCreate, memory_service

router = APIRouter()


@router.post("/vectors/upsert")
async def upsert_vector(request: VectorUpsertRequest) -> dict[str, Any]:
    """Upsert a vector record"""
    try:
        # Convert to memory format
        memory_create = MemoryCreate(
            session_id=request.namespace,
            prompt_text="",  # Using prompt_text as main content
            answer_text=request.text,
            embedding=request.embedding,
            summary_text=request.metadata.get("summary") if request.metadata else None,
        )

        memory = memory_service.create_memory(memory_create)
        return {"object": "vector.upsert", "status": "ok", "id": memory.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vectors/query")
async def query_vector(request: VectorQueryRequest) -> VectorQueryResponse:
    """Query similar vectors"""
    try:
        from ...models.memory import MemoryQuery

        memory_query = MemoryQuery(
            session_id=request.namespace,
            embedding=request.embedding,
            limit=request.top_k,
        )

        memories = memory_service.query_similar_memories(memory_query)

        # Format response
        data = []
        for idx, memory in enumerate(memories):
            data.append(
                {
                    "prompt_text": memory.prompt_text,
                    "answer_text": memory.answer_text,
                    "score": idx,  # Placeholder score
                    "id": memory.id,
                }
            )

        return VectorQueryResponse(data=data, model=request.namespace)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
