"""GhostWire utilities package"""

from .context_optimizer import estimate_token_count, optimize_context_window
from .error_handling import handle_api_error
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
        GhostWireOrchestrator,
        PatchProposal,
        SecondaryValidator,
        create_ghostwire_orchestrator,
        decompose_user_request,
    )

    HAS_ORCHESTRATOR = True
except ImportError:
    # Orchestrator may not be available in all deployments
    HAS_ORCHESTRATOR = False

__all__ = [
    "optimize_context_window",
    "estimate_token_count",
    "handle_api_error",
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
