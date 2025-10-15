# Memory Capability Specification

## Purpose

The Memory capability provides persistent storage and retrieval of chat interactions with embeddings, enabling contextual conversations through vector similarity search.

## Requirements

### Requirement: Memory Creation

The system SHALL store new memory entries with associated embeddings in the database.

#### Scenario: Create Memory with Embedding

- **WHEN** MemoryService.create_memory() is called with session_id, text, and embedding
- **THEN** the system stores the memory in the database and adds the embedding to the HNSW index

#### Scenario: Create Memory with Auto-Generated Embedding

- **WHEN** MemoryService.create_memory() is called with session_id and text but no embedding
- **THEN** the system generates the embedding before storing the memory

#### Scenario: Embedding Dimension Validation

- **WHEN** MemoryService.create_memory() is called with an embedding of incorrect dimension
- **THEN** the system raises an EmbeddingDimMismatchError

#### Scenario: Embedding Value Validation

- **WHEN** MemoryService.create_memory() is called with embedding containing non-finite values
- **THEN** the system raises a ValueError

### Requirement: Memory Retrieval by Session

The system SHALL retrieve memories for a specific session.

#### Scenario: Retrieve Memories by Session

- **WHEN** MemoryService.get_memories_by_session() is called with a session_id
- **THEN** the system returns memories for that session ordered by timestamp

#### Scenario: Retrieve Memories with Limit

- **WHEN** MemoryService.get_memories_by_session() is called with a session_id and limit
- **THEN** the system returns at most the specified number of memories

### Requirement: Similar Memory Query

The system SHALL query for similar memories using HNSW vector search or fallback to cosine similarity.

#### Scenario: HNSW-Based Similarity Search

- **WHEN** MemoryService.query_similar_memories() is called with an embedding and session_id
- **THEN** the system uses HNSW to find similar memories if the index is populated

#### Scenario: Cosine Similarity Fallback

- **WHEN** MemoryService.query_similar_memories() is called but HNSW has no results
- **THEN** the system falls back to cosine similarity search in the database

#### Scenario: Similar Memory Query with Validation

- **WHEN** MemoryService.query_similar_memories() is called with invalid embedding
- **THEN** the system raises appropriate validation errors

### Requirement: Session Management

The system SHALL manage unique session IDs for organizing memory collections.

#### Scenario: Get All Sessions

- **WHEN** MemoryService.get_all_sessions() is called
- **THEN** the system returns a list of all unique session IDs that have memories

### Requirement: Collection Operations

The system SHALL support operations on memory collections (sessions).

#### Scenario: Check Collection Existence

- **WHEN** MemoryService.collection_exists() is called with a collection name
- **THEN** the system returns true if the collection contains memories

#### Scenario: Get Collection Size

- **WHEN** MemoryService.get_collection_size() is called with a collection name
- **THEN** the system returns the number of memories in that collection

### Requirement: Collection Deletion

The system SHALL support deletion of entire memory collections.

#### Scenario: Delete Collection

- **WHEN** MemoryService.delete_collection() is called with a collection name
- **THEN** the system removes all memories in that collection and marks it as dropped

### Requirement: Memory Normalization

The system SHALL normalize embeddings to unit length before storing.

#### Scenario: Embedding Normalization

- **WHEN** MemoryService creates or queries memories with embeddings
- **THEN** the system normalizes the embeddings to unit length before storage or comparison

### Requirement: Memory Repository Operations

The system SHALL provide database operations through the MemoryRepository.

#### Scenario: Create Memory in Database

- **WHEN** MemoryRepository.create_memory() is called
- **THEN** the system inserts the memory record into the database with proper serialization

#### Scenario: Query Similar Memories in Database

- **WHEN** MemoryRepository.query_similar_by_embedding() is called
- **THEN** the system performs cosine similarity calculation and returns ranked results

### Requirement: Memory Metadata Storage

The system SHALL store additional metadata with memory entries.

#### Scenario: Store Summary Text

- **WHEN** MemoryService.create_memory() is called with summary_text
- **THEN** the system stores the summary text with the memory entry

#### Scenario: Retrieve Summary Text

- **WHEN** memories are retrieved from the database
- **THEN** the system includes any available summary text in the results

### Requirement: Similar Memory Query

The system SHALL query for similar memories using HNSW vector search or fallback to cosine similarity.

#### Scenario: HNSW-Based Similarity Search

- **WHEN** MemoryService.query_similar_memories() is called with an embedding and session_id
- **THEN** the system uses HNSW to find similar memories if the index is populated

#### Scenario: Cosine Similarity Fallback

- **WHEN** MemoryService.query_similar_memories() is called but HNSW has no results
- **THEN** the system falls back to cosine similarity search in the database

### Requirement: Session Management

The system SHALL manage unique session IDs for organizing memory collections.

#### Scenario: Get All Sessions

- **WHEN** MemoryService.get_all_sessions() is called
- **THEN** the system returns a list of all unique session IDs that have memories

### Requirement: Collection Operations

The system SHALL support operations on memory collections (sessions).

#### Scenario: Check Collection Existence

- **WHEN** MemoryService.collection_exists() is called with a collection name
- **THEN** the system returns true if the collection contains memories

#### Scenario: Get Collection Size

- **WHEN** MemoryService.get_collection_size() is called with a collection name
- **THEN** the system returns the number of memories in that collection

### Requirement: Collection Deletion

The system SHALL support deletion of entire memory collections.

#### Scenario: Delete Collection

- **WHEN** MemoryService.delete_collection() is called with a collection name
- **THEN** the system removes all memories in that collection and marks it as dropped

## MODIFIED Requirements

## REMOVED Requirements
