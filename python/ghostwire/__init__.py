"""
GhostWire Refractory - Main Package

This package contains the core functionality of the GhostWire Refractory system,
including API, services, configuration, and the new orchestrator system.
"""

# Import the orchestrator functionality to make it accessible at the package level
try:
    from .orchestrator import (
        GhostWireOrchestrator,
        LLMClient,
        Master,
        PatchEngine,
        PermissionManager,
        create_ghostwire_orchestrator,
        decompose_user_request,
    )

    __all__ = [
        "Master",
        "LLMClient",
        "decompose_user_request",
        "PatchEngine",
        "PermissionManager",
        "GhostWireOrchestrator",
        "create_ghostwire_orchestrator",
    ]
except ImportError:
    # If orchestrator is not available, don't break the entire package
    pass
