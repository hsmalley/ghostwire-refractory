"""
RAG (Retrieval-Augmented Generation) service for GhostWire Refractory
"""

import json
import logging
from collections.abc import AsyncGenerator

import httpx

from ..config.settings import settings
from ..models.memory import MemoryQuery
from ..services.embedding_service import embedding_service
from ..services.memory_service import memory_service


class RAGService:
    """Service class for RAG operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = httpx.AsyncClient(timeout=60.0)

    async def retrieve_context(
        self, session_id: str, query: str, top_k: int = 5
    ) -> list[str]:
        """Retrieve relevant context from memory based on the query"""
        try:
            # Generate embedding for the query
            query_embedding = await embedding_service.embed_text(query)
            if not query_embedding:
                raise Exception("Failed to generate embedding for query")

            # Query similar memories
            query_obj = MemoryQuery(
                session_id=session_id, embedding=query_embedding, limit=top_k
            )
            memories = memory_service.query_similar_memories(query_obj)

            # Extract prompt texts as context
            contexts = [m.prompt_text for m in memories]
            self.logger.info(
                f"Retrieved {len(contexts)} contexts for session {session_id}"
            )
            return contexts
        except Exception as e:
            self.logger.error(f"Retrieval failed: {e}")
            raise

    async def generate_response(
        self, prompt: str, model: str = None, stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """Generate a response using Ollama"""
        model = model or settings.DEFAULT_OLLAMA_MODEL

        # Determine if we're using remote or local Ollama
        use_remote = model.startswith("remote-") or model.endswith(":remote")
        actual_model = (
            model.removeprefix("remote-")
            .removeprefix("local-")
            .removesuffix(":remote")
            .removesuffix(":local")
        )

        target_url = (
            f"{settings.REMOTE_OLLAMA_URL}/api/generate"
            if use_remote
            else f"{settings.LOCAL_OLLAMA_URL}/api/generate"
        )

        try:
            payload = {"model": actual_model, "prompt": prompt, "stream": stream}

            response = await self.client.post(target_url, json=payload)
            response.raise_for_status()

            if stream:
                # Handle streaming response
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        chunk = obj.get("response") or (
                            obj.get("message", {}) or {}
                        ).get("content")

                        if chunk:
                            yield chunk

                        if obj.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
            else:
                # Handle non-streaming response
                result = response.json()
                yield result.get("response", "")
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            yield f"[ERROR] Generation failed: {e}"

    async def rag_query(
        self,
        session_id: str,
        query: str,
        model: str = None,
        top_k: int = 5,
        stream: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Perform a complete RAG query with context retrieval and response generation"""
        try:
            # Retrieve relevant context
            contexts = await self.retrieve_context(session_id, query, top_k)

            # Build full prompt with context
            context_text = ""
            if contexts:
                context_snippets = " | ".join(contexts[:3])  # Use top 3 contexts
                context_text = f"Relevant prior notes: {context_snippets}\n\n"

            full_prompt = f"{context_text}User: {query}\n\nAssistant:"

            # Generate and return response
            async for token in self.generate_response(full_prompt, model, stream):
                yield token
        except Exception as e:
            self.logger.error(f"RAG query failed: {e}")
            yield f"[ERROR] RAG query failed: {e}"


# Global instance
rag_service = RAGService()
