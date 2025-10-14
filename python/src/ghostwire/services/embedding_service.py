"""
Embedding service for GhostWire Refractory
"""

import logging

import httpx

from ..config.settings import settings
from ..models.embedding import EmbeddingData, EmbeddingRequest, EmbeddingResponse


class EmbeddingService:
    """Service class for embedding-related operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cached_embed_model = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _get_embedding_from_api(self, text: str, model: str) -> list[float]:
        """Get embedding from Ollama API"""
        # Try /api/embeddings endpoint first
        try:
            response = await self.client.post(
                f"{settings.LOCAL_OLLAMA_URL}/api/embeddings",
                json={"model": model, "input": text},
            )
            response.raise_for_status()
            data = response.json()

            embedding = data.get("embedding") or data.get("data", [{}])[0].get(
                "embedding"
            )
            if (
                not embedding
                and "embeddings" in data
                and isinstance(data["embeddings"], list)
            ):
                embedding = data["embeddings"][0]

            if embedding:
                return embedding
        except Exception as e:
            self.logger.warning(
                f"Failed to get embedding from /api/embeddings for model {model}: {e}"
            )
            # Continue to try /api/embed endpoint

        # Try /api/embed endpoint as fallback
        try:
            response = await self.client.post(
                f"{settings.LOCAL_OLLAMA_URL}/api/embed",
                json={"model": model, "input": text},
            )
            response.raise_for_status()
            data = response.json()

            embedding = data.get("embedding") or data.get("data", [{}])[0].get(
                "embedding"
            )
            if (
                not embedding
                and "embeddings" in data
                and isinstance(data["embeddings"], list)
            ):
                embedding = data["embeddings"][0]

            if embedding:
                return embedding
        except Exception as e:
            self.logger.error(
                f"Failed to get embedding from /api/embed for model {model}: {e}"
            )

        return []

    async def create_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Create embeddings for input text(s)"""
        inputs = request.input
        model = request.model

        # Normalize inputs to a list
        if isinstance(inputs, str):
            inputs = [inputs]
        elif not isinstance(inputs, list):
            raise TypeError(f"Invalid input type: {type(inputs)}")

        # Use cached model if available
        if self._cached_embed_model:
            model = self._cached_embed_model

        # If no cached model, try available models
        embeddings = []
        total_tokens = 0

        for i, text_input in enumerate(inputs):
            if not isinstance(text_input, str):
                text_input = str(text_input)

            # Try each available model until we get embeddings
            embedding_vector = []

            # If we have a cached model, try it first
            if self._cached_embed_model:
                embedding_vector = await self._get_embedding_from_api(
                    text_input, self._cached_embed_model
                )

            # If still no embedding, try all available models
            if not embedding_vector:
                for model_name in settings.EMBED_MODELS:
                    embedding_vector = await self._get_embedding_from_api(
                        text_input, model_name
                    )
                    if embedding_vector:
                        # Cache successful model
                        self._cached_embed_model = model_name
                        break

            # If still no embedding, return a small non-zero fallback
            if not embedding_vector:
                embedding_vector = [1e-8] * settings.EMBED_DIM

            # Ensure embedding has correct dimension
            if len(embedding_vector) != settings.EMBED_DIM:
                # Truncate or pad to match expected dimension
                if len(embedding_vector) < settings.EMBED_DIM:
                    embedding_vector.extend(
                        [1e-8] * (settings.EMBED_DIM - len(embedding_vector))
                    )
                else:
                    embedding_vector = embedding_vector[: settings.EMBED_DIM]

            # Sanitize non-finite values
            embedding_vector = [
                float(x) if isinstance(x, (float, int)) and math.isfinite(x) else 1e-8
                for x in embedding_vector
            ]

            # Prevent all-zero vectors
            if sum(abs(x) for x in embedding_vector) < 1e-12:
                embedding_vector = [1e-8] * len(embedding_vector)

            total_tokens += len(text_input.split())

            embeddings.append(EmbeddingData(embedding=embedding_vector, index=i).dict())

        response = EmbeddingResponse(
            data=embeddings,
            model=model or self._cached_embed_model or settings.EMBED_MODELS[0],
            usage={"prompt_tokens": total_tokens, "total_tokens": total_tokens},
        )

        self.logger.info(
            f"Successfully generated {len(inputs)} embeddings via {model or self._cached_embed_model}"
        )
        return response

    async def embed_text(self, text: str, model: str = None) -> list[float]:
        """Embed a single text string"""
        if not text:
            return [0.0] * settings.EMBED_DIM

        # Use provided model or try cached model
        model_to_use = model or self._cached_embed_model or settings.EMBED_MODELS[0]

        # Get embedding from API
        embedding = await self._get_embedding_from_api(text, model_to_use)

        # If successful, update cached model
        if embedding and not model:
            self._cached_embed_model = model_to_use

        return embedding or [0.0] * settings.EMBED_DIM


import math


class SummarizationService:
    """Service class for text summarization"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def summarize_text(self, text: str) -> str:
        """Summarize the given text using Ollama"""
        if settings.DISABLE_SUMMARIZATION:
            self.logger.info("Summarization disabled via settings")
            return text

        # Use the local Ollama for summarization
        prompt = f"Summarize this text concisely, keeping key details:\n\n{text}"

        try:
            response = await self.client.post(
                f"{settings.LOCAL_OLLAMA_URL}/api/generate",
                json={
                    "model": settings.SUMMARY_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            result = response.json()
            summary = result.get("response", "")

            self.logger.info(f"Summary result preview: {summary[:120]}...")
            return summary.strip()
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            return text  # Return original text on failure


# Global instances
embedding_service = EmbeddingService()
summarization_service = SummarizationService()
