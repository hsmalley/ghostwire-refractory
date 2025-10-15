# Project Context

## Purpose
GhostWire Refractory is a neural network-based chat system with persistent memory capabilities that enables contextual conversations through vector similarity search. The system stores message embeddings in SQLite and uses HNSW (Hierarchical Navigable Small World) for efficient vector similarity search. This is a heavily themed cyberpunk-inspired project that combines advanced retrieval-augmented generation (RAG) with a distinctive aesthetic and BDSM-infused metaphors throughout its architecture and documentation.
 
## Theme

See `openspec/THEME.md` for repository-wide style and tone guidance.

## Tech Stack
- Python 3.12+ (Language)
- FastAPI (Web framework with async/await patterns)
- SQLite with APSW (Database with connection pooling)
- HNSWlib (Vector indexing for fast similarity search)
- Pydantic (Data validation and settings management)
- httpx (HTTP client for async operations)
- numpy (Numerical operations for vector processing)
- pydantic-settings (Configuration management)
- uvicorn (ASGI server)
- passlib[bcrypt] (Password hashing)
- python-jose[cryptography] (JWT handling)

## Project Capabilities

The GhostWire Refractory system consists of several key capabilities:

- **API**: REST endpoints with OpenAI, Qdrant, and Ollama compatibility
- **Authentication**: JWT-based authentication and rate limiting  
- **CLI**: Command-line interface for system management
- **Configuration**: Settings management with Pydantic BaseSettings
- **Database**: SQLite connection pooling and data access
- **Embedding**: Vector generation from text inputs
- **Memory**: Persistent storage with vector similarity search
- **Models**: Pydantic data models for validation
- **Orchestrator**: Multi-LLM coordination with Master/Worker pattern
- **Utils**: Common helper functions and validation
- **Vector**: HNSW index management for similarity search

## Project Conventions

### Code Style
- Follows PEP 8 style guide with Ruff linter configured via pyproject.toml
- Line length set to 88 characters
- Type hints required for all function signatures
- Documentation strings required for all modules, classes, and functions
- Class names use PascalCase, functions and variables use snake_case
- Embrace the project's cyberpunk aesthetic in comments and documentation
- Use the thematic metaphors: controllers are "masters," clients are "submissive," rate limits are "safe words," auth tokens are "collars," and HNSW index is the "chain" that binds memories

### Architecture Patterns
- Hexagonal/Ports & Adapters architecture pattern
- Layered structure: API → Services → Database/Vector → Models
- Dependency injection through service instances
- Thread-safe connection pooling for database operations
- HNSW for O(log n) vector similarity search
- REST API with OpenAI-compatible endpoints
- Async/Await patterns for I/O operations
- Configuration through Pydantic BaseSettings with .env support
- Centralized error handling with GhostWireException hierarchy

### Testing Strategy
- Unit tests using pytest framework for individual components
- Integration tests to verify service interactions
- Test coverage focuses on core business logic, particularly the memory service and RAG functionality
- Mock external services (like Ollama) for consistent testing
- Tests use relative imports consistent with the project structure
- pytest-asyncio for async test functions

### Git Workflow
- Follows Conventional Commits specification with thematic twist
- Commit message format: `type(scope): description` where type includes:
  - `feat`: New features or capabilities
  - `fix`: Bug fixes and error corrections
  - `docs`: Documentation changes
  - `style`: Code style changes
  - `refactor`: Code refactoring
  - `test`: Adding or improving tests
  - `chore`: Maintenance tasks
- Branch naming typically follows feature/bugfix/hotfix patterns
- Theme-specific commit messages should reflect the cyberpunk aesthetic (e.g., "feat: Summon the neural lattice" instead of "feat: Add new feature")

## Domain Context
This is not just a technical codebase but a cyberpunk-themed system that combines advanced AI concepts with narrative elements. The "ghost" concept refers to the AI system itself, which maintains memory across conversations. Vector embeddings are used to retrieve relevant conversation history, creating a form of persistent memory. The system connects to Ollama for embedding generation and text generation. The BDSM metaphors are integral to the design: the controller(master) manages the flow while the client(submissive) requests and receives responses. Rate limiting acts as a "safe word" protecting the system, and authentication tokens function as "collars" granting access to participate in the network.

## Important Constraints
- Requires Python 3.12+ for compatibility with modern async features and dependencies
- SQLite database is used for storage instead of a full-scale distributed database
- Embedding dimension is fixed at 768 by default, requiring normalization of vectors
- HNSW library does not support vector deletion by default, requiring index rebuilds for removals
- The system is designed for single-server deployment and may require additional infrastructure for horizontal scaling
- The thematic elements are intentionally part of the documentation and should be maintained

## Current Development Status
- Codebase has been cleaned following Universal Janitor principles
- Unused files and directories have been removed
- Vector normalization logic has been extracted to shared utilities
- HNSW backfill functionality has been implemented
- OpenSpec documentation has been created for all major capabilities
- An OpenSpec change proposal has been created for token optimization features
- Completed changes have been archived appropriately

## Project Dashboard
For a complete overview of the project status, capabilities, and active changes, see openspec/dashboard.md

## External Dependencies
- Ollama API for embedding generation and text completion (local: http://localhost:11434, remote: http://100.103.237.60:11434)
- Various embedding models: embeddinggemma, granite-embedding, nomic-embed-text, mxbai-embed-large, snowflake-arctic-embed, all-minilm
- Generation models: gemma3:1b (default), gemma3:12b (remote)
- Third-party services may be accessed through the Ollama interface
- SQLite extensions may be used for enhanced security features if needed
