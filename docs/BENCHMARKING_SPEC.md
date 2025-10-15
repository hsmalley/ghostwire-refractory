# GHOSTWIRE Benchmarking Specification

## Overview

GHOSTWIRE benchmarking provides a standardized scoring system to evaluate and compare AI models across multiple dimensions including performance, quality, stability, and efficiency. This specification defines the methodology, scoring calculations, and implementation guidelines for benchmarking different model types.

## Purpose

- Provide objective, standardized metrics for model evaluation
- Enable fair comparison between different AI models
- Track performance improvements over time
- Guide model selection for specific use cases

## GHOSTWIRE Score Components

The GHOSTWIRE score synthesizes multiple performance and quality metrics into a single, normalized score where higher values indicate better performance.

### General GHOSTWIRE Score

Used for basic performance benchmarking where models are evaluated on latency, stability, and resource usage.

**Formula:**

```
Score = weight_latency × normalized_latency + weight_stability × normalized_stability + weight_memory × normalized_memory
```

Where:

- `normalized_latency = 1 / (1 + actual_latency)`
- `normalized_stability = stability_score` (0 to 1)
- `normalized_memory = 1 / (1 + actual_memory_usage)`

Default weights:

- weight_latency = 0.5
- weight_stability = 0.3
- weight_memory = 0.2

### RAG GHOSTWIRE Score

Designed specifically for Retrieval-Augmented Generation systems, evaluating quality, hallucination rate, and response time.

**Formula:**

```
Score = weight_quality × normalized_quality + weight_hallucination × normalized_hallucination + weight_latency × normalized_latency
```

Where:

- `normalized_quality = quality_score` (0 to 1)
- `normalized_hallucination = 1 - hallucination_rate`
- `normalized_latency = 1 / (1 + actual_latency)`

Default weights:

- weight_quality = 0.4
- weight_hallucination = 0.3
- weight_latency = 0.3

### Retrieval GHOSTWIRE Score

For evaluating retrieval systems based on consistency, similarity, and performance.

**Formula:**

```
Score = weight_consistency × consistency_score + weight_similarity × similarity_score + weight_latency × normalized_latency
```

Where:

- `normalized_latency = 1 / (1 + actual_latency)`

Default weights:

- weight_consistency = 0.4
- weight_similarity = 0.4
- weight_latency = 0.2

### Summarization GHOSTWIRE Score

Evaluates text summarization quality, accuracy, and performance.

**Formula:**

```
Score = weight_quality × normalized_quality + weight_hallucination × normalized_hallucination + weight_length × length_penalty + weight_latency × normalized_latency
```

Where:

- `normalized_latency = 1 / (1 + actual_latency)`

Default weights:

- weight_quality = 0.4
- weight_hallucination = 0.3
- weight_length = 0.2
- weight_latency = 0.1

### Comprehensive GHOSTWIRE Score

Advanced scoring for complete system evaluation incorporating multiple dimensions.

**Formula:**

```
Score = weight_latency × normalized_latency + weight_throughput × normalized_throughput + weight_memory × normalized_memory + weight_quality × normalized_quality + weight_stability × normalized_stability
```

Default weights:

- weight_latency = 0.2
- weight_throughput = 0.2
- weight_memory = 0.2
- weight_quality = 0.3
- weight_stability = 0.1

## Benchmark Categories

### 1. Embedding Benchmarks

Measures the quality and performance of vector embeddings.

**Metrics:**

- Latency: Time to generate embedding
- Stability: Consistency of embeddings for same input
- Memory usage: RAM consumption during operation

**Test Scenarios:**

- Short text embeddings (under 100 tokens)
- Medium text embeddings (100-500 tokens)
- Long text embeddings (500+ tokens)

### 2. RAG Benchmarks

Evaluates Retrieval-Augmented Generation systems.

**Metrics:**

- Retrieval latency: Time to retrieve relevant context
- Generation quality: Accuracy and coherence of output
- Hallucination rate: Frequency of generating factually incorrect information
- End-to-end latency: Total response time

**Test Scenarios:**

- Factual questions requiring knowledge lookup
- Complex multi-step queries
- Open-ended conversational tasks

### 3. Retrieval Benchmarks

Assesses the quality of information retrieval.

**Metrics:**

- Retrieval accuracy: Precision and recall of retrieved documents
- Consistency: Stability of results across multiple queries
- Latency: Time to return results

**Test Scenarios:**

- Semantic search queries
- Keyword-based searches
- Multi-modal retrieval (if supported)

### 4. Summarization Benchmarks

Measures text summarization effectiveness.

**Metrics:**

- Quality: Coherence and informativeness of summary
- Factual accuracy: Preservation of key facts
- Compression ratio: Balance between length and information density
- Latency: Time to generate summary

**Test Scenarios:**

- News article summarization
- Technical document summarization
- Multi-document summarization

## Implementation Guidelines

### Metric Calculation

1. **Latency**: Measure from request initiation to first response byte
2. **Stability**: Use cosine similarity to compare embeddings of identical inputs
3. **Quality**: Use ROUGE, BLEU, or other appropriate metrics for text quality
4. **Hallucination**: Compare output against source material for factual accuracy
5. **Memory**: Measure peak memory consumption during operation

### Scoring Normalization

All scores should be normalized to the range [0, 1] where:

- 0 represents the worst possible performance
- 1 represents perfect performance (theoretical or actual)

### Model Comparison

Models should be ranked by their overall GHOSTWIRE scores across relevant benchmarks. The model comparison benchmark runs all categories and produces a weighted average score.

## Usage Examples

### Running Individual Benchmarks

```
# Embedding benchmarks
python -m python.benchmarks.embedding_benchmarks --iterations 10

# RAG benchmarks
python -m python.benchmarks.rag_benchmarks

# Summarization benchmarks
python -m python.benchmarks.summarization_benchmarks

# Model comparison (comprehensive)
python -m python.benchmarks.model_comparison_benchmark --models gemma3:1b nomic-embed-text
```

### Interpreting Results

- Higher GHOSTWIRE scores indicate better performance
- Scores can be compared across different model types
- Category-specific scores help identify strengths and weaknesses
- The overall score provides a single metric for model selection

## Extensibility

The specification is designed to accommodate additional benchmark categories and scoring functions as needed. New metrics should follow the normalization guidelines and integrate with the existing scoring framework.

## Quality Assurance

- All benchmarks must be reproducible
- Results should include confidence intervals when appropriate
- Baseline measurements should be established and periodically validated
- Statistical significance should be considered when comparing models with close scores
