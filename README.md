# GhostWire Refractory - Refactored

A neural network-based chat system with memory that stores message embeddings in SQLite and uses HNSW for efficient vector similarity search.

## Features

- Memory-augmented chat with semantic search
- Support for multiple embedding and generation models through Ollama
- Fast similarity search using HNSW index
- REST API with OpenAI-compatible endpoints
- Rate limiting and authentication
- Comprehensive benchmarking tools

## Architecture

The application is organized in a modular structure:

```
python/
├── src/ghostwire/   # Main application modules
│   ├── config/      # Configuration and settings
│   ├── database/    # Database connection and repositories  
│   ├── models/      # Pydantic models
│   ├── services/    # Business logic
│   ├── vector/      # Vector operations and HNSW management
│   ├── api/         # API endpoints and middleware
│   ├── clients/     # External API clients
│   ├── utils/       # Utilities and helpers
│   └── main.py      # Application entry point
├── client/          # Client applications
├── benchmarks/      # Benchmarking tools
└── tests/           # Unit and integration tests
```

## Installation

1. Clone the repository
2. Install dependencies (requires Python 3.12+):

```bash
pip install -r requirements.txt
```

Or using uv:

```bash
uv pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with your settings:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
DB_PATH=memory.db
EMBED_DIM=768
LOCAL_OLLAMA_URL=http://localhost:11434
REMOTE_OLLAMA_URL=http://100.103.237.60:11434
DEFAULT_OLLAMA_MODEL=gemma3:1b
SUMMARY_MODEL=gemma3:1b
DISABLE_SUMMARIZATION=false
SECRET_KEY=your-super-secret-key-here
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## Running the Application

```bash
cd python/src/ghostwire
python main.py
```

Or with uv:

```bash
uv run python -m python.src.ghostwire.main
```

The API will be available at `http://localhost:8000`

## API Documentation

See [APIDOC.md](APIDOC.md) for detailed API documentation.

## Client Application

To use the operator console client:

```bash
cd python/client
python operator_console.py
```

## Benchmarking

Run the benchmark suite:

```bash
cd python/benchmarks
python embedding_benchmarks.py
python rag_benchmarks.py
python summarization_benchmarks.py
```

## Testing

Run the test suite:

```bash
cd python/tests
python -m pytest
```

## Dependencies

The application requires:
- Python 3.12+
- FastAPI
- SQLite with APSW
- hnswlib for vector indexing
- httpx for HTTP client operations
- pydantic for data validation
- numpy for numerical operations

See `pyproject.toml` for the complete list of dependencies.

## Security

- Rate limiting to prevent API abuse
- Input validation to prevent injection attacks
- Authentication for protected endpoints
- CORS configuration to prevent XSS attacks
- Secure password hashing

## Development

This is a refactored version of the original GhostWire application with:
- Proper separation of concerns
- Modular architecture
- Comprehensive error handling
- Security measures
- Test coverage
- Documentation