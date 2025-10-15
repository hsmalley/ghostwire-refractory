"""
Embedding endpoints for GhostWire Refractory
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from ...models.embedding import EmbeddingRequest, EmbeddingResponse
from ...services.embedding_service import embedding_service
from ...utils.error_handling import handle_exception
from ...utils.security import validate_text_content

router = APIRouter()


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """Create embeddings for input text(s)"""
    try:
        # Validate input text content
        inputs = request.input
        if isinstance(inputs, str):
            validate_text_content(
                inputs, max_length=10000
            )  # Reasonable limit for embedding input
        elif isinstance(inputs, list):
            for text_input in inputs:
                if isinstance(text_input, str):
                    validate_text_content(text_input, max_length=10000)

        response = await embedding_service.create_embedding(request)
        return response
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models() -> dict[str, Any]:
    """List available models"""
    # This would integrate with Ollama to list models
    # For now, return a basic response
    from ...config.settings import settings

    models = [
        {"id": model, "object": "model", "owned_by": "local"}
        for model in settings.EMBED_MODELS
    ]
    models.append(
        {"id": settings.DEFAULT_OLLAMA_MODEL, "object": "model", "owned_by": "local"}
    )

    return {"object": "list", "data": models}
