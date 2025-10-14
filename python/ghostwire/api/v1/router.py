"""
Main API router for GhostWire Refractory v1
"""

from fastapi import APIRouter

from .chat import router as chat_router
from .embeddings import router as embeddings_router
from .health import router as health_router
from .vectors import router as vectors_router

# Main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(embeddings_router, tags=["embeddings"])
api_router.include_router(vectors_router, tags=["vectors"])
api_router.include_router(chat_router, tags=["chat"])
