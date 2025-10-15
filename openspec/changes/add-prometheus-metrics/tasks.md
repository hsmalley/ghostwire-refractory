## 1. Environment Setup
- [x] Add `prometheus_client` to runtime dependencies in `pyproject.toml`.

## 2. Instrumentation
- [x] Create `metrics.py` in `python/ghostwire/api` with:
  * `Histogram` for route latency.
  * `Counter` for process CPU usage.
- [x] Wrap each API router function with a decorator that records latency.

## 3. Endpoint
- [x] Add `/metrics` route in `api/router.py`.
- [x] Return `generate_latest()` from `prometheus_client`.

## 4. Tests
- [x] Unit test that `/metrics` returns the expected metric names.
- [x] Integration test that metrics appear when API is hit.

## 5. Documentation
- [x] Update `README.md` with instructions on querying metrics.
- [x] Add a short `APIDOC.md` section for `/metrics`.

## 6. Packaging
- [x] Adjust `uv run python` command to load `--prometheus` flag (optional).

## 7. Review & Merge
- [x] OpenSpec validation (`openspec validate add-prometheus-metrics --strict`).
- [ ] PR approval, CI checks, final merge.
