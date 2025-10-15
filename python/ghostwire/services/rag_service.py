"""
RAG (Retrieval-Augmented Generation) service for GhostWire Refractory
"""

import json
import logging
from collections.abc import AsyncGenerator

import httpx

from ..config.settings import settings
from ..models.memory import MemoryQuery
from ..services.cache_service import cache_service
from ..services.embedding_service import embedding_service
from ..services.memory_service import memory_service
from ..utils.context_optimizer import format_optimized_context, optimize_context_window


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
        use_cache: bool = True,
        cache_similarity_threshold: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """Perform a complete RAG query with context retrieval and
        response generation, with optional caching to reduce token usage"""
        try:
            # Generate embedding for the query to use for caching
            query_embedding = await embedding_service.embed_text(query)
            if not query_embedding:
                self.logger.error("Failed to generate embedding for caching")
                use_cache = False  # Can't cache without embedding

            # Try to get exact cached response first (most efficient)
            exact_cached_result = None
            if use_cache:
                exact_cached_result = cache_service.get_exact_response(
                    session_id, query
                )

            if exact_cached_result:
                # Return exact cached response (fastest path)
                self.logger.info("Returning exact cached response for repeated request")
                response = exact_cached_result["response"]
                if stream:
                    # Stream the cached response
                    for i in range(0, len(response), 10):  # Stream in chunks
                        yield response[i : i + 10]
                else:
                    yield response
                return

            # Try to get cached response based on similarity if exact match not found
            cached_result = None
            if use_cache and query_embedding:
                cached_result = cache_service.get_cached_response(
                    session_id, query, query_embedding, cache_similarity_threshold
                )

            if cached_result:
                # Return cached response
                response = cached_result["response"]
                if stream:
                    # Stream the cached response
                    for i in range(0, len(response), 10):  # Stream in chunks
                        yield response[i : i + 10]
                else:
                    yield response
                return

            # Retrieve relevant context (this is the expensive part we want to optimize)
            contexts = await self.retrieve_context(session_id, query, top_k)

            # Optimize context window to reduce token usage
            optimized_contexts = optimize_context_window(contexts)

            # Build full prompt with optimized context
            context_text = format_optimized_context(optimized_contexts)

            full_prompt = f"{context_text}User: {query}\n\nAssistant:"

            # Generate response
            response_parts = []
            async for token in self.generate_response(full_prompt, model, stream=False):
                response_parts.append(token)

            complete_response = "".join(response_parts)

            # Cache the response for similar future queries
            if use_cache and query_embedding:
                cache_service.cache_response(
                    session_id=session_id,
                    query=query,
                    query_embedding=query_embedding,
                    response=complete_response,
                    context=context_text if context_text else None,
                    similarity_threshold=cache_similarity_threshold,
                )

                # Also cache exact response for repeated requests (higher efficiency)
                cache_service.cache_exact_response(
                    session_id=session_id,
                    query=query,
                    response=complete_response,
                    context=context_text if context_text else None,
                )

            # Stream the response if requested
            if stream:
                for i in range(0, len(complete_response), 10):  # Stream in chunks
                    yield complete_response[i : i + 10]
            else:
                yield complete_response
        except Exception as e:
            self.logger.error(f"RAG query failed: {e}")
            yield f"[ERROR] RAG query failed: {e}"


# Global instance
rag_service = RAGService()
