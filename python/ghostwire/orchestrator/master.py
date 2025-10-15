"""
GhostWire Openspec Orchestrator - Master Component

Implements the Master component of the GhostWire Openspec Orchestrator
that coordinates multiple LLMs using the Master, Worker, and Secondary Control model.
"""

import logging
from typing import Any

from .decomposition import decompose_user_request
from .llm_clients import LLMClient
from .patch_engine import PatchEngine
from .permission_manager import PermissionManager


class Master:
    def __init__(
        self,
        llm_clients: list[LLMClient],
        patch_engine: PatchEngine | None = None,
        permission_manager: PermissionManager | None = None,
    ):
        """
        Initialize the Master orchestrator.

        Args:
            llm_clients: List of LLM client instances to coordinate
            patch_engine: Optional patch engine for code modifications
            permission_manager: Optional permission manager for access control
        """
        self.llm_clients = llm_clients
        self.patch_engine = patch_engine or PatchEngine()
        self.permission_manager = permission_manager or PermissionManager()
        self.logger = logging.getLogger(__name__)

    async def process_request(
        self, user_request: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Process a user request by coordinating multiple LLMs.

        Args:
            user_request: The original user request
            context: Additional context information

        Returns:
            Dict containing the response and metadata
        """
        self.logger.info(f"Processing user request: {user_request}")

        # Decompose the user request into subtasks
        subtasks = decompose_user_request(user_request)
        self.logger.info(f"Decomposed request into {len(subtasks)} subtasks")

        # Validate permissions for each subtask
        for task in subtasks:
            if not self.permission_manager.check_permission(task, context):
                raise PermissionError(f"Permission denied for task: {task}")

        # Execute subtasks using available LLMs
        results = []
        for i, task in enumerate(subtasks):
            # Select an appropriate LLM client based on task requirements
            llm_client = self._select_llm_client(task)

            # Execute the task
            result = await llm_client.execute_task(task, context)
            results.append({"task_id": i, "task": task, "result": result})

            self.logger.info(f"Completed subtask {i + 1}/{len(subtasks)}")

        # Combine results and generate final response
        final_response = await self._compile_results(results, user_request)

        return {
            "request": user_request,
            "subtasks": subtasks,
            "results": results,
            "response": final_response,
            "metadata": {
                "num_tasks": len(subtasks),
                "num_llms_used": len(self.llm_clients),
            },
        }

    def _select_llm_client(self, task: dict[str, Any]) -> LLMClient:
        """
        Select an appropriate LLM client based on the task requirements.

        Args:
            task: The task to be executed

        Returns:
            An appropriate LLMClient instance
        """
        # For now, use a simple round-robin selection
        # In the future, this could be more sophisticated based on task type
        client_id = hash(str(task)) % len(self.llm_clients)
        return self.llm_clients[client_id]

    async def _compile_results(self, results: list[dict], original_request: str) -> str:
        """
        Compile individual task results into a final response.

        Args:
            results: List of results from subtask execution
            original_request: The original user request

        Returns:
            Compiled final response
        """
        # For now, simply concatenate results with context
        # In a more sophisticated system, this would involve synthesis
        compiled_parts = []

        for result in results:
            if isinstance(result["result"], str):
                compiled_parts.append(result["result"])
            elif isinstance(result["result"], dict):
                compiled_parts.append(str(result["result"]))

        final_response = " ".join(compiled_parts)

        # Contextualize the response based on the original request
        return f"Based on your request '{original_request}', here are the results: {final_response}"
