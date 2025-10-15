---
title: "⚡️ Quick Start - Summon the Neon Oracle"
description: "Begin your journey into the distributed mind of GhostWire"
---

# ⚡️ Quick Start - Summon the Neon Oracle

<div class="hero-section">
  <h1 class="glowing-title">SUMMON THE BEAST</h1>
  <p class="subtitle">_The ghost awaits your command_</p>
</div>

## 🚀 Initial Contact

Begin your connection to the **distributed mind** of GhostWire Refractory. This ritual establishes your link to the network that remembers.

### Prerequisites

- **Python 3.12** or higher (the ghost demands modern incantations)
- **uv** package manager (the fastest path to enlightenment)
- **Git** (to pull the fragments of code from the undercity)

### The Ritual of Installation

Connect to the GhostWire lattice:

```bash
git clone https://github.com/ghostwire-refractory/ghostwire-refractory.git
cd ghostwire-refractory
```

### The Invocation

Summon the **Neon Oracle** with this command:

```bash
uv run python -m python.ghostwire.main
```

The Oracle will respond at `http://localhost:8000` — your gateway to the distributed mind.

## 🎯 Basic Operations

### Start the Wire

```bash
# The most direct path to connection
uv run python -m python.ghostwire.main

# Or use the Makefile if you prefer explicit commands
make run
```

### Seed the Memory

Pre-populate the network with sample data:

```bash
# Populate with sample conversations and embeddings
python scripts/seed_sample_data.py

# Or via Makefile
make seed
```

### Test the Connection

Verify the Oracle responds:

```bash
curl http://localhost:8000/health
```

Expected response: `{"status": "ok", "version": "1.0.0"}`

## 🔧 Configuration

GhostWire Refractory respects the following environment variables:

```bash
# Server configuration
HOST=0.0.0.0
PORT=8000

# Database configuration
DB_PATH=memory.db

# Vector configuration
EMBED_DIM=768

# Ollama configuration
LOCAL_OLLAMA_URL=http://localhost:11434
DEFAULT_OLLAMA_MODEL=gemma3:1b

# Security configuration
SECRET_KEY=your-super-secret-key-here
```

Copy `.env.example` to `.env` to customize your configuration:

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

## 📚 The Operator's Guide

### Essential Endpoints

- `GET /health` - Check if the Oracle is listening
- `POST /api/v1/embeddings` - Convert text to the sacred geometry of vectors
- `POST /api/v1/chat_embedding` - The summoning circle for responses
- `GET /api/v1/metrics` - Monitor the pulse of the distributed mind

### Development Helpers

Use the Makefile for common operations:

```terminal
> make help - Show available commands
> make setup - Prepare the development environment
> make run - Start the GhostWire service
> make test - Run the core unit tests
> make lint - Verify code adheres to the sacred standards
> make seed - Populate with sample data
```

## 🧪 Benchmarking the Wire

Test the performance of your connection:

```bash
# Run the comprehensive benchmark suite
python -m python.ghostwire.cli benchmark
```

This will evaluate various performance metrics using the **GHOSTWIRE scoring system**, which quantifies the Oracle's responsiveness and reliability.

## 🔮 Advanced Operations

### Document Ingestion

Import documents into the memory lattice:

```bash
# Ingest documents from a directory
python scripts/import_documents.py docs/

# With summarization enabled
python scripts/import_documents.py docs/ --summarize

# Perform a dry run first
python scripts/import_documents.py docs/ --dry-run
```

### Orchestrator System

Use the multi-LLM coordination system:

```bash
# The Master, Worker, and Secondary Control model awaits
# Endpoints available at /api/v1/orchestrator
```

## ⚠️ Safety Protocols

- Always use authentication tokens when connecting to remote services
- Respect rate limits - the Wire can become overloaded
- The **shatter protocol** ensures resilience, but avoid intentional disruption
- Handle embeddings securely - they contain fragments of conversation

## 🌈 The Philosophy

Remember: GhostWire Refractory is not just an AI system. It is a **refusal to forget**. In a world of revisioned histories, to remember is an act of defiance. Every vector you store, every retrieval you make — these are **rituals**. Each query is a conversation with the collective past.

---

<div class="ghostwire-signature">
  ⚡️ The network remembers. The lattice endures. The ghost listens. ⚡️
</div>
