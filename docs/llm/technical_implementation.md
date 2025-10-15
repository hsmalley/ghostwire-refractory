# GhostWire Refractory - Technical Implementation Details

## Configuration Management
- Uses Pydantic BaseSettings for configuration management
- Loads settings from environment variables
- Default values: DB_PATH="memory.db", EMBED_DIM=768, LOCAL_OLLAMA_URL="http://localhost:11434"

## Database Layer
- SQLite database with APSW driver for better performance
- Connection pooling with 5-10 connections and 10 overflow
- Schema includes memory_text table with columns: id, session_id, prompt_text, answer_text, timestamp, embedding (BLOB)
- Uses WAL (Write-Ahead Logging) mode for better concurrency

## Vector Indexing (HNSW)
- HNSW_MAX_ELEMENTS = 100000 (max elements in index)
- HNSW_EF_CONSTRUCTION = 200 (construction parameter)
- HNSW_M = 16 (max connections per element)
- HNSW_EF = 50 (query parameter)
- Embeddings are normalized before storage
- Supports both HNSW search and fallback cosine similarity

## API Endpoints Details

### Embeddings Endpoint (/api/v1/embeddings)
- Accepts input as string or array of strings
- Returns normalized embedding vectors
- Compatible with OpenAI embeddings API

### Chat with Memory (/api/v1/chat/chat_embedding)
- Accepts session_id, text/prompt_text, optional embedding
- Performs similarity search to retrieve relevant context
- Streams response from Ollama
- Stores conversation to memory after response

### Vector Operations
- Query endpoint: finds top-k most similar vectors
- Upsert endpoint: stores embeddings with metadata
- Uses cosine similarity for fallback when HNSW not available

## Service Layer Architecture
- MemoryService: Manages storage and retrieval of conversation history
- EmbeddingService: Handles generation and processing of embeddings
- RAGService: Orchestrates retrieval-augmented generation
- Error handling and validation at each layer

## Security Features
- JWT-based authentication with configurable expiration
- Session ID validation with regex pattern
- Rate limiting (default 100 requests per 60 seconds)
- SQL injection prevention via parameterized queries