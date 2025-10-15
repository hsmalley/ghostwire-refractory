<!-- OPENSPEC:START -->

# Proposal: Add unit test skeleton for vector normalization

Status: proposed

Owners: @hsmalley

## Summary

Add a minimal unit test to validate the vector normalization utility (`ghostwire/utils/vector_utils.py` or similar). This provides an onboarding test that runs quickly on laptops and demonstrates running pytest.

## Motivation

Small unit tests give contributors confidence when making changes and provide a low-friction example of how to run and write tests.

## Scope

- Add `python/tests/unit/test_vector_utils.py` with tests for normalization (unit-length behavior and zero-vector handling).
- Ensure tests run quickly and don't require heavy dependencies.

## Acceptance criteria

1. Test file exists and executes under `pytest`.
2. Tests validate normalization and zero-vector behavior.

## Implementation plan

1. Add test skeleton using pytest.
2. Run tests locally as a sanity check.

<!-- OPENSPEC:END -->
