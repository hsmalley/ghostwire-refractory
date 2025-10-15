# Models Capability Specification

## Purpose

The Models capability provides Pydantic data models for the GhostWire Refractory system, ensuring consistent data validation and serialization across all components.

## Requirements

### Requirement: Memory Data Model

The system SHALL provide a Memory model for representing stored memories with embeddings.

#### Scenario: Memory Model Validation

- **WHEN** a Memory object is created or validated
- **THEN** the system validates required fields (session_id, prompt_text, answer_text, timestamp, embedding)

#### Scenario: Memory Model with Optional ID

- **WHEN** a Memory object is created during retrieval
- **THEN** the system allows ID to be None for new memories

#### Scenario: Memory Model with Summary

- **WHEN** a Memory object includes summary_text
- **THEN** the system properly handles the optional summary field

### Requirement: Memory Creation Model

The system SHALL provide a MemoryCreate model for creating new memory entries.

#### Scenario: Memory Creation Validation

- **WHEN** a MemoryCreate object is validated
- **THEN** the system validates required fields and embedding dimensions

#### Scenario: Memory Creation with Summary

- **WHEN** a MemoryCreate object includes summary_text
- **THEN** the system validates and includes the optional summary field

#### Scenario: Memory Creation Timestamp

- **WHEN** a MemoryCreate object is processed
- **THEN** the system uses the specified timestamp or generates current timestamp

### Requirement: Memory Query Model

The system SHALL provide a MemoryQuery model for querying similar memories.

#### Scenario: Memory Query Validation

- **WHEN** a MemoryQuery object is validated
- **THEN** the system validates required fields and embedding dimensions

#### Scenario: Memory Query with Default Limit

- **WHEN** a MemoryQuery object is created without explicit limit
- **THEN** the system uses the default limit of 5

### Requirement: Embedding Request Model

The system SHALL provide an EmbeddingRequest model for requesting embeddings.

#### Scenario: Single Text Embedding Request

- **WHEN** an EmbeddingRequest is created with a single string input
- **THEN** the system validates the input and provides appropriate defaults

#### Scenario: Multiple Text Embedding Request

- **WHEN** an EmbeddingRequest is created with an array of strings
- **THEN** the system validates each input string in the array

#### Scenario: Embedding Request with Model Specification

- **WHEN** an EmbeddingRequest is created with a specific model
- **THEN** the system validates and uses the specified model

#### Scenario: Default Model in Embedding Request

- **WHEN** an EmbeddingRequest is created without a model
- **THEN** the system uses the default embedding model

### Requirement: Embedding Response Model

The system SHALL provide an EmbeddingResponse model for embedding results.

#### Scenario: Embedding Response Validation

- **WHEN** an EmbeddingResponse is created
- **THEN** the system validates the data structure and usage information

#### Scenario: Embedding Response Format

- **WHEN** an embedding request is processed
- **THEN** the system returns response in OpenAI-compatible format

#### Scenario: Embedding Data Structure

- **WHEN** embeddings are returned in a response
- **THEN** the system formats each embedding with object type, embedding vector, and index

### Requirement: Vector Operations Models

The system SHALL provide models for vector upsert and query operations.

#### Scenario: Vector Upsert Request Validation

- **WHEN** a VectorUpsertRequest is validated
- **THEN** the system validates required fields (namespace, text, embedding)

#### Scenario: Vector Upsert with Optional ID

- **WHEN** a VectorUpsertRequest includes an optional ID
- **THEN** the system validates and includes the ID in the operation

#### Scenario: Vector Upsert with Metadata

- **WHEN** a VectorUpsertRequest includes metadata
- **THEN** the system validates and processes the optional metadata

#### Scenario: Vector Query Request Validation

- **WHEN** a VectorQueryRequest is validated
- **THEN** the system validates required fields (namespace, embedding) and defaults for optional fields

#### Scenario: Vector Query with Default Top-K

- **WHEN** a VectorQueryRequest is created without top_k
- **THEN** the system uses the default top_k value of 5

#### Scenario: Vector Query Response Format

- **WHEN** a VectorQueryRequest is processed
- **THEN** the system returns results in the VectorQueryResponse format

### Requirement: Base API Response Model

The system SHALL provide a base model for API responses.

#### Scenario: API Response Validation

- **WHEN** an APIResponse is created
- **THEN** the system validates required fields and optional content

### Requirement: Health Response Model

The system SHALL provide a model for health check responses.

#### Scenario: Health Response Validation

- **WHEN** a HealthResponse is created for the health check endpoint
- **THEN** the system validates required fields (status) and defaults for optional fields

### Requirement: Chat Request Model

The system SHALL provide models for chat requests with proper validation.

#### Scenario: Chat Embedding Request Validation

- **WHEN** a ChatEmbeddingRequest is validated
- **THEN** the system validates required fields (session_id) and validates the session ID format

#### Scenario: Chat Request Text Validation

- **WHEN** a ChatEmbeddingRequest includes text content
- **THEN** the system validates the text content according to validation rules

#### Scenario: Chat Request Embedding Validation

- **WHEN** a ChatEmbeddingRequest includes an embedding
- **THEN** the system validates the embedding dimensions and values

#### Scenario: Chat Request Session ID Validation

- **WHEN** a ChatEmbeddingRequest is validated
- **THEN** the system validates the session ID against security requirements

#### Scenario: Chat Request Text Retrieval

- **WHEN** a ChatEmbeddingRequest has both text and prompt_text
- **THEN** the system provides a method to get the primary text content

### Requirement: Chat Response Model

The system SHALL provide models for chat responses.

#### Scenario: Chat Response Validation

- **WHEN** a ChatResponse is created
- **THEN** the system validates the response format and content

### Requirement: Embedding Data Model

The system SHALL provide a model for individual embedding data.

#### Scenario: Embedding Data Validation

- **WHEN** an EmbeddingData object is created
- **THEN** the system validates the embedding vector and index

#### Scenario: Embedding Vector Format

- **WHEN** embeddings are stored in EmbeddingData
- **THEN** the system ensures the embedding is a list of floats

### Requirement: Validation Models

The system SHALL provide models with appropriate validation using Pydantic.

#### Scenario: Field Type Validation

- **WHEN** models are instantiated with incorrect field types
- **THEN** the system raises appropriate validation errors

#### Scenario: Required Field Validation

- **WHEN** models are instantiated without required fields
- **THEN** the system raises appropriate validation errors

#### Scenario: Field Value Validation

- **WHEN** models are instantiated with invalid field values
- **THEN** the system raises appropriate validation errors

### Requirement: Model Serialization

The system SHALL provide proper serialization and deserialization for all models.

#### Scenario: JSON Serialization

- **WHEN** models need to be serialized to JSON
- **THEN** the system provides proper JSON representation

#### Scenario: JSON Deserialization

- **WHEN** JSON data needs to be converted to models
- **THEN** the system validates and creates appropriate model instances

### Requirement: Session ID Validation in Models

The system SHALL validate session IDs according to security requirements.

#### Scenario: Session ID Format Validation

- **WHEN** models with session_id fields are validated
- **THEN** the system applies session ID format validation rules

#### Scenario: Session ID Character Validation

- **WHEN** session IDs are validated
- **THEN** the system ensures they contain only allowed characters (alphanumeric, hyphens, underscores)

#### Scenario: Session ID Length Validation

- **WHEN** session IDs are validated
- **THEN** the system ensures they are within allowed length limits

### Requirement: Memory Creation Model

The system SHALL provide a MemoryCreate model for creating new memory entries.

#### Scenario: Memory Creation Validation

- **WHEN** a MemoryCreate object is validated
- **THEN** the system validates required fields and embedding dimensions

### Requirement: Memory Query Model

The system SHALL provide a MemoryQuery model for querying similar memories.

#### Scenario: Memory Query Validation

- **WHEN** a MemoryQuery object is validated
- **THEN** the system validates required fields and embedding dimensions

### Requirement: Embedding Request Model

The system SHALL provide an EmbeddingRequest model for requesting embeddings.

#### Scenario: Single Text Embedding Request

- **WHEN** an EmbeddingRequest is created with a single string input
- **THEN** the system validates the input and provides appropriate defaults

#### Scenario: Multiple Text Embedding Request

- **WHEN** an EmbeddingRequest is created with an array of strings
- **THEN** the system validates each input string in the array

### Requirement: Embedding Response Model

The system SHALL provide an EmbeddingResponse model for embedding results.

#### Scenario: Embedding Response Validation

- **WHEN** an EmbeddingResponse is created
- **THEN** the system validates the data structure and usage information

### Requirement: Vector Operations Models

The system SHALL provide models for vector upsert and query operations.

#### Scenario: Vector Upsert Request Validation

- **WHEN** a VectorUpsertRequest is validated
- **THEN** the system validates required fields (namespace, text, embedding)

#### Scenario: Vector Query Request Validation

- **WHEN** a VectorQueryRequest is validated
- **THEN** the system validates required fields (namespace, embedding) and defaults for optional fields

### Requirement: Base API Response Model

The system SHALL provide a base model for API responses.

#### Scenario: API Response Validation

- **WHEN** an APIResponse is created
- **THEN** the system validates required fields and optional content

## MODIFIED Requirements

## REMOVED Requirements
