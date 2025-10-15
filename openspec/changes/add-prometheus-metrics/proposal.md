## Why

Visibility into API performance is critical for ops and for us to validate our latency improvements. Prometheus metrics give us the pulse of the GhostWire lattice.

## What Changes

- Add a `/metrics` endpoint returning Prometheus metrics.
- Record latency histograms per API route using `prometheus_client`.
- Expose a process latency counter for background jobs.

## Impact

- Affects the `api` capability (new endpoint, new metrics).
- Adds a new `vector`-like metric namespace (latency bucket).
- No breaking changes to existing clients; metrics are served on a separate path.
