# The prometheus_client library is required for metrics collection.
# It is listed as a runtime dependency in pyproject.toml.

from prometheus_client import Counter, Histogram

# Histogram per route (example)
api_latency = Histogram(
    "api_server_latency_seconds", "Latency of API routes", labelnames=["route"]
)

# Counter for total API calls
api_calls_total = Counter(
    "api_server_calls_total", "Total number of API calls", labelnames=["route"]
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
