# Proposal: Add Benchmark Tests

## Why

The GhostWire ecosystem needs systematic automated tests that evaluate key NLP metrics (ROUGE‑1/2/L‑F1, ghostwire‑score, embedding stability, latency, memory usage). These tests will validate model quality and performance before releases.

## What Changes

- Create `tests/benchmark/` folder with legacy benchmark scripts.
- Add a `pytest` marker `@pytest.mark.benchmark` and update imports.
- Update CI workflow to run benchmark tests separately.
- Add new spec requirement for benchmark tests.

## Impact

- Adds a new capability **benchmark-tests** in `openspec/specs/core/spec.md`.
- No change to runtime APIs.

## Additional Notes

- Benchmarks may be time‑consuming; they should be run on dedicated CI jobs.
- Metrics are logged to the console and can be parsed by downstream tooling.
