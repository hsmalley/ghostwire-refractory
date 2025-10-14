"""
Chat endpoints for GhostWire Refractory
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, validator

from ...config.settings import settings
from ...models.base import APIResponse
from ...services.embedding_service import embedding_service
from ...services.memory_service import MemoryCreate, memory_service
from ...services.rag_service import rag_service
from ...utils.error_handling import EmbeddingDimMismatchError, handle_exception
from ...utils.security import (
    validate_embedding,
    validate_session_id,
    validate_text_content,
)

router = APIRouter()


class ChatEmbeddingRequest(BaseModel):
    session_id: str
    text: str | None = None
    prompt_text: str | None = None
    embedding: list[float] | None = None
    context: str | None = None

    @validator("session_id")
    def validate_session_id(cls, v):
        validate_session_id(v)
        return v

    @validator("text", "prompt_text", "context", pre=True)
    def validate_text(cls, v):
        if v:
            validate_text_content(v, max_length=5000)  # Reasonable limit for chat input
        return v

    def get_text(self) -> str:
        return self.text or self.prompt_text or ""


class ChatResponse(BaseModel):
    response: str


@router.post("/chat_embedding")
async def chat_with_embedding(request: ChatEmbeddingRequest):
    """Chat endpoint that uses embeddings for context retrieval"""
    try:
        session_id = request.session_id
        text = request.get_text()
        embedding = request.embedding

        # Validate text content
        if text:
            validate_text_content(text, max_length=5000)

        # Generate embedding if not provided
        if not embedding:
            embedding = await embedding_service.embed_text(text)
            if not embedding:
                raise HTTPException(
                    status_code=500, detail="Failed to auto-generate embedding"
                )

        # Validate embedding
        try:
            validate_embedding(embedding, settings.EMBED_DIM)
        except EmbeddingDimMismatchError as e:
            raise e.to_http_exception()

        # Merge context if provided
        if request.context:
            text = f"{request.context.strip()}\n\nQuestion: {text.strip()}"

        # Perform RAG query with streaming
        async def event_generator():
            try:
                async for chunk in rag_service.rag_query(session_id, text, stream=True):
                    yield chunk
            except Exception as e:
                yield f"\n[ERROR] {type(e).__name__}: {e}\n"

        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat_completion")
async def chat_completion(request: ChatEmbeddingRequest):
    """Simple chat completion without retrieval"""
    try:
        session_id = request.session_id
        text = request.get_text()

        if not text:
            raise HTTPException(status_code=422, detail="Text is required")

        # Validate text content
        validate_text_content(text, max_length=5000)

        # Validate session ID
        validate_session_id(session_id)

        # For this endpoint, just return the text for now
        # In a full implementation, this would call the LLM directly
        return {"response": f"Echo: {text}"}
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory")
async def add_memory(request: ChatEmbeddingRequest):
    """Add memory entry to the database"""
    try:
        session_id = request.session_id
        text = request.get_text()
        embedding = request.embedding or []

        # Validate session ID
        validate_session_id(session_id)

        # Validate text content
        if text:
            validate_text_content(
                text, max_length=10000
            )  # Larger limit for memory storage

        # Generate embedding if not provided
        if not embedding:
            embedding = await embedding_service.embed_text(text)
            if not embedding:
                raise HTTPException(
                    status_code=500, detail="Failed to auto-generate embedding"
                )

        # Validate embedding
        try:
            validate_embedding(embedding, settings.EMBED_DIM)
        except EmbeddingDimMismatchError as e:
            raise e.to_http_exception()

        # Create memory
        memory_create = MemoryCreate(
            session_id=session_id,
            prompt_text=text,
            answer_text="Stored in memory",  # Placeholder answer
            embedding=embedding,
        )

        memory = memory_service.create_memory(memory_create)
        return APIResponse(message=f"Memory created with ID: {memory.id}")
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))
