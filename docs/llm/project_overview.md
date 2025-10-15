# GhostWire Refractory - Project Overview for LLMs

## Core Purpose
GhostWire Refractory is a neural network-based chat system with persistent memory capabilities that enables contextual conversations through vector similarity search. The system stores message embeddings in SQLite and uses HNSW (Hierarchical Navigable Small World) for efficient vector similarity search.

## Architecture Pattern
- Hexagonal/Ports & Adapters architecture
- FastAPI web framework with async/await patterns
- SQLite database with connection pooling
- HNSW for fast vector similarity search
- OpenAI, Qdrant, and Ollama-compatible interfaces

## Key Components
1. API Layer: FastAPI endpoints for various operations
2. Services Layer: Business logic encapsulation
3. Database Layer: SQLite with connection pooling
4. Vector Index: HNSW for similarity search
5. Utils: Common utilities including GHOSTWIRE scoring

## Primary Endpoints
- POST /api/v1/embeddings: Generate text embeddings
- POST /api/v1/chat/chat_embedding: Chat with memory context
- POST /api/v1/vectors/query: Vector similarity search
- POST /api/v1/vectors/upsert: Store vector embeddings
- POST /api/v1/chat/chat_completion: Simple chat without retrieval

## Technology Stack
- Language: Python 3.12+
- Framework: FastAPI
- Database: SQLite + APSW
- Vector Indexing: HNSWlib
- HTTP Client: HTTPX
- Data Validation: Pydantic
- Vector Processing: NumPy

## Benchmarking & GHOSTWIRE Scoring
The system includes comprehensive benchmarking tools with standardized GHOSTWIRE scores:
- Embedding Benchmarks: Performance and stability of embeddings
- RAG Benchmarks: Retrieval-Augmented Generation quality
- Summarization Benchmarks: Text summarization effectiveness
- Model Comparison: Overall GHOSTWIRE score for model selection