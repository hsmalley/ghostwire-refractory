# Configuration Capability Specification

## Purpose

The Configuration capability manages application settings and environment variables using Pydantic BaseSettings, providing centralized configuration management for the GhostWire Refractory system.

## Requirements

### Requirement: Server Configuration

The system SHALL provide configurable server settings including host, port, and debug mode.

#### Scenario: Default Server Configuration

- **WHEN** Settings object is initialized without environment variables
- **THEN** the system uses default values (HOST: 0.0.0.0, PORT: 8000, DEBUG: false)

#### Scenario: Environment-Based Server Configuration

- **WHEN** Settings object is initialized with environment variables defined
- **THEN** the system uses the values from the environment variables

#### Scenario: Server Configuration Validation

- **WHEN** Settings object is initialized with invalid values
- **THEN** the system raises validation errors for improper configuration

### Requirement: Database Configuration

The system SHALL provide configurable database settings including path, pool size, and connection options.

#### Scenario: Database Path Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides a configurable DB_PATH with default value "memory.db"

#### Scenario: Connection Pool Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable DB_POOL_SIZE and DB_POOL_OVERFLOW settings

#### Scenario: Database Connection Parameters

- **WHEN** Settings object is initialized
- **THEN** the system provides SQLite optimization parameters (WAL mode, synchronous, cache size)

### Requirement: Vector Configuration

The system SHALL provide configurable vector settings including embedding dimension and HNSW parameters.

#### Scenario: Embedding Dimension Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable EMBED_DIM with default value 768

#### Scenario: HNSW Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable HNSW parameters (max_elements, ef_construction, M, ef)

### Requirement: Ollama Configuration

The system SHALL provide configurable Ollama settings including URLs and model names.

#### Scenario: Local Ollama Endpoint Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable LOCAL_OLLAMA_URL with default value

#### Scenario: Remote Ollama Endpoint Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable REMOTE_OLLAMA_URL with default value

#### Scenario: Default Model Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable DEFAULT_OLLAMA_MODEL and REMOTE_OLLAMA_MODEL

#### Scenario: Embedding Models Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable EMBED_MODELS list with default models

### Requirement: Summarization Configuration

The system SHALL provide configurable summarization settings including model and enable/disable.

#### Scenario: Summarization Model Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable SUMMARY_MODEL with default value

#### Scenario: Summarization Enable/Disable Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable DISABLE_SUMMARIZATION flag

### Requirement: CORS Configuration

The system SHALL provide configurable CORS settings for allowed origins.

#### Scenario: CORS Origins Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable ALLOWED_ORIGINS list with default values

### Requirement: Security Configuration

The system SHALL provide configurable security settings including JWT parameters and secret key.

#### Scenario: JWT Algorithm Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable JWT_ALGORITHM with default value

#### Scenario: Secret Key Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable SECRET_KEY with default value

#### Scenario: Token Expiration Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable ACCESS_TOKEN_EXPIRE_MINUTES with default value

### Requirement: Rate Limiting Configuration

The system SHALL provide configurable rate limiting settings.

#### Scenario: Rate Limit Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW

### Requirement: Logging Configuration

The system SHALL provide configurable logging settings.

#### Scenario: Log Level Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable LOG_LEVEL with default value

#### Scenario: Log File Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable LOG_FILE for file logging (optional)

### Requirement: Environment Configuration Loading

The system SHALL load configuration from .env files.

#### Scenario: .env File Loading

- **WHEN** Settings object is initialized
- **THEN** the system loads configuration from .env file if present

#### Scenario: Case Sensitive Environment Variables

- **WHEN** Settings object is initialized
- **THEN** the system treats environment variables as case sensitive

### Requirement: Configuration Validation

The system SHALL validate configuration settings at startup.

#### Scenario: Missing Required Configuration

- **WHEN** required configuration values are missing or invalid
- **THEN** the system raises validation errors

#### Scenario: Configuration Type Validation

- **WHEN** configuration values are of wrong type
- **THEN** the system raises validation errors with appropriate messages

#### Scenario: Environment-Based Server Configuration

- **WHEN** Settings object is initialized with environment variables defined
- **THEN** the system uses the values from the environment variables

### Requirement: Database Configuration

The system SHALL provide configurable database settings including path, pool size, and connection options.

#### Scenario: Database Path Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides a configurable DB_PATH with default value "memory.db"

#### Scenario: Connection Pool Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable DB_POOL_SIZE and DB_POOL_OVERFLOW settings

### Requirement: Vector Configuration

The system SHALL provide configurable vector settings including embedding dimension and HNSW parameters.

#### Scenario: Embedding Dimension Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable EMBED_DIM with default value 768

#### Scenario: HNSW Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable HNSW parameters (max_elements, ef_construction, M, ef)

### Requirement: Ollama Configuration

The system SHALL provide configurable Ollama settings including URLs and model names.

#### Scenario: Ollama Endpoint Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable LOCAL_OLLAMA_URL and REMOTE_OLLAMA_URL

#### Scenario: Model Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable DEFAULT_OLLAMA_MODEL and EMBED_MODELS

### Requirement: Summarization Configuration

The system SHALL provide configurable summarization settings including model and enable/disable.

#### Scenario: Summarization Model Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable SUMMARY_MODEL

#### Scenario: Summarization Enable/Disable

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable DISABLE_SUMMARIZATION flag

### Requirement: CORS Configuration

The system SHALL provide configurable CORS settings for allowed origins.

#### Scenario: CORS Origins Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable ALLOWED_ORIGINS list

### Requirement: Security Configuration

The system SHALL provide configurable security settings including JWT parameters and secret key.

#### Scenario: JWT Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable JWT_ALGORITHM and ACCESS_TOKEN_EXPIRE_MINUTES

#### Scenario: Secret Key Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable SECRET_KEY

### Requirement: Rate Limiting Configuration

The system SHALL provide configurable rate limiting settings.

#### Scenario: Rate Limit Configuration

- **WHEN** Settings object is initialized
- **THEN** the system provides configurable RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW

## MODIFIED Requirements

## REMOVED Requirements
