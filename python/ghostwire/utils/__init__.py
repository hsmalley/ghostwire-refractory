"""GhostWire utilities package"""

from .context_optimizer import estimate_token_count, optimize_context_window
from .error_handling import handle_exception
from .ghostwire_scoring import (
    compute_comprehensive_ghostwire_score,
    compute_general_ghostwire_score,
    compute_rag_ghostwire_score,
    compute_retrieval_ghostwire_score,
    compute_summarization_ghostwire_score,
    format_benchmark_results_with_scores,
)

# Import orchestrator-related utilities if available
try:
    from ..orchestrator import (
        GhostWireOrchestrator,  # noqa: F401
        PatchProposal,  # noqa: F401
        SecondaryValidator,  # noqa: F401
        create_ghostwire_orchestrator,  # noqa: F401
        decompose_user_request,  # noqa: F401
    )

    HAS_ORCHESTRATOR = True
except ImportError:
    # Orchestrator may not be available in all deployments
    HAS_ORCHESTRATOR = False

__all__ = [
    "optimize_context_window",
    "estimate_token_count",
    "handle_exception",
    "compute_general_ghostwire_score",
    "compute_rag_ghostwire_score",
    "compute_retrieval_ghostwire_score",
    "compute_summarization_ghostwire_score",
    "compute_comprehensive_ghostwire_score",
    "format_benchmark_results_with_scores",
]

# Add orchestrator components if available
if HAS_ORCHESTRATOR:
    __all__.extend(
        [
            "decompose_user_request",
            "GhostWireOrchestrator",
            "create_ghostwire_orchestrator",
            "PatchProposal",
            "SecondaryValidator",
        ]
    )
