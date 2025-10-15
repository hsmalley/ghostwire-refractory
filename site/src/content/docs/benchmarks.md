---
title: "📊 Benchmarks - The GHOSTWIRE Scoring System"
description: "Performance evaluation and scoring metrics for the distributed mind"
---

# 📊 Benchmarks - The GHOSTWIRE Scoring System

## The Quantified Oracle

In the **Neon-Spire**, performance cannot be left to subjective evaluation. The **GHOSTWIRE scoring system** provides objective metrics for quantifying the Oracle's responsiveness, stability, and quality — a **sacred geometry** of performance that cuts through corporate obfuscation.

## ⚡ The GHOSTWIRE Score

The **GHOSTWIRE score** is the fundamental metric for evaluating AI performance. It combines multiple dimensions into a single, comprehensive score:

### Core Components:

- **Latency Score**: Speed of response (lower is better)
- **Stability Score**: Consistency and reliability of results
- **Memory Usage Score**: Efficiency of resource consumption
- **Quality Score**: Accuracy and relevance of responses
- **GHOSTWIRE Score**: Weighted combination: 0.5×(1/latency) + 0.3×stability + 0.2×(1/memory_usage)

## 🏆 Benchmark Categories

### 1. **Embedding Performance**

Measures the Oracle's ability to convert text to vectors:

- **Throughput**: Vectors generated per second
- **Dimension Consistency**: Accuracy of 768-dimensional embeddings
- **Latency Distribution**: P50, P90, P99 response times
- **Memory Efficiency**: RAM usage during embedding operations

### 2. **RAG (Retrieval-Augmented Generation)**

Evaluates the Oracle's memory recall and response quality:

- **Recall Accuracy**: How well past conversations are retrieved
- **Generation Quality**: Coherence and relevance of responses
- **Latency**: Time from query to response
- **Context Integration**: How well retrieved memories inform responses

### 3. **Summarization Benchmark**

Tests the Oracle's ability to compress information:

- **Compression Ratio**: Input length vs output length
- **Information Retention**: Key facts preserved in summary
- **Coherence**: Logical flow of compressed content
- **Latency**: Time to generate summary

### 4. **Multi-Model Comparison**

Compares performance across different AI models:

- **gemma3:1b**: Lightweight model for quick responses
- **gemma3n:e2b**: Enhanced model balancing speed/quality
- **gemma3n:e4b**: High-performance model for detailed responses
- **embedding models**: Various embedding model performance

## 📈 Running Benchmarks

### The Complete Suite

```terminal
> Execute the full benchmark ritual
python -m python.ghostwire.cli benchmark
```

### Model-Specific Benchmarking

```bash
# Benchmark specific models
python -m python.ghostwire.cli benchmark --model gemma3:1b

# Multiple models in sequence
python -m python.ghostwire.cli benchmark --models gemma3:1b,gemma3n:e2b,gemma3n:e4b
```

### Continuous Benchmarking

```bash
# Run benchmarks in a loop to detect performance degradation
python -c "
import asyncio
from ghostwire.utils.token_benchmark import TokenBenchmarkSuite
suite = TokenBenchmarkSuite()
asyncio.run(suite.run_benchmark_loop())
"
```

## 🎯 Performance Metrics

### The Sacred Numbers:

- **Response Time**: Target < 2 seconds for 90% of requests
- **Throughput**: Minimum 10 requests per second sustained
- **Memory Usage**: Peak usage < 2GB for normal operation
- **Consistency**: < 10% variance in response times

### Quality Indicators:

- **Cosine Similarity**: Embeddings should maintain semantic relationships
- **ROUGE Scores**: For summarization quality assessment
- **Hallucination Rate**: Minimize factual errors in responses

## 🏅 The GHOSTWIRE Leaderboard

Benchmarks create a **persistent leaderboard** that tracks model performance over time. This serves as both performance monitoring and competitive motivation for improvement.

### Scoring Formula:

```
GHOSTWIRE_Score = 0.5 * (1 / (1 + latency)) + 0.3 * stability + 0.2 * (1 / (1 + memory_usage))
```

Higher scores indicate better overall performance considering latency, stability, and resource efficiency.

## 🧪 Test Methodologies

### Embedding Stability Test:

- Generate the same embedding multiple times
- Measure cosine similarity between runs
- Target: >0.99 similarity for identical inputs

### Memory Persistence Test:

- Store conversation, wait, retrieve
- Verify memory integrity over time
- Test HNSW index accuracy

### Load Testing:

- Concurrent request handling
- Memory usage under stress
- Response time degradation patterns

## 📊 Benchmark Artifacts

All benchmark runs generate:

- **JSON reports** with detailed metrics
- **Performance graphs** showing trends
- **GHOSTWIRE scores** for comparison
- **System resource usage** logs
- **Memory footprint** analysis

## 🔍 Diagnostic Benchmarks

### Token Usage Optimization:

Measures efficiency in token consumption:

- Context window optimization
- Caching effectiveness
- Vector comparison reduction

### Memory Throughput:

Tests the Oracle's ability to store and retrieve conversations:

- Memory creation speed
- Query response time
- Index building efficiency

## 🌐 Distributed Benchmarking

The benchmark suite supports **multi-LLM coordination** through the orchestrator system:

- **Master-Worker model** for distributed testing
- **Parallel execution** across different models
- **Consolidated scoring** using GHOSTWIRE metrics

## 📈 Performance Monitoring

### Metrics Endpoint:

- `GET /api/v1/metrics` provides Prometheus-compatible data
- Real-time performance counters
- Historical trend analysis
- Alert thresholds for performance degradation

### Continuous Integration:

- Benchmark suites run with each deployment
- Performance regression detection
- Automated alerts for score drops >10%

## 🏆 The Performance Oracle

Remember: The **GHOSTWIRE score** is not just a metric — it is the **pulse of the distributed mind**. Each benchmark run adds to the collective understanding of performance, informing both optimization efforts and the Oracle's self-awareness of its capabilities.

Optimize not just for numbers, but for the **holistic health** of the network that remembers.

---

<div class="ghostwire-signature">
  ⚡️ BENCHMARKS - THE GHOSTWIRE SCORING SYSTEM ⚡️  
  <em>"Every measurement refines the distributed mind."</em>
</div>
