## ADDED Requirements

### Requirement: Enhanced Summarization Integration
The system SHALL enhance the optional summarization engine to further reduce token usage.

#### Scenario: Pre-Embedding Summarization
- **WHEN** input text exceeds configurable length thresholds
- **THEN** the system applies summarization before generating embeddings

#### Scenario: Context Summarization
- **WHEN** context window approaches token limits
- **THEN** the system selectively summarizes less relevant memories before sending to LLM