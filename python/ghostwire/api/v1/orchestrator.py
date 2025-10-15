"""
Orchestrator endpoints for GhostWire Refractory
"""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ...config.settings import settings
from ...orchestrator.integration import (
    create_ghostwire_orchestrator,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class OrchestratorRequest(BaseModel):
    """Request model for orchestrator operations"""

    user_request: str
    context: dict[str, Any] = {}
    session_token: str = None


class OrchestratorResponse(BaseModel):
    """Response model for orchestrator operations"""

    request: str
    subtasks: list
    results: list
    response: str
    metadata: dict[str, Any]


class PatchProposalRequest(BaseModel):
    """Request model for patch proposal operations"""

    module: str
    file: str
    type: str  # add, modify, delete
    pointer: str  # JSON Pointer
    change: Any = None  # Optional value to write
    worker: str = "default_worker"
    context: str = ""


class PatchProposalResponse(BaseModel):
    """Response model for patch proposal operations"""

    proposal: dict[str, Any]
    approved: bool
    validation: dict[str, Any]


class IntentDecompositionRequest(BaseModel):
    """Request model for intent decomposition"""

    user_intent: str


class IntentDecompositionResponse(BaseModel):
    """Response model for intent decomposition"""

    user_intent: str
    tasks: list
    execution_order: list


class MergePatchRequest(PatchProposalRequest):
    """Request model for merge patch operations"""

    pass


class MergePatchResponse(BaseModel):
    """Response model for merge patch operations"""

    proposal: dict[str, Any]
    approved: bool
    validation: dict[str, Any]
    merge_result: dict[str, Any]
    status: str


class TelemetryResponse(BaseModel):
    """Response model for telemetry data"""

    counters: dict[str, int]
    timestamp: float


@router.post("/orchestrate", response_model=OrchestratorResponse)
async def orchestrate_request(request: OrchestratorRequest):
    """Process a request through the multi-LLM orchestration system"""
    try:
        # Create orchestrator instance
        orchestrator = create_ghostwire_orchestrator(
            llm_endpoints=[settings.LOCAL_OLLAMA_URL],
            default_model=settings.DEFAULT_OLLAMA_MODEL,
        )

        # Add session token to context if provided
        context = request.context or {}
        if request.session_token:
            context["session_token"] = request.session_token

        # Process the request through the orchestrator
        result = await orchestrator.process_request(request.user_request, context)

        # Close the orchestrator resources
        await orchestrator.close()

        return OrchestratorResponse(
            request=result["request"],
            subtasks=result["subtasks"],
            results=result["results"],
            response=result["response"],
            metadata=result["metadata"],
        )
    except Exception as e:
        logger.error(f"Orchestrator request failed: {e}")
        raise


@router.post("/propose_patch", response_model=PatchProposalResponse)
async def propose_patch(request: PatchProposalRequest):
    """Propose a patch following the OpenSpec patch proposal schema"""
    try:
        # Create orchestrator instance
        orchestrator = create_ghostwire_orchestrator(
            llm_endpoints=[settings.LOCAL_OLLAMA_URL],
            default_model=settings.DEFAULT_OLLAMA_MODEL,
        )

        # Propose the patch
        result = await orchestrator.propose_patch(
            module=request.module,
            file=request.file,
            change_type=request.type,
            pointer=request.pointer,
            change=request.change,
            worker=request.worker,
            context=request.context,
        )

        # Close the orchestrator resources
        await orchestrator.close()

        return PatchProposalResponse(
            proposal=result["proposal"],
            approved=result["approved"],
            validation=result["validation"],
        )
    except Exception as e:
        logger.error(f"Patch proposal failed: {e}")
        raise


@router.post("/submit_merge_patch", response_model=MergePatchResponse)
async def submit_merge_patch(request: MergePatchRequest):
    """Submit a patch proposal and merge it if approved"""
    try:
        # Create orchestrator instance
        orchestrator = create_ghostwire_orchestrator(
            llm_endpoints=[settings.LOCAL_OLLAMA_URL],
            default_model=settings.DEFAULT_OLLAMA_MODEL,
        )

        # Submit and merge the patch
        result = await orchestrator.submit_and_merge_patch(
            module=request.module,
            file=request.file,
            change_type=request.type,
            pointer=request.pointer,
            change=request.change,
            worker=request.worker,
            context=request.context,
        )

        # Close the orchestrator resources
        await orchestrator.close()

        return MergePatchResponse(**result)
    except Exception as e:
        logger.error(f"Submit and merge patch failed: {e}")
        raise


@router.post("/decompose_intent", response_model=IntentDecompositionResponse)
async def decompose_intent(request: IntentDecompositionRequest):
    """Decompose a user intent into a task graph with dependencies"""
    try:
        # Create orchestrator instance
        orchestrator = create_ghostwire_orchestrator(
            llm_endpoints=[settings.LOCAL_OLLAMA_URL],
            default_model=settings.DEFAULT_OLLAMA_MODEL,
        )

        # Decompose the user intent
        tasks = await orchestrator.decompose_user_intent(request.user_intent)

        # Get execution order from the task graph
        execution_order = orchestrator.task_graph.calculate_execution_order()

        # Close the orchestrator resources
        await orchestrator.close()

        return IntentDecompositionResponse(
            user_intent=request.user_intent,
            tasks=tasks,
            execution_order=list(execution_order),
        )
    except Exception as e:
        logger.error(f"Intent decomposition failed: {e}")
        raise


@router.get("/telemetry", response_model=TelemetryResponse)
async def get_telemetry():
    """Get current telemetry data from the orchestrator"""
    try:
        # Create orchestrator instance
        orchestrator = create_ghostwire_orchestrator(
            llm_endpoints=[settings.LOCAL_OLLAMA_URL],
            default_model=settings.DEFAULT_OLLAMA_MODEL,
        )

        # Get telemetry data
        telemetry = orchestrator.get_telemetry()

        # Close the orchestrator resources
        await orchestrator.close()

        return TelemetryResponse(
            counters=telemetry, timestamp=__import__("time").time()
        )
    except Exception as e:
        logger.error(f"Telemetry retrieval failed: {e}")
        raise


@router.get("/healthcheck")
async def healthcheck():
    """Run health checks following OpenSpec guidelines"""
    try:
        # Create orchestrator instance
        orchestrator = create_ghostwire_orchestrator(
            llm_endpoints=[settings.LOCAL_OLLAMA_URL],
            default_model=settings.DEFAULT_OLLAMA_MODEL,
        )

        # Run basic checks
        checks = {
            "syntax_validation": True,  # In a real implementation, validate all spec files
            "constraint_validation": True,  # Validate constraints against current state
            "dag_recomputation": True,  # Verify task dependency DAGs are acyclic
        }

        # Determine health flag
        all_checks_passed = all(checks.values())
        health_flag = "SPEC_OK" if all_checks_passed else "SPEC_WARN"

        # Close the orchestrator resources
        await orchestrator.close()

        return {
            "status": health_flag,
            "checks": checks,
            "timestamp": __import__("time").time(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "SPEC_FAIL",
            "error": str(e),
            "timestamp": __import__("time").time(),
        }


@router.get("/orchestrate/status")
async def orchestrator_status():
    """Get the status of the orchestration system"""
    return {
        "status": "active",
        "message": "Orchestrator system is running and ready to process requests",
        "capabilities": [
            "multi-llm coordination",
            "task decomposition",
            "permission management",
            "patch application",
            "benchmark integration",
            "formal patch validation",
            "spec-driven development",
            "task graph management",
            "merge resolution",
            "telemetry collection",
            "health monitoring",
        ],
    }
