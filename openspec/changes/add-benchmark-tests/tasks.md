## Implementation

- [x] Move legacy benchmark scripts into `tests/benchmark/`.
- [x] Add `@pytest.mark.benchmark` markers to each test.
- [x] Update `tests/benchmark/test_ghostwire_benchmarks.py` imports to point to the new module locations.
- [x] Ensure `pytest.ini` includes `--maxfail=0` for benchmark tests.
- [x] Modify CI workflow (`.github/workflows/*`) to add a dedicated `benchmark` job that runs `pytest -m benchmark`.
- [x] Add a stub test that verifies the benchmark output JSON structure.
- [x] Document benchmark data sources in `docs/benchmark.md`.
- [x] Run local sanity check with `pytest -m benchmark`.
- [x] Validate with `openspec validate add-benchmark-tests --strict`.
- [x] Push and open a PR after approval.
