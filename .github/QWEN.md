# GhostWire Refractory - QWEN Assistant Context

## Project Overview
GhostWire Refractory is a neural network-based chat system with persistent memory capabilities. The system stores message embeddings in SQLite and uses HNSW (Hierarchical Navigable Small World) for efficient vector similarity search. The project was refactored from a monolithic codebase into a modular Python application with proper separation of concerns.

## Architecture
- **Language**: Python 3.12+
- **Framework**: FastAPI with async/await patterns
- **Database**: SQLite with APSW and connection pooling
- **Vector Indexing**: HNSWlib for fast similarity search
- **API Compatibility**: OpenAI, Qdrant, and Ollama-compatible interfaces

### Directory Structure
```
python/                     # All Python code resides here
├── src/ghostwire/          # Main application modules
│   ├── config/             # Configuration management
│   ├── database/           # Data access layer
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   ├── vector/             # Vector operations
│   ├── api/                # API layer
│   │   └── v1/             # API version 1
│   │       └── middleware/ # API middleware
│   └── utils/              # Utility functions
├── client/                 # Client applications
├── benchmarks/             # Performance tools
└── tests/                  # Unit & integration tests
```

## Development Environment
- **Package Management**: uv (recommended) or pip
- **Project Layout**: PEP 621 compliant pyproject.toml
- **Configuration**: Pydantic BaseSettings with .env support
- **Testing**: pytest with unit and integration tests

## Key Features
- Memory-augmented chat with semantic search
- Support for multiple embedding/generation models (Ollama)
- Fast similarity search using HNSW
- REST API with OpenAI-compatible endpoints
- Rate limiting and JWT authentication
- Comprehensive benchmarking tools

## Critical Implementation Details
1. **Import Handling**: Python path manipulation required for running from project root
2. **Package Installation**: Uses `pip install -e .` for development mode
3. **Entry Point**: `ghostwire` command via pyproject.toml script definition
4. **Resource Management**: HNSW index persistence and database connection pooling

## Configuration Parameters
Key settings are managed in `config/settings.py` using Pydantic:
- `HOST`, `PORT`: Server configuration
- `DB_PATH`, `DB_POOL_SIZE`: Database settings
- `EMBED_DIM`, HNSW parameters: Vector configuration
- `LOCAL_OLLAMA_URL`, `REMOTE_OLLAMA_URL`: Model endpoints
- Security settings: JWT, rate limiting, etc.

## Development Workflow
1. Set up PYTHONPATH when running directly: `PYTHONPATH=python/src`
2. Use `pip install -e .` for development installation
3. Run with `ghostwire` command or via uvicorn
4. Test with `PYTHONPATH=python/src pytest python/tests/`

## Files and Artifacts
- `ARCHITECTURE.md`: Comprehensive technical architecture
- `APIDOC.md`: API reference documentation
- `.env.sample`: Environment configuration template
- `QWEN_TODO.md`: Refactoring task completion log
- `QWEN_CLEANUP.md`: Post-refactoring cleanup documentation
- `QWEN_REVIEW.md`: Code review results

## Security Considerations
- JWT-based authentication
- Rate limiting middleware
- Input validation and sanitization
- Secure password hashing
- CORS configuration

## Performance Notes
- HNSW provides O(log n) search complexity
- Connection pooling for database operations
- Async/await for I/O operations
- Embedding dimension: 768 (default)
- Memory usage scales with vector database size

## Testing Strategy
- Unit tests for individual modules
- Integration tests for API endpoints
- Benchmarking tools for performance analysis
- Mock-based testing for external dependencies

## Deployment Considerations
- Single-server deployment friendly
- SQLite for embedded/development use
- Configurable endpoints for different environments
- Resource usage: 100-200MB base + vector index size