# GhostWire Refractory - Quick Start: Verifying Core Functionality

This guide provides a quick way to verify that all core token optimization functionality is working correctly in GhostWire Refractory.

## Quick Verification Steps

### 1. Run Token Usage Benchmarks

The fastest way to verify core functionality is to run the token usage benchmarks:

```bash
# Navigate to project root
cd /path/to/ghostwire-refractory

# Activate virtual environment
source .venv/bin/activate

# Run benchmarks (takes about 30 seconds)
python -m ghostwire benchmark

# Expected output:
# Overall Token Savings: 44.5%
# All individual components should show positive savings
```

### 2. Check Generated Reports

After running benchmarks, check the generated reports:

```bash
# Look for these files:
ls -la token_benchmark_report.json
cat token_benchmark_report.json | grep "savings_percentage"
```

Expected output should show positive savings percentages for all components.

### 3. Run Unit Tests

Verify that all new functionality passes unit tests:

```bash
# Navigate to project root
cd /path/to/ghostwire-refractory

# Activate virtual environment  
source .venv/bin/activate

# Run new unit tests
python -m pytest python/tests/unit/test_context_optimizer.py -v
python -m pytest python/tests/unit/test_enhanced_summarization.py -v

# Expected: All tests should pass
```

### 4. Test API Endpoints

Verify that Qdrant-compatible endpoints are working:

```bash
# Start the server in one terminal
cd /path/to/ghostwire-refractory
source .venv/bin/activate
python -m ghostwire

# In another terminal, test endpoints
curl -X PUT http://localhost:8000/api/v1/collections/test_collection
curl -X GET http://localhost:8000/api/v1/collections/test_collection  
curl -X DELETE http://localhost:8000/api/v1/collections/test_collection
```

## Expected Results

### Token Savings Benchmarks
- **Overall Savings**: ≥ 40% reduction in token usage
- **Caching Layer**: ≥ 35% savings for similar queries
- **Context Optimization**: ≥ 20% savings through smart selection
- **Summarization**: ≥ 70% savings for long texts
- **Response Caching**: Variable savings based on repetition

### Unit Tests
- **Context Optimizer Tests**: 12/12 should pass
- **Enhanced Summarization Tests**: 9/9 should pass
- **Enhanced Cache Service Tests**: Most should pass (some may have database locking issues in test environment)
- **Enhanced RAG Service Tests**: Core functionality tests should pass

### API Endpoints
- **PUT /collections/{name}**: Should return 200 OK
- **GET /collections/{name}**: Should return collection info
- **DELETE /collections/{name}**: Should return 200 OK

## Quick Health Check

Run this simple verification script:

```bash
#!/bin/bash
# quick_verify.sh

echo "GhostWire Refractory - Quick Functionality Verification"
echo "====================================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment active"

# Check if required modules are available
python -c "from ghostwire.utils.token_benchmark import *" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Token benchmark module available"
else
    echo "❌ Token benchmark module not available"
    exit 1
fi

# Check if context optimizer is available
python -c "from ghostwire.utils.context_optimizer import *" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Context optimizer module available"
else
    echo "❌ Context optimizer module not available"
    exit 1
fi

# Run a quick benchmark component
echo "Running quick benchmark test..."
python -c "
import asyncio
from ghostwire.utils.token_benchmark import TokenBenchmarkSuite
suite = TokenBenchmarkSuite()
# Run just one quick test to verify functionality
result = suite.benchmark_caching_layer()
print('✅ Quick benchmark test completed')
print(f'Expected savings: {result.savings_percentage:.1f}%')
"

if [ $? -eq 0 ]; then
    echo "✅ Core functionality verification successful!"
    echo ""
    echo "Next steps:"
    echo "1. Run full benchmarks: python -m ghostwire benchmark"
    echo "2. Run all unit tests: python -m pytest python/tests/unit/"
    echo "3. Start server: python -m ghostwire"
else
    echo "❌ Core functionality verification failed"
    exit 1
fi
```

## Troubleshooting

### If Benchmarks Fail
```bash
# Check Python version
python --version

# Check if dependencies are installed
pip list | grep -E "(fastapi|ruff|httpx|numpy)"

# Reinstall if needed
pip install -e .
```

### If Unit Tests Fail
```bash
# Check test environment
python -c "import pytest; print('pytest available')"

# Run tests with verbose output
python -m pytest python/tests/unit/ -v --tb=short
```

### If API Endpoints Don't Respond
```bash
# Check if server is running
ps aux | grep uvicorn

# Check server logs
tail -f logs/ghostwire.log
```

## Success Indicators

✅ **All Good Signs:**
- Benchmarks show 40-50% token savings
- Unit tests pass (especially context optimizer and summarization)
- API endpoints respond correctly
- No error messages in logs

⚠️ **Warning Signs:**
- Negative or zero savings in benchmarks
- Multiple unit test failures
- API endpoints return 500 errors
- Database locking errors in cache tests

❌ **Critical Issues:**
- Benchmark module not found
- Core modules fail to import
- Server fails to start
- Persistent database errors

## Next Steps After Verification

Once verification is successful:

1. **Document Results**: Save benchmark reports for future reference
2. **Configure Production Settings**: Adjust caching and optimization parameters
3. **Set Up Monitoring**: Implement logging and metrics collection
4. **Run Load Testing**: Verify performance under production loads
5. **Schedule Regular Benchmarks**: Monthly benchmarking to track optimization effectiveness

## Need Help?

If you encounter issues:

1. **Check Logs**: Look in `logs/` directory for detailed error messages
2. **Verify Installation**: Ensure all dependencies are properly installed
3. **Check Configuration**: Verify `.env` file settings are correct
4. **Review Documentation**: Consult specific component documentation
5. **Contact Support**: Reach out to the development team if needed

The GhostWire Refractory token optimization system should provide immediate and measurable benefits in token usage reduction while maintaining system performance and response quality.