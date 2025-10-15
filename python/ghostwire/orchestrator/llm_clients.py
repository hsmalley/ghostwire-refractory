"""
GhostWire Openspec Orchestrator - LLM Client

Implements the LLM Client component that can interact with various LLM services.
"""

import logging
from typing import Any

import httpx


class LLMClient:
    def __init__(
        self,
        name: str,
        endpoint: str,
        api_key: str | None = None,
        model: str = "gemma3:1b",
        timeout: int = 30,
    ):
        """
        Initialize an LLM client.

        Args:
            name: Name identifier for this client
            endpoint: API endpoint URL
            api_key: API key for authentication (if required)
            model: Model to use for generation
            timeout: Request timeout in seconds
        """
        self.name = name
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.logger = logging.getLogger(__name__)

    async def execute_task(
        self, task: dict[str, Any], context: dict[str, Any] | None = None
    ) -> Any:
        """
        Execute a specific task using this LLM client.

        Args:
            task: The task to execute
            context: Additional context information

        Returns:
            Result of the task execution
        """
        self.logger.info(
            f"Executing task on {self.name}: {task.get('description', 'unknown')}"
        )

        # Determine the type of operation based on the task
        task_type = task.get("type", "chat")

        if task_type == "chat":
            return await self._chat_completion(task, context)
        elif task_type == "embed":
            return await self._embed_text(task, context)
        elif task_type == "summarize":
            return await self._summarize_text(task, context)
        else:
            # Default to chat completion for unrecognized types
            return await self._chat_completion(task, context)

    async def _chat_completion(
        self, task: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Perform a chat completion task.

        Args:
            task: The chat task to execute
            context: Additional context information

        Returns:
            Chat completion result
        """
        prompt = task.get("prompt", task.get("content", ""))

        # Add context if available
        if context:
            context_str = str(context)
            prompt = f"Context: {context_str}\n\nTask: {prompt}"

        # Prepare the request payload
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }

        try:
            response = await self.client.post(
                f"{self.endpoint}/api/generate",  # Standard Ollama endpoint
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()

            data = response.json()
            return {
                "response": data.get("response", ""),
                "model": data.get("model", self.model),
                "total_duration": data.get("total_duration", 0),
                "load_duration": data.get("load_duration", 0),
            }
        except Exception as e:
            self.logger.error(f"Chat completion failed for {self.name}: {e}")
            return {"error": str(e), "response": ""}

    async def _embed_text(
        self, task: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Generate embeddings for text.

        Args:
            task: The embedding task to execute
            context: Additional context information

        Returns:
            Embedding result
        """
        input_text = task.get("input", task.get("text", ""))

        # Prepare the request payload
        payload = {"model": self.model, "prompt": input_text}

        try:
            response = await self.client.post(
                f"{self.endpoint}/api/embeddings",
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()

            data = response.json()
            return {
                "embedding": data.get("embedding", []),
                "model": data.get("model", self.model),
            }
        except Exception as e:
            self.logger.error(f"Embedding generation failed for {self.name}: {e}")
            return {"error": str(e), "embedding": []}

    async def _summarize_text(
        self, task: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Summarize text using the LLM.

        Args:
            task: The summarization task to execute
            context: Additional context information

        Returns:
            Summarization result
        """
        text_to_summarize = task.get("text", "")
        prompt = f"Please summarize the following text:\n\n{text_to_summarize}"

        # Add requirements if specified
        if "requirements" in task:
            prompt += f"\n\nRequirements: {task['requirements']}"

        return await self._chat_completion({"prompt": prompt}, context)

    def _get_headers(self) -> dict[str, str]:
        """
        Get the appropriate headers for API requests.

        Returns:
            Dictionary of headers
        """
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
