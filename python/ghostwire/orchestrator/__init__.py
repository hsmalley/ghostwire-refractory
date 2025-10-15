"""
GhostWire Orchestrator - Package Initialization

This package implements the Master, Worker, and Secondary Control model
for coordinating multiple LLMs in the GhostWire Refractory system.
"""

from .decomposition import decompose_user_request
from .integration import (
    GhostWireOrchestrator,
    MergeEngine,
    PatchProposal,
    SecondaryValidator,
    TaskGraph,
    create_ghostwire_orchestrator,
)
from .llm_clients import LLMClient
from .master import Master
from .patch_engine import PatchEngine
from .permission_manager import PermissionManager

__all__ = [
    "Master",
    "LLMClient",
    "decompose_user_request",
    "PatchEngine",
    "PermissionManager",
    "GhostWireOrchestrator",
    "create_ghostwire_orchestrator",
    "PatchProposal",
    "SecondaryValidator",
    "TaskGraph",
    "MergeEngine",
]

__version__ = "1.0.0"
