# GhostWire Refractory - Token Optimization Benchmarking

This document provides instructions for running token usage benchmarks to verify the core functionality of the token optimization features implemented in GhostWire Refractory.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Running Benchmarks](#running-benchmarks)
4. [Benchmark Components](#benchmark-components)
5. [Interpreting Results](#interpreting-results)
6. [Expected Outcomes](#expected-outcomes)

## Overview

The GhostWire Refractory token optimization system provides significant reduction in token usage through multiple complementary techniques:
- Token caching with similarity thresholds
- Context window optimization
- Intelligent response caching
- Configurable text summarization
- End-to-end integration of all optimizations

The benchmarking system measures the effectiveness of these optimizations and provides quantifiable metrics.

## Prerequisites

Before running benchmarks, ensure you have:
1. Python 3.12+ installed
2. Virtual environment activated
3. Required dependencies installed
4. GhostWire Refractory properly configured

```bash
# Navigate to project root
cd /path/to/ghostwire-refractory

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if not already installed
pip install -e .
```

## Running Benchmarks

### Method 1: Command Line Interface (Recommended)

The easiest way to run benchmarks is through the GhostWire CLI:

```bash
# Run token usage benchmarks
python -m ghostwire benchmark

# Run benchmarks with verbose output
python -m ghostwire benchmark --verbose

# Save benchmark report to specific file
python -m ghostwire benchmark --save-report my_benchmark_results.json

# Generate report only (without running benchmarks)
python -m ghostwire benchmark --report
```

### Method 2: Direct Module Execution

You can also run the benchmark module directly:

```bash
# Navigate to project root
cd /path/to/ghostwire-refractory

# Activate virtual environment
source .venv/bin/activate

# Run benchmarks directly
python python/ghostwire/utils/token_benchmark.py
```

### Method 3: Programmatic Access

For programmatic use, you can run benchmarks from Python code:

```python
import asyncio
from ghostwire.utils.token_benchmark import TokenBenchmarkSuite

# Create and run benchmark suite
async def run_benchmarks():
    suite = TokenBenchmarkSuite()
    await suite.run_all_benchmarks()
    
    # Generate and display report
    report = suite.generate_report()
    print(report)
    
    # Save report to file
    suite.save_report("benchmark_report.json")

# Run the benchmarks
asyncio.run(run_benchmarks())
```

## Benchmark Components

The benchmark suite consists of 5 major components that test different aspects of the token optimization system:

### 1. Caching Layer Benchmark
Measures token savings from the similarity-based caching system.

**Key Metrics:**
- Cache hit rates
- Query processing reduction
- Token savings percentage

### 2. Context Window Optimization Benchmark
Measures effectiveness of context selection and truncation.

**Key Metrics:**
- Context token reduction
- Information preservation
- Processing overhead

### 3. Summarization Optimization Benchmark
Measures text compression effectiveness.

**Key Metrics:**
- Compression ratios
- Token savings
- Quality preservation indicators

### 4. Response Caching Benchmark
Measures savings from repeated identical requests.

**Key Metrics:**
- Cache hit rates for identical queries
- Processing elimination
- Memory efficiency

### 5. End-to-End Optimization Benchmark
Measures combined effect of all optimizations working together.

**Key Metrics:**
- Overall token savings
- Performance impact
- Synergy between components

## Interpreting Results

### Sample Output
```
GhostWire Refractory - Token Usage Benchmark Report
====================================================
Generated: 2025-10-14 14:30:25

SUMMARY OF TOKEN OPTIMIZATION EFFECTIVENESS:
--------------------------------------------
Overall Token Savings: 44.5%
Total Tokens (Baseline): 6,227
Total Tokens (Optimized): 3,456
Tokens Saved: 2,771

INDIVIDUAL OPTIMIZATION RESULTS:
--------------------------------
CACHING LAYER:
  Description: Token caching layer with similarity thresholds
  Token Savings: 42.1%
  Tokens (Before): 190
  Tokens (After): 110
  Tokens Saved: 80
  Execution Time: 0.01ms

CONTEXT WINDOW OPTIMIZATION:
  Description: Context window optimization with token budgeting
  Token Savings: 23.8%
  Tokens (Before): 2,670
  Tokens (After): 2,034
  Tokens Saved: 636
  Execution Time: 0.13ms

OPTIMIZATION IMPACT SUMMARY:
----------------------------
The implemented token optimization features provide significant reductions in
token usage while maintaining quality and performance:

1. Caching Layer: Reduces redundant processing by caching similar queries
2. Context Window Optimization: Minimizes context tokens through smart selection
3. Response Caching: Eliminates processing for repeated identical requests
4. Summarization: Compresses long texts to reduce token consumption
5. End-to-End Integration: Combines all optimizations for maximum savings

EXPECTED PRODUCTION SAVINGS: 44.5% reduction in token usage
```

### Key Interpretation Points

1. **Overall Savings**: The primary metric showing total token usage reduction
2. **Component Effectiveness**: Individual contribution of each optimization layer
3. **Execution Time**: Performance overhead introduced by optimizations
4. **Token Distribution**: How tokens are distributed across different system components

## Expected Outcomes

### Typical Results
- **Overall Token Savings**: 40-50% reduction in token usage
- **Caching Layer**: 35-45% savings for similar query scenarios
- **Context Optimization**: 20-30% savings through smart selection
- **Summarization**: 70-90% savings for long text compression
- **Response Caching**: Variable based on query repetition patterns

### Performance Impact
- **Latency**: Minimal to negative impact (caching often improves response times)
- **Memory Usage**: Slight increase due to caching layers
- **CPU Usage**: Minimal additional overhead for optimization calculations

### Quality Preservation
- **Accuracy**: Maintained through similarity thresholds and intelligent selection
- **Relevance**: Preserved through context-aware optimization
- **Completeness**: Ensured through configurable compression ratios

## Troubleshooting

### Common Issues

1. **Module Not Found Errors**
   ```bash
   # Ensure you're in the correct directory
   cd /path/to/ghostwire-refractory
   
   # Ensure virtual environment is activated
   source .venv/bin/activate
   ```

2. **Permission Denied Errors**
   ```bash
   # Ensure proper file permissions
   chmod +x python/ghostwire/cli.py
   ```

3. **Dependency Issues**
   ```bash
   # Reinstall dependencies
   pip install -e .
   ```

### Logging and Debugging

Enable verbose logging for detailed benchmark information:

```bash
# Run with verbose output
python -m ghostwire benchmark --verbose

# Check log files for detailed diagnostics
tail -f logs/ghostwire.log
```

## Advanced Configuration

### Custom Benchmark Scenarios

You can customize benchmark scenarios by modifying the TokenBenchmarkSuite class in `python/ghostwire/utils/token_benchmark.py`:

```python
# Example: Custom test data
class CustomTokenBenchmark(TokenBenchmarkSuite):
    def __init__(self):
        super().__init__()
        self.custom_test_data = [
            # Your custom test scenarios
        ]
    
    async def run_custom_benchmark(self):
        # Your custom benchmark logic
        pass
```

### Performance Tuning

Adjust optimization parameters in `python/ghostwire/config/settings.py`:

```python
# Caching settings
CACHE_SIMILARITY_THRESHOLD = 0.85  # Adjust similarity threshold
CACHE_TTL_MINUTES = 120             # Adjust cache lifetime

# Context optimization settings
MAX_CONTEXT_TOKENS = 2048           # Adjust context window size
CONTEXT_COMPRESSION_STRATEGY = "hybrid"  # Adjust strategy

# Summarization settings  
SUMMARY_COMPRESSION_RATIO = 0.3    # Adjust compression ratio
```

## Conclusion

The GhostWire Refractory token optimization benchmarking system provides comprehensive measurement of token usage reduction across multiple optimization layers. By following these instructions, you can verify that all core functionality is working correctly and achieving the expected 40-50% token usage reduction.

Regular benchmarking is recommended to:
1. Monitor optimization effectiveness
2. Identify performance regressions
3. Tune parameters for specific use cases
4. Validate system upgrades and changes