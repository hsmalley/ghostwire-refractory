"""
Services package for GhostWire Refractory

This package contains all service layer functionality for the GhostWire Refractory system,
including memory, embedding, RAG, and orchestrator services.
"""

# Import orchestrator-related services if available
try:
    from ..orchestrator.integration import GhostWireOrchestrator

    __all__ = ["GhostWireOrchestrator"]
except ImportError:
    # Orchestrator may not be available in all deployments
    __all__ = []
