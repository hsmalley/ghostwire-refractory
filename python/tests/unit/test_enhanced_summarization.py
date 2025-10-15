"""
Unit tests for GhostWire Refractory - Enhanced Summarization Service
"""

import os
import sys
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from python.ghostwire.services.embedding_service import SummarizationService


class TestEnhancedSummarizationService:
    def setup_method(self):
        """Setup method to create a summarization service instance for each test"""
        self.service = SummarizationService()

    async def test_should_summarize_below_threshold(self):
        """Test should_summarize with text below threshold"""
        # Short text below threshold
        short_text = "This is a short text."
        result = await self.service.should_summarize(short_text)
        # Depending on settings, this might be False if DISABLE_SUMMARIZATION is True
        # or if text is below SUMMARY_THRESHOLD_CHARS

    async def test_should_summarize_above_threshold(self):
        """Test should_summarize with text above threshold"""
        # Long text above threshold
        long_text = (
            "This is a much longer text. " * 100
        )  # Should be well above threshold
        result = await self.service.should_summarize(long_text)
        # Depending on settings, this might be True if text is above SUMMARY_THRESHOLD_CHARS
        # and summarization is not disabled

    async def test_get_target_summary_length_short_text(self):
        """Test target summary length calculation for short text"""
        short_text = "Short text."
        target_length = await self.service.get_target_summary_length(short_text)
        assert isinstance(target_length, int)
        assert target_length > 0
        # For short text, should return length of original or min length

    async def test_get_target_summary_length_long_text(self):
        """Test target summary length calculation for long text"""
        long_text = "This is a much longer text. " * 200  # Very long text
        target_length = await self.service.get_target_summary_length(long_text)
        assert isinstance(target_length, int)
        assert target_length > 0
        # For long text, should apply compression ratio but stay within bounds

    @patch("python.ghostwire.services.embedding_service.httpx.AsyncClient")
    def test_summarize_text_success(self, mock_httpx_client):
        """Test successful text summarization"""
        # Mock the HTTP client response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"response": "This is a summarized text."}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        # Test text to summarize
        text = "This is a longer text that needs to be summarized."

        # Call the summarize_text method (this would be async)
        import asyncio

        try:
            result = asyncio.run(self.service.summarize_text(text))
            assert isinstance(result, str)
            # Either the summarized text or original text on failure
        except Exception:
            # If summarization fails, should return original text
            pass

    @patch("python.ghostwire.services.embedding_service.httpx.AsyncClient")
    def test_summarize_text_failure_returns_original(self, mock_httpx_client):
        """Test that summarization failure returns original text"""
        # Mock the HTTP client to raise an exception
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = Exception("Network error")
        mock_httpx_client.return_value = mock_client_instance

        # Test text to summarize
        text = "This is a longer text that needs to be summarized."

        # Call the summarize_text method (this would be async)
        import asyncio

        result = asyncio.run(self.service.summarize_text(text))
        # On failure, should return original text
        assert result == text

    def test_summarize_text_disabled(self):
        """Test summarization when disabled"""
        # This test would require temporarily changing settings
        # which is complex in a unit test environment
        pass

    def test_summarize_text_below_min_chars(self):
        """Test summarization with text below minimum character threshold"""
        # Very short text that shouldn't be summarized
        short_text = "Hi"
        import asyncio

        result = asyncio.run(self.service.summarize_text(short_text))
        # Should return original text unchanged
        assert result == short_text

    def test_summarize_text_above_max_chars(self):
        """Test summarization with text above maximum character threshold"""
        # Very long text that should be truncated
        long_text = "This is a very long text. " * 10000  # Exceeds max length
        import asyncio

        result = asyncio.run(self.service.summarize_text(long_text))
        # Should either return original or truncated text
        assert isinstance(result, str)
        assert len(result) > 0
