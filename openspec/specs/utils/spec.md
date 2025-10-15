# Utilities Capability Specification

## Purpose

The Utilities capability provides common helper functions for security validation, error handling, and other shared functionality across the GhostWire Refractory system.

## Requirements

### Requirement: Session ID Validation

The system SHALL validate session ID format to prevent injection attacks and ensure proper formatting.

#### Scenario: Valid Session ID

- **WHEN** validate_session_id() is called with a valid alphanumeric session ID
- **THEN** the system returns true and raises no exception

#### Scenario: Invalid Session ID Characters

- **WHEN** validate_session_id() is called with invalid characters (e.g., SQL injection patterns)
- **THEN** the system raises a ValidationError

#### Scenario: Empty Session ID

- **WHEN** validate_session_id() is called with an empty string
- **THEN** the system raises a ValidationError

#### Scenario: Session ID Length Validation

- **WHEN** validate_session_id() is called with a session ID exceeding 64 characters
- **THEN** the system raises a ValidationError

#### Scenario: Session ID Type Validation

- **WHEN** validate_session_id() is called with a non-string value
- **THEN** the system raises a ValidationError

### Requirement: Text Content Validation

The system SHALL validate text content to prevent injection attacks and enforce length limits.

#### Scenario: Valid Text Content

- **WHEN** validate_text_content() is called with valid text within length limits
- **THEN** the system returns true and raises no exception

#### Scenario: Text Content Too Long

- **WHEN** validate_text_content() is called with text exceeding max_length
- **THEN** the system raises a ValidationError

#### Scenario: Text Content Injection Pattern

- **WHEN** validate_text_content() is called with potentially unsafe patterns (e.g., <script>)
- **THEN** the system raises a ValidationError

#### Scenario: Empty Text Content

- **WHEN** validate_text_content() is called with an empty string
- **THEN** the system raises a ValidationError

#### Scenario: Non-String Text Content

- **WHEN** validate_text_content() is called with a non-string value
- **THEN** the system raises a ValidationError

### Requirement: Embedding Validation

The system SHALL validate embedding vectors to ensure proper dimensions and finite values.

#### Scenario: Valid Embedding

- **WHEN** validate_embedding() is called with a properly sized embedding
- **THEN** the system returns true and raises no exception

#### Scenario: Dimension Mismatch

- **WHEN** validate_embedding() is called with incorrect dimension
- **THEN** the system raises an EmbeddingDimMismatchError

#### Scenario: Non-finite Values

- **WHEN** validate_embedding() is called with NaN or infinity values
- **THEN** the system raises a ValidationError

#### Scenario: Non-List Embedding

- **WHEN** validate_embedding() is called with non-list or non-tuple embedding
- **THEN** the system raises a ValidationError

### Requirement: Input Sanitization

The system SHALL provide basic input sanitization to remove potentially harmful content.

#### Scenario: Null Byte Removal

- **WHEN** sanitize_input() is called with text containing null bytes
- **THEN** the system returns the text with null bytes removed

#### Scenario: HTML Entity Encoding

- **WHEN** sanitize_input() is called with text containing HTML characters
- **THEN** the system returns the text with HTML characters encoded

### Requirement: Safe Filename Validation

The system SHALL validate filenames to prevent directory traversal and other attacks.

#### Scenario: Valid Filename

- **WHEN** is_safe_filename() is called with a safe filename
- **THEN** the system returns true

#### Scenario: Directory Traversal Prevention

- **WHEN** is_safe_filename() is called with filename containing "../"
- **THEN** the system returns false

#### Scenario: Dangerous Extension Prevention

- **WHEN** is_safe_filename() is called with executable extension (e.g., ".exe")
- **THEN** the system returns false

### Requirement: Error Handling Utilities

The system SHALL provide standardized error handling and conversion utilities.

#### Scenario: Exception Handling

- **WHEN** handle_exception() is called with a standard exception
- **THEN** the system returns an appropriate GhostWireException

#### Scenario: HTTP Exception Conversion

- **WHEN** handle_exception() is called with an HTTPException
- **THEN** the system returns the appropriate GhostWireException

#### Scenario: GhostWire Exception Pass-Through

- **WHEN** handle_exception() is called with a GhostWireException
- **THEN** the system returns the same exception unchanged

#### Scenario: Error Response Creation

- **WHEN** error_response() is called with error details
- **THEN** the system creates standardized error response with code, message, and details

### Requirement: Vector Utilities

The system SHALL provide shared vector utility functions accessible across services.

#### Scenario: Vector Normalization Utility

- **WHEN** normalize_vector() is called from vector_utils module
- **THEN** the system returns the input vector normalized to unit length

#### Scenario: Zero Vector Normalization

- **WHEN** normalize_vector() is called with a zero vector
- **THEN** the system returns the zero vector unchanged

### Requirement: GhostWire Exception Hierarchy

The system SHALL provide specialized exception classes for different error types.

#### Scenario: Validation Error

- **WHEN** ValidationError is raised
- **THEN** the system provides validation-specific error handling

#### Scenario: Database Error

- **WHEN** DatabaseError is raised
- **THEN** the system provides database-specific error handling

#### Scenario: Embedding Error

- **WHEN** EmbeddingError is raised
- **THEN** the system provides embedding-specific error handling

#### Scenario: Embedding Dimension Mismatch Error

- **WHEN** EmbeddingDimMismatchError is raised
- **THEN** the system provides dimension-specific error handling

#### Scenario: Memory Not Found Error

- **WHEN** MemoryNotFoundError is raised
- **THEN** the system provides memory-specific error handling

#### Scenario: Collection Not Found Error

- **WHEN** CollectionNotFoundError is raised
- **THEN** the system provides collection-specific error handling

#### Scenario: Authentication Error

- **WHEN** AuthenticationError is raised
- **THEN** the system provides authentication-specific error handling

#### Scenario: Authorization Error

- **WHEN** AuthorizationError is raised
- **THEN** the system provides authorization-specific error handling

#### Scenario: Rate Limit Exceeded Error

- **WHEN** RateLimitExceededError is raised
- **THEN** the system provides rate limiting-specific error handling

### Requirement: Error Conversion to HTTP

The system SHALL provide conversion from GhostWire exceptions to HTTP exceptions.

#### Scenario: Exception to HTTP Conversion

- **WHEN** GhostWireException.to_http_exception() is called
- **THEN** the system returns an appropriate HTTPException with details

### Requirement: Error Conversion to API Response

The system SHALL provide conversion from GhostWire exceptions to API error responses.

#### Scenario: Exception to API Error Conversion

- **WHEN** GhostWireException.to_api_error() is called
- **THEN** the system returns an APIError model with error details
