# GhostWire Refractory API Documentation

GhostWire Refractory is a neural network-based chat system with memory that stores message embeddings in SQLite and uses HNSW for efficient vector similarity search.

## Base URL

The API is served at:
`http://localhost:8000/api/v1`

## Authentication

The API supports token-based authentication using JWT. Include your token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Health Check

**GET** `/health`

Check the health status of the API.

Response:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "message": ""
}
```

### Prometheus Metrics

**GET** `/metrics`

Retrieve Prometheus-compatible metrics for monitoring API performance.

Response:

Plain text response containing metrics in Prometheus exposition format:

```text
# HELP api_server_latency_seconds Latency of API routes
# TYPE api_server_latency_seconds histogram
api_server_latency_seconds_bucket{route="health",le="0.005"} 1.0
api_server_latency_seconds_bucket{route="health",le="0.01"} 1.0
# ...
# HELP api_server_calls_total Total number of API calls
# TYPE api_server_calls_total counter
api_server_calls_total{route="health"} 1.0
```

### Embeddings

**POST** `/embeddings`

Create embeddings for input text(s).

Request:

```json
{
  "input": "string or array of strings to embed",
  "model": "embedding model to use (optional)"
}
```

Response:

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ],
  "model": "model used",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

**GET** `/models`

List available models.

Response:

```json
{
  "object": "list",
  "data": [
    {
      "id": "model-name",
      "object": "model",
      "owned_by": "local"
    }
  ]
}
```

### Vectors

**POST** `/vectors/upsert`

Add or update a vector record.

Request:

```json
{
  "namespace": "collection name",
  "id": "optional ID",
  "text": "text content",
  "embedding": [0.1, 0.2, ...],
  "metadata": {"optional": "metadata"}
}
```

Response:

```json
{
  "object": "vector.upsert",
  "status": "ok",
  "id": "memory-id"
}
```

**POST** `/vectors/query`

Query similar vectors.

Request:

```json
{
  "namespace": "collection name",
  "embedding": [0.1, 0.2, ...],
  "top_k": 5
}
```

Response:

```json
{
  "object": "list",
  "data": [
    {
      "prompt_text": "similar content",
      "answer_text": "response content",
      "score": 0,
      "id": 1
    }
  ],
  "model": "namespace"
}
```

### Chat

**POST** `/chat_embedding`

Chat with embeddings for context retrieval.

Request:

```json
{
  "session_id": "session identifier (alphanumeric, hyphens, underscores only)",
  "text": "user message",
  "prompt_text": "alternative field for user message",
  "embedding": [0.1, 0.2, ...] (optional, will be generated if not provided),
  "context": "additional context (optional)"
}
```

Response: Streaming plain text response from the model.

**POST** `/chat_completion`

Simple chat completion without retrieval.

Request:

```json
{
  "session_id": "session identifier",
  "text": "user message",
  "prompt_text": "alternative field for user message"
}
```

Response:

```json
{
  "response": "model response"
}
```

**POST** `/memory`

Add a memory entry to the database.

Request:

```json
{
  "session_id": "session identifier",
  "text": "memory content",
  "prompt_text": "alternative field for content",
  "embedding": [0.1, 0.2, ...] (optional, will be generated if not provided)
}
```

Response:

```json
{
  "status": "ok",
  "message": "Memory created with ID: 1"
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes. Errors are returned in the following format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": {}
  }
}
```

## Rate Limiting

The API implements rate limiting. By default, you can make 100 requests per 60-second window.

## Configuration

The application behavior can be configured through environment variables:

- `HOST`: Host to bind the server to (default: "0.0.0.0")

- `PORT`: Port to bind the server to (default: 8000)

- `DEBUG`: Enable debug mode (default: False)

- `DB_PATH`: Path to SQLite database (default: "memory.db")

- `EMBED_DIM`: Dimension of embedding vectors (default: 768)

- `LOCAL_OLLAMA_URL`: Local Ollama API URL (default: "http://localhost:11434")

- `REMOTE_OLLAMA_URL`: Remote Ollama API URL (default: "http://100.103.237.60:11434")

- `DEFAULT_OLLAMA_MODEL`: Default Ollama model for generation (default: "gemma3:1b")

- `SUMMARY_MODEL`: Model for summarization (default: "gemma3:1b")

- `DISABLE_SUMMARIZATION`: Disable summarization features (default: False)

## Benchmarking Integration

The GhostWire Refractory API includes endpoints specifically designed to support comprehensive benchmarking with GHOSTWIRE scoring:

### Benchmarking Patterns

The following endpoint combinations are used for different benchmark categories:

#### Embedding Benchmarks
- **`/embeddings`**: Measures embedding generation performance and stability
- **Metrics**: Latency, consistency (cosine similarity), memory usage

#### RAG (Retrieval-Augmented Generation) Benchmarks  
- **`/embeddings`** + **`/chat_embedding`**: Measures end-to-end RAG performance
- **Metrics**: Retrieval quality, generation accuracy, hallucination rate, response time

#### Summarization Benchmarks
- **`/chat_completion`**: Measures text summarization effectiveness
- **Metrics**: Quality, compression ratio, factual accuracy, generation speed

### GHOSTWIRE Score Calculation

The benchmarking system uses these API endpoints to calculate standardized GHOSTWIRE scores:

- **General GHOSTWIRE Score**: Combines latency, stability, and memory usage metrics
- **RAG GHOSTWIRE Score**: Evaluates quality, hallucination rate, and response time
- **Retrieval GHOSTWIRE Score**: Assesses consistency, similarity, and performance
- **Summarization GHOSTWIRE Score**: Measures quality, accuracy, and efficiency

## Security

- All API requests should be made over HTTPS in production

- Session IDs must be alphanumeric and contain only hyphens and underscores

- Text content is validated to prevent common injection attacks

- Input lengths are limited to prevent abuse