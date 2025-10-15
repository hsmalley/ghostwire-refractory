"""
# ⚡️ API Router v1

Central hub that stitches together all GhostWire endpoints. Each sub‑module is exposed with a tag to aid OpenAPI docs and client filtering.
"""

from fastapi import APIRouter

from .chat import router as chat_router
from .documents import router as documents_router
from .embeddings import router as embeddings_router
from .health import router as health_router
from .metrics import metrics_router
from .orchestrator import router as orchestrator_router
from .qdrant import router as qdrant_router
from .vectors import router as vectors_router

# Main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(embeddings_router, tags=["embeddings"])
api_router.include_router(vectors_router, tags=["vectors"])
api_router.include_router(qdrant_router, tags=["qdrant"])
api_router.include_router(documents_router, tags=["documents"])
api_router.include_router(orchestrator_router, tags=["orchestrator"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(metrics_router, tags=["metrics"])
