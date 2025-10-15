## Why
To reduce remote LLM token usage by implementing SQLite as a buffer and cache, while adding document storage capabilities and Qdrant-compatible endpoints as outlined in GHOSTWIRE_GOALS.md.

## What Changes
- Implement enhanced token buffering system with intelligent caching
- Add document storage capability for user documents (e.g., code)
- Create Qdrant-compatible API endpoint
- Enhance summarization integration for token reduction
- Optimize remote LLM interactions

## Impact
- Affected specs: api, memory, vector, embedding
- Affected code: services/rag_service.py, services/document_service.py, api/v1/qdrant.py, and related modules