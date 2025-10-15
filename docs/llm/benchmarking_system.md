# GhostWire Refractory - Benchmarking & GHOSTWIRE Scoring System

## GHOSTWIRE Scoring Overview
The GHOSTWIRE scoring system provides standardized metrics to evaluate and compare AI models across multiple dimensions including performance, quality, stability, and efficiency. Each score combines multiple factors into a single normalized value where higher values indicate better performance.

## Scoring Functions

### 1. General GHOSTWIRE Score
- Formula: weight_latency × normalized_latency + weight_stability × normalized_stability + weight_memory × normalized_memory
- Default weights: latency=0.5, stability=0.3, memory=0.2
- normalized_latency = 1 / (1 + actual_latency)
- normalized_memory = 1 / (1 + actual_memory_usage)

### 2. RAG GHOSTWIRE Score
- Formula: weight_quality × normalized_quality + weight_hallucination × normalized_hallucination + weight_latency × normalized_latency
- Default weights: quality=0.4, hallucination=0.3, latency=0.3
- normalized_hallucination = 1 - hallucination_rate

### 3. Retrieval GHOSTWIRE Score
- Formula: weight_consistency × consistency_score + weight_similarity × similarity_score + weight_latency × normalized_latency
- Default weights: consistency=0.4, similarity=0.4, latency=0.2

### 4. Summarization GHOSTWIRE Score
- Formula: weight_quality × normalized_quality + weight_hallucination × normalized_hallucination + weight_length × length_penalty + weight_latency × normalized_latency
- Default weights: quality=0.4, hallucination=0.3, length=0.2, latency=0.1

### 5. Comprehensive GHOSTWIRE Score
- Combines latency, throughput, memory, quality, and stability
- Default weights: latency=0.2, throughput=0.2, memory=0.2, quality=0.3, stability=0.1

## Benchmark Categories

### Embedding Benchmarks (embedding_benchmarks.py)
- Tests embedding generation performance and stability
- Measures latency, memory usage, and embedding consistency using cosine similarity
- Calculates embedding-specific GHOSTWIRE scores
- Uses API endpoint: /api/v1/embeddings

### RAG Benchmarks (rag_benchmarks.py)
- Evaluates Retrieval-Augmented Generation systems
- Tests retrieval performance and generation quality
- Calculates RAG-specific GHOSTWIRE scores
- Uses API endpoints: /api/v1/embeddings and /api/v1/chat/chat_embedding

### Summarization Benchmarks (summarization_benchmarks.py)
- Assesses text summarization effectiveness
- Measures quality, factual accuracy, and generation speed
- Computes summarization-specific GHOSTWIRE scores
- Uses API endpoint: /api/v1/chat/chat_completion

### Model Comparison Benchmark (model_comparison_benchmark.py)
- Comprehensive evaluation across all benchmark categories
- Tests multiple models simultaneously across embedding, RAG, and summarization
- Ranks models based on overall GHOSTWIRE scores
- Provides comparative analysis for model selection

## Benchmark Implementation

### ghostwire_scoring.py Module
- Contains all GHOSTWIRE scoring algorithms
- Provides standardized scoring functions with configurable weights
- Normalized output in [0,1] range where higher is better
- Flexible architecture for adding new scoring categories

### Test Integration
- Dedicated benchmark test suite in tests/benchmark/
- @pytest.mark.benchmark markers for test identification
- JSON structure validation for benchmark outputs
- Continuous integration workflow with dedicated benchmark job

## Configuration
- Models to test are defined in settings.EMBED_MODELS
- Benchmark iterations and test data are configurable
- Scoring weights can be adjusted per use case
- Memory and timing measurements are collected automatically

## Output Format
Benchmark results include:
- Individual metric values (latency, memory, quality, etc.)
- GHOSTWIRE scores for each category
- Overall aggregated scores
- Metadata about the test environment
- Ranked model comparison based on overall GHOSTWIRE score