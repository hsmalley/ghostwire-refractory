# The prometheus_client library is required for metrics collection.
# It is listed as a runtime dependency in pyproject.toml.

from fastapi import APIRouter, Response

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Histogram per route (example)
api_latency = Histogram(
    "api_server_latency_seconds", "Latency of API routes", labelnames=["route"]
)

# Counter for total API calls
api_calls_total = Counter(
    "api_server_calls", "Total number of API calls", labelnames=["route"]
)

# Counter for process CPU usage (simulated)
process_cpu_usage = Counter(
    "process_cpu_usage_seconds", "Process CPU usage time"
)

# Decorator to wrap route handlers
def instrument_route(route_name: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with api_latency.labels(route=route_name).time():
                api_calls_total.labels(route=route_name).inc()
                return await func(*args, **kwargs)

        return wrapper

    return decorator

# Create router for metrics endpoint
metrics_router = APIRouter()

@metrics_router.get("/metrics")
async def metrics():
    """Expose Prometheus metrics"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )