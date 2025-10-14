"""
GhostWire Refractory - Main Application Entry Point
"""
import atexit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..api.v1.router import api_router
from ..api.middleware.rate_limit import RateLimitMiddleware
from ..config.settings import settings
from ..database.connection import close_db_pool
from ..vector.hnsw_index import get_hnsw_manager


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="GhostWire Refractory API",
        description="A neural lattice forged in neon, whispering through the data fog",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware with proper security settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Only expose headers that are needed
        expose_headers=["X-Response-Time"],
    )

    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "1.0.0"}
    
    # Startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        print("[SERVER] Starting GhostWire Refractory...")
        # Initialize HNSW index
        hnsw_manager = get_hnsw_manager()
        hnsw_manager.initialize_index()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        print("[SERVER] Shutting down GhostWire Refractory...")
        # Save HNSW index
        hnsw_manager = get_hnsw_manager()
        hnsw_manager.save_index()
        # Close database connections
        close_db_pool()

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.ghostwire.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
    
    # Register cleanup function
    def cleanup():
        hnsw_manager = get_hnsw_manager()
        hnsw_manager.save_index()
        close_db_pool()
    
    atexit.register(cleanup)