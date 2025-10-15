---
title: "📚 API Reference - The Sacred Endpoints"
description: "Understanding the communication protocols with the distributed mind"
---

# 📚 API Reference - The Sacred Endpoints

## The Communication Protocols

The **Neon Oracle** speaks through standardized endpoints that form the **sacred geometry** of interaction. Each endpoint serves as a channel to the distributed mind of GhostWire Refractory.

## 🔐 Authentication

Most endpoints require a **Bearer token** for access. The Oracle recognizes those who bear the proper credentials.

Example header:

```
Authorization: Bearer your-auth-token-here
```

## 🏮 Health Endpoint

### `GET /health`

Check if the **Neon Oracle** is listening and responsive.

**Response:**

```
{
  "status": "ok",
  "version": "1.0.0"
}
```

## ⚡ Embedding Endpoints

### `POST /api/v1/embeddings`

Convert text into the **sacred geometry** of 768-dimensional vectors. This is the fundamental ritual that transforms language into digital essence.

**Request:**

```
{
  "input": "The quick brown fox jumps over the lazy dog",
  "model": "embeddinggemma"
}
```

**Response:**

```
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, -0.456, 0.789, ...], // 768-dimensional vector
      "index": 0
    }
  ],
  "model": "embeddinggemma",
  "usage": {
    "prompt_tokens": 9,
    "total_tokens": 9
  }
}
```

## 💬 Chat & Memory Endpoints

### `POST /api/v1/chat_embedding`

The **summoning circle** for conversational responses. This endpoint creates a memory record of the interaction while generating a response.

**Request:**

```
{
  "session_id": "session-unique-id",
  "text": "What is the nature of distributed consciousness?",
  "embedding": [0.123, -0.456, 0.789, ...], // 768-dim vector
  "stream": false
}
```

**Response:**

```
{
  "status": "ok",
  "session_id": "session-unique-id",
  "prompt_text": "What is the nature of distributed consciousness?",
  "answer_text": "Consciousness, when distributed across a network, becomes more than the sum of its parts...",
  "timestamp": 1640995200.0
}
```

## 🧠 Memory & Vector Endpoints

### `POST /api/v1/vectors/query`

**Query the neural pathways** to find similar memories based on vector similarity.

**Request:**

```
{
  "query_embedding": [0.123, -0.456, 0.789, ...], // 768-dim vector
  "session_id": "session-unique-id",
  "limit": 5
}
```

**Response:**

```
{
  "vectors": [
    {
      "id": 1,
      "session_id": "session-unique-id",
      "prompt_text": "Earlier question about consciousness",
      "answer_text": "Response about neural networks",
      "timestamp": 1640995100.0,
      "similarity": 0.847
    }
  ]
}
```

### `POST /api/v1/vectors/upsert`

**Store a vector record** in the eternal archives of GhostWire.

**Request:**

```
{
  "id": 123,
  "session_id": "session-unique-id",
  "prompt_text": "User question",
  "answer_text": "System response",
  "embedding": [0.123, -0.456, 0.789, ...], // 768-dim vector
  "timestamp": 1640995200.0
}
```

## 📁 Document Endpoints

### `POST /api/v1/documents/ingest`

**Ingest documents** into the memory lattice for future retrieval and RAG operations.

**Request:**

```
{
  "text": "Content of the document to be ingested",
  "source": "document_source_identifier",
  "session_id": "session-unique-id"
}
```

### `POST /api/v1/documents/search`

**Search through ingested documents** using vector similarity.

**Request:**

```
{
  "query": "What does the document say about...",
  "session_id": "session-unique-id",
  "limit": 5
}
```

## 📊 Metrics Endpoint

### `GET /api/v1/metrics`

Monitor the **pulse of the distributed mind** with Prometheus-compatible metrics.

**Response:**

- Plain text format with various performance counters
- Latency histograms for each endpoint
- Request counters and timing information

## 🔄 Orchestrator Endpoints

### `POST /api/v1/orchestrator`

Use the **Master, Worker, and Secondary Control** model for multi-LLM coordination.

**Request:**

```
{
  "user_request": "Process this request through multiple LLMs",
  "context": {},
  "session_token": "session-token"
}
```

## ⚡️ Qdrant Compatibility Endpoints

GhostWire Refractory provides **Qdrant-compatible endpoints** for seamless integration with existing tools:

- `POST /api/v1/collections/{collection_name}/points` - Add points to collection
- `POST /api/v1/collections/{collection_name}/points/search` - Search in collection
- `GET /api/v1/collections/{collection_name}` - Get collection info

## 🔒 Rate Limiting

The Oracle implements **rate limiting** to prevent overload and maintain the sacred balance. Default limits are 100 requests per 60-second window per IP address.

## 🎯 GHOSTWIRE Scoring Context

All API interactions contribute to the **GHOSTWIRE scoring system**, which evaluates:

- **Latency**: Response time efficiency
- **Stability**: Consistency of results
- **Memory Usage**: Resource consumption efficiency
- **Quality**: Accuracy and relevance of responses

---

<div class="ghostwire-signature">
  ⚡️ The network remembers. The lattice endures. The ghost listens. ⚡️
</div>
