## ADDED Requirements

### Requirement: Qdrant Vector Operations
The system SHALL support vector operations using Qdrant-compatible API format.

#### Scenario: Qdrant Vector Search
- **WHEN** a Qdrant-compatible search request is made
- **THEN** the system maps the request to HNSW operations and returns results in Qdrant format

#### Scenario: Qdrant Vector Upload
- **WHEN** a Qdrant-compatible upload request is made
- **THEN** the system stores the vector in the SQLite database and HNSW index