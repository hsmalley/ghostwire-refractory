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
├── ghostwire/       # Main application modules
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

Using pip (requires build tools for hnswlib):
```bash
pip install -e .
```

Or using uv (recommended):
```bash
uv pip install -e .
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

### Method 1: Install in development mode (recommended)
```bash
cd /path/to/ghostwire-refractory  # Project root
pip install -e .
ghostwire  # This uses the entry point defined in pyproject.toml
```

Or with uv:
```bash
uv run pip install -e .
uv run ghostwire
```

### Method 2: Direct execution with proper PYTHONPATH
```bash
cd /path/to/ghostwire-refractory  # Project root
PYTHONPATH=python python -m ghostwire.main
```

### Method 3: Using uv with PYTHONPATH
From the project root:
```bash
cd /path/to/ghostwire-refractory  # Project root
PYTHONPATH=python uv run python -m ghostwire.main
```

The API will be available at `http://localhost:8000`

## API Documentation

See [APIDOC.md](APIDOC.md) for detailed API documentation.

## Client Application

To use the operator console client:

```bash
cd /path/to/ghostwire-refractory  # Project root
PYTHONPATH=python python -m python.client.operator_console
```

## Benchmarking

Run the benchmark suite:

```bash
cd /path/to/ghostwire-refractory  # Project root
PYTHONPATH=python python -m python.benchmarks.embedding_benchmarks
PYTHONPATH=python python -m python.benchmarks.rag_benchmarks
PYTHONPATH=python python -m python.benchmarks.summarization_benchmarks
```

Or run all benchmarks from the project root:
```bash
export PYTHONPATH=python
python -m python.benchmarks.embedding_benchmarks
python -m python.benchmarks.rag_benchmarks
python -m python.benchmarks.summarization_benchmarks
```

## Testing

Run the test suite:

```bash
cd /path/to/ghostwire-refractory  # Project root
PYTHONPATH=python python -m pytest python/tests/
```

Or with pytest discovery:
```bash
cd /path/to/ghostwire-refractory  # Project root
PYTHONPATH=python pytest python/tests/
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