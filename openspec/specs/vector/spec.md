# Vector Capability Specification

## Purpose
The Vector capability manages HNSW (Hierarchical Navigable Small World) index operations for efficient vector similarity search, including persistent storage and retrieval of vector embeddings.

## Requirements

### Requirement: HNSW Index Initialization
The system SHALL initialize the HNSW index and populate with existing data from the database.

#### Scenario: Fresh Index Initialization
- **WHEN** HNSWIndexManager.initialize_index() is called and no persistent index exists
- **THEN** the system creates a new HNSW index and backfills it with embeddings from the database

#### Scenario: Persistent Index Loading
- **WHEN** HNSWIndexManager.initialize_index() is called and a persistent index exists
- **THEN** the system loads the existing index from disk

#### Scenario: Index Initialization Error Handling
- **WHEN** HNSWIndexManager.initialize_index() fails to load persistent index
- **THEN** the system logs warning and proceeds with backfill from database

### Requirement: Vector Index Backfilling
The system SHALL backfill the HNSW index with existing vectors from the database.

#### Scenario: Database Backfill
- **WHEN** HNSWIndexManager._backfill_from_db() is called
- **THEN** the system retrieves all embeddings from the database and adds them to the HNSW index

#### Scenario: Backfill with Session Data
- **WHEN** HNSWIndexManager._backfill_from_db() executes
- **THEN** the system fetches all unique session IDs and retrieves memories for each session

#### Scenario: Backfill with Dimension Validation
- **WHEN** HNSWIndexManager._backfill_from_db() processes embeddings
- **THEN** the system validates each embedding dimension matches the configured EMBED_DIM

#### Scenario: Backfill with Memory Conversion
- **WHEN** HNSWIndexManager._backfill_from_db() retrieves memory entries
- **THEN** the system converts stored embedding bytes back to arrays and adds to index

### Requirement: Vector Addition to Index
The system SHALL add new vectors to the HNSW index.

#### Scenario: Add Single Vector
- **WHEN** HNSWIndexManager.add_items() is called with a single vector and ID
- **THEN** the system adds the vector to the index and returns success status

#### Scenario: Add Multiple Vectors
- **WHEN** HNSWIndexManager.add_items() is called with multiple vectors and IDs
- **THEN** the system adds all vectors to the index and returns success status

#### Scenario: Add Items Before Initialization
- **WHEN** HNSWIndexManager.add_items() is called before index is initialized
- **THEN** the system raises an exception indicating the index is not initialized

### Requirement: Vector KNN Query
The system SHALL perform K-nearest neighbor queries on the HNSW index.

#### Scenario: KNN Query Execution
- **WHEN** HNSWIndexManager.knn_query() is called with a query vector and k parameter
- **THEN** the system returns the k most similar vectors from the index

#### Scenario: Query Before Initialization
- **WHEN** HNSWIndexManager.knn_query() is called before index is initialized
- **THEN** the system raises an exception indicating the index is not initialized

#### Scenario: Query with Insufficient Results
- **WHEN** HNSWIndexManager.knn_query() is called but index has fewer than k elements
- **THEN** the system returns all available results

### Requirement: Index Persistence
The system SHALL save the HNSW index to disk for persistence.

#### Scenario: Index Saving
- **WHEN** HNSWIndexManager.save_index() is called during shutdown
- **THEN** the system saves the current index state to disk

#### Scenario: Index Saving Failure
- **WHEN** HNSWIndexManager.save_index() encounters a file system error
- **THEN** the system logs a warning about the failure

### Requirement: Current Count Retrieval
The system SHALL provide the current number of elements in the index.

#### Scenario: Get Element Count
- **WHEN** HNSWIndexManager.get_current_count() is called
- **THEN** the system returns the current number of elements in the index

#### Scenario: Count Before Initialization
- **WHEN** HNSWIndexManager.get_current_count() is called before index is initialized
- **THEN** the system returns 0

### Requirement: Vector Deletion
The system SHALL handle requests to delete vectors from the index.

#### Scenario: Delete Vectors
- **WHEN** HNSWIndexManager.delete_from_index() is called with vector IDs
- **THEN** the system logs that deletion is not supported by hnswlib and suggests rebuilding the index

### Requirement: Thread Safety
The system SHALL ensure thread-safe operations on the HNSW index.

#### Scenario: Concurrent Index Operations
- **WHEN** multiple threads attempt to access the HNSW index simultaneously
- **THEN** the system ensures data integrity through appropriate locking

### Requirement: Index Configuration
The system SHALL support configurable HNSW parameters.

#### Scenario: Configurable HNSW Parameters
- **WHEN** HNSWIndexManager initializes the index
- **THEN** the system uses parameters from the configuration (max_elements, ef_construction, M, ef)

### Requirement: Index Status Monitoring
The system SHALL provide information about the index state.

#### Scenario: Index Initialization Status
- **WHEN** HNSWIndexManager.initialize_index() completes
- **THEN** the system logs the number of vectors loaded into the index

#### Scenario: Persistent Index Loading
- **WHEN** HNSWIndexManager.initialize_index() is called and a persistent index exists
- **THEN** the system loads the existing index from disk

### Requirement: Vector Index Backfilling
The system SHALL backfill the HNSW index with existing vectors from the database.

#### Scenario: Database Backfill
- **WHEN** HNSWIndexManager._backfill_from_db() is called
- **THEN** the system retrieves all embeddings from the database and adds them to the HNSW index

### Requirement: Vector Index Backfill Implementation
The system SHALL implement the database backfill functionality to load existing embeddings at initialization.

#### Scenario: Implemented Backfill Logic
- **WHEN** HNSWIndexManager.initialize_index() is called and needs to backfill
- **THEN** the system executes the implemented backfill logic that fetches sessions, retrieves memories, converts embedding bytes to arrays, validates dimensions, and adds vectors to the HNSW index

### Requirement: Vector Addition to Index
The system SHALL add new vectors to the HNSW index.

#### Scenario: Add Single Vector
- **WHEN** HNSWIndexManager.add_items() is called with a single vector and ID
- **THEN** the system adds the vector to the index and returns success status

### Requirement: Vector KNN Query
The system SHALL perform K-nearest neighbor queries on the HNSW index.

#### Scenario: KNN Query Execution
- **WHEN** HNSWIndexManager.knn_query() is called with a query vector and k parameter
- **THEN** the system returns the k most similar vectors from the index

### Requirement: Index Persistence
The system SHALL save the HNSW index to disk for persistence.

#### Scenario: Index Saving
- **WHEN** HNSWIndexManager.save_index() is called during shutdown
- **THEN** the system saves the current index state to disk

### Requirement: Current Count Retrieval
The system SHALL provide the current number of elements in the index.

#### Scenario: Get Element Count
- **WHEN** HNSWIndexManager.get_current_count() is called
- **THEN** the system returns the current number of elements in the index

### Requirement: Vector Deletion
The system SHALL handle requests to delete vectors from the index.

#### Scenario: Delete Vectors
- **WHEN** HNSWIndexManager.delete_from_index() is called with vector IDs
- **THEN** the system logs that deletion is not supported by hnswlib and suggests rebuilding the index

## MODIFIED Requirements

## REMOVED Requirements