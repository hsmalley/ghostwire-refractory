"""
Unit tests for GhostWire Refractory - Context Optimizer
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from python.ghostwire.utils.context_optimizer import (
    estimate_token_count,
    format_optimized_context,
    optimize_context_window,
    truncate_text_to_tokens,
)


class TestContextOptimizer:
    def test_estimate_token_count_short_text(self):
        """Test token estimation for short text"""
        text = "Hello world"
        tokens = estimate_token_count(text)
        assert isinstance(tokens, int)
        assert tokens > 0
        assert tokens < 10  # Should be very few tokens for short text

    def test_estimate_token_count_longer_text(self):
        """Test token estimation for longer text"""
        text = "The quick brown fox jumps over the lazy dog. " * 10  # 440 chars
        tokens = estimate_token_count(text)
        assert isinstance(tokens, int)
        assert tokens > 0
        # Roughly estimate: 440 chars / 4 = ~110 tokens, but we're estimating so allow variance
        assert tokens > 50
        assert tokens < 200

    def test_truncate_text_to_tokens_no_truncation_needed(self):
        """Test truncation when no truncation is needed"""
        text = "Short text"
        max_tokens = 100
        truncated = truncate_text_to_tokens(text, max_tokens)
        assert truncated == text

    def test_truncate_text_to_tokens_truncation(self):
        """Test truncation when text exceeds token limit"""
        text = "The quick brown fox jumps over the lazy dog. " * 50  # Very long text
        max_tokens = 10
        truncated = truncate_text_to_tokens(text, max_tokens)
        assert len(truncated) < len(text)
        assert len(truncated) > 0  # Should not be empty

    def test_truncate_text_to_zero_tokens(self):
        """Test truncation to zero tokens"""
        text = "Some text"
        max_tokens = 0
        truncated = truncate_text_to_tokens(text, max_tokens)
        assert truncated == ""

    def test_optimize_context_window_empty_contexts(self):
        """Test optimization with empty contexts"""
        contexts = []
        optimized = optimize_context_window(contexts)
        assert optimized == []

    def test_optimize_context_window_single_context(self):
        """Test optimization with single context"""
        contexts = ["This is a single context."]
        optimized = optimize_context_window(contexts)
        assert len(optimized) == 1
        assert optimized[0] == contexts[0]

    def test_optimize_context_window_multiple_contexts(self):
        """Test optimization with multiple contexts"""
        contexts = [
            "First context with some information.",
            "Second context with more details.",
            "Third context with additional data.",
        ]
        optimized = optimize_context_window(contexts)
        assert len(optimized) <= len(contexts)
        assert isinstance(optimized, list)

    def test_optimize_context_window_token_limit(self):
        """Test optimization with token limit"""
        contexts = [
            "This is a fairly long context that should consume several tokens when processed properly.",
            "Another long context with lots of information that needs to be handled efficiently.",
            "Yet another context that contributes to the overall token count significantly.",
        ]
        max_tokens = 50
        optimized = optimize_context_window(contexts, max_tokens=max_tokens)
        assert len(optimized) <= len(contexts)
        # Verify that contexts are returned (even if truncated)
        assert isinstance(optimized, list)

    def test_format_optimized_context_empty_contexts(self):
        """Test formatting with empty contexts"""
        contexts = []
        formatted = format_optimized_context(contexts)
        assert formatted == ""

    def test_format_optimized_context_single_context(self):
        """Test formatting with single context"""
        contexts = ["Single context."]
        formatted = format_optimized_context(contexts)
        assert "Single context." in formatted
        assert formatted.startswith("Relevant prior notes:")

    def test_format_optimized_context_multiple_contexts(self):
        """Test formatting with multiple contexts"""
        contexts = ["First context.", "Second context.", "Third context."]
        formatted = format_optimized_context(contexts)
        assert "First context." in formatted
        assert "Second context." in formatted
        assert "Third context." in formatted
        assert " | " in formatted  # Contexts should be joined with separators
        assert formatted.startswith("Relevant prior notes:")
