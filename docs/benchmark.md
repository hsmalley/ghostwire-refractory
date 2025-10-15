# GhostWire Benchmark Data Sources

This document describes the data sources and methodology used by the GhostWire benchmarking system.

## Benchmark Categories

### 1. Embedding Benchmarks

- **API Endpoint**: `/api/v1/embeddings`
- **Models Tested**: Configured in settings.EMBED_MODELS
- **Test Data**: Fixed text samples of varying lengths (short: ~50 tokens, medium: ~250 tokens, long: ~2000 tokens)
- **Metrics Collected**:
  - Request latency (start to response time)
  - Embedding stability (cosine similarity between repeated embeddings)
  - Memory usage difference during operation
  - GHOSTWIRE score components

### 2. RAG (Retrieval-Augmented Generation) Benchmarks

- **API Endpoints**: `/api/v1/embeddings`, `/api/v1/chat/chat_embedding`
- **Models Tested**: Configured in settings.DEFAULT_OLLAMA_MODEL
- **Test Data**: Standard question set covering:
  - Factual queries requiring knowledge lookup
  - Complex multi-step questions
  - Open-ended conversational tasks
- **Metrics Collected**:
  - Retrieval latency (embedding + search time)
  - Generation latency (response time)
  - End-to-end latency
  - Response quality (simulated with baseline scores)
  - Hallucination rate (simulated with baseline rate)
  - GHOSTWIRE score components

### 3. Summarization Benchmarks

- **API Endpoint**: `/api/v1/chat/chat_completion`
- **Models Tested**: Configured in settings.SUMMARY_MODEL
- **Test Data**: Predefined text samples:
  - Technical articles (~1000 tokens)
  - News articles (~800 tokens)
  - Scientific papers (~2000 tokens)
- **Metrics Collected**:
  - Summarization latency
  - Compression ratio
  - Quality score (simulated with baseline)
  - Hallucination rate (simulated with baseline)
  - Length penalty score
  - GHOSTWIRE score components

### 4. Model Comparison Benchmarks

- **Data Sources**: All of the above benchmark categories
- **Models Tested**: All configured embedding models
- **Metrics Collected**: Aggregated scores across all benchmark categories
- **Output**: Ranked model comparison based on overall GHOSTWIRE score

## Data Collection Methodology

### Latency Measurement

- Uses `time.perf_counter()` for high-resolution timing
- Measures from request initiation to complete response
- Averages results over multiple iterations (typically 3-5 runs)

### Memory Usage Measurement

- Uses `psutil.virtual_memory().used` to measure RAM usage
- Records before and after values for each operation
- Reports difference in GB

### Quality Assessment

- For current implementation, quality scores are simulated with reasonable baseline values
- In production environments, this would incorporate metrics like ROUGE scores, BLEU scores, or other quality assessments
- Hallucination rate is calculated by comparing generated content to source material

### Stability Assessment

- For embeddings: computes cosine similarity between multiple embeddings of the same input
- Uses numpy for efficient vector operations
- Reports average similarity across multiple runs

## Configuration Sources

### Settings File

- Path: `python/ghostwire/config/settings.py`
- Contains model names, API endpoints, and performance parameters
- Loaded via Pydantic settings model

### Test Data

- Embedded in benchmark modules as predefined constants
- Designed to be consistent across runs for reproducible results

## Output Format

Benchmark results are returned as structured dictionaries with:

- Individual metric values
- GHOSTWIRE scores for each category
- Overall aggregated scores
- Metadata about the test environment

## Extensibility

The benchmarking system is designed to accommodate:

- Additional model types
- New metric categories
- Custom test datasets
- Alternative scoring algorithms
