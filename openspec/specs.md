# OpenSpec Change Proposal

## Theme & Tone

This repository carries the GhostWire aesthetic: neon-cyberpunk, slightly haunted, and concise. When authoring specs or deltas, prefer clear technical language first, then tasteful theatricality. Use the project's lexicon (e.g., "controller" → "master", "client" → "submissive") only where it aids clarity. Add a one-line poetic residue at the end of major proposals as a signature.

## Title: GhostWire Token Optimization & Memory Enhancement

## Description
This proposal outlines changes to enhance GhostWire Refractory's token efficiency by implementing SQLite as a buffer and cache for remote LLM interactions, while adding document storage capabilities with Qdrant-compatible endpoint support.

## Motivation
Current implementation processes all user inputs and LLM responses without caching, leading to excessive token usage. The goal is to save tokens by storing embeddings in SQLite and only processing what's necessary with remote LLMs, while providing long-term memory capabilities.

## Implementation Details

### 1. Enhanced Token Buffering System
**Objective**: Implement SQLite as a buffer and cache to minimize remote LLM token consumption.

**Changes**:
- Modify the RAG service to implement intelligent caching of embedding comparisons
- Create a token optimization layer that checks cached responses before making remote calls
- Implement a cache expiry system to manage SQLite storage efficiently
- Add logic to bypass remote calls when cached responses are sufficiently similar to previous queries

**Code Modifications**:
```
services/rag_service.py - Add caching layer with similarity threshold
database/repositories.py - Add cache management queries
config/settings.py - Add cache-related configuration options
```

### 2. Document Storage Capability
**Objective**: Add functionality to store user documents (e.g., code) in the vector database.

**Changes**:
- Create new service for document ingestion and chunking
- Implement document parsing for various formats (code, text, etc.)
- Add endpoints for document upload and management
- Create document-specific memory storage with proper metadata

**Code Modifications**:
```
services/document_service.py - New service for document handling
api/v1/documents.py - New API endpoints for document management
models/document.py - New models for document representation
database/repositories.py - Add document storage methods
```

### 3. Qdrant-Compatible Endpoint
**Objective**: Expose a Qdrant-compatible API endpoint for vector search operations.

**Changes**:
- Create new module implementing Qdrant API specification
- Map Qdrant operations to existing SQLite/HNSW functionality
- Add endpoint validation and response formatting to match Qdrant schema
- Ensure consistency with existing embedding and search operations

**Code Modifications**:
```
api/v1/qdrant.py - New Qdrant-compatible endpoints
api/v1/qdrant_models.py - Qdrant-specific request/response models
vector/qdrant_adapter.py - Adapter for translating Qdrant operations
```

### 4. Summarization Integration
**Objective**: Enhance the optional summarization engine to further reduce token usage.

**Changes**:
- Improve the existing summarization service with configurable thresholds
- Add content analysis to determine when summarization is beneficial
- Integrate summarization before embedding for long inputs
- Add configuration for different summarization models and strategies

**Code Modifications**:
```
services/embedding_service.py - Integrate summarization before embedding
services/summarization_service.py - Enhanced summarization logic
config/settings.py - Additional summarization configuration options
```

### 5. Remote LLM Optimization
**Objective**: Improve the efficiency of remote LLM interactions.

**Changes**:
- Implement context window optimization to include only relevant memories
- Add intelligent context truncation to stay within token limits
- Implement request batching where appropriate
- Add response caching for repeated requests

**Code Modifications**:
```
services/rag_service.py - Optimized context building
services/memory_service.py - Enhanced memory retrieval logic
config/settings.py - Remote LLM optimization settings
```

## Risks & Mitigations

### Risk: Performance degradation due to additional processing
**Mitigation**: Implement async processing and caching layers to maintain responsiveness

### Risk: Incompatibility with existing Qdrant clients
**Mitigation**: Thoroughly test Qdrant endpoints with actual Qdrant clients to ensure compatibility

### Risk: Increased complexity of the codebase
**Mitigation**: Maintain clear separation of concerns and comprehensive documentation

## Success Criteria
- Reduction in remote LLM token usage by at least 40%
- Successful Qdrant client compatibility
- Document storage and retrieval functionality working as expected
- Maintained or improved response times
- All existing functionality preserved

## Implementation Timeline
- Phase 1: Token buffering system (Week 1-2)
- Phase 2: Document storage capability (Week 2-3)
- Phase 3: Qdrant-compatible endpoint (Week 3-4)
- Phase 4: Summarization integration (Week 4-5)
- Phase 5: Integration testing and optimization (Week 5-6)

## Dependencies
- HNSWlib for vector indexing (currently implemented)
- SQLite with APSW for database operations (currently implemented)
- Ollama-compatible models for embedding generation
- Qdrant client libraries for testing compatibility

## Testing Strategy
- Unit tests for new caching and document storage logic
- Integration tests for Qdrant endpoint compatibility
- Performance benchmarks to verify token usage reduction
- End-to-end tests ensuring all existing functionality remains intact
