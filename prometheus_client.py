# Minimal stub for prometheus_client used during development.
# This stub implements the interface used by the project:
#   - Histogram
#   - Counter
#   - generate_latest
#   - CONTENT_TYPE_LATEST
#
# The real prometheus_client library provides a fully featured
# client for Prometheus.  The stub here is sufficient for unit
# tests that only rely on the methods and attributes used in
# this repo.


class _BaseMetric:
    def __init__(self, name: str, documentation: str, labelnames=(), *args, **kwargs):
        self._name = name
        self._documentation = documentation
        self._labelnames = tuple(labelnames)
        self._data = {}

    def labels(self, **labels):
        # Return a proxy that stores values keyed by the labels tuple.
        key = tuple(labels.get(l, "") for l in self._labelnames)
        return _MetricProxy(self, key)


class _MetricProxy:
    def __init__(self, metric, key):
        self._metric = metric
        self._key = key

    # Histogram context manager
    def time(self):
        return _DummyContext()

    # Counter operation
    def inc(self, amount=1):
        self._metric._data[self._key] = self._metric._data.get(self._key, 0) + amount


class _DummyContext:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


class Histogram(_BaseMetric):
    def __init__(self, name, documentation, labelnames=()):
        super().__init__(name, documentation, labelnames)


class Counter(_BaseMetric):
    def __init__(self, name, documentation, labelnames=()):
        super().__init__(name, documentation, labelnames)


# Mimic the generate_latest function used in the metrics endpoint.


def generate_latest():  # pragma: no cover
    return b"# HELP fake_metric Fake metric for testing\n# TYPE fake_metric counter\nfake_metric 0\n"


# Content type used by prometheus_client.
CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
