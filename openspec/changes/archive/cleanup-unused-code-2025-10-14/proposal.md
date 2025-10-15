## Why

The GhostWire Refractory codebase contained unused files and incomplete functionality that needed to be cleaned up following Universal Janitor principles to reduce technical debt and improve maintainability.

## What Changes

- Remove empty clients directory that was never used
- Remove unused logging module that wasn't imported anywhere
- Implement the HNSW `_backfill_from_db()` method that was a placeholder
- Extract common vector normalization logic to shared utilities
- Create comprehensive OpenSpec documentation for all capabilities

## Impact

- Affected specs: utils, vector, changes
- Affected code: vector/hnsw_index.py, services/memory_service.py, utils/vector_utils.py, and various cleanup tasks
