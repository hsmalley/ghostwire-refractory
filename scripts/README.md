# GhostWire Refractory Scripts

This directory contains utility scripts for working with the GhostWire Refractory system.

## Available Scripts

### `import_documents.py`

A CLI tool for ingesting documents into the GhostWire Refractory vector database.
Supports txt/md/code inputs, chunking, optional summarization, embedding generation,
and storage into the local vector DB.

Usage:

```bash
# Ingest a single file
python scripts/import_documents.py README.md

# Ingest a directory with summarization
python scripts/import_documents.py docs/ --summarize

# Dry run (preview without storing)
python scripts/import_documents.py src/ --dry-run

# Verbose output
python scripts/import_documents.py docs/ --verbose
```

Options:

- `--dry-run`: Perform a dry run without actually storing documents
- `--summarize`: Enable summarization of large chunks
- `--chunk-size`: Size of chunks in tokens/words (default: 500)
- `--overlap-size`: Size of overlap between chunks (default: 50)
- `--extensions`: File extensions to process (default: .txt .md)
- `--verbose`: Enable verbose logging

### Other Scripts

Additional scripts may be available in subdirectories:

- `benchmarks/`: Performance testing scripts
- `tests/`: Unit and integration test runners

## Running Scripts

Most scripts can be run directly with Python:

```bash
python scripts/script_name.py [arguments]
```

Some scripts may require specific environment variables or dependencies to be set up.
See individual script documentation for requirements.

## Environment Variables

Scripts respect the same environment variables as the main application:

- `DB_PATH`: Path to SQLite database (default: "memory.db")
- `LOCAL_OLLAMA_URL`: Local Ollama API URL (default: "http://localhost:11434")
- `REMOTE_OLLAMA_URL`: Remote Ollama API URL (default: "http://100.103.237.60:11434")
- `DEFAULT_OLLAMA_MODEL`: Default Ollama model for generation (default: "gemma3:1b")
- `EMBED_DIM`: Dimension of embedding vectors (default: 768)

See `.env.example` for a complete list of configurable variables.
