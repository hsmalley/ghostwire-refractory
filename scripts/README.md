# GhostWire Refractory Scripts

This directory contains utility scripts for working with the GhostWire Refractory system.

## Available Scripts

### `seed_sample_data.py`

A CLI tool for seeding the GhostWire Refractory database with sample data for local development and testing.

Usage:
```bash
# Seed with default settings
python scripts/seed_sample_data.py

# Seed with verbose output
python scripts/seed_sample_data.py --verbose

# Force re-seeding even if data already exists
python scripts/seed_sample_data.py --force

# Seed to a custom database path
python scripts/seed_sample_data.py --db-path custom.db
```

Options:
- `--db-path`: Path to SQLite database (defaults to `DB_PATH` from settings)
- `--embed-dim`: Embedding dimension (defaults to `EMBED_DIM` from settings)
- `--force`: Force insertion even if sample data already exists
- `--verbose`: Enable verbose output

### Sample Data Seeding

The script will:
- Create tables if they don't exist
- Insert sample sessions, messages, and synthetic embeddings
- Generate realistic sample data that mimics actual usage
- Populate the database with 15 sample memory entries across 5 sessions

The seeder is idempotent by default to prevent duplicate entries.

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