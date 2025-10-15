"""
Document endpoints for GhostWire Refractory
"""

import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ...models.base import APIResponse
from ...services.document_service import document_service
from ...utils.error_handling import handle_exception
from ...utils.security import validate_session_id, validate_text_content

router = APIRouter()
logger = logging.getLogger(__name__)


class IngestDocumentRequest(BaseModel):
    """Request model for document ingestion"""

    session_id: str
    content: str
    source: str
    document_id: str | None = None


class SearchDocumentsRequest(BaseModel):
    """Request model for document search"""

    session_id: str
    query: str
    limit: int = 10


class DocumentChunk(BaseModel):
    """Model for document chunk response"""

    id: int
    content: str
    source: str
    summary: str | None
    session_id: str


class SearchDocumentsResponse(BaseModel):
    """Response model for document search"""

    results: list[DocumentChunk]


class DocumentListResponse(BaseModel):
    """Response model for document listing"""

    documents: list[dict]


@router.post("/documents/ingest", response_model=APIResponse)
async def ingest_document(request: IngestDocumentRequest):
    """Ingest a document and store its chunks in the vector database"""
    try:
        # Validate session ID
        validate_session_id(request.session_id)

        # Validate content
        validate_text_content(
            request.content, max_length=50000
        )  # Allow larger documents

        # Validate source
        if not request.source or len(request.source) > 200:
            raise HTTPException(status_code=422, detail="Invalid source specified")

        # Process the document ingestion
        memory_ids = await document_service.ingest_document(
            content=request.content,
            source=request.source,
            session_id=request.session_id,
            document_id=request.document_id,
        )

        return APIResponse(
            message=f"Successfully ingested document. Created {len(memory_ids)} chunks with IDs: {memory_ids}"
        )
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/ingest_file", response_model=APIResponse)
async def ingest_document_from_file(
    session_id: str = Form(...), source: str = Form(...), file: UploadFile = File(...)
):
    """Ingest a document from file upload"""
    try:
        # Validate session ID
        validate_session_id(session_id)

        # Validate source
        if not source or len(source) > 200:
            raise HTTPException(status_code=422, detail="Invalid source specified")

        # Read file content
        content = await file.read()
        content_str = content.decode("utf-8")

        # Validate content
        validate_text_content(content_str, max_length=50000)  # Allow larger documents

        # Process the document ingestion
        memory_ids = await document_service.ingest_document(
            content=content_str, source=source, session_id=session_id
        )

        return APIResponse(
            message=f"Successfully ingested document {file.filename}. Created {len(memory_ids)} chunks with IDs: {memory_ids}"
        )
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/search", response_model=SearchDocumentsResponse)
async def search_documents(request: SearchDocumentsRequest):
    """Search for document chunks similar to the query"""
    try:
        # Validate session ID
        validate_session_id(request.session_id)

        # Validate query
        validate_text_content(request.query, max_length=1000)

        # Perform search
        results = await document_service.search_document_chunks(
            query=request.query, session_id=request.session_id, limit=request.limit
        )

        return SearchDocumentsResponse(results=results)
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/session/{session_id}", response_model=DocumentListResponse)
async def list_documents_in_session(session_id: str):
    """List all document chunks in a session"""
    try:
        # Validate session ID
        validate_session_id(session_id)

        # List documents
        documents = await document_service.list_documents_in_session(session_id)

        return DocumentListResponse(documents=documents)
    except Exception as e:
        handled_exc = handle_exception(e)
        if isinstance(handled_exc, HTTPException):
            raise handled_exc
        raise HTTPException(status_code=500, detail=str(e))
