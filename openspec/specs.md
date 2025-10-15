# GhostWire Refractory - OpenSpec Specifications Overview

## Theme & Tone

This repository carries the GhostWire aesthetic: neon-cyberpunk, slightly haunted, and concise. When authoring specs or deltas, prefer clear technical language first, then tasteful theatricality. Use the project's lexicon (e.g., "controller" → "master", "client" → "submissive") only where it aids clarity. Add a one-line poetic residue at the end of major proposals as a signature.

## Capabilities

The GhostWire Refractory system is organized into several key capabilities, each with its own specification:

- **API**: REST endpoints with OpenAI, Qdrant, and Ollama compatibility
- **Authentication**: JWT-based authentication and rate limiting
- **CLI**: Command-line interface for system management
- **Configuration**: Settings management with Pydantic BaseSettings
- **Database**: SQLite connection pooling and data access
- **Embedding**: Vector generation from text inputs
- **Memory**: Persistent storage with vector similarity search
- **Models**: Pydantic data models for validation
- **Utils**: Common helper functions and validation
- **Vector**: HNSW index management for similarity search
- **Orchestrator**: Multi-LLM coordination with Master/Worker pattern
- **Changes**: Tracking of implemented improvements and features

## Active Changes

- `token-optimization-features`: Implement token optimization, document storage, and Qdrant compatibility
- `add-openspec-orchestrator`: Multi-LLM orchestration with Master/Worker pattern

## Purpose

This specification system provides a comprehensive reference for all capabilities of the GhostWire Refractory system, enabling systematic development, testing, and maintenance of the codebase. Each capability has detailed requirements with scenarios that describe expected behavior.
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
