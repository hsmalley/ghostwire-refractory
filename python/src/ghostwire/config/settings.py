"""
Configuration settings for GhostWire Refractory
"""
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Host to bind the server to")
    PORT: int = Field(default=8000, description="Port to bind the server to")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Database settings
    DB_PATH: str = Field(default="memory.db", description="Path to SQLite database")
    DB_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DB_POOL_OVERFLOW: int = Field(default=10, description="Database connection pool overflow")
    
    # Vector settings
    EMBED_DIM: int = Field(default=768, description="Dimension of embedding vectors")
    HNSW_MAX_ELEMENTS: int = Field(default=100_000, description="Max elements in HNSW index")
    HNSW_EF_CONSTRUCTION: int = Field(default=200, description="HNSW construction parameter")
    HNSW_M: int = Field(default=16, description="HNSW parameter M")
    HNSW_EF: int = Field(default=50, description="HNSW parameter EF")
    
    # Ollama settings
    LOCAL_OLLAMA_URL: str = Field(default="http://localhost:11434", description="Local Ollama API URL")
    REMOTE_OLLAMA_URL: str = Field(default="http://100.103.237.60:11434", description="Remote Ollama API URL")
    DEFAULT_OLLAMA_MODEL: str = Field(default="gemma3:1b", description="Default Ollama model for generation")
    REMOTE_OLLAMA_MODEL: str = Field(default="gemma3:12b", description="Remote Ollama model")
    EMBED_MODELS: List[str] = Field(
        default=[
            "embeddinggemma", "granite-embedding", "nomic-embed-text", 
            "mxbai-embed-large", "snowflake-arctic-embed", "all-minilm"
        ],
        description="List of available embedding models"
    )
    
    # Summarization settings
    SUMMARY_MODEL: str = Field(default="gemma3:1b", description="Model for summarization")
    DISABLE_SUMMARIZATION: bool = Field(default=False, description="Disable summarization features")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed origins for CORS"
    )
    
    # Security settings
    SECRET_KEY: str = Field(default="your-secret-key-here", description="Secret key for security")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorithm for JWT encoding")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Number of requests allowed")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Time window in seconds for rate limiting")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(default=None, description="File to write logs to")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()