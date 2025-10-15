## 1. Environment Setup
- [ ] Add `prometheus_client` to runtime dependencies in `pyproject.toml`.

## 2. Instrumentation
- [ ] Create `metrics.py` in `python/ghostwire/api` with:
  * `Histogram` for route latency.
  * `Counter` for process CPU usage.
- [ ] Wrap each API router function with a decorator that records latency.

## 3. Endpoint
- [ ] Add `/metrics` route in `api/router.py`.
- [ ] Return `generate_latest()` from `prometheus_client`.

## 4. Tests
- [ ] Unit test that `/metrics` returns the expected metric names.
- [ ] Integration test that metrics appear when API is hit.

## 5. Documentation
- [ ] Update `README.md` with instructions on querying metrics.
- [ ] Add a short `APIDOC.md` section for `/metrics`.

## 6. Packaging
- [ ] Adjust `uv run python` command to load `--prometheus` flag (optional).

## 7. Review & Merge
- [ ] OpenSpec validation (`openspec validate add-prometheus-metrics --strict`).
- [ ] PR approval, CI checks, final merge.
