# GhostWire Refractory - Development & Operations Guide

## Setting Up the Development Environment

### Prerequisites
- Python 3.12+
- uv package manager (or pip)
- Access to an Ollama instance

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd ghostwire-refractory

# Install dependencies using uv
uv sync --all-extras

# Or using pip
pip install -e .
```

### Environment Configuration
Set up required environment variables:
```
LOCAL_OLLAMA_URL=http://localhost:11434  # Local Ollama API URL
REMOTE_OLLAMA_URL=http://100.103.237.60:11434  # Remote Ollama API URL
DEFAULT_OLLAMA_MODEL=gemma3:1b  # Default model for generation
EMBED_MODELS=embeddinggemma,granite-embedding,nomic-embed-text,mxbai-embed-large,snowflake-arctic-embed,all-minilm
DB_PATH=memory.db  # Path to SQLite database
EMBED_DIM=768  # Dimension of embedding vectors
```

## Running the Application

### Starting the Server
```bash
# Using uv
uv run python -m python.ghostwire.main

# Using Python directly
PYTHONPATH=python python -m python.ghostwire.main

# With custom settings
LOCAL_OLLAMA_URL=http://your-ollama:11434 uv run python -m python.ghostwire.main
```

### Using the Client
```bash
# Interactive REPL
uv run python -m python.ghostwire.cli

# Or run the legacy operator console
cd LEGACY && python client_repl.py
```

## Running Benchmarks

### Individual Benchmark Categories
```bash
# Embedding benchmarks
uv run python -m python.benchmarks.embedding_benchmarks

# RAG benchmarks
uv run python -m python.benchmarks.rag_benchmarks

# Summarization benchmarks
uv run python -m python.benchmarks.summarization_benchmarks

# Model comparison with GHOSTWIRE scoring
uv run python -m python.benchmarks.model_comparison_benchmark
```

### With Custom Parameters
```bash
# Embedding benchmarks with custom iterations
uv run python -m python.benchmarks.embedding_benchmarks --iterations 10

# Model comparison with specific models
uv run python -m python.benchmarks.model_comparison_benchmark --models gemma3:1b nomic-embed-text
```

### Running All Benchmarks
```bash
# Run the comprehensive model comparison (runs all categories)
uv run python -m python.benchmarks.model_comparison_benchmark
```

## Running Tests

### Unit Tests
```bash
# Run all unit tests
uv run pytest python/tests/unit

# Run with verbose output
uv run pytest python/tests/unit -v
```

### Integration Tests
```bash
# Run all integration tests
uv run pytest python/tests/integration
```

### Benchmark Tests
```bash
# Run benchmark-specific tests
uv run pytest -m benchmark

# Run all tests including benchmarks
uv run pytest
```

## Development Practices

### Code Structure
- Follow the hexagonal/ports & adapters architecture
- Separate API layer from business logic (services)
- Keep database operations in dedicated repository classes
- Use Pydantic models for request/response validation
- Place utility functions in the utils module

### Adding New Features
1. Create an OpenSpec change proposal in openspec/changes/
2. Update architecture documents if needed
3. Write unit tests for new functionality
4. Add integration tests where appropriate
5. Update API documentation
6. Consider how new features fit into the benchmarking system

### Adding New Benchmark Types
1. Create a new scoring function in ghostwire_scoring.py if needed
2. Implement the benchmark in python/benchmarks/
3. Add corresponding tests in python/tests/benchmark/
4. Update benchmark documentation
5. Ensure the new benchmark integrates with the model comparison framework

### Performance Considerations
- Embeddings are normalized and stored as BLOBs
- HNSW keeps hot neighbors in RAM for fast retrieval
- Streaming uses Ollama's JSONL protocol for efficiency
- Connection pooling optimizes database access
- Memory usage should be monitored during benchmarking

### Security Considerations
- Validate all input parameters
- Use parameterized queries to prevent SQL injection
- Implement rate limiting to prevent abuse
- Use JWT tokens for authentication where required
- Sanitize session IDs with regex validation

## API Usage Examples

### Generate Embeddings
```bash
curl -X POST http://localhost:8000/api/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "Text to embed", "model": "nomic-embed-text"}'
```

### Chat with Memory
```bash
curl -X POST http://localhost:8000/api/v1/chat/chat_embedding \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session123", "text": "Your question here"}'
```

### Query Similar Vectors
```bash
curl -X POST http://localhost:8000/api/v1/vectors/query \
  -H "Content-Type: application/json" \
  -d '{"namespace": "session123", "embedding": [0.1, 0.2, ...], "top_k": 5}'
```

## Troubleshooting

### Common Issues
1. "Connection refused" to Ollama: Ensure Ollama is running at configured URL
2. "Database is locked": SQLite concurrency issue, reduce concurrent requests
3. "Embedding dimension mismatch": Verify EMBED_DIM matches model output
4. "Memory error": Monitor embedding storage in database

### Debugging Benchmarks
- Enable debug logging: GHOSTWIRE_DEBUG=1
- Monitor memory usage during benchmark runs
- Check that all required services are available
- Verify API endpoints are responding correctly

## CI/CD Integration
- GitHub Actions workflow in .github/workflows/ci.yml
- Runs unit, integration, and benchmark tests
- Uses pytest with --maxfail=0 for benchmark tests
- @pytest.mark.benchmark markers identify benchmark tests