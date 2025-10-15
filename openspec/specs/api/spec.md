# API Capability Specification

## Purpose
The API capability provides REST endpoints for the GhostWire Refractory system, including compatibility with OpenAI, Qdrant, and Ollama APIs to enable neural network-based chat with memory capabilities.

## Requirements

### Requirement: Health Check Endpoint
The system SHALL provide a health check endpoint to verify the system status.

#### Scenario: Health Check Success
- **WHEN** a GET request is made to `/health`
- **THEN** the system returns status "ok" with version information

### Requirement: Embeddings Endpoint
The system SHALL provide an endpoint to create embeddings for input text(s).

#### Scenario: Single Text Embedding
- **WHEN** a POST request is made to `/embeddings` with a single string input
- **THEN** the system returns an embedding vector with the specified model

#### Scenario: Multiple Text Embedding
- **WHEN** a POST request is made to `/embeddings` with an array of strings
- **THEN** the system returns embedding vectors for each input string

#### Scenario: Model Specification
- **WHEN** a POST request is made to `/embeddings` with a specific model parameter
- **THEN** the system attempts to use the specified model for embedding generation

### Requirement: Model Listing Endpoint
The system SHALL provide an endpoint to list available embedding models.

#### Scenario: Model Listing Success
- **WHEN** a GET request is made to `/models`
- **THEN** the system returns a list of available embedding models

### Requirement: Vector Operations Endpoint
The system SHALL provide endpoints for vector upsert and query operations.

#### Scenario: Vector Upsert
- **WHEN** a POST request is made to `/vectors/upsert` with namespace, text, and embedding
- **THEN** the system stores the vector and returns success status with the assigned ID

#### Scenario: Vector Query
- **WHEN** a POST request is made to `/vectors/query` with an embedding and top_k parameter
- **THEN** the system returns the most similar vectors from the specified namespace

### Requirement: Chat with Memory Endpoint
The system SHALL provide a chat endpoint that uses embeddings for context retrieval from memory.

#### Scenario: Chat with Memory Retrieval
- **WHEN** a POST request is made to `/chat_embedding` with session_id and text
- **THEN** the system retrieves relevant memories, generates response with context, and stores the interaction

#### Scenario: Streaming Response
- **WHEN** a chat request is made with streaming enabled
- **THEN** the system returns the response in a streaming format

### Requirement: Simple Chat Completion Endpoint
The system SHALL provide a simple chat completion endpoint without memory retrieval.

#### Scenario: Simple Chat Response
- **WHEN** a POST request is made to `/chat_completion` with session_id and text
- **THEN** the system returns a simple response without memory retrieval

### Requirement: Memory Storage Endpoint
The system SHALL provide an endpoint to store memories directly.

#### Scenario: Memory Storage
- **WHEN** a POST request is made to `/memory` with session_id, text, and optional embedding
- **THEN** the system stores the memory with generated or provided embedding

### Requirement: OpenAI Compatibility
The system SHALL provide API endpoints compatible with OpenAI's API schema.

#### Scenario: OpenAI-Compatible Request
- **WHEN** a client makes requests using OpenAI API format
- **THEN** the system processes the request and returns responses in OpenAI-compatible format

### Requirement: Qdrant Compatibility
The system SHALL provide API endpoints compatible with Qdrant's vector database API.

#### Scenario: Qdrant-Compatible Vector Operations
- **WHEN** a client makes requests using Qdrant API format
- **THEN** the system processes the request and returns responses in Qdrant-compatible format

### Requirement: Authentication
The system SHALL support token-based authentication using JWT.

#### Scenario: Authenticated Request
- **WHEN** an API request includes a valid Bearer token in the Authorization header
- **THEN** the system processes the request normally

#### Scenario: Unauthenticated Request
- **WHEN** an API request does not include a valid token
- **THEN** the system returns HTTP 401 Unauthorized

### Requirement: Rate Limiting
The system SHALL enforce rate limits to prevent API abuse.

#### Scenario: Within Rate Limit
- **WHEN** a client makes requests within the configured rate limit
- **THEN** the system processes requests normally

#### Scenario: Rate Limit Exceeded
- **WHEN** a client exceeds the configured number of requests within the time window
- **THEN** the system returns HTTP 429 Too Many Requests

### Requirement: Input Validation
The system SHALL validate input parameters and return appropriate error messages.

#### Scenario: Invalid Input Validation
- **WHEN** an API request includes invalid parameters
- **THEN** the system returns HTTP 422 Unprocessable Entity with validation errors

### Requirement: CORS Configuration
The system SHALL support CORS for cross-origin requests.

#### Scenario: Cross-Origin Request
- **WHEN** a browser client makes a cross-origin request to the API
- **THEN** the system allows requests from configured origins with appropriate headers

### Requirement: Embeddings Endpoint
The system SHALL provide an endpoint to create embeddings for input text(s).

#### Scenario: Single Text Embedding
- **WHEN** a POST request is made to `/embeddings` with a single string input
- **THEN** the system returns an embedding vector with the specified model

#### Scenario: Multiple Text Embedding
- **WHEN** a POST request is made to `/embeddings` with an array of strings
- **THEN** the system returns embedding vectors for each input string

### Requirement: Vector Operations Endpoint
The system SHALL provide endpoints for vector upsert and query operations.

#### Scenario: Vector Upsert
- **WHEN** a POST request is made to `/vectors/upsert` with namespace, text, and embedding
- **THEN** the system stores the vector and returns success status with the assigned ID

#### Scenario: Vector Query
- **WHEN** a POST request is made to `/vectors/query` with an embedding and top_k parameter
- **THEN** the system returns the most similar vectors from the specified namespace

### Requirement: Chat with Memory Endpoint
The system SHALL provide a chat endpoint that uses embeddings for context retrieval from memory.

#### Scenario: Chat with Memory Retrieval
- **WHEN** a POST request is made to `/chat_embedding` with session_id and text
- **THEN** the system retrieves relevant memories, generates response with context, and stores the interaction

### Requirement: OpenAI Compatibility
The system SHALL provide API endpoints compatible with OpenAI's API schema.

#### Scenario: OpenAI-Compatible Request
- **WHEN** a client makes requests using OpenAI API format
- **THEN** the system processes the request and returns responses in OpenAI-compatible format

### Requirement: Qdrant Compatibility
The system SHALL provide API endpoints compatible with Qdrant's vector database API.

#### Scenario: Qdrant-Compatible Vector Operations
- **WHEN** a client makes requests using Qdrant API format
- **THEN** the system processes the request and returns responses in Qdrant-compatible format

## MODIFIED Requirements

## REMOVED Requirements