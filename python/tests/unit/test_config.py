"""
Unit tests for GhostWire Refractory - Configuration
"""
import pytest
from unittest.mock import patch
from src.ghostwire.config.settings import Settings


def test_settings_defaults():
    """Test that settings have proper defaults"""
    settings = Settings()
    
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.EMBED_DIM == 768
    assert settings.DB_PATH == "memory.db"
    
    # Check that embed models list is not empty
    assert len(settings.EMBED_MODELS) > 0
    assert "nomic-embed-text" in settings.EMBED_MODELS


@patch.dict("os.environ", {"EMBED_DIM": "1024", "DB_PATH": "/tmp/test.db"})
def test_settings_from_environment():
    """Test that settings can be overridden by environment variables"""
    settings = Settings()
    
    assert settings.EMBED_DIM == 1024
    assert settings.DB_PATH == "/tmp/test.db"