"""
Context window optimization utilities for GhostWire Refractory
"""

import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for a text string.
    This is a simple estimation - in practice, you'd use the tokenizer for the specific model.
    """
    # Rough estimation: 1 token ≈ 4 characters or 0.75 words
    char_count = len(text)
    word_count = len(text.split())

    # Average of character-based and word-based estimation
    char_tokens = char_count / 4
    word_tokens = word_count / 0.75

    estimated_tokens = int((char_tokens + word_tokens) / 2)
    return max(1, estimated_tokens)


def truncate_text_to_tokens(text: str, max_tokens: int) -> str:
    """
    Truncate text to fit within a maximum token count.
    """
    if max_tokens <= 0:
        return ""

    current_tokens = estimate_token_count(text)
    if current_tokens <= max_tokens:
        return text

    # Simple truncation by character ratio
    ratio = max_tokens / current_tokens
    target_chars = int(len(text) * ratio * 0.9)  # 0.9 for safety margin

    # Truncate at sentence boundaries if possible
    truncated = text[:target_chars]

    # Try to find a sentence boundary
    last_period = truncated.rfind(". ")
    last_exclamation = truncated.rfind("! ")
    last_question = truncated.rfind("? ")

    sentence_end = max(last_period, last_exclamation, last_question)

    if sentence_end > int(target_chars * 0.7):  # If we have a reasonable sentence
        truncated = truncated[: sentence_end + 1]

    return truncated


def optimize_context_window(
    contexts: list[str], max_tokens: int = None, strategy: str = None
) -> list[str]:
    """
    Optimize context window by selecting and truncating contexts to fit within token limits.

    Args:
        contexts: List of context strings to optimize
        max_tokens: Maximum tokens allowed in context window
        strategy: Strategy for context selection ('recency', 'relevance', 'hybrid')

    Returns:
        List of optimized context strings
    """
    max_tokens = max_tokens or settings.MAX_CONTEXT_TOKENS
    strategy = strategy or settings.CONTEXT_COMPRESSION_STRATEGY

    if not contexts:
        return []

    if not settings.CONTEXT_WINDOW_OPTIMIZATION:
        logger.info("Context window optimization disabled, returning original contexts")
        return contexts[: settings.MAX_CONTEXT_ITEMS]

    logger.info(
        f"Optimizing context window with {len(contexts)} contexts, max {max_tokens} tokens"
    )

    # Apply strategy for context selection
    if strategy == "recency":
        # Most recent contexts first (they're already ordered by timestamp in retrieval)
        selected_contexts = contexts[: settings.MAX_CONTEXT_ITEMS]
    elif strategy == "relevance":
        # Most relevant contexts first (they're already ordered by similarity)
        selected_contexts = contexts[: settings.MAX_CONTEXT_ITEMS]
    else:  # hybrid
        # Mix of most recent and most relevant
        if (
            len(contexts) <= settings.MIN_CONTEXT_ITEMS
            or len(contexts) <= settings.MAX_CONTEXT_ITEMS
        ):
            selected_contexts = contexts
        else:
            # Take a mix - most relevant + some recent
            half_max = settings.MAX_CONTEXT_ITEMS // 2
            selected_contexts = contexts[:half_max]  # Most relevant
            # Add some recent ones (more diverse)
            recent_contexts = (
                contexts[-half_max:] if len(contexts) > half_max else contexts
            )
            # Combine and deduplicate
            seen = set()
            combined = []
            for ctx in selected_contexts + recent_contexts:
                if ctx not in seen:
                    combined.append(ctx)
                    seen.add(ctx)
            selected_contexts = combined[: settings.MAX_CONTEXT_ITEMS]

    # Ensure minimum context items
    if len(selected_contexts) < settings.MIN_CONTEXT_ITEMS and contexts:
        selected_contexts = contexts[: settings.MIN_CONTEXT_ITEMS]

    # Optimize each context for token usage
    optimized_contexts = []
    remaining_tokens = max_tokens

    for context in selected_contexts:
        if remaining_tokens <= 0:
            break

        # Estimate current context token usage
        context_tokens = estimate_token_count(context)

        if context_tokens <= remaining_tokens:
            # Context fits completely
            optimized_contexts.append(context)
            remaining_tokens -= context_tokens
        else:
            # Need to truncate context
            truncated_context = truncate_text_to_tokens(context, remaining_tokens)
            if (
                truncated_context and len(truncated_context) > 50
            ):  # Minimum sensible length
                optimized_contexts.append(truncated_context)
                remaining_tokens = 0
            # If truncated context is too short, skip it

    logger.info(
        f"Optimized context window: {len(optimized_contexts)} contexts, "
        f"estimated {max_tokens - remaining_tokens} tokens used"
    )

    return optimized_contexts


def format_optimized_context(contexts: list[str]) -> str:
    """
    Format optimized contexts into a single context string for the prompt.
    """
    if not contexts:
        return ""

    # Join contexts with separators
    context_snippets = " | ".join(contexts)
    return f"Relevant prior notes: {context_snippets}\n\n"
