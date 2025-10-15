"""
GhostWire Openspec Orchestrator - Task Decomposition

Implements request decomposition logic to break down user requests into subtasks
that can be handled by different LLMs in the orchestration system.
"""

import logging
import re
from typing import Any


def decompose_user_request(req: str) -> list[dict[str, Any]]:
    """
    Decompose a user request into subtasks that can be distributed among LLMs.

    Args:
        req: The original user request

    Returns:
        List of subtasks to be executed
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Decomposing user request: {req}")

    # Identify the type of request and decompose accordingly
    req_lower = req.lower()

    subtasks = []

    # Add the original request as a primary task
    subtasks.append(
        {
            "type": "analysis",
            "description": f"Analyze and understand the user request: {req}",
            "priority": "high",
            "content": req,
        }
    )

    # Identify and add specific subtasks based on keywords
    if any(keyword in req_lower for keyword in ["embed", "embedding", "vector"]):
        # Request involves embeddings
        subtasks.append(
            {
                "type": "embed",
                "description": f"Generate embeddings for relevant text in request: {req}",
                "priority": "medium",
                "input": _extract_text_for_embedding(req),
            }
        )

    if any(
        keyword in req_lower for keyword in ["summarize", "summary", "summarization"]
    ):
        # Request involves summarization
        subtasks.append(
            {
                "type": "summarize",
                "description": f"Summarize the relevant content based on request: {req}",
                "priority": "medium",
                "text": _extract_text_for_summarization(req),
            }
        )

    if any(keyword in req_lower for keyword in ["find", "search", "retrieve", "query"]):
        # Request involves search/retrieval
        subtasks.append(
            {
                "type": "retrieval",
                "description": f"Retrieve relevant information for request: {req}",
                "priority": "high",
                "query": req,
            }
        )

    # If no specific keywords matched, create a general processing task
    if len(subtasks) == 1:  # Only the original analysis task
        subtasks.append(
            {
                "type": "chat",
                "description": f"Process the request conversationally: {req}",
                "priority": "medium",
                "prompt": req,
            }
        )

    # Add any code-related tasks if detected
    if any(
        keyword in req_lower
        for keyword in ["code", "implement", "function", "method", "class", "api"]
    ):
        subtasks.append(
            {
                "type": "code_generation",
                "description": f"Generate code based on request: {req}",
                "priority": "high",
                "requirement": req,
            }
        )

    # Add benchmark-related tasks if detected
    if any(
        keyword in req_lower
        for keyword in ["benchmark", "performance", "speed", "test"]
    ):
        subtasks.append(
            {
                "type": "benchmark",
                "description": f"Run performance benchmarks related to request: {req}",
                "priority": "medium",
                "benchmark_type": _identify_benchmark_type(req),
            }
        )

    logger.info(f"Decomposed into {len(subtasks)} subtasks")
    return subtasks


def _extract_text_for_embedding(req: str) -> str:
    """Extract text that should be embedded from a request."""
    # Look for text that follows keywords like "embed" or "vectorize"
    patterns = [
        r"embed\s+(?:the\s+)?(.+?)(?:\s+with|\s+using|$)",
        r"vectorize\s+(?:the\s+)?(.+?)(?:\s+with|\s+using|$)",
        r"generate\s+embedding\s+for\s+(?:the\s+)?(.+?)(?:\s+with|\s+using|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, req, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If no specific pattern matches, return the whole request
    return req


def _extract_text_for_summarization(req: str) -> str:
    """Extract text that should be summarized from a request."""
    # Look for text that follows keywords like "summarize"
    patterns = [
        r"summarize\s+(?:the\s+)?(.+?)(?:\s+with|\s+using|\s+to|$)",
        r"summary\s+of\s+(?:the\s+)?(.+?)(?:\s+with|\s+using|\s+to|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, req, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If no specific pattern matches, return the whole request
    return req


def _identify_benchmark_type(req: str) -> str:
    """Identify the type of benchmark requested."""
    req_lower = req.lower()

    if "embedding" in req_lower:
        return "embedding"
    elif "rag" in req_lower or "retrieval" in req_lower:
        return "rag"
    elif "summarization" in req_lower or "summary" in req_lower:
        return "summarization"
    elif "model" in req_lower and "compare" in req_lower:
        return "model_comparison"
    else:
        return "general"
