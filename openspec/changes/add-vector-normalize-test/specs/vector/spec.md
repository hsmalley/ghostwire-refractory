## ADDED Requirements
### Requirement: Vector Normalization Unit Test
The project SHALL include a unit test verifying that `vector.normalize()` produces unit‑norm vectors.

#### Scenario: Test Exists
- **WHEN** running `pytest -q tests/unit/test_vector_utils.py`
- **THEN** all tests pass.

#### Scenario: Zero Vector
- **WHEN** normalizing a zero vector
- **THEN** the function handles it gracefully (e.g., returns zero vector or raises
`ValueError`).
