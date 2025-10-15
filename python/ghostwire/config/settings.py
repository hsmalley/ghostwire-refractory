"""
Configuration settings for GhostWire Refractory
"""

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Host to bind the server to")
    PORT: int = Field(default=8000, description="Port to bind the server to")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Database settings
    DB_PATH: str = Field(default="memory.db", description="Path to SQLite database")
    DB_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DB_POOL_OVERFLOW: int = Field(
        default=10, description="Database connection pool overflow"
    )

    # Vector settings
    EMBED_DIM: int = Field(default=768, description="Dimension of embedding vectors")
    HNSW_MAX_ELEMENTS: int = Field(
        default=100_000, description="Max elements in HNSW index"
    )
    HNSW_EF_CONSTRUCTION: int = Field(
        default=200, description="HNSW construction parameter"
    )
    HNSW_M: int = Field(default=16, description="HNSW parameter M")
    HNSW_EF: int = Field(default=50, description="HNSW parameter EF")

    # Ollama settings
    LOCAL_OLLAMA_URL: str = Field(
        default="http://localhost:11434", description="Local Ollama API URL"
    )
    REMOTE_OLLAMA_URL: str = Field(
        default="http://100.103.237.60:11434", description="Remote Ollama API URL"
    )
    DEFAULT_OLLAMA_MODEL: str = Field(
        default="gemma3:1b", description="Default Ollama model for generation"
    )
    REMOTE_OLLAMA_MODEL: str = Field(
        default="gemma3:12b", description="Remote Ollama model"
    )
    EMBED_MODELS: list[str] = Field(
        default=[
            "embeddinggemma",
            "granite-embedding",
            "nomic-embed-text",
            "mxbai-embed-large",
            "snowflake-arctic-embed",
            "all-minilm",
        ],
        description="List of available embedding models",
    )

    # Summarization settings
    SUMMARY_MODEL: str = Field(
        default="gemma3:1b", description="Model for summarization"
    )
    DISABLE_SUMMARIZATION: bool = Field(
        default=False, description="Disable summarization features"
    )
    SUMMARY_THRESHOLD_CHARS: int = Field(
        default=1000, description="Minimum character count to trigger summarization"
    )
    SUMMARY_MAX_LENGTH_CHARS: int = Field(
        default=50000, description="Maximum character count for summarization"
    )
    SUMMARY_COMPRESSION_RATIO: float = Field(
        default=0.3,
        description="Target compression ratio for summarization (0.1 = 10% of original)",
    )
    SUMMARY_MIN_OUTPUT_LENGTH: int = Field(
        default=100, description="Minimum length of summarized output in characters"
    )
    SUMMARY_MAX_OUTPUT_LENGTH: int = Field(
        default=2000, description="Maximum length of summarized output in characters"
    )

    # Context window optimization settings
    CONTEXT_WINDOW_OPTIMIZATION: bool = Field(
        default=True,
        description="Enable context window optimization to reduce token usage",
    )
    MAX_CONTEXT_TOKENS: int = Field(
        default=2048, description="Maximum tokens to send in context window"
    )
    CONTEXT_COMPRESSION_STRATEGY: str = Field(
        default="recency",
        description="Strategy for context selection (recency, relevance, hybrid)",
    )
    CONTEXT_TRUNCATION_METHOD: str = Field(
        default="sentence",
        description="Method for truncating context (sentence, word, character)",
    )
    MIN_CONTEXT_ITEMS: int = Field(
        default=1, description="Minimum number of context items to include"
    )
    MAX_CONTEXT_ITEMS: int = Field(
        default=10, description="Maximum number of context items to include"
    )

    # CORS settings
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed origins for CORS",
    )

    # Security settings
    SECRET_KEY: str = Field(
        default="your-secret-key-here", description="Secret key for security"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256", description="Algorithm for JWT encoding"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(
        default=100, description="Number of requests allowed"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60, description="Time window in seconds for rate limiting"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str | None = Field(default=None, description="File to write logs to")
    LOG_FORMAT: str = Field(
        default="emoji", description="Logging format: plain, emoji, or json"
    )
    GHOSTWIRE_NO_EMOJI: bool = Field(
        default=False, description="Disable emoji/ANSI logging output (opt-out)"
    )

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


# Create settings instance
def get_settings():
    """Get the settings instance, creating it if necessary."""
    return Settings()


# For backward compatibility, create a global instance
settings = get_settings()
