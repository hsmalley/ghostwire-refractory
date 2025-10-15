# GhostWire Refractory - Project Structure & Files

## Directory Structure
```
python/
├── benchmarks/              # Performance tools
│   ├── embedding_benchmarks.py      # Embedding performance benchmarks
│   ├── rag_benchmarks.py            # RAG (Retrieval-Augmented Generation) benchmarks
│   ├── summarization_benchmarks.py  # Text summarization benchmarks
│   └── model_comparison_benchmark.py # Model comparison with GHOSTWIRE scoring
├── client/                  # Client applications
├── ghostwire/               # Main application modules
│   ├── api/                 # API layer (FastAPI)
│   │   └── v1/              # API version 1
│   ├── cli/                 # Command line interface
│   ├── config/              # Configuration management
│   ├── database/            # Data access layer
│   ├── models/              # Data models (Pydantic)
│   ├── services/            # Business logic layer
│   ├── utils/               # Utility functions
│   │   ├── context_optimizer.py     # Context window optimization
│   │   ├── error_handling.py        # Error handling utilities
│   │   ├── ghostwire_scoring.py     # GHOSTWIRE scoring functions
│   │   ├── security.py              # Security utilities
│   │   └── token_benchmark.py       # Token usage benchmarking
│   └── vector/              # Vector operations
├── tests/                   # Unit & integration tests
│   ├── benchmark/           # Benchmark-specific tests
│   ├── integration/         # Integration tests
│   └── unit/                # Unit tests
└── __init__.py
```

## Key Files & Their Purpose

### API Layer Files
- `python/ghostwire/api/v1/`: FastAPI endpoints
  - chat.py: Chat endpoints with memory functionality
  - embeddings.py: Embedding generation and search
  - health.py: Health check endpoint
  - models.py: Model listing endpoint
  - vectors.py: Vector storage and query operations

### Configuration Files
- `python/ghostwire/config/settings.py`: Application settings using Pydantic BaseSettings
  - Contains database, Ollama, embedding, and security configurations
  - Loads values from environment variables with safe defaults

### Service Layer Files
- `python/ghostwire/services/memory_service.py`: Manages memory storage and retrieval
- `python/ghostwire/services/embedding_service.py`: Handles embedding operations
- `python/ghostwire/services/rag_service.py`: Coordinates Retrieval-Augmented Generation

### Utility Files
- `python/ghostwire/utils/ghostwire_scoring.py`: GHOSTWIRE scoring algorithms
- `python/ghostwire/utils/context_optimizer.py`: Optimizes context window usage
- `python/ghostwire/utils/token_benchmark.py`: Token usage optimization benchmarks

### Benchmark Files
- `python/benchmarks/embedding_benchmarks.py`: Embedding performance tests
- `python/benchmarks/rag_benchmarks.py`: RAG system evaluation
- `python/benchmarks/summarization_benchmarks.py`: Text summarization tests
- `python/benchmarks/model_comparison_benchmark.py`: Model comparison framework

### Test Files
- `python/tests/benchmark/test_ghostwire_benchmarks.py`: Benchmark-specific tests with pytest markers
- `python/tests/unit/`: Unit tests for individual components
- `python/tests/integration/`: Integration tests for system-wide functionality

## Documentation Files
- `ARCHITECTURE.md`: System architecture and component interactions
- `APIDOC.md`: API endpoints and usage documentation
- `CONTRIBUTING.md`: Contribution guidelines
- `BENCHMARKING.md`: Benchmark methodology and usage
- `BENCHMARKING_SPEC.md`: GHOSTWIRE scoring specification
- `llm/`: LLM-specific project information (this project)

## Configuration Files
- `pyproject.toml`: Project dependencies and configuration
- `openspec/`: OpenSpec change proposals and specifications
- `.env.sample`: Sample environment variables
- `.github/workflows/`: CI/CD workflows including benchmark job

## Build/Deployment Files
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `Dockerfile`: Docker image configuration (if present)
- Various configuration files for development workflows