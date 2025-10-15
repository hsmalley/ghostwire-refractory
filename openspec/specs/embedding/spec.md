# Embedding Capability Specification

## Purpose

The Embedding capability manages the generation and processing of vector embeddings from text inputs using Ollama-compatible APIs, with caching and model selection functionality.

## Requirements

### Requirement: Text Embedding Generation

The system SHALL generate embeddings for input text using available embedding models.

#### Scenario: Single Text Embedding Generation

- **WHEN** EmbeddingService.embed_text() is called with a text string
- **THEN** the system returns a normalized embedding vector of the specified dimension

#### Scenario: Empty Text Handling

- **WHEN** EmbeddingService.embed_text() is called with empty text
- **THEN** the system returns a zero vector of the configured embedding dimension

#### Scenario: API Communication Failure

- **WHEN** EmbeddingService.\_get_embedding_from_api() fails to communicate with Ollama
- **THEN** the system tries alternative endpoints before returning fallback vector

### Requirement: Batch Embedding Generation

The system SHALL generate embeddings for multiple text inputs in a single request.

#### Scenario: Multiple Text Embedding Generation

- **WHEN** EmbeddingService.create_embedding() is called with multiple text inputs
- **THEN** the system returns embeddings for each input text in order

#### Scenario: Mixed Input Types

- **WHEN** EmbeddingService.create_embedding() is called with non-string inputs
- **THEN** the system converts inputs to strings before embedding generation

### Requirement: Model Selection and Caching

The system SHALL select appropriate embedding models and cache successful models for efficiency.

#### Scenario: Automatic Model Selection

- **WHEN** EmbeddingService.create_embedding() is called without a specified model
- **THEN** the system tries available embedding models in order and caches the first successful one

#### Scenario: Model Caching

- **WHEN** EmbeddingService successfully generates embeddings with a model
- **THEN** the system caches that model for future requests

#### Scenario: Failed Model Handling

- **WHEN** all available models fail to generate embeddings
- **THEN** the system returns a fallback embedding vector

### Requirement: API Integration

The system SHALL integrate with Ollama-compatible embedding APIs to generate embeddings.

#### Scenario: Primary API Endpoint

- **WHEN** EmbeddingService.\_get_embedding_from_api() attempts to use /api/embeddings endpoint
- **THEN** the system makes requests to the primary endpoint first

#### Scenario: Fallback API Endpoint

- **WHEN** requests to /api/embeddings fail
- **THEN** the system attempts to use the /api/embed endpoint as fallback

#### Scenario: API Response Parsing

- **WHEN** API responses contain embeddings in different formats
- **THEN** the system handles various response formats (embedding, data.embedding, embeddings)

### Requirement: Embedding Fallback

The system SHALL provide fallback mechanisms when primary embedding generation fails.

#### Scenario: API Endpoint Fallback

- **WHEN** requests to /api/embeddings fail, the system tries /api/embed endpoint
- **THEN** the system returns embeddings if successfully generated from fallback endpoint

#### Scenario: Model Fallback

- **WHEN** all available models fail to generate embeddings
- **THEN** the system returns a small non-zero fallback embedding vector

#### Scenario: Dimension Mismatch Fallback

- **WHEN** generated embedding has different dimension than expected
- **THEN** the system truncates or pads the embedding to match the expected dimension

### Requirement: Embedding Validation

The system SHALL validate embeddings to ensure proper dimensions and values.

#### Scenario: Dimension Validation

- **WHEN** an embedding with incorrect dimension is generated
- **THEN** the system truncates or pads the embedding to match the expected dimension

#### Scenario: Value Sanitization

- **WHEN** an embedding contains non-finite values (NaN or infinity)
- **THEN** the system replaces these values with small finite numbers

#### Scenario: Zero Vector Prevention

- **WHEN** an embedding contains all zero values
- **THEN** the system replaces with small non-zero values to prevent all-zero vectors

### Requirement: Summarization Service

The system SHALL provide text summarization functionality to reduce token usage.

#### Scenario: Text Summarization

- **WHEN** SummarizationService.summarize_text() is called with text
- **THEN** the system returns a concise summary using the configured summarization model

#### Scenario: Summarization Disabled

- **WHEN** DISABLE_SUMMARIZATION setting is true
- **THEN** SummarizationService returns the original text unchanged

#### Scenario: Summarization Failure

- **WHEN** SummarizationService fails to generate a summary
- **THEN** the system returns the original text as fallback

### Requirement: Embedding Token Counting

The system SHALL provide token usage information with embedding responses.

#### Scenario: Token Count Calculation

- **WHEN** EmbeddingService.create_embedding() processes text inputs
- **THEN** the system calculates and returns prompt token counts in usage field

### Requirement: Error Handling

The system SHALL handle and log errors during embedding operations.

#### Scenario: Service Error Logging

- **WHEN** EmbeddingService encounters errors during processing
- **THEN** the system logs appropriate error messages for debugging

#### Scenario: Multiple Text Embedding Generation

- **WHEN** EmbeddingService.create_embedding() is called with an embedding request
- **THEN** the system processes each input text and returns corresponding embeddings

### Requirement: Model Selection and Caching

The system SHALL select appropriate embedding models and cache successful models for efficiency.

#### Scenario: Automatic Model Selection

- **WHEN** EmbeddingService.create_embedding() is called without a specified model
- **THEN** the system tries available embedding models in order and caches the first successful one

#### Scenario: Model Caching

- **WHEN** EmbeddingService successfully generates embeddings with a model
- **THEN** the system caches that model for future requests

### Requirement: API Integration

The system SHALL integrate with Ollama-compatible embedding APIs to generate embeddings.

#### Scenario: Ollama API Request

- **WHEN** EmbeddingService.\_get_embedding_from_api() is called with text and model
- **THEN** the system makes requests to Ollama endpoints and returns the embedding vector

### Requirement: Embedding Fallback

The system SHALL provide fallback mechanisms when primary embedding generation fails.

#### Scenario: API Endpoint Fallback

- **WHEN** requests to /api/embeddings fail, the system tries /api/embed endpoint
- **THEN** the system returns embeddings if successfully generated from fallback endpoint

#### Scenario: Model Fallback

- **WHEN** all available models fail to generate embeddings
- **THEN** the system returns a small non-zero fallback embedding vector

### Requirement: Embedding Validation

The system SHALL validate embeddings to ensure proper dimensions and values.

#### Scenario: Dimension Validation

- **WHEN** an embedding with incorrect dimension is generated
- **THEN** the system truncates or pads the embedding to match the expected dimension

#### Scenario: Value Sanitization

- **WHEN** an embedding contains non-finite values (NaN or infinity)
- **THEN** the system replaces these values with small finite numbers

### Requirement: Summarization Service

The system SHALL provide text summarization functionality to reduce token usage.

#### Scenario: Text Summarization

- **WHEN** SummarizationService.summarize_text() is called with text
- **THEN** the system returns a concise summary using the configured summarization model

## MODIFIED Requirements

## REMOVED Requirements
